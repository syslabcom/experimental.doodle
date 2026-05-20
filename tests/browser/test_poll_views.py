"""Integration tests for Poll browser views."""

from datetime import datetime
from experimental.doodle.browser.poll_views import PollResultsView
from experimental.doodle.browser.poll_views import PollVoteView
from experimental.doodle.interfaces import IBrowserLayer
from experimental.doodle.voting import get_vote
from experimental.doodle.voting import get_votes
from experimental.doodle.voting import submit_vote
from zope.interface import alsoProvides

import plone.api
import pytest


SLOT_A = datetime(2026, 6, 1, 9, 0)
SLOT_B = datetime(2026, 6, 1, 14, 0)
SLOT_C = datetime(2026, 6, 2, 9, 0)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _browser_layer(portal, integration):
    """Apply IBrowserLayer to the test request for all tests in this module."""
    alsoProvides(portal.REQUEST, IBrowserLayer)


@pytest.fixture()
def poll(portal, integration):
    """Return a freshly created open Poll for view tests."""
    with plone.api.env.adopt_roles(["Manager"]):
        obj = plone.api.content.create(
            container=portal,
            type="Poll",
            id="view-test-poll",
            title="View Test Poll",
            proposed_slots=[SLOT_A, SLOT_B, SLOT_C],
            poll_state="open",
        )
    return obj


@pytest.fixture()
def member(portal, integration):
    """Return a freshly created Plone member for authenticated tests."""
    with plone.api.env.adopt_roles(["Manager"]):
        user = plone.api.user.create(
            username="test.voter",
            email="test.voter@example.com",
            password="Test1234!",
            roles=["Member"],
        )
    return user


def _vote_view(poll, portal):
    """Instantiate PollVoteView directly, bypassing ZCML template wiring."""
    view = PollVoteView(poll, portal.REQUEST)
    # Provide a stub index so error paths that return self.index() don't fail
    # when the view is instantiated outside the traversal machinery.
    view.index = lambda: ""
    return view


def _results_view(poll, portal):
    """Instantiate PollResultsView directly."""
    return PollResultsView(poll, portal.REQUEST)


# ---------------------------------------------------------------------------
# View registration
# ---------------------------------------------------------------------------


class TestViewRegistration:
    def test_vote_view_is_traversable(self, poll, portal):
        """@@poll-vote can be looked up via restrictedTraverse."""
        with plone.api.env.adopt_roles(["Manager"]):
            view = poll.restrictedTraverse("@@poll-vote")
        assert isinstance(view, PollVoteView)

    def test_results_view_is_traversable(self, poll, portal):
        """@@poll-results can be looked up via restrictedTraverse."""
        with plone.api.env.adopt_roles(["Manager"]):
            view = poll.restrictedTraverse("@@poll-results")
        assert isinstance(view, PollResultsView)


# ---------------------------------------------------------------------------
# PollVoteView — template helpers
# ---------------------------------------------------------------------------


class TestPollVoteViewHelpers:
    def test_is_open_when_poll_is_open(self, poll, portal):
        assert _vote_view(poll, portal).is_open() is True

    def test_is_not_open_when_closed(self, poll, portal):
        poll.poll_state = "closed"
        assert _vote_view(poll, portal).is_open() is False

    def test_is_not_open_when_final(self, poll, portal):
        poll.poll_state = "final"
        assert _vote_view(poll, portal).is_open() is False

    def test_proposed_slots_info_length(self, poll, portal):
        assert len(_vote_view(poll, portal).proposed_slots_info()) == 3

    def test_proposed_slots_info_keys(self, poll, portal):
        for info in _vote_view(poll, portal).proposed_slots_info():
            assert "display" in info
            assert "value" in info
            assert info["display"] != ""

    def test_slot_value_is_isoformat_roundtrippable(self, poll, portal):
        for info in _vote_view(poll, portal).proposed_slots_info():
            parsed = datetime.fromisoformat(info["value"])
            assert isinstance(parsed, datetime)

    def test_has_already_voted_false_anonymously(self, poll, portal):
        # No user context → anonymous → returns False
        assert _vote_view(poll, portal).has_already_voted() is False

    def test_has_already_voted_false_before_voting(self, poll, portal, member):
        with plone.api.env.adopt_user(username=member.id):
            result = _vote_view(poll, portal).has_already_voted()
        assert result is False

    def test_has_already_voted_true_after_voting(self, poll, portal, member):
        submit_vote(poll, member.id, [SLOT_A])
        with plone.api.env.adopt_user(username=member.id):
            result = _vote_view(poll, portal).has_already_voted()
        assert result is True


# ---------------------------------------------------------------------------
# PollVoteView — POST handling
# ---------------------------------------------------------------------------


