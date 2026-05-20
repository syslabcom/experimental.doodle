from experimental.doodle import _
from experimental.doodle.answers import build_results
from experimental.doodle.answers import get_answer_for_user
from experimental.doodle.answers import get_answers
from experimental.doodle.answers import upsert_answer
from experimental.doodle.utils import can_view_results
from experimental.doodle.utils import format_date
from experimental.doodle.utils import format_date_long
from experimental.doodle.utils import get_member_info
from experimental.doodle.utils import is_doodle_manager
from experimental.doodle.utils import parse_iso_dates
from experimental.doodle.utils import require_authenticated
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from zExceptions import Unauthorized


class AnswerView(BrowserView):
    """Answer form: pick dates that work for you."""

    index = ViewPageTemplateFile("doodle_answer.pt")

    def __call__(self):
        self.update()
        return self.index()

    def update(self):
        require_authenticated(self.request)
        self.userid, self.display_name = get_member_info()
        self.candidate_dates = list(self.context.candidate_dates or [])
        self.existing = get_answer_for_user(self.context, self.userid)
        self.selected = (
            set(self.existing.get("selected_dates", [])) if self.existing else set()
        )
        self.is_creator = is_doodle_manager(self.context)
        self.can_view_results = can_view_results(self.context)
        self.results_url = f"{self.context.absolute_url()}/@@results"

        if self.request.method != "POST":
            return
        if not self.request.form.get("form.submitted"):
            return

        selected_dates = parse_iso_dates(self.request.form.get("selected_dates"))
        valid = {candidate.isoformat() for candidate in self.candidate_dates}
        if not selected_dates:
            IStatusMessage(self.request).add(
                _("Please select at least one date."),
                type="error",
            )
            return
        if not all(value.isoformat() in valid for value in selected_dates):
            IStatusMessage(self.request).add(
                _("Invalid date selection."),
                type="error",
            )
            return

        upsert_answer(
            self.context,
            self.userid,
            self.display_name,
            selected_dates,
        )
        IStatusMessage(self.request).add(_("Your answer was saved."))
        self.selected = {value.isoformat() for value in selected_dates}
        self.existing = get_answer_for_user(self.context, self.userid)

    def format_date(self, value):
        return format_date(value)

    def format_date_long(self, value):
        return format_date_long(value)


class ResultsView(BrowserView):
    """Summary of all answers for users allowed to view results."""

    index = ViewPageTemplateFile("doodle_results.pt")

    def __call__(self):
        self.update()
        return self.index()

    def update(self):
        require_authenticated(self.request)
        if not can_view_results(self.context):
            raise Unauthorized()
        self.rows = build_results(self.context)
        self.total_users = len(get_answers(self.context))
        self.answer_url = self.context.absolute_url()

    def format_date(self, value):
        return format_date(value)
