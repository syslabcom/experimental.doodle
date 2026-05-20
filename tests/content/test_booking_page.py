"""Integration tests for the BookingPage content type."""

import pytest


class TestBookingPageTypeRegistration:
    def test_booking_page_fti_registered(self, portal):
        """Test that the BookingPage FTI is registered in portal_types."""
        assert "BookingPage" in portal.portal_types

    def test_booking_page_fti_meta_type(self, portal):
        """Test that the BookingPage FTI has the correct meta_type."""
        fti = portal.portal_types["BookingPage"]
        assert fti.meta_type == "Dexterity FTI"

    def test_booking_page_schema(self, portal):
        """Test that the BookingPage FTI references the correct schema."""
        fti = portal.portal_types["BookingPage"]
        assert fti.schema == "experimental.doodle.content.booking_page.IBookingPage"

    def test_booking_page_klass(self, portal):
        """Test that the BookingPage FTI references the correct class."""
        fti = portal.portal_types["BookingPage"]
        assert fti.klass == "experimental.doodle.content.booking_page.BookingPage"


class TestBookingPageCreation:
    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        """Use the integration testing layer."""

    def test_booking_page_is_creatable(self, portal):
        """Test that a BookingPage object can be created."""
        import plone.api

        with plone.api.env.adopt_roles(["Manager"]):
            page = plone.api.content.create(
                container=portal,
                type="BookingPage",
                id="test-booking-page",
                title="My Booking Page",
            )
        assert page is not None

    def test_booking_page_default_state(self, portal):
        """Test that a new BookingPage defaults to booking_state 'open'."""
        import plone.api

        with plone.api.env.adopt_roles(["Manager"]):
            page = plone.api.content.create(
                container=portal,
                type="BookingPage",
                id="test-booking-page-state",
                title="State Test Page",
            )
        assert page.booking_state == "open"

    def test_booking_page_default_slot_duration(self, portal):
        """Test that a new BookingPage defaults to slot_duration 30 minutes."""
        import plone.api

        with plone.api.env.adopt_roles(["Manager"]):
            page = plone.api.content.create(
                container=portal,
                type="BookingPage",
                id="test-booking-page-slot",
                title="Slot Test Page",
            )
        assert page.slot_duration == 30

    def test_booking_page_default_working_hours(self, portal):
        """Test that a new BookingPage defaults to 9–17 working hours."""
        import plone.api

        with plone.api.env.adopt_roles(["Manager"]):
            page = plone.api.content.create(
                container=portal,
                type="BookingPage",
                id="test-booking-page-hours",
                title="Hours Test Page",
            )
        assert page.working_hours_start == 9
        assert page.working_hours_end == 17

    def test_booking_page_default_working_days_empty(self, portal):
        """Test that working_days defaults to an empty list."""
        import plone.api

        with plone.api.env.adopt_roles(["Manager"]):
            page = plone.api.content.create(
                container=portal,
                type="BookingPage",
                id="test-booking-page-days",
                title="Days Test Page",
            )
        assert page.working_days == []

    def test_booking_page_stores_organizer(self, portal):
        """Test that the organizer field can be set and read back."""
        import plone.api

        with plone.api.env.adopt_roles(["Manager"]):
            page = plone.api.content.create(
                container=portal,
                type="BookingPage",
                id="test-booking-page-organizer",
                title="Organizer Test Page",
                organizer="alice@example.com",
            )
        assert page.organizer == "alice@example.com"

    def test_booking_page_stores_working_days(self, portal):
        """Test that working_days can be set to specific weekday values."""
        import plone.api

        with plone.api.env.adopt_roles(["Manager"]):
            page = plone.api.content.create(
                container=portal,
                type="BookingPage",
                id="test-booking-page-weekdays",
                title="Weekdays Test Page",
                working_days=[0, 1, 2, 3, 4],
            )
        assert page.working_days == [0, 1, 2, 3, 4]

    def test_booking_page_stores_availability_exceptions(self, portal):
        """Test that availability_exceptions defaults to an empty list."""
        import plone.api

        with plone.api.env.adopt_roles(["Manager"]):
            page = plone.api.content.create(
                container=portal,
                type="BookingPage",
                id="test-booking-page-exceptions",
                title="Exceptions Test Page",
            )
        assert page.availability_exceptions == []

    def test_ibooking_page_provides(self, portal):
        """Test that the created object provides IBookingPage."""
        from experimental.doodle.content.booking_page import IBookingPage

        import plone.api

        with plone.api.env.adopt_roles(["Manager"]):
            page = plone.api.content.create(
                container=portal,
                type="BookingPage",
                id="test-booking-page-iface",
                title="Interface Test Page",
            )
        assert IBookingPage.providedBy(page)
