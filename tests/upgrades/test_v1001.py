"""Tests for the 1000 -> 1001 upgrade step."""

from experimental.doodle import PACKAGE_NAME
from experimental.doodle.upgrades.v1001 import install_poll_type
from plone import api


PROFILE = f"{PACKAGE_NAME}:default"


def _list_upgrades(setup_tool, source):
    """Return a flat list of upgrade step info dicts starting at ``source``."""
    grouped = setup_tool.listUpgrades(PROFILE, show_old=True)
    flat = []
    for entry in grouped:
        if isinstance(entry, list):
            flat.extend(entry)
        else:
            flat.append(entry)
    return [step for step in flat if step.get("ssource") == source]


class TestUpgradeStepRegistration:
    """The 1000 -> 1001 upgrade step is registered."""

    def test_upgrade_step_registered(self, integration):
        setup_tool = api.portal.get_tool("portal_setup")
        steps = _list_upgrades(setup_tool, "1000")

        destinations = {step.get("sdest") for step in steps}
        assert "1001" in destinations, (
            f"No 1000 -> 1001 upgrade step registered for {PROFILE}; "
            f"found destinations: {destinations}"
        )


class TestInstallPollTypeHandler:
    """The handler (re-)installs the Poll FTI."""

    def test_handler_restores_missing_poll_fti(self, integration):
        portal_types = api.portal.get_tool("portal_types")
        setup_tool = api.portal.get_tool("portal_setup")

        # Simulate a pre-1001 site: no Poll FTI yet.
        portal_types.manage_delObjects(["Poll"])
        assert "Poll" not in portal_types.objectIds()

        install_poll_type(setup_tool)

        assert "Poll" in portal_types.objectIds()
        fti = portal_types["Poll"]
        assert fti.klass == "experimental.doodle.content.poll.Poll"
        assert fti.schema == "experimental.doodle.content.poll.IPoll"

    def test_handler_is_idempotent(self, integration):
        portal_types = api.portal.get_tool("portal_types")
        setup_tool = api.portal.get_tool("portal_setup")

        # Poll is already there from the install profile.
        assert "Poll" in portal_types.objectIds()

        install_poll_type(setup_tool)
        install_poll_type(setup_tool)

        assert "Poll" in portal_types.objectIds()
