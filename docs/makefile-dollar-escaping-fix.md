# Makefile Dollar-Sign Escaping Fix

## Problem

The `release-patch`, `release-minor`, and `release-major` targets in the
PyScaffold Clickstart Makefile produce garbage tag names (e.g. `EW` instead
of `v1.0.0`) because shell variables and shell arithmetic are not properly
escaped for GNU Make.

## Root Cause

In GNU Make recipes, `$` is the variable-expansion character:

| Makefile syntax | Make sees | Shell receives |
|----------------|-----------|----------------|
| `$N` | Variable `N` (single-char) | empty string (unless Make var `N` is set) |
| `$(NAME)` | Variable `NAME` | empty string (unless Make var `NAME` is set) |
| `$$` | Literal dollar | `$` |

When the recipe contained:

```makefile
@NEW="v$(($(MAJOR) + 1)).0.0"; \
echo "Tagging $NEW ..."
```

Make expanded `$N` (the Make variable `N`, which is empty) leaving `EW` as a
literal.  Similarly, `$((...))`  was partially consumed by Make's `$(`
expansion before reaching the shell.

## Fix

Escape every shell `$` as `$$` in Make recipes.  Only Make-level variables
like `$(MAJOR)` and `$(CHANGELOG)` remain single-`$`:

```makefile
# BEFORE (broken)
@NEW="v$(($(MAJOR) + 1)).0.0"; \
echo "Tagging $NEW (from LAST_TAG=$(LAST_TAG))"; \
TMP="$(mktemp -t dof-tagmsg.XXXXXX)"; \
printf 'release: %s\n\n%s\n' "$NEW" "$(CHANGELOG)" > "$TMP"; \
git tag -a "$NEW" -F "$TMP"; \
rm -f "$TMP"; \
git push origin "$NEW"; \
echo "Tagged $NEW"

# AFTER (fixed)
@NEW="v$$(($(MAJOR) + 1)).0.0"; \
echo "Tagging $$NEW (from LAST_TAG=$(LAST_TAG))"; \
TMP="$$(mktemp -t dof-tagmsg.XXXXXX)"; \
printf 'release: %s\n\n%s\n' "$$NEW" "$(CHANGELOG)" > "$$TMP"; \
git tag -a "$$NEW" -F "$$TMP"; \
rm -f "$$TMP"; \
git push origin "$$NEW"; \
echo "Tagged $$NEW"
```

## Affected Targets

| Target | Shell vars needing `$$` |
|--------|------------------------|
| `release-patch` | `$$NEW`, `$$TMP`, `$$(($(PATCH) + 1))` |
| `release-minor` | `$$NEW`, `$$TMP`, `$$(($(MINOR) + 1))` |
| `release-major` | `$$NEW`, `$$TMP`, `$$(($(MAJOR) + 1))` |
| `check-clean` | `$$(git rev-parse ...)` |

## Quick Rule

> In a Makefile recipe, every `$` that is **meant for the shell** must be
> doubled to `$$`.  Only `$(MAKE_VAR)` references stay single-`$`.

## How to Audit Your Template

Search for unescaped shell dollars in recipes:

```bash
# Find recipe lines with likely unescaped shell vars
grep -n '^\t.*\$[^$(]' Makefile
grep -n '^\t.*\$([a-z]' Makefile   # lowercase = likely shell, not Make
```

Make variables are conventionally UPPER_CASE; shell variables are often
lower_case or mixed.  Any `$foo`, `$(cmd ...)`, or `$((expr))` in a recipe
line almost certainly needs `$$`.
