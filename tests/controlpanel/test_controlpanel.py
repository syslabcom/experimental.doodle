"""Integration tests for the doodle control panel and registry settings."""

from experimental.doodle.controlpanels.doodle_settings import IDoodleSettings
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

import pytest


class TestRegistryRecords:
    """Registry records are created with correct default values on install."""

    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        """Use the integration testing layer."""

    def test_default_poll_slot_duration_exists(self, portal):
        registry = getUtility(IRegistry)
        assert "experimental.doodle.default_poll_slot_duration" in registry

    def test_default_poll_slot_duration_default(self, portal):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IDoodleSettings, prefix="experimental.doodle")
        assert settings.default_poll_slot_duration == 30

    def test_default_booking_slot_duration_exists(self, portal):
        registry = getUtility(IRegistry)
        assert "experimental.doodle.default_booking_slot_duration" in registry

    def test_default_booking_slot_duration_default(self, portal):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IDoodleSettings, prefix="experimental.doodle")
        assert settings.default_booking_slot_duration == 30

    def test_allow_anonymous_voting_exists(self, portal):
        registry = getUtility(IRegistry)
        assert "experimental.doodle.allow_anonymous_voting" in registry

    def test_allow_anonymous_voting_default_false(self, portal):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IDoodleSettings, prefix="experimental.doodle")
        assert settings.allow_anonymous_voting is False

    def test_require_booking_confirmation_exists(self, portal):
        registry = getUtility(IRegistry)
        assert "experimental.doodle.require_booking_confirmation" in registry

    def test_require_booking_confirmation_default_false(self, portal):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IDoodleSettings, prefix="experimental.doodle")
        assert settings.require_booking_confirmation is False

    def test_default_timezone_exists(self, portal):
        registry = getUtility(IRegistry)
        assert "experimental.doodle.default_timezone" in registry

    def test_default_timezone_default_utc(self, portal):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IDoodleSettings, prefix="experimental.doodle")
        assert settings.default_timezone == "UTC"

    def test_settings_are_mutable(self, portal):
        """Registry values can be updated after install."""
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IDoodleSettings, prefix="experimental.doodle")
        settings.default_poll_slot_duration = 60
        assert registry["experimental.doodle.default_poll_slot_duration"] == 60


class TestControlPanelRegistration:
    """Control panel configlet is registered after install."""

    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        """Use the integration testing layer."""

    def test_configlet_is_registered(self, portal):
        """The doodle-settings configlet appears in portal_controlpanel."""
        action_ids = [a.id for a in portal.portal_controlpanel.listActions()]
        assert "doodle-settings" in action_ids

    def test_configlet_title(self, portal):
        """The configlet has the correct title."""
        actions = {a.id: a for a in portal.portal_controlpanel.listActions()}
        assert actions["doodle-settings"].title == "Doodle Settings"

    def test_configlet_category(self, portal):
        """The configlet is filed under the Products category."""
        actions = {a.id: a for a in portal.portal_controlpanel.listActions()}
        assert actions["doodle-settings"].category == "Products"

    def test_configlet_url_contains_view_name(self, portal):
        """The configlet URL expression references @@doodle-settings."""
        actions = {a.id: a for a in portal.portal_controlpanel.listActions()}
        url_expr = actions["doodle-settings"].action.text
        assert "doodle-settings" in url_expr