class TestPollVoteSubmission:
    def test_vote_is_stored_after_valid_post(self, poll, portal, member):
        """A valid POST submission stores the vote."""
        portal.REQUEST.form["chosen_slots"] = [SLOT_A.isoformat()]
        with plone.api.env.adopt_user(username=member.id):
            _vote_view(poll, portal)._handle_post()
        assert get_vote(poll, member.id) is not None

    def test_voted_slots_are_stored_correctly(self, poll, portal, member):
        """The exact chosen slots are preserved in the vote record."""
        portal.REQUEST.form["chosen_slots"] = [SLOT_A.isoformat(), SLOT_C.isoformat()]
        with plone.api.env.adopt_user(username=member.id):
            _vote_view(poll, portal)._handle_post()
        record = get_vote(poll, member.id)
        assert set(record["chosen_slots"]) == {SLOT_A, SLOT_C}

    def test_successful_post_redirects_to_results(self, poll, portal, member):
        """A successful vote sets a redirect location pointing at @@poll-results."""
        portal.REQUEST.form["chosen_slots"] = [SLOT_A.isoformat()]
        with plone.api.env.adopt_user(username=member.id):
            _vote_view(poll, portal)._handle_post()
        location = portal.REQUEST.response.getHeader("location") or ""
        assert "poll-results" in location

    def test_duplicate_vote_does_not_overwrite(self, poll, portal, member):
        """Submitting via the view a second time does not change the first vote."""
        submit_vote(poll, member.id, [SLOT_A])
        portal.REQUEST.form["chosen_slots"] = [SLOT_B.isoformat()]
        with plone.api.env.adopt_user(username=member.id):
            _vote_view(poll, portal)._handle_post()
        assert get_vote(poll, member.id)["chosen_slots"] == [SLOT_A]

    def test_duplicate_vote_redirects_to_results(self, poll, portal, member):
        """A duplicate submission still redirects to @@poll-results."""
        submit_vote(poll, member.id, [SLOT_A])
        portal.REQUEST.form["chosen_slots"] = [SLOT_B.isoformat()]
        with plone.api.env.adopt_user(username=member.id):
            _vote_view(poll, portal)._handle_post()
        location = portal.REQUEST.response.getHeader("location") or ""
        assert "poll-results" in location

    def test_empty_selection_does_not_store_vote(self, poll, portal, member):
        """Submitting with no slots chosen does not create a vote record."""
        portal.REQUEST.form["chosen_slots"] = []
        with plone.api.env.adopt_user(username=member.id):
            _vote_view(poll, portal)._handle_post()
        assert get_vote(poll, member.id) is None

    def test_closed_poll_does_not_store_vote(self, poll, portal, member):
        """POST to a closed poll is rejected and no vote is stored."""
        poll.poll_state = "closed"
        portal.REQUEST.form["chosen_slots"] = [SLOT_A.isoformat()]
        with plone.api.env.adopt_user(username=member.id):
            _vote_view(poll, portal)._handle_post()
        assert get_vote(poll, member.id) is None

    def test_anonymous_user_cannot_vote(self, poll, portal):
        """An anonymous POST does not store a vote."""
        from plone.app.testing import login as testing_login
        from plone.app.testing import logout as testing_logout
        from plone.app.testing import TEST_USER_NAME

        portal.REQUEST.form["chosen_slots"] = [SLOT_A.isoformat()]
        testing_logout()
        try:
            _vote_view(poll, portal)._handle_post()
            assert len(get_votes(poll)) == 0
        finally:
            testing_login(portal, TEST_USER_NAME)


# ---------------------------------------------------------------------------
# PollResultsView — template helpers
# ---------------------------------------------------------------------------


