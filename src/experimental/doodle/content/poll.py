"""Poll content type."""

from experimental.doodle import _
from plone.dexterity.content import Item
from plone.supermodel import model
from zope import schema
from zope.interface import implementer
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


POLL_STATES = SimpleVocabulary([
    SimpleTerm(value="open", title=_("Open")),
    SimpleTerm(value="closed", title=_("Closed")),
    SimpleTerm(value="final", title=_("Final")),
])


class IPoll(model.Schema):
    """Schema for a scheduling poll."""

    location = schema.TextLine(
        title=_("Location"),
        description=_("Optional meeting location or URL."),
        required=False,
    )

    deadline = schema.Datetime(
        title=_("Deadline"),
        description=_("Last date and time for voting."),
        required=False,
    )

    proposed_slots = schema.List(
        title=_("Proposed slots"),
        description=_("List of proposed date and time options."),
        value_type=schema.Datetime(title=_("Slot")),
        required=False,
        defaultFactory=list,
    )

    poll_state = schema.Choice(
        title=_("Poll state"),
        description=_("Current lifecycle state of the poll."),
        vocabulary=POLL_STATES,
        required=True,
        default="open",
    )

    final_selected_slot = schema.Datetime(
        title=_("Final selected slot"),
        description=_("The slot chosen by the organizer after closing the poll."),
        required=False,
    )


@implementer(IPoll)
class Poll(Item):
    """A scheduling poll."""
