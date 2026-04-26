---
name: gitignore
description: Use whenever creating or editing a .gitignore file, deciding what to exclude from version control, cleaning up `git status` noise, or reviewing untracked files before a commit. Triggers on phrases like "add to gitignore", "ignore this", "what should I gitignore", "git is tracking <file>", and on any edit to a .gitignore file. Enforces minimal, anchored, alphabetically-sorted entries that reflect what actually exists in the repo — never speculative bulk-adds from generic templates.
---

# .gitignore

A `.gitignore` is a contract about what *this* repository considers noise. It is read constantly (every `git status`, every code review, every onboarding) and it ages — patterns added "just in case" rot into clutter that nobody dares delete because nobody remembers what they were for.

The rules below keep `.gitignore` tight, predictable, and verifiable. They optimize for a reader who scans top-to-bottom and wants to know exactly what's being hidden, without consulting outside knowledge about toolchains.

## Rules

### 1. Only ignore things that actually exist in this repo

Before adding a pattern, confirm a matching file or directory is **currently present on disk**. Not "the toolchain will eventually produce it." Not "it might appear later." Currently present, right now, visible to `ls -A` or `git status --short`.

This is strict on purpose. On a brand-new Spring Boot project where Maven hasn't run yet, you do not add `/target/` to `.gitignore` — there is no `target/` yet. Add it the first time it appears. Same for `node_modules/` before `npm install`, `dist/` before the first build, `.env` before someone creates one.

Do not paste in `github/gitignore` boilerplate templates. Do not pre-emptively ignore folders for tooling nobody is using yet.

**Why:** Speculative ignores hide real problems. If `.idea/` shows up later and shouldn't be committed, *that's the moment* to add it — at which point you also know whether the whole team uses JetBrains or just one person (whose ignore belongs in `~/.config/git/ignore` instead, not the repo). And the cost of adding a missing entry later is one line of diff; the cost of removing a stale one nobody remembers is endless "should I touch this?" friction.

**How to check:**

```bash
git status --short             # what's currently untracked
git ls-files --others --exclude-standard   # untracked, ignoring already-ignored
ls -A                          # what's actually on disk at the root
```

If a candidate pattern doesn't match anything from those, don't add it.

### 2. Anchor every entry with a leading `/`

Every line starts with `/`. This anchors the pattern to the directory containing the `.gitignore` (the repo root, for the top-level file). Without the leading slash, gitignore matches the basename anywhere in the tree — usually broader than intended.

Good — only the top-level `build/` dir:

```
/build/
```

Bad — matches `build/` anywhere, including `src/build/`, `vendor/build/`, etc.:

```
build/
```

**Why:** Anchored entries match what you can see when you `ls`. Unanchored entries silently catch things in subdirectories you didn't think about, which violates rule 1 (you can't have verified an unbounded set actually exists).

**Exception:** Subdirectory `.gitignore` files (e.g. `src/generated/.gitignore`) follow the same rule — entries start with `/` and are anchored to that subdirectory.

### 3. Directory entries end with a trailing `/`

A trailing `/` tells git "this is a directory" and prevents accidental matches against files of the same name. Directory entries end in `/`; file entries don't.

```
/dist/
/.env
```

(Here `/dist/` is a directory and `/.env` is a file.)

**Why:** Without the trailing `/`, `dist` would also match a file called `dist`. Being explicit removes ambiguity for the reader and for git.

### 4. Sort alphabetically — directories first, then files

List all directory entries (alphabetically) first, then all file entries (alphabetically). Separate the two blocks with a single blank line. This produces a predictable scan order and makes diffs of `.gitignore` itself meaningful (a moved line is a real change, not a re-sort).

```
/build/
/dist/
/node_modules/
/target/

/.env
/.env.local
/npm-debug.log
```

Leading dots sort before letters in standard ASCII order, so `/.env` comes before `/npm-debug.log`. That's fine — keep ASCII order, don't try to be clever.

### 5. Use wildcards only when you actually need them

Prefer enumerating real entries over patterns. Wildcards expand the contract — they say "and anything that matches in the future" — which makes the file harder to reason about and easy to over-match.

Good — these specific files exist and need ignoring:

```
/npm-debug.log
/yarn-error.log
```

Wildcard only justified when there are many rotating files you can't enumerate (e.g. log dir):

```
/logs/*.log
```

Reach for `*` when:
- The set is genuinely unbounded (rotating logs, generated files with hashes in the name, OS crash dumps).
- Listing every file would mean editing `.gitignore` constantly for the same category.

Otherwise, list the actual filenames. Three explicit lines beat one clever pattern.

### 6. No comments unless the user explicitly asks for them

Don't add `#` comment lines to `.gitignore` — no section headers (`# build artifacts`), no per-entry annotations (`# IDE`), no "what this is for" notes. The file should be a clean list of patterns.

**Why:** Comments are usually trying to compensate for unclear entries. With rule 1 (entries match real files) and rule 4 (sorted, dirs-then-files layout), each line is already self-explanatory — `/target/` is obviously the Maven output dir to anyone who knows this is a Maven project. Comments also rot independently of the patterns they describe and add diff noise when the file is reorganized.

**Exception:** Only add a comment when the user explicitly tells you to (e.g. "add a `# secrets` header above these"). Don't volunteer them.

This applies to the `.gitignore` you commit. It does *not* prohibit explanatory comments in markdown / docs / examples about gitignore (like this skill itself).

## Process when editing `.gitignore`

1. Run `git status --short` and `ls -A` to see what's actually present.
2. For each candidate ignore: confirm it exists, decide directory vs. file, write the pattern with a leading `/` (and trailing `/` for directories).
3. Insert the new line(s) into the right alphabetical position (directories block first, files block second).
4. Do not add comments.
5. Re-read the diff: every line should correspond to something a reader could `ls` and find.

## Things that don't belong in the repo's `.gitignore`

- **Editor/IDE files specific to one developer** (`.idea/`, `.vscode/`, `*.swp`) — put these in `~/.config/git/ignore` (your global gitignore) so they don't impose your tooling on the team.
- **OS-specific cruft** (`.DS_Store`, `Thumbs.db`) — same; global gitignore.
- **Anything you "might want later"** — add it later, when "later" arrives.

The repo's `.gitignore` should describe *the project*, not *your machine*.

## Example

A real Java/Maven repo where the developer has confirmed `target/`, `.idea/` (no — global), an `.env` file, and a `dependency-reduced-pom.xml` are present:

```
/target/

/.env
/dependency-reduced-pom.xml
```

That's it. No `*.class` ("Maven puts those under target/, already covered"), no `.idea/` ("that's my problem, not the repo's"), no `node_modules/` ("there's no JS here").
