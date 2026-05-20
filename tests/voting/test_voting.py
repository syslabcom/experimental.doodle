"""Integration tests for Poll voting backend logic."""

from datetime import datetime
from experimental.doodle.voting import aggregate_votes
from experimental.doodle.voting import DuplicateVoteError
from experimental.doodle.voting import get_vote
from experimental.doodle.voting import get_votes
from experimental.doodle.voting import get_winning_slot
from experimental.doodle.voting import InvalidSlotError
from experimental.doodle.voting import PollClosedError
from experimental.doodle.voting import submit_vote

import plone.api
import pytest


SLOT_A = datetime(2026, 6, 1, 9, 0)
SLOT_B = datetime(2026, 6, 1, 14, 0)
SLOT_C = datetime(2026, 6, 2, 9, 0)


# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------


@pytest.fixture()
def open_poll(portal, integration):
    """Return a freshly created open Poll with three proposed slots."""
    with plone.api.env.adopt_roles(["Manager"]):
        poll = plone.api.content.create(
            container=portal,
            type="Poll",
            id="voting-test-poll",
            title="Voting Test Poll",
            proposed_slots=[SLOT_A, SLOT_B, SLOT_C],
            poll_state="open",
        )
    return poll


# ---------------------------------------------------------------------------
# Vote submission — happy path
# ---------------------------------------------------------------------------


class TestValidVoteSubmission:
    def test_vote_is_stored(self, open_poll):
        """Submitting a valid vote stores it under the participant_id."""
        submit_vote(open_poll, "alice", [SLOT_A, SLOT_B])
        record = get_vote(open_poll, "alice")
        assert record is not None
        assert set(record["chosen_slots"]) == {SLOT_A, SLOT_B}

    def test_vote_stores_submitted_at(self, open_poll):
        """The vote record includes a submitted_at timestamp."""
        submit_vote(open_poll, "alice", [SLOT_A])
        record = get_vote(open_poll, "alice")
        assert isinstance(record["submitted_at"], datetime)

    def test_single_slot_vote(self, open_poll):
        """A participant may vote for exactly one slot."""
        submit_vote(open_poll, "bob", [SLOT_C])
        record = get_vote(open_poll, "bob")
        assert record["chosen_slots"] == [SLOT_C]

    def test_all_slots_vote(self, open_poll):
        """A participant may vote for all proposed slots."""
        submit_vote(open_poll, "carol", [SLOT_A, SLOT_B, SLOT_C])
        record = get_vote(open_poll, "carol")
        assert len(record["chosen_slots"]) == 3

    def test_get_votes_returns_all(self, open_poll):
        """get_votes returns a mapping for every participant who voted."""
        submit_vote(open_poll, "alice", [SLOT_A])
        submit_vote(open_poll, "bob", [SLOT_B])
        all_votes = get_votes(open_poll)
        assert set(all_votes.keys()) == {"alice", "bob"}

    def test_get_vote_returns_none_for_unknown(self, open_poll):
        """get_vote returns None for a participant who has not voted."""
        assert get_vote(open_poll, "nobody") is None


# ---------------------------------------------------------------------------
# Duplicate vote prevention
# ---------------------------------------------------------------------------


class TestDuplicateVotePrevention:
    def test_duplicate_raises_error(self, open_poll):
        """Submitting a second vote for the same participant raises DuplicateVoteError."""
        submit_vote(open_poll, "alice", [SLOT_A])
        with pytest.raises(DuplicateVoteError):
            submit_vote(open_poll, "alice", [SLOT_B])

    def test_original_vote_is_unchanged_after_duplicate_attempt(self, open_poll):
        """The original vote is not mutated when a duplicate is rejected."""
        submit_vote(open_poll, "alice", [SLOT_A])
        with pytest.raises(DuplicateVoteError):
            submit_vote(open_poll, "alice", [SLOT_B])
        record = get_vote(open_poll, "alice")
        assert record["chosen_slots"] == [SLOT_A]

    def test_different_participants_can_vote_independently(self, open_poll):
        """Two different participants can each submit one vote without conflict."""
        submit_vote(open_poll, "alice", [SLOT_A])
        submit_vote(open_poll, "bob", [SLOT_A])
        assert get_vote(open_poll, "alice") is not None
        assert get_vote(open_poll, "bob") is not None


# ---------------------------------------------------------------------------
# Closed poll rejects votes
# ---------------------------------------------------------------------------


