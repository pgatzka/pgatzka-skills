---
name: database-design
description: "Use this skill whenever the user is doing anything with a relational database. Triggers include: designing or modifying schemas, creating or altering tables and columns, defining relationships, writing or reviewing migrations, writing SQL queries (SELECT, INSERT, UPDATE, DELETE, DDL), optimizing queries, adding indexes, reviewing ERDs, seeding data, or working with ORMs against a relational backend (Hibernate, JPA, Prisma, Drizzle, SQLAlchemy, ActiveRecord, TypeORM, jOOQ, etc.). Applies to relational systems: Postgres, MySQL, MariaDB, SQLite, SQL Server, Oracle. If the task touches a relational database in any way, use this skill."
---

# Database design

## Overview

This skill defines the conventions to follow when designing relational database schemas. Apply these rules whenever creating or modifying tables, columns, or relationships. When a rule conflicts with something the user has already established in their existing schema, flag the conflict and ask before deviating.

**When something is not fully specified — any decision is open (column type, length, nullability, naming, indexes, relationships, on-delete behavior, default values, etc.) — invoke the `ask-user-questions` skill and ASK. Never make the decision yourself.** Do not infer "reasonable defaults", do not pick "the obvious choice", do not silently fill gaps. If the user did not state it, ask.

**When asking, always include the best-practice option (with the reasoning) as one of the choices** — typically the first option, marked as recommended. Don't present neutral menus that hide which choice is industry-standard or safer; explain *why* the recommended option is the default so the user can make an informed call (or override knowingly).

## Dialect coverage

Rules are written dialect-agnostically. Where the syntax or behavior differs between Postgres, MySQL, SQL Server, Oracle, and SQLite, the rule includes a per-dialect note. When a single name is needed for a feature, Postgres terminology is used (e.g. `timestamp with time zone`).

If the project's dialect is unclear, ASK before producing DDL.

## Rules

### SQL style

- **All SQL is lowercase unless the user states otherwise.** Keywords (`select`, `create table`, `not null`, `primary key`, `default`, `references`, etc.), built-in types (`uuid`, `timestamp with time zone`, `varchar`, `text`), and function names are written in lowercase.
- **Identifiers use `snake_case`.** Tables, columns, constraints, indexes — all `snake_case`. No `camelCase`, no `PascalCase`. Postgres folds unquoted identifiers to lowercase anyway, and `snake_case` removes the need to ever quote them.

### Migration files

- **Flyway is the assumed migration tool unless the user says otherwise.** When the project uses something else (Liquibase, Alembic, Knex, Prisma migrate, …), ASK how the project's conventions differ.
- **One SQL statement per Flyway file.** Easier to review, easier to roll back, easier to read in `git blame`. If a logical change requires multiple statements, that's multiple Flyway files in the right `V` order.
- **Flyway filenames follow `V<number>__<description>.sql`** — Versioned migrations only; if the project also uses repeatable (`R__`) or undo (`U__`) migrations, follow project convention but ASK on first use.
- **The `<description>` should state what the migration does, in `<action>_<object>_<name>` shape** for the operations below. **For any operation not in the table** (data backfills, multi-statement, anything else), invoke the `ask-user-questions` skill and ASK what filename shape to use — propose a candidate as the recommended option, but don't pick on the user's behalf:

  | Operation | Filename shape | Example |
  |---|---|---|
  | Create table | `V<n>__create_table_<tablename>.sql` | `V0042__create_table_user.sql` |
  | Create function | `V<n>__create_function_<functionname>.sql` | `V0043__create_function_set_updated_at.sql` |
  | Create trigger | `V<n>__create_trigger_<triggername>.sql` | `V0044__create_trigger_user_set_updated_at.sql` |
  | Create type | `V<n>__create_type_<typename>.sql` | `V0045__create_type_role.sql` |
  | Create index | `V<n>__create_index_<indexname>.sql` | `V0046__create_index_idx_user_email.sql` |
  | Create view | `V<n>__create_view_<viewname>.sql` | `V0047__create_view_active_user.sql` |
  | Create materialized view | `V<n>__create_materialized_view_<name>.sql` | `V0048__create_materialized_view_user_stats.sql` |
  | Create sequence | `V<n>__create_sequence_<sequencename>.sql` | `V0049__create_sequence_invoice_number.sql` |
  | Drop *(any object type)* | `V<n>__drop_<object>_<name>.sql` | `V0060__drop_table_legacy_audit.sql`, `V0061__drop_index_idx_user_legacy.sql` |
  | Alter table | `V<n>__alter_table_<table>_<what_changed>.sql` | `V0070__alter_table_user_add_email.sql`, `V0071__alter_table_order_drop_legacy_id.sql` |
  | Rename *(any object type)* | `V<n>__rename_<object>_<old>_to_<new>.sql` | `V0080__rename_table_user_to_account.sql`, `V0081__rename_column_email_to_email_address_on_account.sql` |

