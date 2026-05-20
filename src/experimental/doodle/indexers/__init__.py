"""Catalog indexers for experimental.doodle content types."""

from experimental.doodle.content.poll import IPoll
from plone.indexer import indexer


@indexer(IPoll)
def poll_state_indexer(obj):
    """Index the poll_state field so it can be searched in the catalog."""
    return obj.poll_state
