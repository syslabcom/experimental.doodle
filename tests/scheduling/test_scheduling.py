"""Integration tests for the booking scheduling logic."""

from experimental.doodle.scheduling import BookingPageClosedError
from experimental.doodle.scheduling import create_booking
from experimental.doodle.scheduling import get_available_slots
from experimental.doodle.scheduling import get_booking
from experimental.doodle.scheduling import get_bookings
from experimental.doodle.scheduling import InvalidSlotError
from experimental.doodle.scheduling import SlotUnavailableError

import datetime
import plone.api
import pytest


# ---------------------------------------------------------------------------
# Shared fixtures and helpers
# ---------------------------------------------------------------------------

# A known Monday — 2 June 2026 is a Tuesday, 1 June 2026 is a Monday.
MONDAY = datetime.date(2026, 6, 1)
TUESDAY = datetime.date(2026, 6, 2)
WEDNESDAY = datetime.date(2026, 6, 3)

# The 09:00 slot on that Monday (naive datetime, matching storage convention).
SLOT_0900 = datetime.datetime(2026, 6, 1, 9, 0)
SLOT_0930 = datetime.datetime(2026, 6, 1, 9, 30)
SLOT_1000 = datetime.datetime(2026, 6, 1, 10, 0)
SLOT_1030 = datetime.datetime(2026, 6, 1, 10, 30)


@pytest.fixture()
def booking_page(portal, integration):
    """A minimal open BookingPage with Mon-Fri, 09:00-11:00, 30-min slots."""
    with plone.api.env.adopt_roles(["Manager"]):
        page = plone.api.content.create(
            container=portal,
            type="BookingPage",
            id="test-booking-page",
            title="Test Booking Page",
            working_days=[0, 1, 2, 3, 4],  # Mon–Fri
            working_hours_start=9,
            working_hours_end=11,
            slot_duration=30,
            buffer_duration=0,
            availability_exceptions=[],
            booking_state="open",
        )
    return page


# ---------------------------------------------------------------------------
# Slot computation tests
# ---------------------------------------------------------------------------


class TestSlotComputation:
    def test_working_day_produces_slots(self, booking_page):
        """A working day within working hours produces the expected slots."""
        # 9:00, 9:30, 10:00, 10:30 — last slot ends exactly at 11:00.
        slots = get_available_slots(booking_page, MONDAY)
        assert slots == [SLOT_0900, SLOT_0930, SLOT_1000, SLOT_1030]

    def test_non_working_day_produces_no_slots(self, booking_page):
        """A day not listed in working_days produces an empty list."""
        # MONDAY is day 0; pass a Saturday (day 5) which is not in [0,1,2,3,4].
        saturday = datetime.date(2026, 6, 6)
        assert get_available_slots(booking_page, saturday) == []

    def test_exception_date_produces_no_slots(self, booking_page):
        """A date in availability_exceptions produces an empty list."""
        booking_page.availability_exceptions = [MONDAY]
        assert get_available_slots(booking_page, MONDAY) == []

    def test_slots_respect_working_hours_start(self, booking_page):
        """First slot starts at working_hours_start."""
        slots = get_available_slots(booking_page, MONDAY)
        assert slots[0].hour == 9
        assert slots[0].minute == 0

    def test_slots_respect_working_hours_end(self, booking_page):
        """No slot begins so late that it would end after working_hours_end."""
        # With 9-11, 30-min slots: last valid start is 10:30 (ends at 11:00).
        booking_page.working_hours_end = 11
        slots = get_available_slots(booking_page, MONDAY)
        for slot in slots:
            assert slot + datetime.timedelta(
                minutes=booking_page.slot_duration
            ) <= datetime.datetime(
                MONDAY.year, MONDAY.month, MONDAY.day, booking_page.working_hours_end, 0
            )

    def test_buffer_widens_step_between_slots(self, booking_page):
        """Setting buffer_duration shifts the start of each subsequent slot."""
        booking_page.buffer_duration = 15  # 30-min slot + 15-min buffer = 45-min step
        slots = get_available_slots(booking_page, MONDAY)
        # 09:00, 09:45 — 10:30 would also fit (10:30 + 0:30 = 11:00 ≤ 11:00)
        assert slots[0] == datetime.datetime(2026, 6, 1, 9, 0)
        assert slots[1] == datetime.datetime(2026, 6, 1, 9, 45)

    def test_empty_working_days_allows_any_day(self, booking_page):
        """When working_days is empty no weekday filter is applied."""
        booking_page.working_days = []
        saturday = datetime.date(2026, 6, 6)
        slots = get_available_slots(booking_page, saturday)
        assert len(slots) > 0


# ---------------------------------------------------------------------------
# Booking creation tests
# ---------------------------------------------------------------------------


