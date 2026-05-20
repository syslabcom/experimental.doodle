"""Viewlets rendered on the Plone site root (home page)."""

from plone.app.layout.viewlets.common import ViewletBase

import plone.api


class OpenPollsViewlet(ViewletBase):
    """Shows all open polls on the home page."""

    def open_polls(self):
        """Return a list of dicts for every poll with poll_state == 'open'."""
        catalog = plone.api.portal.get_tool("portal_catalog")
        brains = catalog(portal_type="Poll", poll_state="open")
        return [
            {
                "title": brain.Title,
                "description": brain.Description,
                "url": brain.getURL(),
            }
            for brain in brains
        ]
