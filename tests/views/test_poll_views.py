"""Functional tests for the Poll browser views."""

from datetime import datetime
from datetime import timedelta
from datetime import timezone
from experimental.doodle.interfaces import IVoteStorage
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.testing.zope import Browser

import pytest
import transaction


@pytest.fixture
def three_slots():
    base = datetime.now(tz=timezone.utc) + timedelta(days=1)
    return [base, base + timedelta(hours=1), base + timedelta(hours=2)]


@pytest.fixture
def poll_url(functional, three_slots):
    """Create a Poll, commit it, and return its absolute URL.

    We return the URL string — not the object — so that functional-layer
    tests can access it through the WSGI browser without crossing ZODB
    connection boundaries.
    """
    portal = functional["portal"]
    setRoles(portal, TEST_USER_ID, ["Manager"])
    poll = api.content.create(
        container=portal,
        type="Poll",
        title="Lunch poll",
        description="Pick a time for lunch.",
        options=three_slots,
    )
    api.content.transition(poll, "publish")
    url = poll.absolute_url()
    transaction.commit()
    return url


@pytest.fixture
def browser(functional):
    """An unauthenticated Zope test browser."""
    b = Browser(functional["app"])
    b.handleErrors = False
    return b


@pytest.fixture
def auth_browser(functional):
    """A test browser authenticated as the test manager."""
    b = Browser(functional["app"])
    b.handleErrors = False
    portal_url = functional["portal"].absolute_url()
    b.open(portal_url + "/login")
    b.getControl(name="__ac_name").value = TEST_USER_NAME
    b.getControl(name="__ac_password").value = TEST_USER_PASSWORD
    b.getControl(name="buttons.login").click()
    return b


class TestPollView:
    """The ``@@poll_view`` renders the vote form."""

    def test_poll_view_renders(self, poll_url, browser):
        browser.open(poll_url + "/@@poll_view")
        assert browser.headers["Status"] == "200 OK"
        assert "Lunch poll" in browser.contents

    def test_poll_view_shows_options(self, poll_url, browser, three_slots):
        browser.open(poll_url + "/@@poll_view")
        for slot in three_slots:
            assert slot.strftime("%H:%M") in browser.contents

    def test_poll_view_form_present(self, poll_url, browser):
        browser.open(poll_url + "/@@poll_view")
        assert 'method="POST"' in browser.contents
        assert 'name="name"' in browser.contents


class TestVotePost:
    """Submitting the vote form records the vote and redirects."""

    def _submit_vote(self, browser, poll_url, name, yes_indices=()):
        """Open the poll view, fill in ``name``, set yes on ``yes_indices``."""
        browser.open(poll_url + "/@@poll_view")
        browser.getControl(name="name").value = name
        for i in yes_indices:
            browser.getControl(name=f"votes_{i}", index=0).selected = True
        browser.getForm(action="@@poll_view").submit()

    def test_vote_redirects_to_poll_view(self, poll_url, browser):
        self._submit_vote(browser, poll_url, "Alice")
        assert "@@poll_view" in browser.url

    def test_vote_is_stored(self, poll_url, functional, browser):
        self._submit_vote(browser, poll_url, "Alice")

        portal = functional["portal"]
        poll_id = poll_url.rstrip("/").split("/")[-1]
        poll = portal[poll_id]
        assert "Alice" in IVoteStorage(poll).participants()

    def test_vote_missing_name_shows_error(self, poll_url, browser):
        self._submit_vote(browser, poll_url, "")
        assert "@@poll_view" in browser.url
        assert "name" in browser.contents.lower()

    def test_second_vote_overwrites_first(self, poll_url, functional, browser):
        for _ in range(2):
            self._submit_vote(browser, poll_url, "Alice")

        portal = functional["portal"]
        poll_id = poll_url.rstrip("/").split("/")[-1]
        poll = portal[poll_id]
        assert IVoteStorage(poll).participants().count("Alice") == 1


class TestResultsView:
    """The ``@@results`` view shows the tally."""

    def test_results_view_renders(self, poll_url, browser):
        browser.open(poll_url + "/@@results")
        assert browser.headers["Status"] == "200 OK"
        assert "Lunch poll" in browser.contents

    def test_results_view_shows_tally_after_vote(self, poll_url, browser):
        browser.open(poll_url + "/@@poll_view")
        browser.getControl(name="name").value = "Alice"
        for i in range(3):
            browser.getControl(name=f"votes_{i}").value = ["true"]
        browser.getForm(action="@@poll_view").submit()

        browser.open(poll_url + "/@@results")
        assert ">1<" in browser.contents

    def test_results_view_lists_participants(self, poll_url, browser):
        browser.open(poll_url + "/@@poll_view")
        browser.getControl(name="name").value = "Bob"
        browser.getForm(action="@@poll_view").submit()

        browser.open(poll_url + "/@@results")
        assert "Bob" in browser.contents

    def test_results_view_links_back_to_poll(self, poll_url, browser):
        browser.open(poll_url + "/@@results")
        assert "@@poll_view" in browser.contents


class TestUpgradeStep1002:
    """The 1001 → 1002 upgrade step updates the Poll FTI."""

    def test_upgrade_step_registered(self, integration):
        setup_tool = api.portal.get_tool("portal_setup")
        grouped = setup_tool.listUpgrades(
            "experimental.doodle:default", show_old=True
        )
        flat = []
        for entry in grouped:
            flat.extend(entry if isinstance(entry, list) else [entry])
        destinations = {s.get("sdest") for s in flat if s.get("ssource") == "1001"}
        assert "1002" in destinations

    def test_handler_updates_fti_default_view(self, integration):
        from experimental.doodle.upgrades.v1002 import install_poll_views

        portal_types = api.portal.get_tool("portal_types")
        fti = portal_types["Poll"]
        fti.default_view = "view"  # simulate pre-1002 state

        install_poll_views(api.portal.get_tool("portal_setup"))

        assert fti.default_view == "poll_view"
