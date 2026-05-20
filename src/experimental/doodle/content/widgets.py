from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form.browser.multi import MultiWidget


class CandidateDatesWidget(MultiWidget):
    """Default multi widget with a table layout for checkbox + date columns."""

    template = ViewPageTemplateFile("candidate_dates_input.pt")
    showLabel = False
    klass = "multi-widget candidate-dates-table-widget"
