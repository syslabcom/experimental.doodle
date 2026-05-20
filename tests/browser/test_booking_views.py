"""Integration tests for BookingPage browser views."""

from experimental.doodle.browser.booking_views import BookingPageView
from experimental.doodle.interfaces import IBrowserLayer
from experimental.doodle.scheduling import create_booking
from experimental.doodle.scheduling import get_available_slots
from experimental.doodle.scheduling import get_booking
from experimental.doodle.scheduling import get_bookings
from zope.interface import alsoProvides

import datetime
import plone.api
import pytest


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# June 1 2026 is a Monday (weekday 0).
MONDAY = datetime.date(2026, 6, 1)
SLOT_0900 = datetime.datetime(2026, 6, 1, 9, 0)
SLOT_0930 = datetime.datetime(2026, 6, 1, 9, 30)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _browser_layer(portal, integration):
    """Apply IBrowserLayer to the test request for all tests in this module."""
    alsoProvides(portal.REQUEST, IBrowserLayer)


@pytest.fixture()
def page(portal):
    """An open BookingPage with Mon–Fri, 09:00–11:00, 30-min slots."""
    with plone.api.env.adopt_roles(["Manager"]):
        obj = plone.api.content.create(
            container=portal,
            type="BookingPage",
            id="test-booking-page",
            title="Test Booking Page",
            organizer="alice@example.com",
            working_days=[0, 1, 2, 3, 4],
            working_hours_start=9,
            working_hours_end=11,
            slot_duration=30,
            buffer_duration=0,
            availability_exceptions=[],
            booking_state="open",
        )
    return obj


@pytest.fixture()
def member(portal):
    """A regular Plone member for authenticated booking tests."""
    with plone.api.env.adopt_roles(["Manager"]):
        user = plone.api.user.create(
            username="test.booker",
            email="test.booker@example.com",
            password="Test1234!",
            roles=["Member"],
        )
    return user


def _booking_view(page, portal):
    """Instantiate BookingPageView directly, bypassing ZCML template wiring."""
    view = BookingPageView(page, portal.REQUEST)
    # Stub index so error paths that call self.index() don't raise AttributeError.
    view.index = lambda: ""
    return view


# ---------------------------------------------------------------------------
# View registration
# ---------------------------------------------------------------------------


class TestViewRegistration:
    def test_booking_page_view_is_traversable(self, page, portal):
        """@@booking-page can be looked up via restrictedTraverse."""
        with plone.api.env.adopt_roles(["Manager"]):
            view = page.restrictedTraverse("@@booking-page")
        assert isinstance(view, BookingPageView)


# ---------------------------------------------------------------------------
# BookingPageView — template helpers
# ---------------------------------------------------------------------------


class TestBookingPageViewHelpers:
    def test_is_open_when_open(self, page, portal):
        assert _booking_view(page, portal).is_open() is True

    def test_is_not_open_when_closed(self, page, portal):
        page.booking_state = "closed"
        assert _booking_view(page, portal).is_open() is False

    def test_selected_date_defaults_to_today(self, page, portal):
        view = _booking_view(page, portal)
        assert view.selected_date() == datetime.date.today()

    def test_selected_date_parsed_from_form(self, page, portal):
        portal.REQUEST.form["date"] = "2026-06-01"
        assert _booking_view(page, portal).selected_date() == MONDAY

    def test_selected_date_invalid_falls_back_to_today(self, page, portal):
        portal.REQUEST.form["date"] = "not-a-date"
        assert _booking_view(page, portal).selected_date() == datetime.date.today()

    def test_selected_date_str_returns_iso(self, page, portal):
        portal.REQUEST.form["date"] = "2026-06-01"
        assert _booking_view(page, portal).selected_date_str() == "2026-06-01"

    def test_available_slots_info_returns_slots_for_working_day(self, page, portal):
        portal.REQUEST.form["date"] = "2026-06-01"
        info = _booking_view(page, portal).available_slots_info()
        assert len(info) == 4  # 09:00, 09:30, 10:00, 10:30

    def test_available_slots_info_has_display_and_value_keys(self, page, portal):
        portal.REQUEST.form["date"] = "2026-06-01"
        for slot in _booking_view(page, portal).available_slots_info():
            assert "display" in slot
            assert "value" in slot
            assert slot["display"] != ""

    def test_available_slots_info_value_is_isoformat_roundtrippable(self, page, portal):
        portal.REQUEST.form["date"] = "2026-06-01"
        for slot in _booking_view(page, portal).available_slots_info():
            parsed = datetime.datetime.fromisoformat(slot["value"])
            assert isinstance(parsed, datetime.datetime)

    def test_available_slots_info_empty_for_non_working_day(self, page, portal):
        portal.REQUEST.form["date"] = "2026-06-06"  # Saturday
        assert _booking_view(page, portal).available_slots_info() == []


