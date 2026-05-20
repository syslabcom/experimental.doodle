from datetime import date

from zope.annotation.interfaces import IAnnotations


ANSWERS_KEY = "experimental.doodle.answers"


def get_answers(context):
    """Return stored answers for a doodle."""
    return list(IAnnotations(context).get(ANSWERS_KEY, []))


def get_answer_for_user(context, userid):
    """Return one user's answer or None."""
    for entry in get_answers(context):
        if entry.get("userid") == userid:
            return entry
    return None


def upsert_answer(context, userid, display_name, selected_dates):
    """Create or replace a user's answer."""
    normalized = sorted({
        value.isoformat() if isinstance(value, date) else value
        for value in selected_dates
    })
    annotations = IAnnotations(context)
    answers = list(annotations.get(ANSWERS_KEY, []))
    for entry in answers:
        if entry.get("userid") == userid:
            entry["display_name"] = display_name
            entry["selected_dates"] = normalized
            annotations[ANSWERS_KEY] = answers
            return
    answers.append({
        "userid": userid,
        "display_name": display_name,
        "selected_dates": normalized,
    })
    annotations[ANSWERS_KEY] = answers


def build_results(context):
    """Aggregate counts and names per candidate date."""
    candidate_dates = list(context.candidate_dates or [])
    by_date = {
        candidate.isoformat(): {"count": 0, "names": []}
        for candidate in candidate_dates
    }
    for entry in get_answers(context):
        name = entry.get("display_name") or entry.get("userid")
        for selected in entry.get("selected_dates", []):
            if selected in by_date:
                by_date[selected]["count"] += 1
                by_date[selected]["names"].append(name)
    rows = []
    for candidate in candidate_dates:
        iso = candidate.isoformat()
        info = by_date[iso]
        rows.append({
            "date": candidate,
            "iso": iso,
            "count": info["count"],
            "names": info["names"],
        })
    rows.sort(key=lambda row: (-row["count"], row["iso"]))
    return rows
