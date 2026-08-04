# Narrative State Layer

The narrative state layer is an optional CanonLoom enhancement. It does not change the existing S0–S6 gates by default. It records what happened, who knows what, and which reveals remain open.

## Files

```text
memory/narrative-state/
  state-policy.json
  events.jsonl
  knowledge.jsonl
  reveals.json
```

Use it with:

```sh
./bin/canonloom --root ~/my-novel state report
./bin/canonloom --root ~/my-novel state validate
```

New projects start with `narrative_state.mode=optional`. Adopt it gradually:

1. record events for important chapters without changing gates;
2. run `state validate` for duplicate IDs, statuses, sources, and reveal state;
3. after the format is stable, add selected state checks to chapter contracts or project gates.

AI may propose `PROPOSED` records. Author confirmation is required before records become `CONFIRMED`; promotion into project `canon/` remains a separate author-approved settlement decision.

The chapter contract can later add causal change, character agency, reader effect, and reveal updates. See the Chinese guide and the four narrative-state schemas for the complete protocol.
