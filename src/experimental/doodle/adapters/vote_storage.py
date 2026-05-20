"""Annotation-backed vote storage adapter for ``Poll`` objects."""

from collections.abc import Sequence
from experimental.doodle.content.poll import IPoll
from experimental.doodle.interfaces import IVoteStorage
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from zope.annotation.interfaces import IAnnotations
from zope.component import adapter
from zope.interface import implementer


ANNOTATION_KEY = "experimental.doodle.votes"


@implementer(IVoteStorage)
@adapter(IPoll)
class VoteStorage:
    """Store and aggregate votes as an annotation on a Poll."""

    def __init__(self, context):
        self.context = context
        annotations = IAnnotations(context)
        if ANNOTATION_KEY not in annotations:
            annotations[ANNOTATION_KEY] = PersistentMapping()
        self._votes: PersistentMapping = annotations[ANNOTATION_KEY]

    # ----- helpers -----------------------------------------------------

    @property
    def _option_count(self) -> int:
        return len(self.context.options or [])

    @staticmethod
    def _clean_name(name: str) -> str:
        if not isinstance(name, str):
            raise ValueError("Participant name must be a string.")
        cleaned = name.strip()
        if not cleaned:
            raise ValueError("Participant name must not be empty.")
        return cleaned

    # ----- public API --------------------------------------------------

    def cast_vote(self, name: str, votes: Sequence[bool]) -> None:
        cleaned = self._clean_name(name)
        votes_list = list(votes)
        expected = self._option_count
        if len(votes_list) != expected:
            raise ValueError(
                f"Expected {expected} votes (one per option), got {len(votes_list)}."
            )
        self._votes[cleaned] = PersistentList(bool(v) for v in votes_list)

    def get_vote(self, name: str) -> list[bool] | None:
        cleaned = self._clean_name(name)
        stored = self._votes.get(cleaned)
        if stored is None:
            return None
        return list(stored)

    def get_votes(self) -> dict[str, list[bool]]:
        return {name: list(votes) for name, votes in self._votes.items()}

    def remove_vote(self, name: str) -> bool:
        cleaned = self._clean_name(name)
        if cleaned in self._votes:
            del self._votes[cleaned]
            return True
        return False

    def participants(self) -> list[str]:
        return sorted(self._votes.keys())

    def tally(self) -> list[int]:
        counts = [0] * self._option_count
        for votes in self._votes.values():
            for index, choice in enumerate(votes):
                if index >= len(counts):
                    break
                if choice:
                    counts[index] += 1
        return counts