class TestClosedPollRejectsVote:
    def test_closed_state_raises_error(self, open_poll):
        """Submitting a vote to a closed poll raises PollClosedError."""
        open_poll.poll_state = "closed"
        with pytest.raises(PollClosedError):
            submit_vote(open_poll, "alice", [SLOT_A])

    def test_final_state_raises_error(self, open_poll):
        """Submitting a vote to a finalised poll raises PollClosedError."""
        open_poll.poll_state = "final"
        with pytest.raises(PollClosedError):
            submit_vote(open_poll, "alice", [SLOT_A])

    def test_open_poll_does_not_raise(self, open_poll):
        """No error is raised when poll_state is 'open'."""
        submit_vote(open_poll, "alice", [SLOT_A])  # must not raise


# ---------------------------------------------------------------------------
# Invalid slot rejection
# ---------------------------------------------------------------------------


class TestInvalidSlotRejection:
    def test_unknown_slot_raises_error(self, open_poll):
        """Choosing a slot not in proposed_slots raises InvalidSlotError."""
        unknown = datetime(2099, 1, 1, 12, 0)
        with pytest.raises(InvalidSlotError):
            submit_vote(open_poll, "alice", [unknown])

    def test_empty_chosen_slots_raises_value_error(self, open_poll):
        """Submitting an empty list of chosen slots raises ValueError."""
        with pytest.raises(ValueError):
            submit_vote(open_poll, "alice", [])


# ---------------------------------------------------------------------------
# Vote aggregation
# ---------------------------------------------------------------------------


class TestVoteAggregation:
    def test_all_slots_present_in_counts(self, open_poll):
        """aggregate_votes includes every proposed slot, even those with no votes."""
        counts = aggregate_votes(open_poll)
        assert set(counts.keys()) == {SLOT_A, SLOT_B, SLOT_C}

    def test_zero_counts_before_any_votes(self, open_poll):
        """All slot counts are 0 before any votes are submitted."""
        counts = aggregate_votes(open_poll)
        assert all(v == 0 for v in counts.values())

    def test_correct_count_after_votes(self, open_poll):
        """Counts correctly reflect the votes cast."""
        submit_vote(open_poll, "alice", [SLOT_A, SLOT_B])
        submit_vote(open_poll, "bob", [SLOT_A])
        submit_vote(open_poll, "carol", [SLOT_C])
        counts = aggregate_votes(open_poll)
        assert counts[SLOT_A] == 2
        assert counts[SLOT_B] == 1
        assert counts[SLOT_C] == 1

    def test_aggregation_is_independent_per_poll(self, portal, integration):
        """Votes on one poll do not affect aggregation on another."""
        with plone.api.env.adopt_roles(["Manager"]):
            poll1 = plone.api.content.create(
                container=portal,
                type="Poll",
                id="agg-poll-1",
                title="Aggregation Poll 1",
                proposed_slots=[SLOT_A],
                poll_state="open",
            )
            poll2 = plone.api.content.create(
                container=portal,
                type="Poll",
                id="agg-poll-2",
                title="Aggregation Poll 2",
                proposed_slots=[SLOT_A],
                poll_state="open",
            )
        submit_vote(poll1, "alice", [SLOT_A])
        assert aggregate_votes(poll1)[SLOT_A] == 1
        assert aggregate_votes(poll2)[SLOT_A] == 0


# ---------------------------------------------------------------------------
# Winning / best slot
# ---------------------------------------------------------------------------


class TestWinningSlot:
    def test_no_votes_returns_none(self, open_poll):
        """get_winning_slot returns None when no votes have been cast."""
        assert get_winning_slot(open_poll) is None

    def test_clear_winner(self, open_poll):
        """The slot with the most votes is returned as the winner."""
        submit_vote(open_poll, "alice", [SLOT_A, SLOT_B])
        submit_vote(open_poll, "bob", [SLOT_A])
        assert get_winning_slot(open_poll) == SLOT_A

    def test_tie_broken_by_position(self, open_poll):
        """When two slots tie, the one appearing first in proposed_slots wins."""
        # SLOT_A and SLOT_B each get 1 vote; SLOT_A appears first.
        submit_vote(open_poll, "alice", [SLOT_A])
        submit_vote(open_poll, "bob", [SLOT_B])
        assert get_winning_slot(open_poll) == SLOT_A

    def test_final_state_returns_final_selected_slot(self, open_poll):
        """When poll_state is 'final', final_selected_slot is returned directly."""
        submit_vote(open_poll, "alice", [SLOT_B])
        open_poll.poll_state = "final"
        open_poll.final_selected_slot = SLOT_C
        assert get_winning_slot(open_poll) == SLOT_C

    def test_no_proposed_slots_returns_none(self, portal, integration):
        """get_winning_slot returns None when proposed_slots is empty."""
        with plone.api.env.adopt_roles(["Manager"]):
            empty_poll = plone.api.content.create(
                container=portal,
                type="Poll",
                id="empty-slots-poll",
                title="Empty Slots Poll",
                proposed_slots=[],
                poll_state="open",
            )
        assert get_winning_slot(empty_poll) is None
