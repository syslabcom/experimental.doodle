import plone.api

from AccessControl import Unauthorized
from Products.Five.browser import BrowserView
from plone.protect.authenticator import check


class ToggleParticipationView(BrowserView):
    """Toggle the current user in and out of date participants."""

    def __call__(self):
        if self.request.get("REQUEST_METHOD", "GET") != "POST":
            raise Unauthorized("Participation changes require POST")

        check(self.request)

        user = plone.api.user.get_current()
        userid = user.getId() if user else None
        if not userid:
            raise Unauthorized("Login required")

        values = set(getattr(self.context, "participants", set()) or set())
        if userid in values:
            values.remove(userid)
        else:
            values.add(userid)
        self.context.participants = values

        target = self.request.get("HTTP_REFERER")
        if not target:
            target = f"{self.context.aq_parent.absolute_url()}/@@doodle"
        self.request.response.redirect(target)
        return ""
