from experimental.doodle.content.interfaces import IDoodle
from plone.dexterity.content import Container
from zope.interface import implementer


@implementer(IDoodle)
class Doodle(Container):
    """A date poll for scheduling meetings."""

    portal_type = "Doodle"
