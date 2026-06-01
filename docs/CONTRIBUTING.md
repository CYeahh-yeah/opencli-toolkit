# Contributing

Thanks for considering a contribution. This is a small toolkit, and
we want to keep it small.

## Ground rules

1. **The script must solve a real problem you've hit at least once.**
   Toy demos and "this could be useful" tools don't ship.
2. **Stay under 200 lines.** Force yourself to cut scope.
3. **Default to safe (dry-run / no-network).** Make destructive ops
   require an explicit flag.
4. **Add an entry to the README's toolkit table** and to `CHANGELOG.md`.
5. **Don't add dependencies** unless the standard library can't do it
   in <20 lines.

## Adding a new script

1. Drop the script in `scripts/` with a one-line shebang and a
   module-level docstring explaining **why this exists**, not just
   what it does.
2. Add a subcommand in `otk/__main__.py` that calls it via
   `subprocess` (avoids re-importing Python modules with side-effects).
3. Add a row to the README's toolkit table.
4. Bump the version in `pyproject.toml` and add a CHANGELOG entry.

## Style

- Python: `black` + `ruff`, target 3.10+
- Bash: `shellcheck` clean
- Markdown: 80-char line wrap, no trailing whitespace

## Reporting issues

Use the GitHub issue tracker. Include:
- The exact command you ran
- The expected vs actual output
- Your OS and Python version

## Code of conduct

Be kind. We delete mean comments, not the people who wrote them.
