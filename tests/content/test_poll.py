"""Integration tests for the Poll content type."""

import pytest


class TestPollTypeRegistration:
    def test_poll_fti_registered(self, portal):
        """Test that the Poll FTI is registered in portal_types."""
        assert "Poll" in portal.portal_types

    def test_poll_fti_meta_type(self, portal):
        """Test that the Poll FTI has the correct meta_type."""
        fti = portal.portal_types["Poll"]
        assert fti.meta_type == "Dexterity FTI"

    def test_poll_schema(self, portal):
        """Test that the Poll FTI references the correct schema."""
        fti = portal.portal_types["Poll"]
        assert fti.schema == "experimental.doodle.content.poll.IPoll"

    def test_poll_klass(self, portal):
        """Test that the Poll FTI references the correct class."""
        fti = portal.portal_types["Poll"]
        assert fti.klass == "experimental.doodle.content.poll.Poll"


class TestPollCreation:
    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        """Use the integration testing layer."""

    def test_poll_is_creatable(self, portal):
        """Test that a Poll object can be created."""
        import plone.api

        with plone.api.env.adopt_roles(["Manager"]):
            poll = plone.api.content.create(
                container=portal,
                type="Poll",
                id="test-poll",
                title="Team Meeting Poll",
            )
        assert poll is not None

    def test_poll_default_state(self, portal):
        """Test that a new Poll defaults to poll_state 'open'."""
        import plone.api

        with plone.api.env.adopt_roles(["Manager"]):
            poll = plone.api.content.create(
                container=portal,
                type="Poll",
                id="test-poll-state",
                title="State Test Poll",
            )
        assert poll.poll_state == "open"

    def test_poll_stores_location(self, portal):
        """Test that the location field can be set and read back."""
        import plone.api

        with plone.api.env.adopt_roles(["Manager"]):
            poll = plone.api.content.create(
                container=portal,
                type="Poll",
                id="test-poll-location",
                title="Location Test Poll",
                location="Room 42",
            )
        assert poll.location == "Room 42"

    def test_poll_proposed_slots_default_empty(self, portal):
        """Test that proposed_slots defaults to an empty list."""
        import plone.api

        with plone.api.env.adopt_roles(["Manager"]):
            poll = plone.api.content.create(
                container=portal,
                type="Poll",
                id="test-poll-slots",
                title="Slots Test Poll",
            )
        assert poll.proposed_slots == [] or poll.proposed_slots is None

    def test_poll_implements_ipoll(self, portal):
        """Test that a Poll object implements IPoll."""
        from experimental.doodle.content.poll import IPoll

        import plone.api

        with plone.api.env.adopt_roles(["Manager"]):
            poll = plone.api.content.create(
                container=portal,
                type="Poll",
                id="test-poll-iface",
                title="Interface Test Poll",
            )
        assert IPoll.providedBy(poll)
