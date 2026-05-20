"""Tests for the Poll content type."""

from datetime import datetime
from datetime import timedelta
from datetime import timezone
from experimental.doodle.content.poll import IPoll
from experimental.doodle.content.poll import Poll
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from types import SimpleNamespace
from zope.interface import Invalid

import pytest


@pytest.fixture
def two_slots():
    """Return two timezone-aware datetimes in the future."""
    base = datetime.now(tz=timezone.utc) + timedelta(days=1)
    return [base, base + timedelta(hours=2)]


@pytest.fixture
def portal_with_manager(integration):
    """Portal with the test user elevated to Manager."""
    portal = integration["portal"]
    setRoles(portal, TEST_USER_ID, ["Manager"])
    return portal


class TestPollFTI:
    """The Poll FTI is registered by the install profile."""

    def test_fti_registered(self, portal_with_manager):
        portal_types = api.portal.get_tool("portal_types")
        assert "Poll" in portal_types.objectIds()

    def test_fti_meta_type(self, portal_with_manager):
        fti = api.portal.get_tool("portal_types")["Poll"]
        assert fti.meta_type == "Dexterity FTI"

    def test_fti_klass(self, portal_with_manager):
        fti = api.portal.get_tool("portal_types")["Poll"]
        assert fti.klass == "experimental.doodle.content.poll.Poll"

    def test_fti_schema(self, portal_with_manager):
        fti = api.portal.get_tool("portal_types")["Poll"]
        assert fti.schema == "experimental.doodle.content.poll.IPoll"

    def test_fti_is_leaf(self, portal_with_manager):
        """A Poll does not allow nested content."""
        fti = api.portal.get_tool("portal_types")["Poll"]
        assert fti.filter_content_types is True
        assert tuple(fti.allowed_content_types) == ()


class TestPollSchema:
    """The IPoll schema declares the expected fields."""

    def test_options_field_exists(self):
        assert "options" in IPoll
        assert IPoll["options"].required is True

    def test_options_value_type_is_datetime(self):
        from zope.schema import Datetime

        assert isinstance(IPoll["options"].value_type, Datetime)

    def test_options_default_is_empty_list(self):
        """The default lets the add form render before the user enters data."""
        field = IPoll["options"]
        # Either an explicit default of [] or a defaultFactory yielding [].
        default = field.default if field.default is not None else field.defaultFactory()
        assert default == []


class TestPollInvariant:
    """The 'at least two options' rule is enforced via a schema invariant."""

    def test_invariant_fails_with_one_option(self, two_slots):
        data = SimpleNamespace(options=[two_slots[0]])
        with pytest.raises(Invalid):
            IPoll.validateInvariants(data)

    def test_invariant_fails_with_empty_options(self):
        data = SimpleNamespace(options=[])
        with pytest.raises(Invalid):
            IPoll.validateInvariants(data)

    def test_invariant_passes_with_two_options(self, two_slots):
        data = SimpleNamespace(options=two_slots)
        # Must not raise.
        IPoll.validateInvariants(data)


class TestPollCreate:
    """A Poll can be created and round-trips its fields."""

    def test_create_poll(self, portal_with_manager, two_slots):
        poll = api.content.create(
            container=portal_with_manager,
            type="Poll",
            title="Team lunch",
            description="When can everyone make it?",
            options=two_slots,
        )

        assert poll.title == "Team lunch"
        assert poll.description == "When can everyone make it?"
        assert poll.options == two_slots

    def test_created_object_is_poll(self, portal_with_manager, two_slots):
        poll = api.content.create(
            container=portal_with_manager,
            type="Poll",
            title="Team lunch",
            options=two_slots,
        )

        assert isinstance(poll, Poll)
        assert IPoll.providedBy(poll)
