"""Browser views for the Poll content type."""

from experimental.doodle import _
from experimental.doodle.interfaces import IVoteStorage
from plone.protect.interfaces import IDisableCSRFProtection
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import alsoProvides


def _format_slot(dt) -> str:
    """Return a human-readable label for a datetime option."""
    return dt.strftime("%a %d %b %Y, %H:%M UTC")


class PollView(BrowserView):
    """Default view for a Poll: shows the vote form.

    Handles GET (render) and POST (record vote, then redirect).
    """

    index = ViewPageTemplateFile("templates/poll_view.pt")

    def __call__(self):
        if self.request.method == "POST":
            error = self._handle_post()
            if error is None:
                # Post/Redirect/Get: prevent duplicate submissions on refresh.
                url = self.context.absolute_url() + "/@@poll_view"
                self.request.response.redirect(url)
                return ""
            self._error = error
        else:
            self._error = None
        return self.index()

    # ------------------------------------------------------------------
    # Template helpers
    # ------------------------------------------------------------------

    @property
    def options(self):
        """Return ``[(index, label), ...]`` for every proposed slot."""
        return [
            (i, _format_slot(dt))
            for i, dt in enumerate(self.context.options or [])
        ]

    @property
    def error(self):
        return self._error

    @property
    def participant_count(self):
        return len(IVoteStorage(self.context).participants())

    # ------------------------------------------------------------------
    # POST handler
    # ------------------------------------------------------------------

    def _handle_post(self):
        """Validate the submitted form and cast the vote.

        Returns ``None`` on success, or a translated error string to
        display on the form.

        Voting is open to anonymous users, so there is no valid CSRF
        authenticator token for them. We explicitly opt out of CSRF
        protection here — the write is intentional and the form is
        publicly accessible by design.
        """
        alsoProvides(self.request, IDisableCSRFProtection)
        form = self.request.form
        name = (form.get("name") or "").strip()
        if not name:
            return _("Please enter your name.")

        options = self.context.options or []
        votes = []
        for i in range(len(options)):
            raw = form.get(f"votes_{i}", "false")
            votes.append(raw == "true")

        try:
            IVoteStorage(self.context).cast_vote(name, votes)
        except ValueError as exc:
            return str(exc)

        return None


class PollResultsView(BrowserView):
    """Results view for a Poll: shows the tally."""

    index = ViewPageTemplateFile("templates/results.pt")

    def __call__(self):
        return self.index()

    # ------------------------------------------------------------------
    # Template helpers
    # ------------------------------------------------------------------

    @property
    def rows(self):
        """Return ``[(label, yes_count, max_count), ...]`` for each slot."""
        storage = IVoteStorage(self.context)
        counts = storage.tally()
        max_count = max(counts) if counts else 0
        return [
            (_format_slot(dt), count, max_count)
            for dt, count in zip(self.context.options or [], counts)
        ]

    @property
    def participants(self):
        return IVoteStorage(self.context).participants()