class TestBookingCreation:
    def test_successful_booking_returns_record(self, booking_page):
        """create_booking returns a dict with booker_id and booked_at."""
        record = create_booking(booking_page, "alice", SLOT_0900)
        assert record["booker_id"] == "alice"
        assert "booked_at" in record

    def test_booking_is_stored(self, booking_page):
        """After create_booking the record is retrievable via get_booking."""
        create_booking(booking_page, "alice", SLOT_0900)
        record = get_booking(booking_page, SLOT_0900)
        assert record is not None
        assert record["booker_id"] == "alice"

    def test_booked_slot_disappears_from_availability(self, booking_page):
        """A booked slot is no longer returned by get_available_slots."""
        create_booking(booking_page, "alice", SLOT_0900)
        available = get_available_slots(booking_page, MONDAY)
        assert SLOT_0900 not in available

    def test_other_slots_remain_available(self, booking_page):
        """Booking one slot does not affect the availability of other slots."""
        create_booking(booking_page, "alice", SLOT_0900)
        available = get_available_slots(booking_page, MONDAY)
        assert SLOT_0930 in available
        assert SLOT_1000 in available
        assert SLOT_1030 in available

    def test_get_bookings_returns_all(self, booking_page):
        """get_bookings returns a plain dict of all bookings."""
        create_booking(booking_page, "alice", SLOT_0900)
        create_booking(booking_page, "bob", SLOT_0930)
        bookings = get_bookings(booking_page)
        assert SLOT_0900 in bookings
        assert SLOT_0930 in bookings
        assert bookings[SLOT_0900]["booker_id"] == "alice"
        assert bookings[SLOT_0930]["booker_id"] == "bob"

    def test_get_booking_returns_none_for_unbooked(self, booking_page):
        """get_booking returns None for a slot that has not been booked."""
        assert get_booking(booking_page, SLOT_0900) is None


# ---------------------------------------------------------------------------
# Conflict detection tests
# ---------------------------------------------------------------------------


class TestConflictDetection:
    def test_double_booking_raises_slot_unavailable(self, booking_page):
        """A second attempt to book the same slot raises SlotUnavailableError."""
        create_booking(booking_page, "alice", SLOT_0900)
        with pytest.raises(SlotUnavailableError):
            create_booking(booking_page, "bob", SLOT_0900)

    def test_double_booking_does_not_overwrite_original(self, booking_page):
        """The original booking record is unchanged after a failed double-booking."""
        create_booking(booking_page, "alice", SLOT_0900)
        try:
            create_booking(booking_page, "bob", SLOT_0900)
        except SlotUnavailableError:
            pass
        assert get_booking(booking_page, SLOT_0900)["booker_id"] == "alice"


# ---------------------------------------------------------------------------
# Closed / invalid booking page tests
# ---------------------------------------------------------------------------


class TestBookingPageGuards:
    def test_closed_page_raises_booking_page_closed(self, booking_page):
        """Booking on a closed page raises BookingPageClosedError."""
        booking_page.booking_state = "closed"
        with pytest.raises(BookingPageClosedError):
            create_booking(booking_page, "alice", SLOT_0900)

    def test_closed_page_stores_no_booking(self, booking_page):
        """No booking is stored when the page is closed."""
        booking_page.booking_state = "closed"
        try:
            create_booking(booking_page, "alice", SLOT_0900)
        except BookingPageClosedError:
            pass
        assert get_bookings(booking_page) == {}

    def test_invalid_slot_raises_invalid_slot_error(self, booking_page):
        """Booking a datetime that is not a valid slot raises InvalidSlotError."""
        bad_slot = datetime.datetime(2026, 6, 1, 8, 0)  # before working hours
        with pytest.raises(InvalidSlotError):
            create_booking(booking_page, "alice", bad_slot)

    def test_non_working_day_slot_raises_invalid_slot_error(self, booking_page):
        """Booking a slot on a non-working day raises InvalidSlotError."""
        saturday_slot = datetime.datetime(2026, 6, 6, 9, 0)  # Saturday
        with pytest.raises(InvalidSlotError):
            create_booking(booking_page, "alice", saturday_slot)

    def test_exception_date_slot_raises_invalid_slot_error(self, booking_page):
        """Booking a slot on an exception date raises InvalidSlotError."""
        booking_page.availability_exceptions = [MONDAY]
        with pytest.raises(InvalidSlotError):
            create_booking(booking_page, "alice", SLOT_0900)


# ---------------------------------------------------------------------------
# Registry default slot duration tests
# ---------------------------------------------------------------------------


class TestRegistrySlotDuration:
    """Tests that default_booking_slot_duration registry setting is used as
    fallback when slot_duration is not set on the BookingPage object."""

    @pytest.fixture(autouse=True)
    def _reset_registry(self, portal, integration):
        """Restore the registry to its default value after each test."""
        from plone.registry.interfaces import IRegistry
        from zope.component import getUtility

        registry = getUtility(IRegistry)
        registry["experimental.doodle.default_booking_slot_duration"] = 30
        yield
        registry["experimental.doodle.default_booking_slot_duration"] = 30

    def test_uses_registry_default_when_slot_duration_is_none(
        self, booking_page, portal
    ):
        """When slot_duration is None the registry value drives slot generation."""
        from plone.registry.interfaces import IRegistry
        from zope.component import getUtility

        getUtility(IRegistry)["experimental.doodle.default_booking_slot_duration"] = 60
        booking_page.slot_duration = None
        # 09:00–11:00, 60-min slots: 09:00 and 10:00 only.
        slots = get_available_slots(booking_page, MONDAY)
        assert len(slots) == 2
        assert slots[0] == SLOT_0900
        assert slots[1] == SLOT_1000

    def test_field_value_takes_precedence_over_registry(self, booking_page, portal):
        """An explicit slot_duration on the object overrides the registry."""
        from plone.registry.interfaces import IRegistry
        from zope.component import getUtility

        getUtility(IRegistry)["experimental.doodle.default_booking_slot_duration"] = 60
        booking_page.slot_duration = 30  # explicit field value wins
        slots = get_available_slots(booking_page, MONDAY)
        # 09:00–11:00, 30-min slots: 09:00, 09:30, 10:00, 10:30.
        assert len(slots) == 4
