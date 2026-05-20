from datetime import date

from AccessControl import Unauthorized
from plone import api


def require_authenticated(request):
    """Raise Unauthorized for anonymous users."""
    if api.user.is_anonymous():
        raise Unauthorized()


def get_member_info():
    """Return userid and display name for the current member."""
    member = api.user.get_current()
    if member is None:
        return None, None
    userid = member.getId()
    return userid, member.getProperty("fullname") or userid


def can_view_results(context):
    """True if the current user may open the results view."""
    if api.user.is_anonymous():
        return False
    member = api.user.get_current()
    if member is None:
        return False
    if member.has_role("Manager"):
        return True
    creator = getattr(context, "Creator", lambda: None)()
    if creator == member.getId():
        return True
    if getattr(context, "allow_members_view_results", False):
        return True
    return False


def is_doodle_manager(context):
    """True if the current user may manage doodle settings (creator UI)."""
    if api.user.is_anonymous():
        return False
    member = api.user.get_current()
    if member is None:
        return False
    if member.has_role("Manager"):
        return True
    creator = getattr(context, "Creator", lambda: None)()
    return creator == member.getId()


def merge_proposed_dates(context, new_dates):
    """Add proposed dates to candidate_dates and return the merged list."""
    if not new_dates:
        return list(context.candidate_dates or [])
    existing = {
        value.isoformat() if isinstance(value, date) else value
        for value in (context.candidate_dates or [])
    }
    for value in new_dates:
        existing.add(value.isoformat() if isinstance(value, date) else value)
    merged = [date.fromisoformat(iso) for iso in sorted(existing)]
    with api.env.adopt_roles(["Manager"]):
        context.candidate_dates = merged
    return merged


def parse_iso_dates(values):
    """Parse and deduplicate ISO date strings from form input."""
    if not values:
        return []
    if isinstance(values, str):
        values = [values]
    parsed = []
    seen = set()
    for value in values:
        value = value.strip()
        if not value or value in seen:
            continue
        seen.add(value)
        parsed.append(date.fromisoformat(value))
    return parsed


def format_date(value):
    """Format a date for display."""
    if isinstance(value, str):
        value = date.fromisoformat(value)
    return value.strftime("%B %d, %Y")


def format_date_long(value):
    """Format a date with weekday for answer form labels."""
    if isinstance(value, str):
        value = date.fromisoformat(value)
    return value.strftime("%B %d, %Y · %A")
