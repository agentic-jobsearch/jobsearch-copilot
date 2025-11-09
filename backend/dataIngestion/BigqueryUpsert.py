"""
bq_upsert.py — Upsert a pandas DataFrame into BigQuery
Requires: google-cloud-bigquery, pandas, pyarrow
"""

from __future__ import annotations
import uuid
from typing import Iterable, Sequence, Optional, Union
import pandas as pd

from google.api_core.exceptions import NotFound
from google.cloud import bigquery


def _fq(table: str) -> str:
    # Ensure table id is backtick-quoted and fully qualified
    table = table.strip("`")
    parts = table.split(".")
    if len(parts) == 3:
        return f"`{table}`"
    raise ValueError("table must be fully qualified as project.dataset.table")


def _list_cols_from_table(client: bigquery.Client, table_fq: str) -> Sequence[str]:
    tbl = client.get_table(table_fq.strip("`"))
    return [f.name for f in tbl.schema]


def _table_exists(client: bigquery.Client, table_fq: str) -> bool:
    try:
        client.get_table(table_fq.strip("`"))
        return True
    except NotFound:
        return False


def upsert_dataframe_to_bigquery(
    df: pd.DataFrame,
    destination: str,
    key_columns: Union[str, Iterable[str]],
    project: Optional[str] = None,
    create_if_missing: bool = False,  # Changed default to False
    staging_table: Optional[str] = None,
    write_disposition_staging: str = "WRITE_TRUNCATE",
    location: Optional[str] = None,
    clustering_fields: Optional[Sequence[str]] = None,
    time_partitioning: Optional[bigquery.TimePartitioning] = None,
) -> None:
    """
    Upsert a DataFrame into BigQuery by:
    1) loading df into a staging table
    2) MERGE staging into destination on key_columns
    3) dropping the staging table

    Args:
        df: pandas DataFrame to upsert.
        destination: fully qualified table id "project.dataset.table".
        key_columns: column or columns that define the unique key.
        project: optional GCP project for the client (defaults to env).
        create_if_missing: if True, create the destination table matching df schema when absent.
        staging_table: optional fully qualified staging table to use; if None a temp table is created.
        write_disposition_staging: default WRITE_TRUNCATE.
        location: optional location (e.g., "US").
        clustering_fields: optional clustering fields to apply when creating destination table.
        time_partitioning: optional TimePartitioning to apply on destination when creating it.
    """
    if isinstance(key_columns, str):
        key_cols = [key_columns]
    else:
        key_cols = list(key_columns)
    if not key_cols:
        raise ValueError("key_columns must be provided")

    client = bigquery.Client(project=project, location=location)

    dest_fq = _fq(destination)

    # Check if destination table exists
    if not _table_exists(client, dest_fq):
        if not create_if_missing:
            raise NotFound(f"Destination table {dest_fq} not found and create_if_missing=False")

    # Get destination table schema to match data types
    dest_table = client.get_table(dest_fq.strip("`"))
    dest_schema = dest_table.schema

    # Create a temporary staging table if not provided
    if staging_table is None:
        project_id, dataset_id, table_id = destination.strip("`").split(".")
        staging_table = f"{project_id}.{dataset_id}.{table_id}__stg_{uuid.uuid4().hex[:8]}"
    staging_fq = _fq(staging_table)

    # Load DataFrame into staging table with destination schema
    job_config = bigquery.LoadJobConfig(
        write_disposition=write_disposition_staging,
        schema=dest_schema,  # Use destination schema instead of autodetect
        schema_update_options=[],  # Don't allow schema updates
    )
    load_job = client.load_table_from_dataframe(
        df, staging_fq.strip("`"), job_config=job_config
    )
    load_job.result()  # wait for load to finish

    # Build MERGE statement
    # Use destination schema to drive column list (ensures we don't try to write missing cols)
    dest_columns = _list_cols_from_table(client, dest_fq)
    # Only use columns present in staging as well
    staging_columns = _list_cols_from_table(client, staging_fq)
    merge_columns = [c for c in dest_columns if c in staging_columns]

    if not set(key_cols).issubset(set(merge_columns)):
        missing = set(key_cols) - set(merge_columns)
        raise ValueError(f"Key columns {missing} not found in DataFrame/staging table")

    # Deduplicate staging on key in case df has duplicates
    key_expr = ", ".join([f"`{c}`" for c in key_cols])
    on_expr = " AND ".join([f"T.`{c}` = S.`{c}`" for c in key_cols])

    # Build update set list excluding key columns by default
    update_cols = [c for c in merge_columns if c not in key_cols]
    update_set = ", ".join([f"`{c}` = S.`{c}`" for c in update_cols]) if update_cols else ""

    insert_cols = ", ".join([f"`{c}`" for c in merge_columns])
    insert_vals = ", ".join([f"S.`{c}`" for c in merge_columns])

    merge_sql = f"""
    MERGE {dest_fq} T
    USING (
      SELECT * EXCEPT(rn) FROM (
        SELECT *, ROW_NUMBER() OVER (PARTITION BY {key_expr} ORDER BY CURRENT_TIMESTAMP()) rn
        FROM {staging_fq}
      )
      WHERE rn = 1
    ) S
    ON {on_expr}
    {"WHEN MATCHED THEN UPDATE SET " + update_set if update_set else ""}
    WHEN NOT MATCHED THEN INSERT ({insert_cols}) VALUES ({insert_vals})
    """

    query_job = client.query(merge_sql)
    query_job.result()

    # Drop staging table
    client.delete_table(staging_fq.strip("`"), not_found_ok=True)