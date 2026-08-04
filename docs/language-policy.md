# Language Policy

CanonLoom supports Chinese, English, and mixed-language projects. Language is configured at the project level, while the machine protocol remains language-neutral.

## Stable protocol language

The following should remain stable English identifiers:

- JSON keys and schema enum values;
- CLI command names;
- directory names and artifact filenames;
- stage IDs such as `S0`, `S1`, and `S6`;
- approval and severity values such as `AUTHOR_APPROVED`, `BLOCKER`, and `ADVISORY`.

This prevents Codex, Claude, scripts, and future adapters from interpreting translated keys as different fields.

## Project content language

The author chooses the content language in `intent/author-setup.json`:

```json
{
  "language": "zh-CN"
}
```

Use values such as `zh-CN`, `en-US`, or another BCP-47-style tag. The setting applies to author intent, planning prose, chapter drafts, and human-facing review explanations unless the author overrides it.

## Agent instruction language

Agent instructions may be bilingual. The important requirement is semantic consistency:

- preserve the exact paths and protocol fields;
- do not translate status values inside JSON;
- do not silently translate canon facts;
- if a reviewer uses another language, keep the evidence path and finding ID unchanged.

## Recommended default

For a Chinese novel, use Chinese for prose and review explanations, English for protocol identifiers, and bilingual repository instructions. For an English novel, reverse the prose/review preference while keeping the same protocol layer.

Do not require the model to think or prompt in one language if the author can review another language more reliably. The project language is a review and artifact contract, not a restriction on the model's internal reasoning.
