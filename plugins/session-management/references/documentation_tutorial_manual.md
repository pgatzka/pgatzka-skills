# Building Documentation That People Actually Use

*A Tutorial Manual on Structuring Project Documentation*

> What pages to create, what each page should contain, and what can be merged.

---

## Contents

- [Introduction: Why Structure Matters More Than Volume](#introduction-why-structure-matters-more-than-volume)
- [Part 1. Foundations](#part-1-foundations)
  - [1.1 The Three Tenets](#11-the-three-tenets)
  - [1.2 The Diátaxis Framework](#12-the-diátaxis-framework)
- [Part 2. The Documents: What Pages You Need](#part-2-the-documents-what-pages-you-need)
  - [2.1 Project Initiation Documents](#21-project-initiation-documents)
  - [2.2 Planning Documents](#22-planning-documents)
  - [2.3 Requirements Documents](#23-requirements-documents)
  - [2.4 Design and Technical Documents](#24-design-and-technical-documents)
  - [2.5 Process Documents](#25-process-documents)
  - [2.6 Communication Documents](#26-communication-documents)
  - [2.7 Knowledge Transfer Documents](#27-knowledge-transfer-documents)
  - [2.8 Closure Documents](#28-closure-documents)
  - [2.9 Deciding Which Documents Your Project Needs](#29-deciding-which-documents-your-project-needs)
- [Part 3. Building the Structure: A Workflow](#part-3-building-the-structure-a-workflow)
  - [3.1 Decision Rules: When to Split, When to Merge](#31-decision-rules-when-to-split-when-to-merge)
  - [3.2 Naming and Structuring Pages](#32-naming-and-structuring-pages)
  - [3.3 Organizing Pages Into a Hierarchy](#33-organizing-pages-into-a-hierarchy)
  - [3.4 The Build Order](#34-the-build-order)
  - [3.5 Maintenance: Keeping It All Alive](#35-maintenance-keeping-it-all-alive)
- [Appendix: Quick Reference Checklists](#appendix-quick-reference-checklists)

---

# Introduction: Why Structure Matters More Than Volume

Most documentation fails for the same reason: it grows by accretion. Someone writes a how-to. Someone else adds an FAQ. A third person dumps technical notes into the same page. Six months later, no one can find anything, and new readers bounce off the chaos.

This manual teaches you the opposite approach: build documentation by deliberate design. You will learn which pages every project needs, what belongs on its own page, what can be safely merged, and how to organize the whole thing so readers find what they need on the first try.

The guidance here is built on three sources: the catalog of essential documentation types every project benefits from, the three tenets of good documentation (clear, concise, structured), and the Diátaxis framework for organizing content by purpose.

> **How to use this manual**
>
> - Read Part 1 first. It establishes the three tenets and the Diátaxis framework, which everything else depends on.
> - Use Part 2 as a reference. Each chapter describes one document type, what belongs there, and what you can merge it with.
> - Apply Part 3 when you sit down to build. It contains the step-by-step workflow and decision rules.

---

# Part 1. Foundations

Before deciding what pages to create, you need a mental model for why pages exist at all. Two ideas drive everything that follows.

## 1.1 The Three Tenets

Every page you write should be evaluated against three principles. If a page violates one, fix it before publishing.

### Clear

Use plain language. Ask yourself whether anyone in your target audience would stumble on an acronym or piece of jargon. If yes, either swap it for simpler language or define it the first time it appears. Clarity is an accessibility issue: the goal is to make documentation usable by the widest possible audience.

### Concise

Document only what is necessary. Trying to cover every edge case overwhelms readers and buries the information that actually matters. Write for the vast majority of readers who need to get started, understand core concepts, and use your project. Edge cases can go in separate pages, linked when relevant.

### Structured

Make pages easy to scan. Put the most important information first, use headings and a table of contents, apply text highlighting like bold sparingly (aim for ten percent of body text or less), and stay consistent with styling across documents. If terminology is bold in one document, make it bold in all of them.

> **The litmus test**
>
> Before publishing any page, read it as if you have never seen the project before. Can you find the key point in under thirty seconds? If not, restructure before you add more content.

## 1.2 The Diátaxis Framework

Diátaxis is a systematic approach to organizing documentation. It divides every document into one of four categories based on its purpose. Each category has a different reader in mind and a different shape.

| Category | Purpose | Reader's mindset | Example |
|---|---|---|---|
| **Tutorial** | Learning-oriented. Teaches a skill through guided practice. | "I'm new. Walk me through it." | "Build your first API integration in 20 minutes" |
| **How-to guide** | Goal-oriented. Solves a specific problem. | "I know what I'm doing. I need to get this one thing done." | "How to rotate API keys" |
| **Reference** | Information-oriented. Describes the machinery. | "I need to look something up." | API endpoint specs, configuration keys, CLI flags |
| **Explanation** | Understanding-oriented. Discusses why things are the way they are. | "I want to understand the design." | "Why we chose event-driven architecture" |

The framework matters because mixing categories on a single page is the single most common documentation mistake. A tutorial that suddenly veers into architectural justification loses beginners. A reference page padded with tutorial-style hand-holding wastes the time of experienced readers. Keep each page in one category.

> **Rule of thumb for assigning pages**
>
> - If the page teaches a skill from scratch: tutorial.
> - If it answers "how do I do X": how-to.
> - If it answers "what does X do" or "what are the options for X": reference.
> - If it answers "why does X exist" or "why was X built this way": explanation.

---

# Part 2. The Documents: What Pages You Need

This part walks through the documents most projects need. For each one, you get its purpose, what belongs on its own page, what can be merged with something else, and which Diátaxis category it falls into. Not every project needs every document. Use Chapter 2.9 to decide which ones apply to yours.

## 2.1 Project Initiation Documents

These set the stage. They are written once at the start and revisited at major milestones.

### Project Charter

**Diátaxis category:** Explanation (it justifies why the project exists).

Purpose: authorize the project and give the project lead authority to allocate resources.

**Belongs on its own page when:** the project has formal stakeholders, a budget, or anyone who might later ask "why are we doing this?"

**Can be merged with the Business Case** for small internal projects where the same audience reads both. For anything cross-team or external, keep them separate; they have different review cycles.

- Project purpose and justification
- High-level requirements and success criteria
- Budget summary
- Key stakeholders and their roles
- Approval signatures

### Business Case

**Diátaxis category:** Explanation.

Purpose: justify the project from a business perspective. Read by leadership when budget questions arise.

**Belongs on its own page when:** ROI, cost-benefit analysis, or strategic alignment will be revisited. This is the document leadership pulls up when priorities shift.

**Can be merged with the Charter** for small projects, as noted above.

### Stakeholder Register

**Diátaxis category:** Reference.

Purpose: list everyone with an interest in the project, their influence, and how they prefer to be communicated with.

**Belongs on its own page when:** you have more than five stakeholders or any cross-organizational dependencies.

**Can be merged into the Project Management Plan** for small projects with a handful of well-known stakeholders.

## 2.2 Planning Documents

### Project Management Plan

**Diátaxis category:** Reference.

Purpose: describe how the project will be executed. This is the operational bible.

**Belongs on its own page when:** always, for any project larger than a single sprint. For tiny projects, a short README section may suffice.

**What to merge inside it (don't make these separate pages):**

- Communications plan
- Quality management plan
- Resource management plan
- Procurement plan (if procurement is minimal)

**What to keep on its own page:**

- Risk register (this is a living document, updated weekly)
- Project schedule (updated continuously)
- Stakeholder register (if substantial)

### Work Breakdown Structure (WBS) and Schedule

**Diátaxis category:** Reference.

Purpose: break work into trackable units and show when each unit happens.

**Belongs on its own page** always. The schedule is the most frequently consulted artifact in any project; do not bury it inside a larger plan.

**Merge the WBS into the schedule** for most projects. Maintaining them as separate documents creates drift.

### Risk Register

**Diátaxis category:** Reference.

Purpose: track identified risks, their probability and impact, mitigation strategies, and owners.

**Belongs on its own page** always. The register changes every week; embedding it in another document means the other document is constantly stale.

## 2.3 Requirements Documents

### Requirements Specification or Product Requirements Document (PRD)

**Diátaxis category:** Reference (with some explanation interleaved).

Purpose: define what will be built. The bridge between business stakeholders and technical teams.

**Belongs on its own page when:** the project has more than a handful of features or any non-functional requirements (performance, security, compliance).

**How to split it when it grows:** when a PRD exceeds about 20 pages, split by feature area into separate documents, with a top-level PRD that summarizes and links to each one. Do not split by document type (functional vs. non-functional) because readers want to see all requirements for a given feature together.

- Functional requirements (what the system does)
- Non-functional requirements (performance, security, usability)
- User stories or use cases
- Acceptance criteria
- Assumptions and constraints

### User Stories

**Diátaxis category:** Reference.

Purpose: short descriptions of features from the user's perspective. Format: "As a [user type], I want [goal] so that [benefit]."

**Live where the work lives.** User stories belong in your work tracker (Jira, Linear, GitHub Issues), not in standalone documents. The PRD links to them.

## 2.4 Design and Technical Documents

### System Architecture Document

**Diátaxis category:** Explanation (primarily) with reference elements.

Purpose: communicate the structure of the system and the reasoning behind key decisions.

**Belongs on its own page** always for anything beyond a trivial system. This is the document new engineers read on day one.

**What to include:**

- Architecture diagram (one clear diagram, not five overlapping ones)
- Component responsibilities
- Integration points and external dependencies
- Why this architecture was chosen, and what alternatives were rejected

> **Include the why, not just the what**
>
> Future maintainers need to know the reasoning behind architectural decisions, not just the final shape. Without the why, they will re-litigate decided questions or make changes that quietly break invariants the original team relied on.

### Technical Design Documents (per feature)

**Diátaxis category:** Explanation.

Purpose: detailed design for a specific feature or subsystem. Separate from the system architecture, which is the top-level view.

**One page per significant feature.** Do not collect them into a single mega-document. Each design doc is a contained artifact that can be linked from a feature ticket.

### API Documentation

**Diátaxis category:** Reference.

Purpose: comprehensive guide to endpoints, request and response formats, authentication, and error codes.

**Belongs on its own page** always. API docs should be generated from the API definition (OpenAPI, GraphQL schema) wherever possible so they cannot drift from reality.

### Database Schema Documentation

**Diátaxis category:** Reference.

Purpose: describe tables, columns, relationships, and indexes.

**Auto-generate this from the database** wherever possible. Hand-maintained schema docs are almost always wrong. If the project is small, an entity-relationship diagram with a short prose summary is enough; merge it into the system architecture document.

## 2.5 Process Documents

### Standard Operating Procedures (SOPs)

**Diátaxis category:** How-to.

Purpose: step-by-step instructions for recurring tasks.

**One page per procedure.** Resist the urge to collect SOPs into a single "operations manual." Each SOP is consulted in isolation, usually when someone is in the middle of doing the task. They need to find it fast.

**Merge related SOPs when:** two procedures are always performed together ("deploy and verify") or one is meaningless without the other.

### Workflow Documentation

**Diátaxis category:** Explanation.

Purpose: describe how work flows through the team. Shows handoffs, decision points, and approval requirements.

**Belongs on its own page** when the workflow involves more than two roles or any branching logic. Otherwise a short section in the team README suffices.

### Quality Assurance and Testing Strategy

**Diátaxis category:** Explanation (the strategy) plus Reference (the standards).

**Belongs on its own page** for the strategy and definition of done. Test cases themselves live in your test framework, not in documentation.

## 2.6 Communication Documents

### Status Reports

**Diátaxis category:** Reference (point-in-time snapshots).

Purpose: regular updates on progress, issues, and upcoming work.

**One page per report**, filed in a clearly dated folder or channel. Use a single template across all reports so readers can compare across time without re-learning the layout.

### Meeting Minutes

**Diátaxis category:** Reference.

**One page per meeting.** Circulate within twenty-four hours. Decisions made in meetings should also be cross-posted to the decision log (see below) so they outlive the meeting record.

### Decision Log (often missed)

**Diátaxis category:** Explanation. (A decision record's primary job is to answer "why was this chosen and what alternatives were rejected" — that's understanding-oriented content, even though the page is consulted later as a reference.)

Purpose: record significant decisions, their rationale, and who made them. Often called Architecture Decision Records (ADRs) in technical contexts.

**Belongs on its own page** (or one short page per decision). This is what saves you when someone asks "why did we decide this six months ago?" Without it, decisions get re-litigated endlessly.

### Change Requests

**Diátaxis category:** Reference.

Purpose: formal proposals to modify project scope, schedule, or budget.

**One page per request**, with status tracked in a single index page that lists all requests and their state.

## 2.7 Knowledge Transfer Documents

### Tutorials (Getting Started)

**Diátaxis category:** Tutorial.

Purpose: teach a new user how to do something useful, end to end, on their first attempt.

**Belongs on its own page** always. The first tutorial a new user encounters determines whether they keep going or give up. It deserves a dedicated, well-tested page.

**Have multiple tutorials when:** your project has more than one type of user (admin vs. developer, for instance). One tutorial per audience.

### User Manuals

**Diátaxis category:** How-to (mostly) with some Reference.

**Organize by user goal, not system structure.** Users do not care about your architecture; they want to accomplish tasks. "How do I export my data" is a better page title than "Data Export Subsystem."

### Training Materials

**Diátaxis category:** Tutorial.

**Merge with the Getting Started tutorial** when the audience is the same. Keep them separate when training is for administrators or operators with different needs than end users.

### Knowledge Base

**Diátaxis category:** How-to.

Purpose: searchable repository of answers to specific problems.

**One short article per problem.** Tag and categorize aggressively. The knowledge base is only valuable if articles can be found via search; that means descriptive titles, keywords, and tags matter more than prose elegance.

## 2.8 Closure Documents

### Lessons Learned

**Diátaxis category:** Explanation.

**One page per project.** Capture lessons throughout the project, not only at the end. Memory degrades; real-time reflection is more accurate.

### Project Closure Report

**Diátaxis category:** Reference.

Purpose: formal record of project completion, final deliverables, and transition to operations.

## 2.9 Deciding Which Documents Your Project Needs

Use this matrix to scope your documentation set. Small projects can skip many documents entirely; complex or regulated projects need most of them.

| Document | Solo / tiny | Small team | Mid-size | Large / regulated |
|---|---|---|---|---|
| Charter | — | Short | Full | Full |
| Business case | — | Optional | Full | Full |
| PRD or requirements | README section | Short | Full | Full, split by feature |
| System architecture | README section | Page | Page + per-feature designs | Full hierarchy |
| API docs | Auto-generate | Auto-generate | Auto-generate | Auto-generate |
| SOPs | — | As needed | One per procedure | One per procedure, audited |
| Risk register | — | Optional | Required | Required, formal |
| Decision log | Recommended | Required | Required | Required |
| Tutorial / getting started | Required | Required | Required | Required, per audience |
| Lessons learned | Optional | Recommended | Required | Required |

---

# Part 3. Building the Structure: A Workflow

This part is the practical guide. Follow it in order the first time you set up documentation for a project; revisit it whenever you reorganize.

## 3.1 Decision Rules: When to Split, When to Merge

The single hardest question in documentation is whether something deserves its own page. Apply these rules in order, and stop at the first one that gives a clear answer.

1. **Different Diátaxis category? Always split.** A tutorial and a reference page never belong together, regardless of how related their subjects are.
2. **Different update cadences? Split.** If one document changes weekly and another changes yearly, keeping them together guarantees one will be stale.
3. **Different audiences? Usually split.** A page written for executives and engineers simultaneously tends to serve neither well.
4. **Different ownership? Split.** Two owners for one page is two owners for nothing.
5. **Read together every time? Merge.** If readers always need both at once, splitting wastes their time.
6. **One is meaningless without the other? Merge.** A two-paragraph appendix on its own page is friction; fold it in.
7. **Combined page exceeds about twenty pages? Split.** Long pages discourage reading; readers scroll past the part they need.

## 3.2 Naming and Structuring Pages

How you name and structure individual pages determines whether anyone can find them later.

### Naming conventions

- Use descriptive titles that match the words your readers would search for. "How to rotate API keys" beats "API Key Rotation Procedure" beats "Procedure-007."
- Include the document type in formal documents: "SOP - Customer Onboarding," "ADR - 2026-03-15 - Choosing Postgres."
- Use ISO date format (YYYY-MM-DD) when dates appear in titles. It sorts correctly and avoids ambiguity.
- Be consistent. If your SOPs use one naming pattern and your ADRs use another, that is fine. But every SOP should follow the same pattern.

### Page structure

Every page should follow the same internal structure. Pick a template per document type and use it everywhere.

- **Header:** title, version or last-updated date, owner.
- **Purpose statement:** one or two sentences explaining who the page is for and what they will get from it. This is the second thing readers look at after the title.
- **Table of contents:** for any document longer than three printed pages.
- **Body:** most important information first. Reverse the academic instinct to build up to your conclusion.
- **Related links:** at the end. Sibling documents, parent documents, and any external resources.

## 3.3 Organizing Pages Into a Hierarchy

Once you have decided which pages exist, organize them so people can navigate without help.

### Two organizing schemes that work

**By Diátaxis category.** Top-level sections are "Tutorials," "How-to guides," "Reference," and "Explanation." Inside each, group by topic. This is the default for technical and product documentation, especially anything user-facing.

**By project phase.** Top-level sections are "Planning," "Design," "Development," "Deployment," "Operations." Inside each, group by document type. This works better for internal project documentation where readers are looking for documents created at a specific phase.

Do not mix the two at the top level. Pick one organizing scheme and apply it consistently. Mixed schemes confuse readers because they cannot predict where to look.

### Depth limits

- Three levels of nesting maximum. Beyond three, readers get lost.
- If a section has more than about ten items, split it. Long flat lists are unscannable.
- Every page should be reachable from the top in three clicks or fewer.

### Index pages

At each level of the hierarchy, include an index page that explains what is in this section, who it is for, and links to every page below. Index pages are how readers orient themselves; without them, navigation depends entirely on guessing from sidebar labels.

> **The thirty-second test**
>
> Ask someone unfamiliar with the project to find a specific piece of information. Time them. If it takes more than thirty seconds, your navigation is broken. The fix is almost always better page titles or a clearer index, not more documentation.

## 3.4 The Build Order

If you are starting from scratch, build documentation in this order. Do not try to build everything at once.

1. **Start with a README at the top level.** One page, written for someone arriving today. What is this project? Who is it for? Where do they go next?
2. **Add a single getting-started tutorial.** The most important page in your documentation. Test it by handing it to someone new and watching them work through it.
3. **Add the system architecture document.** One page, one diagram, the reasoning behind the design.
4. **Add reference documentation for the parts you have.** API docs, configuration reference, schema. Auto-generate whenever possible.
5. **Add how-to guides as questions come up.** Every time someone asks a question that should have been documented, write a how-to. The questions tell you what is missing.
6. **Add explanation documents for the decisions worth preserving.** Architecture decisions, trade-offs, history.
7. **Add process documents (SOPs, workflows)** once the team is large enough that things vary between people.
8. **Add governance documents (charter, business case, status reports)** for any project with formal stakeholders.

## 3.5 Maintenance: Keeping It All Alive

Documentation that is created once and never updated is worse than no documentation, because readers trust it and then act on wrong information.

- **Assign an owner to every page.** Without an owner, no one is responsible for updates.
- **Set review cadences by document type.** Schedules and risk registers: weekly. SOPs: quarterly. Architecture: when it changes, plus an annual review.
- **Define update triggers.** When a feature ships, which pages must be updated? Make this a checklist item in your release process.
- **Archive aggressively.** Pages that no longer apply should be moved to an archive section, not deleted. Deletion loses history; leaving them in place misleads readers.
- **Budget time.** Roughly ten to twenty percent of project time goes to documentation creation and maintenance. Treat it as essential work, not overhead.

---

# Appendix: Quick Reference Checklists

## Before you create a new page

- What Diátaxis category is this? (Tutorial, how-to, reference, or explanation.)
- Who is the audience? Name them specifically.
- What decision or action does this page enable?
- Does an existing page already cover this? If yes, extend or split that page instead of creating a new one.
- Who will own and maintain this page?
- When will it next be reviewed?

## Before you publish a page

- Does the title match how a reader would search for this?
- Does the purpose statement appear in the first two sentences?
- Can a new reader find the key information in under thirty seconds?
- Are all acronyms and jargon defined or removed?
- Is text highlighting under ten percent of body text?
- Are related documents linked?

## When you are deciding to split or merge

- Different Diátaxis category? Split.
- Different update cadences? Split.
- Different audiences or owners? Usually split.
- Always read together? Merge.
- One meaningless without the other? Merge.
- Combined length exceeds twenty pages? Split.

## Common mistakes to avoid

- Documenting for its own sake, without a clear reader or purpose.
- Creating one giant document that mixes tutorial, reference, and explanation.
- Assuming context the reader does not have.
- Burying important pages three or four levels deep in the hierarchy.
- Creating documentation once and never updating it.
- Storing documentation in places no one searches.

---

*End of Manual*
