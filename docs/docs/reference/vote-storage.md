---
myst:
  html_meta:
    "description": "Reference for the IVoteStorage adapter on Poll"
    "property=og:description": "Reference for the IVoteStorage adapter on Poll"
    "property=og:title": "Vote storage"
    "keywords": "Plone, experimental.doodle, vote, adapter, annotation"
---

# Vote storage

The `IVoteStorage` adapter records and aggregates votes for a `Poll`. It
provides the Python API that higher-level layers (REST services, browser
views) will build on in later steps.

## Interface

The interface lives at `experimental.doodle.interfaces.IVoteStorage` and
adapts an `IPoll`. The implementation is
`experimental.doodle.adapters.vote_storage.VoteStorage`, registered through
ZCML.

| Method | Returns | Notes |
|---|---|---|
| `cast_vote(name, votes)` | `None` | Records a participant's vote. Idempotent: casting again with the same name overwrites. Raises `ValueError` on invalid input. |
| `get_vote(name)` | `list[bool]` or `None` | The participant's stored votes, or `None` if they haven't voted. |
| `get_votes()` | `dict[str, list[bool]]` | Plain snapshot of all stored votes; safe to mutate. |
| `remove_vote(name)` | `bool` | Removes the entry. Returns `True` if a vote was removed, `False` otherwise. |
| `participants()` | `list[str]` | Participant names sorted alphabetically. |
| `tally()` | `list[int]` | Yes-counts per option, parallel to `poll.options`. |

## Validation rules

`cast_vote` enforces three rules:

- The `name` must be a non-empty string after `.strip()`. Leading and
  trailing whitespace is removed; case is preserved.
- The `votes` sequence must have exactly `len(poll.options)` entries.
- Each entry of `votes` is coerced through `bool(...)` before storage.

Violations raise `ValueError` with a descriptive message. Reading methods
(`get_vote`, `get_votes`, `remove_vote`, `participants`, `tally`) never
raise on missing data; they return sensible empty values instead.

## Where the data lives

Votes are stored as a `zope.annotation` entry on the Poll under the key
`experimental.doodle.votes`. The value is a `PersistentMapping` of
participant names to `PersistentList` choices. Both types come from
`persistent` so that ZODB picks up mutations correctly.

The annotation is created on first adapter instantiation. A poll that
has never been voted on costs nothing extra in storage until someone
casts a vote.

## Example

```python
from datetime import datetime, timedelta, timezone
from experimental.doodle.interfaces import IVoteStorage
from plone import api


def create_and_vote(container):
    now = datetime.now(tz=timezone.utc)
    poll = api.content.create(
        container=container,
        type="Poll",
        title="Team lunch",
        options=[
            now + timedelta(days=1, hours=12),
            now + timedelta(days=1, hours=13),
            now + timedelta(days=2, hours=12),
        ],
    )

    storage = IVoteStorage(poll)
    storage.cast_vote("Alice", [True, False, True])
    storage.cast_vote("Bob", [True, True, False])

    return storage.tally()  # -> [2, 1, 1]
```

## What's not in this layer

The adapter intentionally stays minimal. The following arrive in later
steps:

- HTTP endpoints (`plone.restapi` services).
- Browser views and a vote form.
- Anonymous voter tokens, email notifications, vote history.

## Related references

- {doc}`poll-content-type`: the content type the adapter works on.
- {doc}`/concepts/domain-model`: the overall Doodle-style domain.
