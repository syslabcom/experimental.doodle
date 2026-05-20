from datetime import date

import plone.api
from Products.Five.browser import BrowserView


class DoodleView(BrowserView):
    """Render date options in a simple doodle-style table."""

    def rows(self):
        current = plone.api.user.get_current()
        userid = current.getId() if current else None
        items = [
            obj
            for obj in self.context.objectValues()
            if obj.portal_type == "experimental.doodle.date"
        ]

        def sort_key(item):
            value = getattr(item, "date", None)
            if isinstance(value, date):
                return value
            return date.max

        rows = []
        for item in sorted(items, key=sort_key):
            when = getattr(item, "date", None)
            values = getattr(item, "participants", None)
            if values is None:
                values = getattr(item, "participants", set())
            participants = sorted(values or set())
            rows.append(
                {
                    "title": item.Title(),
                    "date": when,
                    "participants": participants,
                    "selected": bool(userid and userid in participants),
                    "toggle_url": f"{item.absolute_url()}/@@toggle-participation",
                    "can_toggle": bool(userid),
                }
            )
        return rows

    def date_label(self, value):
        if not isinstance(value, date):
            return "-"
        return value.strftime("%Y-%m-%d")
