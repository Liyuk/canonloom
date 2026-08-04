# Public Release Checklist

## Repository

- [ ] Update `VERSION` and `CHANGELOG.md`.
- [ ] Run the Python compile check, test suite, and `git diff --check`.
- [ ] Run `python3 scripts/public_check.py --root .`.
- [ ] Run `examples/minimal-project/smoke.sh`.
- [ ] Confirm `README.md` and `README.en.md` describe the same commands.
- [ ] Confirm the license and contribution policy are present.

## Content and privacy

- [ ] Remove real manuscripts, private paths, API keys, and sensitive logs.
- [ ] Remove unauthorized reference text and copied passages.
- [ ] Keep examples original and small.
- [ ] Review `canon/`, `memory/`, `runs/`, and `logs/` before publishing a project repository.

## Runtime compatibility

- [ ] Confirm Python 3.9+ support.
- [ ] State the supported Python version.
- [ ] Test with the intended Codex/Claude Code instructions.
- [ ] Document which files the agent may write and where author approval is required.
- [ ] Keep protocol keys, enum values, paths, and stage IDs stable.