### Naming

- **Table names are always singular.** Use `user`, `order`, `invoice_line_item` — never `users`, `orders`, `invoice_line_items`.
- **Do not use reserved keywords from the current SQL dialect as table or column names.** Pick a non-reserved alternative rather than relying on quoting — quoted-identifier ergonomics are bad and the burden leaks into every query for years. See the cross-dialect collision list below for the words that bite most often.
- **Constraint and index names use a type prefix:**
  - `idx_` — index
  - `pk_` — primary key
  - `fk_` — foreign key
  - `uq_` — unique constraint
  - `ck_` — check constraint
  - `df_` — default constraint *(SQL Server only — Postgres and MySQL don't name default constraints. Skip on those dialects.)*

### Reserved-keyword collisions across dialects

Words reserved in at least one major dialect — avoid as table or column names. Pick a non-reserved synonym instead.

| Word | Reserved in |
|---|---|
| `user` | Postgres, MySQL, SQL Server, Oracle |
| `order` | All |
| `group` | All |
| `select`, `from`, `where`, `join` | All |
| `desc` | All — and easy to grab as a short form of `description` |
| `type` | Postgres |
| `table`, `column` | All |
| `default`, `primary`, `references` | All |
| `lock`, `read`, `write` | MySQL, Oracle |

If a domain name collides (you really want a `user` table), use a non-reserved alternative: `account`, `app_user`, `member`. Don't quote.

### Column ordering

- **Audit columns come right after `id`, in this exact order:** `id`, `created_at`, `created_by`, `updated_at`, `updated_by`, then domain columns. Pair each timestamp with its actor: `created_at` is followed by `created_by`, and `updated_at` is followed by `updated_by`. Never interleave domain columns between audit columns.
- **"Default fields" terminology.** If the user mentions "the default fields" (or "default columns", "standard fields", "audit fields"), they mean exactly: `id`, `created_at`, `created_by`, `updated_at`, `updated_by` — in that order. Apply them as-is without asking.
- **Soft-delete columns, when present, come immediately *after* the audit columns and *before* domain columns.** Order: `id, created_at, created_by, updated_at, updated_by, deleted_at, deleted_by, <domain columns>`. Soft delete is opt-in — see the soft-delete rule below.

### Primary key (`id`) type

**ASK the user which `id` type to use** when designing a new table or adding `id` to an existing one. Don't pick silently.

- **Recommended option: UUID v7** — time-ordered, globally unique, no central counter. Safe in distributed inserts, sortable by creation order, doesn't leak insertion volume to clients.
  - **Postgres** — `uuid` column. UUID v7 generation: `pg_uuidv7` extension, or generate app-side.
  - **MySQL** — `binary(16)` storage with an app-side UUID v7 generator. Avoid `char(36)` for the index size cost.
  - **SQL Server** — `uniqueidentifier`; v7 generated app-side (`newid()` is v4).
  - **SQLite** — `text` storing the canonical 36-char form, or `blob` for the 16-byte form.
- Other options the skill should offer: `bigserial` / `IDENTITY` (auto-increment integer — compact, sequential, leaks insertion volume), `uuid v4` (random — globally unique but worse btree index locality than v7).

### Timestamp columns (`created_at`, `updated_at`)

- **Always store with timezone.** Naive timestamps drift the moment two services in different zones touch the same row. Per dialect:
  - **Postgres** — `timestamp with time zone` (a.k.a. `timestamptz`). Use the long form per the SQL style rule, never the shorthand.
  - **Oracle** — `timestamp with time zone`.
  - **SQL Server** — `datetimeoffset`.
  - **MySQL** — `timestamp` (always stored as UTC; no separate "with timezone" syntax). Configure session/server timezone explicitly. `datetime` is naive — don't use it for these columns.
  - **SQLite** — `text` storing ISO 8601 with offset, or `integer` Unix epoch. Document the convention in a column comment.
- **Database-managed by default.** Use `default current_timestamp` (or equivalent) for `created_at`. Use a trigger or the dialect's built-in mechanism (`on update current_timestamp` in MySQL) for `updated_at`. The DB owns these values.
- **ORM-managed timestamps are acceptable when the project has standardized on ORM-only writes.** If every write demonstrably goes through Hibernate / Prisma / etc., features like `@CreationTimestamp` / `@CreatedDate` / `@default(now())` are fine. If raw SQL writes happen anywhere (Flyway data migrations, scheduled jobs, direct `INSERT`s), the DB must own the timestamp — otherwise values drift between code paths and the bug is invisible until you `order by created_at`.

### Audit actor columns (`created_by`, `updated_by`)

**ASK the user how actors are referenced** — there's no single right answer:

- Foreign key to a `user` table (`bigint` or `uuid` references `user(id)`) — strongest integrity; system jobs need a sentinel `system` user row.
- Free-form string (username or display name) — simpler, no FK; weaker integrity (renames/deletes leave dangling values).
- Hybrid (`actor_type` + `actor_id`) — flexible; lets non-human actors (cron, integrations) be first-class.

The decision usually depends on the auth model and whether non-human actors need to write. Ask when designing the first table that uses these; the answer applies project-wide.

### Soft delete (`deleted_at`, `deleted_by`)

- **Default: no soft delete.** Hard delete unless there's a real reason (regulatory audit trail, "restore" feature with a real product use case).
- **ASK before adding.** The skill prompts: "should this entity have soft delete?" with the default NO and the reasons to consider it.
- **If added:** mirror the audit-column shape — `deleted_at` (`timestamp with time zone`), `deleted_by` (same type as `created_by`/`updated_by`). Both default `null`.
- **Every read must scope `where deleted_at is null`.** Forgotten filters cause silent data leaks. Encode the filter in a view, an ORM scope, or a row-level security policy — don't trust individual query authors to remember.
- **GDPR / right-to-erasure still requires actual deletion of the row.** Soft delete does not satisfy data-subject erasure requests; you'll need a separate hard-delete path for those.

### Optimistic locking (`version` column)

- **Default: no `version` column.** Add only on entities with real concurrent-edit potential — user-edited orders, profiles, configs that multiple admins touch. Append-only or single-writer entities don't need it.
- **ASK before adding.** The skill prompts on entities where contention is plausible.
- **When added:** an `integer` column, default `0`, incremented on every update. The application or ORM handles the bump (`@Version` in Hibernate / JPA, equivalent in Spring Data, etc.). Update statements check the previous version:

  ```sql
  update foo set ..., version = version + 1 where id = ? and version = ?
  ```

  Zero rows affected → optimistic-lock failure; the application retries or surfaces the conflict.

### Indices

- **Foreign keys always have an index on the *referencing* side.** Many DBs auto-index the referenced (target) primary key, but the FK column on the child table usually isn't indexed by default. Without it, every `delete` or `update` of the parent row scans the child table.
- **Composite-index column order matters.** Put the most-selective column (or the leftmost prefix of common query predicates) first. An index on `(tenant_id, created_at)` serves `where tenant_id = ?`, `where tenant_id = ? and created_at > ?`, and `where tenant_id = ? order by created_at` — but not `where created_at > ?` alone.
- **Partial indexes for sparse predicates** (Postgres / SQLite). If 99% of rows have `archived = false`, an index `where archived = false` is much smaller and faster than a full one. MySQL has no partial indexes; use a generated column + index as a workaround.
- **Don't add an index until a query needs it.** Indexes cost write throughput and storage. Speculative indexes ("we might query by this") rot.

### Enums

- **If a column has a fixed set of values, use a native enum type — not a check constraint.**
  - **Postgres** — `create type role as enum ('admin', 'member')`, then `role role`. Adding a value is a migration (`alter type role add value 'guest'`); that's a feature, not a bug.
  - **MySQL** — `enum('admin', 'member')` inline on the column.
  - **SQL Server, Oracle, SQLite** — no native enum type. Fall back to a `varchar` + `check` constraint, or a lookup table with a foreign key. Document the "enum" intent in the column comment.

### Data types

- **Pick the type that matches the expected size of the data.** Don't reach for unbounded types like `text` by default, but don't artificially cap fields that genuinely grow either.
  - **Short, bounded fields → `varchar(n)`** with a length that reflects the domain. A `name` column should be `varchar(100..255)` — pick a number that fits the domain, not the dialect's max.
  - **Free-form, potentially long fields → `text`.**
  - **Postgres note:** `text` and `varchar` perform identically and use the same storage; `varchar(n)` is purely a length check. Use `text` when there's no real upper bound, `varchar(n)` when the bound is meaningful.
  - **MySQL note:** `varchar(n)` and `text` differ in storage and indexing. Pick deliberately.
- **JSON content uses a JSON column type, not text.** When the column genuinely holds JSON:
  - **Postgres** — `jsonb` (always — `json` keeps text formatting and is slower to query).
  - **MySQL** — `json` (since 5.7).
  - **SQL Server** — `nvarchar(max)` with the `json` validity check; use the JSON functions for querying.
  - **SQLite** — `text` plus the `json1` extension functions.
  - A normalized table is preferable to a JSON blob unless the data is genuinely heterogeneous (third-party payloads, user-defined custom fields). JSON is the escape hatch for shapes you can't model up front.

### Normalization

- **Don't flatten related entities into a single table.** Even when the relationship is strictly 1:1 — e.g. a customer has exactly one address and an address belongs to exactly one customer — keep them as separate tables with a foreign key. Merging loses the conceptual boundary, makes future changes (multiple addresses, shared addresses, address history) painful, and bloats rows with rarely-used columns. Model each distinct entity as its own table.
- **Don't merge distinct data points into a single column.** Store composite data in separate, atomic columns so it can be queried, validated, and indexed independently. For example, an address like `8330 Pfäffikon ZH, Florastrasse 123` should not live in a single `address` field — split it into `postal_code`, `city`, `street`, `house_number`. Same for full names (`first_name` / `last_name`), coordinates (`latitude` / `longitude`), and similar composites.

### Online migration safety

When the migration runs against a live production database, schema changes can lock tables, break running queries, or block writes. The rules below cover the common gotchas; for anything riskier, ASK.

- **Adding a `not null` column to a large table — never in one step.** Three migrations: (1) add the column nullable with a default, (2) backfill in batches, (3) set `not null`. The naive `alter table ... add column foo not null default ...` rewrites every row in many DBs and locks the table for the duration.
- **Dropping a column — drop only after the application has stopped reading and writing it.** Two deploys: (1) ship code that doesn't reference the column, wait for it to be live, (2) run the `drop column` migration.
- **Renaming a column — never in one step.** Add the new column, dual-write from the application, backfill, switch reads to the new column, drop the old. Pure-DB renames break running services that reference the old name.
- **Adding an index on a large table — use the dialect's online-friendly form.**
  - **Postgres** — `create index concurrently`, no transaction.
  - **MySQL** — `algorithm=inplace, lock=none` where supported.
  - **SQL Server** — `with (online = on)` on Enterprise edition.
  - Plain `create index` takes a write lock and can be many minutes on a hot table.
- **Adding a foreign key on a large table (Postgres)** — `add constraint ... not valid` (skips the validation scan, locks briefly), then `alter table ... validate constraint ...` (no lock) afterwards. Splits the lock-heavy validation from the cutover.
- **If the production DB is small (`< 1M` rows) and a brief outage is acceptable**, the strict online-safety rules don't all apply — but ASK to confirm before bypassing them.
