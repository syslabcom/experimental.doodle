"""Registry-backed settings and control panel for experimental.doodle."""

from experimental.doodle import _
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from zope import schema
from zope.interface import Interface


class IDoodleSettings(Interface):
    """Site-wide defaults for the experimental.doodle add-on."""

    default_poll_slot_duration = schema.Int(
        title=_("Default poll slot duration (minutes)"),
        description=_("Initial slot duration applied when a new Poll is created."),
        required=True,
        default=30,
        min=1,
    )

    default_booking_slot_duration = schema.Int(
        title=_("Default booking slot duration (minutes)"),
        description=_(
            "Initial slot duration applied when a new Booking Page is created."
        ),
        required=True,
        default=30,
        min=1,
    )

    allow_anonymous_voting = schema.Bool(
        title=_("Allow anonymous voting"),
        description=_(
            "When enabled, visitors who are not logged in may cast votes in polls."
        ),
        required=True,
        default=False,
    )

    require_booking_confirmation = schema.Bool(
        title=_("Require booking confirmation"),
        description=_(
            "When enabled, the organiser must confirm each booking request "
            "before it is finalised."
        ),
        required=True,
        default=False,
    )

    default_timezone = schema.TextLine(
        title=_("Default timezone"),
        description=_(
            "IANA timezone name used when displaying and computing slots "
            "(e.g. 'Europe/Amsterdam', 'UTC'). "
            "Full timezone support is not yet implemented."
        ),
        required=False,
        default="UTC",
    )


class DoodleSettingsForm(RegistryEditForm):
    """Edit form for site-wide doodle settings."""

    schema = IDoodleSettings
    schema_prefix = "experimental.doodle"
    label = _("Doodle Settings")
    description = _("Site-wide defaults for polls and booking pages.")


class DoodleSettingsControlPanel(ControlPanelFormWrapper):
    """Control panel view wrapping the DoodleSettingsForm."""

    form = DoodleSettingsForm
