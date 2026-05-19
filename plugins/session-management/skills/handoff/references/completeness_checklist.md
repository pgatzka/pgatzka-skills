# Handoff completeness checklist

The handoff skill walks this list once per invocation. For each item, capture what this session produced. If nothing applies, write "nothing this session" in the final report — never fabricate content, because the next session orients off this report and a fabricated item costs more than a missing one.

1. **Project overview** — purpose, tech stack one-liner, top-level structure. Updates the project root index page.
2. **Current state of work** — what's implemented and working, what's stubbed, what's incomplete. Concrete file:line pointers over prose.
3. **Open tasks** — what the next session should pick up. Priority-ordered, with acceptance criteria per task. If the current session used a task-tracking tool (`TodoWrite`, `TaskCreate`, etc.) and its open items are visible in working memory, transcribe them here. The handoff skill itself never invokes a task tool — it captures what's already there.
4. **Open questions** — decisions pending the user. Include why each blocks progress.
5. **Decisions made this session** — each becomes an ADR (Explanation, one page per decision). Title `ADR - YYYY-MM-DD - <short decision>.md`. Body: context, decision, alternatives considered, reasoning, links to related pages.
6. **Tech-stack changes** — new deps, version bumps, tool swaps. Merges into the tech-stack Reference page.
7. **New or extended features** — one Reference or Explanation page per feature ("Structured Questions Plugin", "Session Management Plugin", etc.). Reference for *what it is*; Explanation for *why it's shaped that way*.
8. **Gotchas and dead ends** — surprises hit, with root cause and fix or workaround. File:line pointers. Usually a Reference page ("Known issues") or appended to the relevant feature page.
9. **Conventions or rules learned** — durable preferences the user expressed (commit style, error-handling preference, naming convention). Reference page per area.
10. **Next-session orientation** — a one-paragraph "start here" pointer; lives on the index page.

For each captured item, also classify whether it is *universally applicable to every session in this project*. If yes, flag it as a possible CLAUDE.md addition in the final report — but do not modify CLAUDE.md from this skill. CLAUDE.md edits are the user's call. Overlap with Obsidian is expected: CLAUDE.md gets the one-liner, Obsidian gets the depth.