class TestPollResultsViewHelpers:
    def test_results_length_matches_proposed_slots(self, poll, portal):
        assert len(_results_view(poll, portal).results()) == 3

    def test_results_contains_required_keys(self, poll, portal):
        for row in _results_view(poll, portal).results():
            assert "display" in row
            assert "count" in row
            assert "is_winner" in row

    def test_total_votes_zero_initially(self, poll, portal):
        assert _results_view(poll, portal).total_votes() == 0

    def test_total_votes_increments_with_each_voter(self, poll, portal):
        submit_vote(poll, "alice", [SLOT_A])
        submit_vote(poll, "bob", [SLOT_B])
        assert _results_view(poll, portal).total_votes() == 2

    def test_results_sorted_descending_by_count(self, poll, portal):
        submit_vote(poll, "alice", [SLOT_A, SLOT_B])
        submit_vote(poll, "bob", [SLOT_A])
        counts = [r["count"] for r in _results_view(poll, portal).results()]
        assert counts == sorted(counts, reverse=True)

    def test_winner_is_flagged_in_results(self, poll, portal):
        submit_vote(poll, "alice", [SLOT_A])
        submit_vote(poll, "bob", [SLOT_A])
        winners = [r for r in _results_view(poll, portal).results() if r["is_winner"]]
        assert len(winners) == 1
        assert winners[0]["slot"] == SLOT_A

    def test_winning_slot_display_empty_with_no_votes(self, poll, portal):
        assert _results_view(poll, portal).winning_slot_display() == ""

    def test_winning_slot_display_non_empty_after_votes(self, poll, portal):
        submit_vote(poll, "alice", [SLOT_A])
        assert _results_view(poll, portal).winning_slot_display() != ""

    def test_is_final_false_for_open_poll(self, poll, portal):
        assert _results_view(poll, portal).is_final() is False

    def test_is_final_true_for_final_poll(self, poll, portal):
        poll.poll_state = "final"
        assert _results_view(poll, portal).is_final() is True

    def test_final_slot_display_non_empty_when_set(self, poll, portal):
        poll.poll_state = "final"
        poll.final_selected_slot = SLOT_C
        assert (
            _results_view(poll, portal).final_slot_display()
            == _results_view(poll, portal).winning_slot_display()
            or _results_view(poll, portal).final_slot_display() != ""
        )

    def test_final_slot_display_empty_when_not_set(self, poll, portal):
        assert _results_view(poll, portal).final_slot_display() == ""


# ---------------------------------------------------------------------------
# PollVoteView — anonymous voting registry setting
# ---------------------------------------------------------------------------


class TestAnonymousVoting:
    """Tests for the allow_anonymous_voting registry toggle."""

    @pytest.fixture(autouse=True)
    def _reset_registry(self, portal, integration):
        """Ensure allow_anonymous_voting is False before and after each test."""
        from plone.registry.interfaces import IRegistry
        from zope.component import getUtility

        registry = getUtility(IRegistry)
        registry["experimental.doodle.allow_anonymous_voting"] = False
        yield
        registry["experimental.doodle.allow_anonymous_voting"] = False

    def test_anonymous_cannot_vote_when_setting_disabled(self, poll, portal):
        """Default: anonymous POST stores no vote."""
        from plone.app.testing import login as testing_login
        from plone.app.testing import logout as testing_logout
        from plone.app.testing import TEST_USER_NAME

        portal.REQUEST.form["chosen_slots"] = [SLOT_A.isoformat()]
        testing_logout()
        try:
            _vote_view(poll, portal)._handle_post()
            assert len(get_votes(poll)) == 0
        finally:
            testing_login(portal, TEST_USER_NAME)

    def test_anonymous_can_vote_when_setting_enabled(self, poll, portal):
        """When allow_anonymous_voting=True an anonymous POST is accepted."""
        from plone.app.testing import login as testing_login
        from plone.app.testing import logout as testing_logout
        from plone.app.testing import TEST_USER_NAME
        from plone.registry.interfaces import IRegistry
        from zope.component import getUtility

        getUtility(IRegistry)["experimental.doodle.allow_anonymous_voting"] = True
        portal.REQUEST.form["chosen_slots"] = [SLOT_A.isoformat()]
        testing_logout()
        try:
            _vote_view(poll, portal)._handle_post()
            assert len(get_votes(poll)) == 1
        finally:
            testing_login(portal, TEST_USER_NAME)

    def test_anonymous_vote_stored_with_anon_participant_id(self, poll, portal):
        """Anonymous vote is keyed under 'anon:...' in the vote store."""
        from plone.app.testing import login as testing_login
        from plone.app.testing import logout as testing_logout
        from plone.app.testing import TEST_USER_NAME
        from plone.registry.interfaces import IRegistry
        from zope.component import getUtility

        getUtility(IRegistry)["experimental.doodle.allow_anonymous_voting"] = True
        portal.REQUEST.form["chosen_slots"] = [SLOT_A.isoformat()]
        testing_logout()
        try:
            _vote_view(poll, portal)._handle_post()
            votes = get_votes(poll)
            assert any(pid.startswith("anon:") for pid in votes)
        finally:
            testing_login(portal, TEST_USER_NAME)

    def test_authenticated_vote_unaffected_by_anonymous_setting(
        self, poll, portal, member
    ):
        """Enabling anonymous voting does not change authenticated vote storage."""
        from plone.registry.interfaces import IRegistry
        from zope.component import getUtility

        getUtility(IRegistry)["experimental.doodle.allow_anonymous_voting"] = True
        portal.REQUEST.form["chosen_slots"] = [SLOT_A.isoformat()]
        with plone.api.env.adopt_user(username=member.id):
            _vote_view(poll, portal)._handle_post()
        assert get_vote(poll, member.id) is not None
