"""Browser views for the Poll content type."""

from datetime import datetime
from experimental.doodle import _
from experimental.doodle.voting import aggregate_votes
from experimental.doodle.voting import DuplicateVoteError
from experimental.doodle.voting import get_vote
from experimental.doodle.voting import get_votes
from experimental.doodle.voting import get_winning_slot
from experimental.doodle.voting import InvalidSlotError
from experimental.doodle.voting import PollClosedError
from experimental.doodle.voting import submit_vote
from plone.protect.interfaces import IDisableCSRFProtection
from Products.Five.browser import BrowserView
from zope.interface import alsoProvides

import plone.api


def _format_slot(slot):
    """Return a human-readable string for a datetime slot, or '' for None."""
    if slot is None:
        return ""
    return slot.strftime("%A %d %B %Y, %H:%M")


def _allow_anonymous_voting():
    """Return True when the registry permits anonymous poll voting."""
    try:
        from experimental.doodle.controlpanels.doodle_settings import IDoodleSettings
        from plone.registry.interfaces import IRegistry
        from zope.component import getUtility

        settings = getUtility(IRegistry).forInterface(
            IDoodleSettings, prefix="experimental.doodle"
        )
        return bool(settings.allow_anonymous_voting)
    except Exception:
        return False


def _anonymous_participant_id(request):
    """Return a participant identifier for an anonymous voter.

    Uses the request's ``REMOTE_ADDR`` so that a single client IP address
    produces a stable key within a Plone transaction.  Shared IP addresses
    (NAT, proxies) and IP spoofing are known limitations accepted for MVP.
    """
    return f"anon:{request.get('REMOTE_ADDR', 'unknown')}"


class PollVoteView(BrowserView):
    """Vote submission form for a Poll.

    GET  — renders the vote form (checkboxes for each proposed slot).
    POST — processes the submission and redirects to @@poll-results on success.

    Anonymous access is permitted to see the form.  Submitting a vote requires
    an authenticated Plone user unless the ``allow_anonymous_voting`` registry
    setting is enabled, in which case the client's remote address is used as
    the participant identifier.
    """

    # ------------------------------------------------------------------
    # Template helpers (called from poll_vote.pt)
    # ------------------------------------------------------------------

    def is_open(self):
        """Return True when the poll is accepting votes."""
        return self.context.poll_state == "open"

    def proposed_slots_info(self):
        """Return a list of dicts for each proposed slot.

        Each dict has:
        - ``display``: human-readable string for use in templates
        - ``value``:   ISO-format string used as the checkbox value
        """
        return [
            {
                "display": _format_slot(slot),
                "value": slot.isoformat(),
            }
            for slot in (self.context.proposed_slots or [])
        ]

    def has_already_voted(self):
        """Return True if the current user (or anonymous client) has already voted."""
        if plone.api.user.is_anonymous():
            if not _allow_anonymous_voting():
                return False
            participant_id = _anonymous_participant_id(self.request)
        else:
            participant_id = plone.api.user.get_current().id
        return get_vote(self.context, participant_id) is not None

    # ------------------------------------------------------------------
    # Request handling
    # ------------------------------------------------------------------

    def __call__(self):
        if self.request.method == "POST":
            return self._handle_post()
        return self.index()

    def _handle_post(self):
        """Process a vote submission.

        Reads ``chosen_slots`` from the request form (list of ISO-formatted
        datetime strings), validates them, and delegates to ``submit_vote``.
        Redirects to ``@@poll-results`` on success or duplicate vote.
        Re-renders the form for validation errors.
        """
        alsoProvides(self.request, IDisableCSRFProtection)
        if plone.api.user.is_anonymous():
            if not _allow_anonymous_voting():
                plone.api.portal.show_message(
                    message=_("You must be logged in to vote."),
                    request=self.request,
                    type="error",
                )
                return self.index()
            participant_id = _anonymous_participant_id(self.request)
        else:
            participant_id = plone.api.user.get_current().id

        chosen_strs = self.request.form.get("chosen_slots", [])
        if isinstance(chosen_strs, str):
            chosen_strs = [chosen_strs]

        if not chosen_strs:
            plone.api.portal.show_message(
                message=_("Please select at least one time slot."),
                request=self.request,
                type="error",
            )
            return self.index()

        chosen = []
        for s in chosen_strs:
            try:
                chosen.append(datetime.fromisoformat(s))
            except (ValueError, TypeError):
                plone.api.portal.show_message(
                    message=_("One or more selected slots could not be read."),
                    request=self.request,
                    type="error",
                )
                return self.index()

        try:
            submit_vote(self.context, participant_id, chosen)
        except PollClosedError:
            plone.api.portal.show_message(
                message=_("This poll is no longer open for voting."),
                request=self.request,
                type="error",
            )
            return self.index()
        except DuplicateVoteError:
            plone.api.portal.show_message(
                message=_("You have already voted in this poll."),
                request=self.request,
                type="info",
            )
            return self.request.response.redirect(
                f"{self.context.absolute_url()}/@@poll-results"
            )
        except InvalidSlotError:
            plone.api.portal.show_message(
                message=_("One or more selected slots are no longer valid."),
                request=self.request,
                type="error",
            )
            return self.index()

        plone.api.portal.show_message(
            message=_("Your vote has been recorded. Thank you!"),
            request=self.request,
            type="info",
        )
        return self.request.response.redirect(
            f"{self.context.absolute_url()}/@@poll-results"
        )


class PollResultsView(BrowserView):
    """Results view showing aggregated votes per proposed slot.

    Displays:
    - total vote count
    - per-slot counts sorted by count (highest first)
    - the leading/winning slot
    - the final selected slot when the poll is in 'final' state
    """

    # ------------------------------------------------------------------
    # Template helpers (called from poll_results.pt)
    # ------------------------------------------------------------------

    def is_open(self):
        """Return True when the poll is still accepting votes."""
        return self.context.poll_state == "open"

    def is_final(self):
        """Return True when the organiser has selected a final slot."""
        return self.context.poll_state == "final"

    def total_votes(self):
        """Return the number of participants who have voted."""
        return len(get_votes(self.context))

    def results(self):
        """Return a list of dicts for each proposed slot, sorted by count descending.

        Each dict has:
        - ``display``:   human-readable slot label
        - ``count``:     number of votes for this slot
        - ``is_winner``: True for the slot returned by get_winning_slot()
        """
        counts = aggregate_votes(self.context)
        proposed = self.context.proposed_slots or []
        winner = get_winning_slot(self.context)
        rows = [
            {
                "slot": slot,
                "display": _format_slot(slot),
                "count": counts.get(slot, 0),
                "is_winner": slot == winner,
            }
            for slot in proposed
        ]
        return sorted(rows, key=lambda r: r["count"], reverse=True)

    def winning_slot_display(self):
        """Return a formatted string for the current leading slot, or ''."""
        return _format_slot(get_winning_slot(self.context))

    def final_slot_display(self):
        """Return a formatted string for the final selected slot, or ''."""
        return _format_slot(self.context.final_selected_slot)
