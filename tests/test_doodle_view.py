from datetime import date

import plone.api


class TestDoodleView:
    def test_doodle_view_lists_sorted_dates(self, portal, request):
        with plone.api.env.adopt_roles(["Manager"]):
            folder = plone.api.content.create(
                container=portal,
                type="experimental.doodle.folder",
                id="poll",
                title="Poll",
            )

            plone.api.content.create(
                container=folder,
                type="experimental.doodle.date",
                id="late",
                title="Late option",
                date=date(2026, 6, 1),
                participants={"bob"},
            )
            plone.api.content.create(
                container=folder,
                type="experimental.doodle.date",
                id="early",
                title="Early option",
                date=date(2026, 5, 1),
                participants={"alice", "bob"},
            )

        view = folder.restrictedTraverse("@@doodle")
        html = view()

        assert "Early option" in html
        assert "Late option" in html
        assert html.index("Early option") < html.index("Late option")
        assert "alice" in html
        assert "bob" in html
