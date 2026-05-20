"""Module where all interfaces, events and exceptions live."""

from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IBrowserLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IVoteStorage(Interface):
    """Storage adapter for votes on a Poll.

    Votes are persisted as an annotation on the adapted Poll. Each entry
    maps a participant's display name to a list of booleans whose length
    equals ``len(poll.options)`` at write time.
    """

    def cast_vote(name, votes):
        """Record ``votes`` for the participant ``name``.

        ``name`` is stripped of surrounding whitespace; case is preserved.
        Casting again with the same name overwrites the previous vote.

        Raises ``ValueError`` if ``name`` is empty after stripping, or if
        ``votes`` has a different length than the poll's options.
        """

    def get_vote(name):
        """Return the votes cast by ``name`` as a plain ``list[bool]``,
        or ``None`` if the participant has not voted yet."""

    def get_votes():
        """Return a plain ``dict[str, list[bool]]`` snapshot of all votes.

        Mutating the returned mapping or its lists does not affect the
        stored state.
        """

    def remove_vote(name):
        """Remove ``name``'s vote. Return ``True`` if a vote was removed,
        ``False`` if the participant had not voted."""

    def participants():
        """Return participant names that have cast a vote, sorted
        alphabetically."""

    def tally():
        """Return a ``list[int]`` of ``yes`` counts, parallel to
        ``poll.options``."""
