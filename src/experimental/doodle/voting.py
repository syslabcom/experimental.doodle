"""Voting logic for Poll content objects.

Votes are stored in ZODB annotations on the Poll object itself using
``IAnnotations(poll)[VOTES_KEY]``.  The annotation value is a
``PersistentMapping`` that maps participant identifiers (strings) to vote
records::

    {
        "<participant_id>": {
            "chosen_slots": [datetime, ...],
            "submitted_at": datetime,
        },
        ...
    }

This approach keeps votes co-located with their poll, requires no extra
content type, and lets ZODB handle persistence automatically.  The trade-off
is that votes are not individually catalogued or visible through the Plone UI;
the public surface is the aggregation API defined in this module.
"""

from datetime import datetime
from persistent.mapping import PersistentMapping
from zope.annotation.interfaces import IAnnotations


VOTES_KEY = "experimental.doodle.votes"


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class VotingError(Exception):
    """Base class for all voting-related errors."""


class PollClosedError(VotingError):
    """Raised when a vote is submitted to a poll that is not open."""


class DuplicateVoteError(VotingError):
    """Raised when a participant submits a second vote on the same poll."""


class InvalidSlotError(VotingError):
    """Raised when a chosen slot is not in the poll's proposed_slots."""


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _get_responses(poll):
    """Return the persistent vote mapping for *poll*, creating it if needed."""
    annotations = IAnnotations(poll)
    if VOTES_KEY not in annotations:
        annotations[VOTES_KEY] = PersistentMapping()
    return annotations[VOTES_KEY]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def submit_vote(poll, participant_id, chosen_slots):
    """Submit a vote for one or more proposed slots.

    Parameters
    ----------
    poll:
        The Poll content object.
    participant_id : str
        A string identifying the participant (typically the Plone user ID).
    chosen_slots : list[datetime]
        The proposed slots the participant is available for.  Must be a
        non-empty subset of ``poll.proposed_slots``.

    Raises
    ------
    PollClosedError
        If the poll is not in the ``'open'`` state.
    DuplicateVoteError
        If the participant has already submitted a vote on this poll.
    InvalidSlotError
        If any item in *chosen_slots* is not in ``poll.proposed_slots``.
    ValueError
        If *chosen_slots* is empty.
    """
    if poll.poll_state != "open":
        raise PollClosedError("This poll is not open for voting.")

    responses = _get_responses(poll)

    if participant_id in responses:
        raise DuplicateVoteError(
            f"Participant '{participant_id}' has already voted in this poll."
        )

    if not chosen_slots:
        raise ValueError("At least one slot must be chosen.")

    proposed = list(poll.proposed_slots or [])
    invalid = [s for s in chosen_slots if s not in proposed]
    if invalid:
        raise InvalidSlotError(
            f"The following slots are not in the poll's proposed slots: {invalid!r}"
        )

    responses[participant_id] = {
        "chosen_slots": list(chosen_slots),
        "submitted_at": datetime.utcnow(),
    }


def get_vote(poll, participant_id):
    """Return the vote record for *participant_id*, or ``None`` if not found."""
    return _get_responses(poll).get(participant_id)


def get_votes(poll):
    """Return a plain dict mapping participant_id → vote record for all votes."""
    return dict(_get_responses(poll))


def aggregate_votes(poll):
    """Return a dict mapping each proposed slot to its vote count.

    All proposed slots are included; slots with no votes have count ``0``.
    """
    proposed = list(poll.proposed_slots or [])
    counts = {slot: 0 for slot in proposed}
    for record in _get_responses(poll).values():
        for slot in record.get("chosen_slots", []):
            if slot in counts:
                counts[slot] += 1
    return counts


def get_winning_slot(poll):
    """Return the proposed slot with the highest vote count.

    Returns ``None`` when there are no proposed slots or no votes have been
    cast yet.  In a tie the slot that appears **first** in
    ``poll.proposed_slots`` is returned.

    When ``poll.poll_state`` is ``'final'`` and ``poll.final_selected_slot``
    is set, that value is returned directly without recomputing from votes.
    """
    if poll.poll_state == "final" and poll.final_selected_slot:
        return poll.final_selected_slot

    proposed = list(poll.proposed_slots or [])
    if not proposed:
        return None

    counts = aggregate_votes(poll)
    max_count = max(counts.values(), default=0)
    if max_count == 0:
        return None

    # Return the first proposed slot that has the maximum count, preserving
    # the order from proposed_slots (earliest position wins ties).
    for slot in proposed:
        if counts.get(slot, 0) == max_count:
            return slot

    return None  # pragma: no cover
