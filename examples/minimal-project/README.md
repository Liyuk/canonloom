# Minimal Project Example

This directory documents the smallest supported author workflow. It is intentionally not a novel and contains no model-generated manuscript.

Requirements: Python 3.9+. From the CanonLoom repository root:

```sh
./bin/canonloom init /tmp/my-canonloom-story \
  --name "Minimal Story" \
  --language en-US \
  --genre "mystery" \
  --audience "adult readers" \
  --pov close-third

cd /tmp/my-canonloom-story
./bin/canonloom setup
./bin/canonloom setup --confirm
./bin/canonloom idea --input "A locked room and an unreliable witness"
./bin/canonloom status
./bin/canonloom diagnose
```

The important files are:

```text
intent/author-setup.json    author-controlled configuration
intent/ai-recognition.json  AI proposal layer
intent/style-profile.json   project writing constraints
canonloom.json               workflow state
tasks/current.md             current agent instruction
```

For a real chapter, continue with a chapter contract, bounded context package, draft, review reports, and explicit S6 approval. See `docs/strong-constraints.md`.
