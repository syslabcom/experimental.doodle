"""Booking Page content type."""

from experimental.doodle import _
from plone.dexterity.content import Item
from plone.supermodel import model
from zope import schema
from zope.interface import implementer
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


BOOKING_STATES = SimpleVocabulary([
    SimpleTerm(value="open", title=_("Open")),
    SimpleTerm(value="closed", title=_("Closed")),
])

WORKING_DAYS_VOCAB = SimpleVocabulary([
    SimpleTerm(value=0, title=_("Monday")),
    SimpleTerm(value=1, title=_("Tuesday")),
    SimpleTerm(value=2, title=_("Wednesday")),
    SimpleTerm(value=3, title=_("Thursday")),
    SimpleTerm(value=4, title=_("Friday")),
    SimpleTerm(value=5, title=_("Saturday")),
    SimpleTerm(value=6, title=_("Sunday")),
])


class IBookingPage(model.Schema):
    """Schema for a booking page."""

    organizer = schema.TextLine(
        title=_("Organizer"),
        description=_("Name or email address of the person accepting bookings."),
        required=False,
    )

    working_days = schema.List(
        title=_("Working days"),
        description=_(
            "Days of the week on which bookings are accepted (0=Monday, 6=Sunday)."
        ),
        value_type=schema.Choice(vocabulary=WORKING_DAYS_VOCAB),
        required=False,
        defaultFactory=list,
    )

    working_hours_start = schema.Int(
        title=_("Working hours start"),
        description=_("Hour of day when bookings open (0–23)."),
        required=False,
        default=9,
        min=0,
        max=23,
    )

    working_hours_end = schema.Int(
        title=_("Working hours end"),
        description=_("Hour of day when bookings close (0–23)."),
        required=False,
        default=17,
        min=0,
        max=23,
    )

    slot_duration = schema.Int(
        title=_("Slot duration (minutes)"),
        description=_("Length of each bookable slot in minutes."),
        required=False,
        default=30,
        min=1,
    )

    buffer_duration = schema.Int(
        title=_("Buffer duration (minutes)"),
        description=_("Gap between consecutive slots in minutes."),
        required=False,
        default=0,
        min=0,
    )

    availability_exceptions = schema.List(
        title=_("Availability exceptions"),
        description=_("Dates on which no bookings are accepted."),
        value_type=schema.Date(title=_("Date")),
        required=False,
        defaultFactory=list,
    )

    booking_state = schema.Choice(
        title=_("Booking state"),
        description=_("Current lifecycle state of the booking page."),
        vocabulary=BOOKING_STATES,
        required=True,
        default="open",
    )


@implementer(IBookingPage)
class BookingPage(Item):
    """A booking page that lets visitors schedule time with the organizer."""
