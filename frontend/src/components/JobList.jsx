export default function JobList({ jobs, generatedDocs, onApplyClick }) {
  return (
    <div className="jobs-card">
      <h3 className="jobs-title">Matched Jobs</h3>
      <p className="jobs-subtitle">
        Based on your CV & transcript. Review and apply with one click.
      </p>

      <div className="jobs-list">
        {jobs.length === 0 && (
          <p className="jobs-empty">
            No jobs yet. Try: “Find junior software engineering jobs in Florida”.
          </p>
        )}

        {jobs.map((job) => {
          const matchScore = job.matchScore ?? job.match_score ?? 0;
          const jobId = job.id || job.job_id;

          return (
            <div key={jobId} className="job-item">
              <div className="job-main">
                <div>
                  <div className="job-title">{job.title}</div>
                  <div className="job-company">{job.company}</div>
                  <div className="job-meta">
                    {job.location} • Match score: {matchScore}
                  </div>
                </div>
                <button
                  className="job-apply-btn"
                  onClick={() => onApplyClick(job)}
                  aria-label={`Apply to ${job.title} at ${job.company}`}
                >
                  Apply
                </button>
              </div>
              {job.url && (
                <a
                  href={job.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="job-link"
                >
                  View posting
                </a>
              )}
            </div>
          );
        })}
      </div>

      {generatedDocs && (
        <div className="docs-preview">
          <h4>Generated CV (preview)</h4>
          <pre>{generatedDocs.cv}</pre>
          <h4>Cover Letter (preview)</h4>
          <pre>{generatedDocs.coverLetter}</pre>
        </div>
      )}
    </div>
  );
}
