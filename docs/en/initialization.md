# Initialization Protocol

CanonLoom does not treat initialization as “create folders and immediately write prose.” It first establishes the project's boundaries.

## Author-controlled configuration

The author fills in or confirms `intent/author-setup.json`:

- project title, language, genre, and subgenres;
- target audience;
- viewpoint, tense, and tone direction;
- content boundaries;
- chapter length and dialogue ratio;
- automation mode and review profile;
- author notes and non-negotiable principles.

These fields are not final project constraints until `author_confirmed` is `true`.

You may provide the first author inputs during initialization:

```sh
./bin/canonloom init ~/my-novel --name "Harbor Mystery" \
  --language en-US --genre "speculative mystery" \
  --audience "adult readers" --pov close-third \
  --chapter-min 3000 --chapter-max 7000
```

The flags write the setup file but do not confirm it automatically.

## AI recognition layer

After reading the author setup, existing manuscripts, or reference notes, an agent may write candidates to `intent/ai-recognition.json`:

- candidate characters, places, organizations, and timeline items;
- open loops in imported material;
- possible genre mechanisms and transferable techniques;
- inferred style candidates;
- uncertainty and questions for the author.

AI recognition is a proposal layer. It must not silently promote facts to `canon/`. The author reviews candidates before later workflow stages use them as canon.

## Recommended flow

```text
./bin/canonloom init
  ↓
./bin/canonloom --root ~/my-novel setup
  ↓
author confirms author-setup
  ↓
agent proposes ai-recognition
  ↓
author confirms candidates and style profile
  ↓
idea → planning → contract → work
```

Confirm the author setup with:

```sh
./bin/canonloom --root ~/my-novel setup --confirm
```

Before confirmation, CanonLoom does not allow `planning`, `work`, `characters`, `world`, `research`, `revision`, or `review`. `idea` and `reference` remain available for exploration.
