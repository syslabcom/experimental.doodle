"""Module where all interfaces, events and exceptions live."""

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from plone.autoform import directives as form
from plone.supermodel import model
from zope import schema


class IBrowserLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


# MVP: Folderish Doodle container schema interface
class IExperimentalDoodleFolder(model.Schema):
    """Folderish Doodle container (MVP)"""
    # Dublin Core fields (title, description) are included by default
    form.order_after(description='title')
    description = schema.Text(
        title="Description",
        required=False,
    )
    # Optionally, add a text field for body/content
    body = schema.Text(
        title="Body",
        required=False,
    )
