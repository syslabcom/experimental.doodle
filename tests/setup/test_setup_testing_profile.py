from plone.app.testing import applyProfile

import plone.api


class TestTestingProfile:
    def test_testing_profile_creates_users_and_doodles(self, portal):
        applyProfile(portal, "experimental.doodle:testing")

        for username in ("alice", "bob", "carol", "dave"):
            assert plone.api.user.get(username=username) is not None

        doodles = [
            obj
            for obj in portal.objectValues()
            if obj.portal_type == "experimental.doodle.folder" and obj.getId().startswith("test-")
        ]
        assert len(doodles) == 10

        first = portal.get("test-01")
        assert first is not None
        options = [
            obj
            for obj in first.objectValues()
            if obj.portal_type == "experimental.doodle.date"
        ]
        assert len(options) == 3
