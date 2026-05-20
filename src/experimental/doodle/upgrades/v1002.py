"""Upgrade step to profile version 1002: register Poll browser views."""

from experimental.doodle import logger
from experimental.doodle import PACKAGE_NAME


PROFILE_ID = f"profile-{PACKAGE_NAME}:default"


def install_poll_views(setup_tool):
    """Update the Poll FTI with the new default view on existing sites.

    Re-imports the ``typeinfo`` step from the default profile so that
    the ``default_view`` and ``view_methods`` on the Poll FTI are
    updated to include ``poll_view`` and ``results``.
    """
    logger.info("Upgrading to 1002: registering Poll browser views.")
    setup_tool.runImportStepFromProfile(PROFILE_ID, "typeinfo")
