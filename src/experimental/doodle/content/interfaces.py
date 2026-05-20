from experimental.doodle import _
from experimental.doodle.content.widgets import CandidateDatesWidget
from plone.autoform import directives
from plone.supermodel import model
from zope import schema


class IDoodle(model.Schema):
    """Scheduling poll with date-only options."""

    directives.widget("candidate_dates", CandidateDatesWidget)
    candidate_dates = schema.List(
        title=_("Candidate dates"),
        description=_(
            "Dates participants can choose from. "
            "Check rows to remove, click Remove selected, then Save."
        ),
        value_type=schema.Date(),
        required=True,
        min_length=1,
    )
