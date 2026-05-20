"""Tests for the VoteStorage adapter."""

from datetime import datetime
from datetime import timedelta
from datetime import timezone
from experimental.doodle.adapters.vote_storage import ANNOTATION_KEY
from experimental.doodle.adapters.vote_storage import VoteStorage
from experimental.doodle.interfaces import IVoteStorage
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from zope.annotation.interfaces import IAnnotations

import pytest


@pytest.fixture
def three_slots():
    """Three timezone-aware datetimes in the future."""
    base = datetime.now(tz=timezone.utc) + timedelta(days=1)
    return [base, base + timedelta(hours=1), base + timedelta(hours=2)]


@pytest.fixture
def poll(integration, three_slots):
    """A Poll with three options inside the test portal."""
    portal = integration["portal"]
    setRoles(portal, TEST_USER_ID, ["Manager"])
    return api.content.create(
        container=portal,
        type="Poll",
        title="Team lunch",
        options=three_slots,
    )


class TestAdapterLookup:
    """``IVoteStorage`` resolves to ``VoteStorage`` for a Poll."""

    def test_adapter_returns_vote_storage(self, poll):
        storage = IVoteStorage(poll)
        assert isinstance(storage, VoteStorage)

    def test_adapter_uses_annotation_key(self, poll):
        IVoteStorage(poll)  # triggers annotation initialization
        annotations = IAnnotations(poll)
        assert ANNOTATION_KEY in annotations


class TestCastVote:
    """Recording votes."""

    def test_cast_vote_stores_choices(self, poll):
        storage = IVoteStorage(poll)
        storage.cast_vote("Alice", [True, False, True])
        assert storage.get_vote("Alice") == [True, False, True]

    def test_cast_vote_is_idempotent_overwrite(self, poll):
        storage = IVoteStorage(poll)
        storage.cast_vote("Alice", [True, False, True])
        storage.cast_vote("Alice", [False, False, False])
        assert storage.get_vote("Alice") == [False, False, False]
        assert storage.participants() == ["Alice"]

    def test_cast_vote_strips_whitespace_preserves_case(self, poll):
        storage = IVoteStorage(poll)
        storage.cast_vote("  Alice  ", [True, True, True])
        assert storage.get_vote("Alice") == [True, True, True]
        assert "Alice" in storage.participants()

    def test_cast_vote_coerces_to_bool(self, poll):
        storage = IVoteStorage(poll)
        storage.cast_vote("Alice", [1, 0, "yes"])
        assert storage.get_vote("Alice") == [True, False, True]


class TestCastVoteErrors:
    """``cast_vote`` rejects invalid input."""

    @pytest.mark.parametrize("bad_name", ["", "   ", "\t\n"])
    def test_empty_name_raises(self, poll, bad_name):
        storage = IVoteStorage(poll)
        with pytest.raises(ValueError):
            storage.cast_vote(bad_name, [True, False, True])

    def test_non_string_name_raises(self, poll):
        storage = IVoteStorage(poll)
        with pytest.raises(ValueError):
            storage.cast_vote(None, [True, False, True])

    def test_wrong_length_raises(self, poll):
        storage = IVoteStorage(poll)
        with pytest.raises(ValueError):
            storage.cast_vote("Alice", [True, False])  # poll has 3 options


class TestReading:
    """Reading back stored votes."""

    def test_get_vote_returns_none_for_unknown(self, poll):
        storage = IVoteStorage(poll)
        assert storage.get_vote("Nobody") is None

    def test_get_votes_returns_plain_dict_snapshot(self, poll):
        storage = IVoteStorage(poll)
        storage.cast_vote("Alice", [True, False, True])

        snapshot = storage.get_votes()
        assert snapshot == {"Alice": [True, False, True]}

        # Mutating the snapshot must not affect the stored state.
        snapshot["Alice"][0] = False
        snapshot["Mallory"] = [True, True, True]
        assert storage.get_vote("Alice") == [True, False, True]
        assert "Mallory" not in storage.participants()

    def test_participants_sorted(self, poll):
        storage = IVoteStorage(poll)
        storage.cast_vote("Charlie", [True, True, True])
        storage.cast_vote("Alice", [False, False, False])
        storage.cast_vote("Bob", [True, False, True])

        assert storage.participants() == ["Alice", "Bob", "Charlie"]


class TestRemoveVote:
    """Removing votes."""

    def test_remove_vote_existing_returns_true(self, poll):
        storage = IVoteStorage(poll)
        storage.cast_vote("Alice", [True, False, True])

        assert storage.remove_vote("Alice") is True
        assert storage.get_vote("Alice") is None

    def test_remove_vote_unknown_returns_false(self, poll):
        storage = IVoteStorage(poll)
        assert storage.remove_vote("Nobody") is False


class TestTally:
    """Aggregating yes-counts per option."""

    def test_tally_empty_poll(self, poll):
        storage = IVoteStorage(poll)
        assert storage.tally() == [0, 0, 0]

    def test_tally_counts_yes_per_option(self, poll):
        storage = IVoteStorage(poll)
        storage.cast_vote("Alice", [True, False, True])
        storage.cast_vote("Bob", [True, True, False])
        storage.cast_vote("Charlie", [False, True, True])

        # Option 0: Alice + Bob = 2 yes
        # Option 1: Bob + Charlie = 2 yes
        # Option 2: Alice + Charlie = 2 yes
        assert storage.tally() == [2, 2, 2]

    def test_tally_ignores_extra_entries_when_options_shrink(self, poll):
        """If the Poll loses an option after a vote, tally truncates."""
        storage = IVoteStorage(poll)
        storage.cast_vote("Alice", [True, True, True])

        # Simulate the Poll losing one option.
        poll.options = poll.options[:2]

        assert storage.tally() == [1, 1]
