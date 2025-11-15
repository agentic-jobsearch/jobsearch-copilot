import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

_USER_PROFILES: Dict[str, Dict[str, Any]] = {}
_USER_FILES: Dict[str, Dict[str, str]] = {}
_PROFILE_DIR = Path("storage/profiles")
_PROFILE_DIR.mkdir(parents=True, exist_ok=True)


def _profile_path(user_id: str) -> Path:
  safe_id = user_id.replace("/", "_")
  return _PROFILE_DIR / f"{safe_id}.json"


def _files_path(user_id: str) -> Path:
  safe_id = user_id.replace("/", "_")
  return _PROFILE_DIR / f"{safe_id}_files.json"


def set_profile(user_id: str, profile: Dict[str, Any], files: Optional[Dict[str, str]] = None) -> None:
  """Store/overwrite the parsed profile and uploaded file metadata for a user."""
  if not user_id or not isinstance(profile, dict):
    return

  _USER_PROFILES[user_id] = profile
  _PROFILE_DIR.mkdir(parents=True, exist_ok=True)
  _profile_path(user_id).write_text(json.dumps(profile), encoding="utf-8")

  if files:
    _USER_FILES[user_id] = files
    _files_path(user_id).write_text(json.dumps(files), encoding="utf-8")


def get_profile(user_id: Optional[str]) -> Optional[Dict[str, Any]]:
  if not user_id:
    return None
  if user_id in _USER_PROFILES:
    return _USER_PROFILES[user_id]

  path = _profile_path(user_id)
  if path.exists():
    try:
      data = json.loads(path.read_text(encoding="utf-8"))
      _USER_PROFILES[user_id] = data
      return data
    except json.JSONDecodeError:
      return None
  return None


def get_files(user_id: Optional[str]) -> Dict[str, str]:
  if not user_id:
    return {}
  if user_id in _USER_FILES:
    return _USER_FILES[user_id]
  path = _files_path(user_id)
  if path.exists():
    try:
      data = json.loads(path.read_text(encoding="utf-8"))
      _USER_FILES[user_id] = data
      return data
    except json.JSONDecodeError:
      return {}
  return {}


def set_files(user_id: str, files: Dict[str, str]) -> None:
  if not user_id or not isinstance(files, dict):
    return
  _USER_FILES[user_id] = files
  _files_path(user_id).write_text(json.dumps(files), encoding="utf-8")


def clear_profile(user_id: Optional[str]) -> None:
  if not user_id:
    return
  _USER_PROFILES.pop(user_id, None)
  _USER_FILES.pop(user_id, None)
  profile_file = _profile_path(user_id)
  files_file = _files_path(user_id)
  if profile_file.exists():
    profile_file.unlink()
  if files_file.exists():
    files_file.unlink()
