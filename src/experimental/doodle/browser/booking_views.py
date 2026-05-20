"""Browser views for the BookingPage content type."""

from experimental.doodle import _
from experimental.doodle.scheduling import BookingPageClosedError
from experimental.doodle.scheduling import create_booking
from experimental.doodle.scheduling import get_available_slots
from experimental.doodle.scheduling import InvalidSlotError
from experimental.doodle.scheduling import SlotUnavailableError
from Products.Five.browser import BrowserView
from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import alsoProvides

import datetime
import plone.api


def _format_slot(slot):
    """Return a human-readable string for a datetime slot, or '' for None."""
    if slot is None:
        return ""
    return slot.strftime("%A %d %B %Y, %H:%M")


class BookingPageView(BrowserView):
    """Public booking view for a BookingPage.

    GET  — renders a date picker and the list of available slots for the
           selected date.
    POST — submits a booking for one selected slot and redirects back to
           the same view (with the date preserved) on success.

    Anonymous access is permitted to view the form; submitting a booking
    requires an authenticated Plone user.  Anonymous booking is intentionally
    not supported in this MVP release.
    """

    # ------------------------------------------------------------------
    # Template helpers (called from booking_page.pt)
    # ------------------------------------------------------------------

    def is_open(self):
        """Return True when the booking page is accepting new bookings."""
        return self.context.booking_state == "open"

    def selected_date(self):
        """Return the calendar date to display slots for.

        Reads ``date`` from the request form (ISO format YYYY-MM-DD).
        Falls back to today if the parameter is absent or unparseable.
        """
        date_str = self.request.form.get("date", "")
        if date_str:
            try:
                return datetime.date.fromisoformat(date_str)
            except (ValueError, TypeError):
                pass
        return datetime.date.today()

    def selected_date_str(self):
        """Return the selected date as an ISO string for use in templates."""
        return self.selected_date().isoformat()

    def available_slots_info(self):
        """Return a list of dicts for each available slot on the selected date.

        Each dict has:
        - ``display``: human-readable string for use in templates
        - ``value``:   ISO-format datetime string used as the radio-button value
        """
        slots = get_available_slots(self.context, self.selected_date())
        return [
            {
                "display": _format_slot(slot),
                "value": slot.isoformat(),
            }
            for slot in slots
        ]

    # ------------------------------------------------------------------
    # Request handling
    # ------------------------------------------------------------------

    def __call__(self):
        if self.request.method == "POST":
            return self._handle_post()
        return self.index()

    def _handle_post(self):
        """Process a booking submission.

        Reads ``slot`` from the request form (ISO-formatted datetime string),
        validates it, and delegates to ``create_booking``.
        Redirects to ``@@booking-page`` on success, preserving the selected
        date in the query string.  Re-renders the form for validation errors.
        """
        alsoProvides(self.request, IDisableCSRFProtection)
        if plone.api.user.is_anonymous():
            plone.api.portal.show_message(
                message=_("You must be logged in to make a booking."),
                request=self.request,
                type="error",
            )
            return self.index()

        booker_id = plone.api.user.get_current().id

        slot_str = self.request.form.get("slot", "")
        if not slot_str:
            plone.api.portal.show_message(
                message=_("Please select a time slot."),
                request=self.request,
                type="error",
            )
            return self.index()

        try:
            slot = datetime.datetime.fromisoformat(slot_str)
        except (ValueError, TypeError):
            plone.api.portal.show_message(
                message=_("The selected slot could not be read."),
                request=self.request,
                type="error",
            )
            return self.index()

        try:
            create_booking(self.context, booker_id, slot)
        except BookingPageClosedError:
            plone.api.portal.show_message(
                message=_("This booking page is not accepting new bookings."),
                request=self.request,
                type="error",
            )
            return self.index()
        except SlotUnavailableError:
            plone.api.portal.show_message(
                message=_("That slot has just been taken. Please choose another."),
                request=self.request,
                type="error",
            )
            return self.index()
        except InvalidSlotError:
            plone.api.portal.show_message(
                message=_("The selected slot is no longer available."),
                request=self.request,
                type="error",
            )
            return self.index()

        plone.api.portal.show_message(
            message=_("Your booking has been confirmed. See you then!"),
            request=self.request,
            type="info",
        )
        date_str = slot.date().isoformat()
        return self.request.response.redirect(
            f"{self.context.absolute_url()}/@@booking-page?date={date_str}"
        )
