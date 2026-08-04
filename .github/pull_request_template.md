## Summary

## What changed

- [ ] CLI
- [ ] Schema or artifact protocol
- [ ] Agent instructions
- [ ] Documentation
- [ ] Tests

## Safety and workflow impact

- Does this change canon, manuscript, approval, or repair boundaries?
- Are protocol keys and stage IDs backward compatible?

## Checks

```sh
python3 -m py_compile scripts/*.py
python3 -m unittest discover -s tests -q
python3 scripts/public_check.py --root .
examples/minimal-project/smoke.sh
git diff --check
```
