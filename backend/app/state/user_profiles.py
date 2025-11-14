from typing import Any, Dict, Optional

_USER_PROFILES: Dict[str, Dict[str, Any]] = {}


def set_profile(user_id: str, profile: Dict[str, Any]) -> None:
  """Store/overwrite the parsed profile for a user."""
  if not user_id or not isinstance(profile, dict):
    return
  _USER_PROFILES[user_id] = profile


def get_profile(user_id: Optional[str]) -> Optional[Dict[str, Any]]:
  if not user_id:
    return None
  return _USER_PROFILES.get(user_id)


def clear_profile(user_id: Optional[str]) -> None:
  if not user_id:
    return
  _USER_PROFILES.pop(user_id, None)
