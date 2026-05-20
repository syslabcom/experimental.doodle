from datetime import date

import plone.api
from plone.protect.authenticator import createToken


class TestParticipation:
    def test_member_can_toggle_own_participation(self, portal):
        with plone.api.env.adopt_roles(["Manager"]):
            plone.api.user.create(
                username="alice",
                email="alice@example.com",
                roles=["Member"],
            )
            folder = plone.api.content.create(
                container=portal,
                type="experimental.doodle.folder",
                id="poll-toggle",
                title="Toggle Poll",
            )
            option = plone.api.content.create(
                container=folder,
                type="experimental.doodle.date",
                id="date1",
                title="Date 1",
                date=date(2026, 9, 1),
                participants=set(),
            )
            option.manage_setLocalRoles("alice", ["Owner"])
            option.reindexObjectSecurity()

        with plone.api.env.adopt_user(username="alice"):
            option.REQUEST.environ["REQUEST_METHOD"] = "POST"
            option.REQUEST.form["_authenticator"] = createToken()
            option.restrictedTraverse("@@toggle-participation")()
            assert "alice" in option.participants

            option.REQUEST.form["_authenticator"] = createToken()
            option.restrictedTraverse("@@toggle-participation")()
            assert "alice" not in option.participants
