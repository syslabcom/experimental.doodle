from datetime import date

import pytest
from experimental.doodle.answers import build_results
from experimental.doodle.answers import get_answer_for_user
from experimental.doodle.answers import upsert_answer
from experimental.doodle.browser.views import AnswerView
from experimental.doodle.browser.views import ResultsView
from experimental.doodle.interfaces import IBrowserLayer
from plone import api
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.app.testing import logout
from zExceptions import Unauthorized
from zope.interface import alsoProvides


CANDIDATE_DATES = [date(2026, 5, 20), date(2026, 5, 22)]


def _prepare_request(http_request):
    alsoProvides(http_request, IBrowserLayer)
    return http_request


def _create_doodle(portal, title="Team sync", dates=None):
    dates = dates or CANDIDATE_DATES
    with api.env.adopt_user(SITE_OWNER_NAME):
        obj = api.content.create(
            container=portal,
            type="Doodle",
            title=title,
            candidate_dates=dates,
        )
        workflow = api.portal.get_tool("portal_workflow")
        if workflow.getWorkflowsFor(obj):
            api.content.transition(obj, "publish")
    return obj


class TestDoodleContent:
    def test_create_doodle(self, portal):
        obj = _create_doodle(portal)
        assert obj.portal_type == "Doodle"
        assert obj.Title() == "Team sync"
        assert [value.isoformat() for value in obj.candidate_dates] == [
            "2026-05-20",
            "2026-05-22",
        ]

    def test_upsert_answer(self, portal):
        obj = _create_doodle(portal)
        upsert_answer(obj, "member1", "Member One", [date(2026, 5, 20)])
        upsert_answer(
            obj,
            "member2",
            "Member Two",
            [date(2026, 5, 20), date(2026, 5, 22)],
        )
        upsert_answer(obj, "member1", "Member One", [date(2026, 5, 22)])

        answer = get_answer_for_user(obj, "member1")
        assert answer["selected_dates"] == ["2026-05-22"]

        rows = build_results(obj)
        assert rows[0]["count"] == 1
        assert rows[0]["names"] == ["Member Two"]
        assert rows[1]["count"] == 2


class TestDoodleViews:
    def test_anonymous_cannot_view_answer(self, portal, http_request):
        obj = _create_doodle(portal)
        logout()
        request = _prepare_request(http_request)
        view = AnswerView(obj, request)
        with pytest.raises(Unauthorized):
            view.update()

    def test_member_can_answer(self, portal, http_request):
        obj = _create_doodle(portal)
        login(portal, TEST_USER_NAME)
        request = _prepare_request(http_request)
        request.method = "GET"

        html = AnswerView(obj, request)()
        assert "Which dates work for you?" in html

        request.method = "POST"
        request.form["form.submitted"] = "1"
        request.form["selected_dates"] = ["2026-05-20"]
        html = AnswerView(obj, request)()
        assert "Your answer was saved." in html

        answer = get_answer_for_user(obj, TEST_USER_ID)
        assert answer["selected_dates"] == ["2026-05-20"]

    def test_creator_can_view_results(self, portal, http_request):
        obj = _create_doodle(portal)
        upsert_answer(obj, "member", "Member", [date(2026, 5, 20)])
        request = _prepare_request(http_request)

        with api.env.adopt_user(SITE_OWNER_NAME):
            html = ResultsView(obj, request)()

        assert "Who can make it" in html
        assert "Member" in html

    def test_non_creator_cannot_view_results(self, portal, http_request):
        obj = _create_doodle(portal)
        login(portal, TEST_USER_NAME)
        request = _prepare_request(http_request)
        view = ResultsView(obj, request)
        with pytest.raises(Unauthorized):
            view.update()

    def test_member_can_view_results_when_allowed(self, portal, http_request):
        obj = _create_doodle(portal)
        obj.allow_members_view_results = True
        upsert_answer(obj, "member", "Member", [date(2026, 5, 20)])
        login(portal, TEST_USER_NAME)
        request = _prepare_request(http_request)

        html = ResultsView(obj, request)()

        assert "Who can make it" in html
        assert "Member" in html

    def test_member_sees_results_link_when_allowed(self, portal, http_request):
        obj = _create_doodle(portal)
        obj.allow_members_view_results = True
        login(portal, TEST_USER_NAME)
        request = _prepare_request(http_request)
        request.method = "GET"

        html = AnswerView(obj, request)()

        assert "View results" in html
        assert "Share this link" not in html
