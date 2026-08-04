#!/bin/sh
set -eu

repo_root=$(CDPATH= cd -- "$(dirname "$0")/../.." && pwd)
project=$(mktemp -d "${TMPDIR:-/tmp}/canonloom-minimal.XXXXXX")
trap 'rm -rf "$project"' EXIT

"$repo_root/bin/canonloom" init "$project" \
  --name "Minimal Story" \
  --language en-US \
  --genre mystery \
  --audience "adult readers" \
  --pov close-third >/dev/null

"$repo_root/bin/canonloom" --root "$project" setup --confirm >"$project/setup.out"
grep -q "AUTHOR_SETUP_CONFIRMED" "$project/setup.out"
"$repo_root/bin/canonloom" --root "$project" idea --input "A locked room and an unreliable witness" >/dev/null
"$repo_root/bin/canonloom" --root "$project" diagnose >/dev/null
grep -q "LANGUAGE: en" "$project/tasks/current.md"
grep -q "Start ideation" "$project/tasks/current.md"

echo "MINIMAL PROJECT SMOKE: OK"
