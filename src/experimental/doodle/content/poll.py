"""Poll content type: a Doodle-style scheduling poll."""

from experimental.doodle import _
from plone.dexterity.content import Item
from plone.supermodel import model
from zope import schema
from zope.interface import implementer
from zope.interface import Invalid
from zope.interface import invariant


MIN_OPTIONS = 2


class IPoll(model.Schema):
    """Schema for a Doodle-style poll.

    A poll proposes a list of date/time options and collects yes/no votes
    from participants who identify themselves by a free-text name.
    """

    options = schema.List(
        title=_("Proposed time slots"),
        description=_("Date and time options that participants can vote on."),
        value_type=schema.Datetime(
            title=_("Time slot"),
        ),
        required=True,
        defaultFactory=list,
    )

    @invariant
    def at_least_two_options(data):
        """A poll needs at least two distinct time slots to be meaningful."""
        options = getattr(data, "options", None) or []
        if len(options) < MIN_OPTIONS:
            raise Invalid(
                _("A poll needs at least two proposed time slots."),
            )


@implementer(IPoll)
class Poll(Item):
    """A Doodle-style poll."""