# ---------------------------------------------------------------------------
# BookingPageView — POST handling
# ---------------------------------------------------------------------------


class TestBookingSubmission:
    def test_booking_is_stored_after_valid_post(self, page, portal, member):
        """A valid POST from an authenticated user stores the booking."""
        portal.REQUEST.form["slot"] = SLOT_0900.isoformat()
        with plone.api.env.adopt_user(username=member.id):
            _booking_view(page, portal)._handle_post()
        assert get_booking(page, SLOT_0900) is not None

    def test_booked_slot_has_correct_booker_id(self, page, portal, member):
        """The stored booking record carries the authenticated user's ID."""
        portal.REQUEST.form["slot"] = SLOT_0900.isoformat()
        with plone.api.env.adopt_user(username=member.id):
            _booking_view(page, portal)._handle_post()
        assert get_booking(page, SLOT_0900)["booker_id"] == member.id

    def test_booking_removes_slot_from_availability(self, page, portal, member):
        """After a successful booking the slot disappears from available slots."""
        portal.REQUEST.form["slot"] = SLOT_0900.isoformat()
        with plone.api.env.adopt_user(username=member.id):
            _booking_view(page, portal)._handle_post()
        assert SLOT_0900 not in get_available_slots(page, MONDAY)

    def test_other_slots_remain_available_after_booking(self, page, portal, member):
        """Booking one slot does not affect availability of other slots."""
        portal.REQUEST.form["slot"] = SLOT_0900.isoformat()
        with plone.api.env.adopt_user(username=member.id):
            _booking_view(page, portal)._handle_post()
        assert SLOT_0930 in get_available_slots(page, MONDAY)

    def test_successful_post_redirects_to_booking_page(self, page, portal, member):
        """A successful booking redirects to @@booking-page with the date."""
        portal.REQUEST.form["slot"] = SLOT_0900.isoformat()
        with plone.api.env.adopt_user(username=member.id):
            _booking_view(page, portal)._handle_post()
        location = portal.REQUEST.response.getHeader("location") or ""
        assert "booking-page" in location
        assert "2026-06-01" in location

    def test_double_booking_is_rejected(self, page, portal, member):
        """A second booking attempt for the same slot does not overwrite the first."""
        create_booking(page, "first.booker", SLOT_0900)
        portal.REQUEST.form["slot"] = SLOT_0900.isoformat()
        with plone.api.env.adopt_user(username=member.id):
            _booking_view(page, portal)._handle_post()
        # Original booking is unchanged.
        assert get_booking(page, SLOT_0900)["booker_id"] == "first.booker"

    def test_double_booking_stores_only_one_record(self, page, portal, member):
        """Only one booking exists after a double-booking attempt."""
        create_booking(page, "first.booker", SLOT_0900)
        portal.REQUEST.form["slot"] = SLOT_0900.isoformat()
        with plone.api.env.adopt_user(username=member.id):
            _booking_view(page, portal)._handle_post()
        assert len(get_bookings(page)) == 1

    def test_closed_page_rejects_booking(self, page, portal, member):
        """POST to a closed booking page stores no booking."""
        page.booking_state = "closed"
        portal.REQUEST.form["slot"] = SLOT_0900.isoformat()
        with plone.api.env.adopt_user(username=member.id):
            _booking_view(page, portal)._handle_post()
        assert get_bookings(page) == {}

    def test_anonymous_user_cannot_book(self, page, portal):
        """An anonymous POST does not store a booking."""
        from plone.app.testing import login as testing_login
        from plone.app.testing import logout as testing_logout
        from plone.app.testing import TEST_USER_NAME

        portal.REQUEST.form["slot"] = SLOT_0900.isoformat()
        testing_logout()
        try:
            _booking_view(page, portal)._handle_post()
            assert get_bookings(page) == {}
        finally:
            testing_login(portal, TEST_USER_NAME)

    def test_missing_slot_in_post_stores_nothing(self, page, portal, member):
        """Submitting without selecting a slot does not create a booking."""
        portal.REQUEST.form.pop("slot", None)
        with plone.api.env.adopt_user(username=member.id):
            _booking_view(page, portal)._handle_post()
        assert get_bookings(page) == {}
