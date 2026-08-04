# Style Profile

`intent/style-profile.json` is a project-level prose protocol. It moves “how this project should read” out of a temporary chapter prompt so agents, context compilation, and Python checks can use the same source.

It has two layers:

```text
mechanically checkable: length, rhythm, dialogue ratio, forbidden terms, punctuation
literary judgment: narrative distance, tone, imagery, subtext, emotional expression
```

Example:

```json
{
  "schema_version": "0.1",
  "profile_id": "harbor-mystery-v1",
  "name": "Restrained wet investigative prose",
  "narrative": {
    "viewpoint": "close-third",
    "distance": "observational",
    "tense": "past",
    "register": "restrained",
    "voice_keywords": ["quiet", "wet", "evidence-driven"],
    "avoid_tendencies": ["explaining emotions directly"]
  },
  "dialogue": {
    "min_ratio": 0.08,
    "max_ratio": 0.25,
    "dialogue_must_change": true
  }
}
```

The profile is a constraint and review aid, not a guarantee of literary quality and not a request to imitate a living author. Use high-level, original characteristics and keep copyright boundaries explicit.
