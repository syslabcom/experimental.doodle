from datetime import date
from Products.Five.browser import BrowserView


class DoodleView(BrowserView):
    """Render date options in a simple doodle-style table."""

    def rows(self):
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
            participants = sorted(getattr(item, "participants", set()) or set())
            rows.append(
                {
                    "title": item.Title(),
                    "date": when,
                    "participants": participants,
                }
            )
        return rows

    def date_label(self, value):
        if not isinstance(value, date):
            return "-"
        return value.strftime("%Y-%m-%d")
