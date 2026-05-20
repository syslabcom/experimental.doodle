"""Upgrade step to profile version 1001: install the Poll content type."""

from experimental.doodle import logger
from experimental.doodle import PACKAGE_NAME


PROFILE_ID = f"profile-{PACKAGE_NAME}:default"


def install_poll_type(setup_tool):
    """Register the Poll Dexterity FTI on sites installed before 1001.

    Re-imports the ``typeinfo`` step from the default profile, which is
    idempotent: existing FTIs are updated, missing ones are added.
    """
    logger.info("Upgrading to 1001: installing Poll content type.")
    setup_tool.runImportStepFromProfile(PROFILE_ID, "typeinfo")
