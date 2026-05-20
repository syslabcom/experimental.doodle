"""Booking scheduling logic for BookingPage content objects.

Bookings are stored in ZODB annotations on the BookingPage object itself using
``IAnnotations(booking_page)[BOOKINGS_KEY]``.  The annotation value is a
``PersistentMapping`` that maps slot start ``datetime`` objects to booking
records::

    {
        datetime(2026, 6, 2, 9, 0): {
            "booker_id": "<user_id_or_email>",
            "booked_at": datetime(...),
        },
        ...
    }

Using the slot ``datetime`` as the mapping key gives O(1) conflict detection
at the Python layer.  ZODB's transaction model adds a second safety net: if
two concurrent requests attempt to book the same slot in parallel, only one
transaction can commit the mutation; the other receives a ``ConflictError``
and retries, at which point the slot is already present and
``SlotUnavailableError`` is raised.

The trade-off versus a separate ``Booking`` content type is that individual
bookings are not visible in the Plone content tree, not independently
workflowable, and cannot be found via the catalog.  These constraints are
acceptable for the current MVP scope.
"""

from datetime import datetime
from datetime import timedelta
from persistent.mapping import PersistentMapping
from zope.annotation.interfaces import IAnnotations


BOOKINGS_KEY = "experimental.doodle.bookings"


# ---------------------------------------------------------------------------
# Registry helpers
# ---------------------------------------------------------------------------


def _registry_default_slot_duration():
    """Return the default booking slot duration from the Plone registry.

    Falls back to 30 minutes when the registry is unavailable (e.g. during
    unit tests that run outside the full Zope component architecture).
    """
    try:
        from experimental.doodle.controlpanels.doodle_settings import IDoodleSettings
        from plone.registry.interfaces import IRegistry
        from zope.component import getUtility

        settings = getUtility(IRegistry).forInterface(
            IDoodleSettings, prefix="experimental.doodle"
        )
        return settings.default_booking_slot_duration or 30
    except Exception:
        return 30


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class BookingError(Exception):
    """Base class for all booking-related errors."""


class BookingPageClosedError(BookingError):
    """Raised when a booking is submitted to a page that is not open."""


class SlotUnavailableError(BookingError):
    """Raised when the requested slot is already booked."""


class InvalidSlotError(BookingError):
    """Raised when the requested slot is not a valid slot for the booking page."""


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _get_bookings_map(booking_page):
    """Return the persistent booking mapping for *booking_page*, creating it if needed."""
    annotations = IAnnotations(booking_page)
    if BOOKINGS_KEY not in annotations:
        annotations[BOOKINGS_KEY] = PersistentMapping()
    return annotations[BOOKINGS_KEY]


def _slots_for_day(booking_page, day):
    """Return all theoretically possible slot start times for a calendar day.

    Parameters
    ----------
    booking_page:
        A ``BookingPage`` content object.
    day : datetime.date
        The calendar date to enumerate slots for.

    Returns
    -------
    list[datetime]
        Ordered list of naive UTC slot start datetimes.  Empty when the day
        is not a working day or is listed in ``availability_exceptions``.
    """
    working_days = list(booking_page.working_days or [])
    if working_days and day.weekday() not in working_days:
        return []

    exceptions = list(booking_page.availability_exceptions or [])
    if day in exceptions:
        return []

    start_h = booking_page.working_hours_start
    if start_h is None:
        start_h = 9
    end_h = booking_page.working_hours_end
    if end_h is None:
        end_h = 17

    slot_min = booking_page.slot_duration
    if not slot_min:
        slot_min = _registry_default_slot_duration()
    buffer_min = booking_page.buffer_duration
    if buffer_min is None:
        buffer_min = 0

    step = timedelta(minutes=slot_min + buffer_min)
    slot_length = timedelta(minutes=slot_min)

    window_start = datetime(day.year, day.month, day.day, start_h, 0)
    window_end = datetime(day.year, day.month, day.day, end_h, 0)

    slots = []
    current = window_start
    while current + slot_length <= window_end:
        slots.append(current)
        current += step
    return slots


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_available_slots(booking_page, day):
    """Return available slot start times for a given calendar day.

    A slot is available when it exists in ``_slots_for_day`` **and** has not
    yet been booked.

    Parameters
    ----------
    booking_page:
        A ``BookingPage`` content object.
    day : datetime.date
        The calendar date to query.

    Returns
    -------
    list[datetime]
        Ordered list of available slot start datetimes.
    """
    all_slots = _slots_for_day(booking_page, day)
    if not all_slots:
        return []
    booked = _get_bookings_map(booking_page)
    return [s for s in all_slots if s not in booked]


def create_booking(booking_page, booker_id, slot):
    """Create a booking for a specific slot on a booking page.

    Parameters
    ----------
    booking_page:
        The ``BookingPage`` content object.
    booker_id : str
        Identifier for the person making the booking (e.g. Plone user ID or
        an email address for anonymous visitors).
    slot : datetime
        The slot start time being booked.  Must be a value returned by
        ``get_available_slots`` for the corresponding day.

    Returns
    -------
    dict
        The newly created booking record.

    Raises
    ------
    BookingPageClosedError
        If ``booking_page.booking_state != 'open'``.
    InvalidSlotError
        If *slot* is not a valid slot for the booking page on its date.
    SlotUnavailableError
        If *slot* is already booked.
    """
    if booking_page.booking_state != "open":
        raise BookingPageClosedError("This booking page is not open for new bookings.")

    valid_slots = _slots_for_day(booking_page, slot.date())
    if slot not in valid_slots:
        raise InvalidSlotError(
            f"The slot {slot!r} is not a valid slot for this booking page."
        )

    bookings = _get_bookings_map(booking_page)
    if slot in bookings:
        raise SlotUnavailableError(f"The slot {slot!r} is already booked.")

    record = {
        "booker_id": booker_id,
        "booked_at": datetime.utcnow(),
    }
    bookings[slot] = record
    return record


def get_booking(booking_page, slot):
    """Return the booking record for *slot*, or ``None`` if not booked.

    Parameters
    ----------
    booking_page:
        The ``BookingPage`` content object.
    slot : datetime
        The slot start time to look up.
    """
    return _get_bookings_map(booking_page).get(slot)


def get_bookings(booking_page):
    """Return all bookings as a plain dict mapping slot → booking record."""
    return dict(_get_bookings_map(booking_page))
