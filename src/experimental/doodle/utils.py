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
    return creator == member.getId()


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
