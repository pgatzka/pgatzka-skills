---
name: java-logging
description: Use whenever writing, reviewing, or modifying Java code that emits logs - including adding new log statements, debugging issues that require instrumentation, replacing System.out.println calls, configuring SLF4J/Logback/Log4j2, or reviewing logs in PRs. Triggers on phrases like "add logging", "log this", "debug output", "instrument", "trace", "audit log", and on any Java file containing Logger, LoggerFactory, log., logger., System.out, System.err, or printStackTrace. Enforces structured parameterized logging, sensible log levels, guarded expensive computation, and refusal to log sensitive data.
---

# Java Logging

Logs are a product surface. They get scraped, indexed, alerted on, and read at 3am during incidents. Treat every log line as something a future engineer (or an SRE who's never seen this code) will rely on. The rules below exist to make that future moment less painful — not as bureaucracy.

## Core rules

### 1. Use a structured logging framework, never `System.out` / `System.err`

Default to **SLF4J** as the API (`org.slf4j.Logger` + `org.slf4j.LoggerFactory`). The backing implementation (Logback, Log4j2, java.util.logging via slf4j-jdk14) is a project decision — don't change it without reason.

```java
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class OrderService {
    private static final Logger log = LoggerFactory.getLogger(OrderService.class);
    // ...
}
```

`System.out.println`, `System.err.println`, and `Throwable.printStackTrace()` are **forbidden in production code**. They bypass the logging pipeline (no levels, no MDC, no appenders, no log aggregation, no structured output), can block on stdout, and leak into container logs unstructured.

**If the project has no logging framework configured at all**, stop and ask the user before falling back to `System.out`. Adding SLF4J is usually a one-line dependency change and almost always the right move. Only use `System.out` after the user explicitly says so (e.g., a CLI tool that prints to stdout as its actual output, throwaway scripts, or `main` methods in examples).

The logger field convention: `private static final Logger log = LoggerFactory.getLogger(<EnclosingClass>.class);`. Static + final + named `log` (or `LOG`) — keep it consistent with the surrounding file.

**If Lombok is on the classpath, use the Lombok logger annotation instead of declaring the field by hand.** Lombok generates the same `private static final Logger log = ...` for you, removing the boilerplate (and the chance of pasting the wrong class into `getLogger(...)` after a rename).

```java
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class OrderService {
    // log.info(...) just works — Lombok generates the field
}
```

Pick the annotation that matches the project's logging API:

| Annotation | Generates a logger for |
|---|---|
| `@Slf4j` (default — match this skill's SLF4J default) | `org.slf4j.Logger` |
| `@Log4j2` | `org.apache.logging.log4j.Logger` |
| `@CommonsLog` | Apache Commons Logging |
| `@JBossLog` | JBoss Logging |
| `@Flogger` | Google Flogger |
| `@Log` | `java.util.logging.Logger` (avoid unless the project has chosen JUL) |

How to tell Lombok is present: a `lombok` dependency in `pom.xml` / `build.gradle` (group `org.projectlombok`), or existing usage of any Lombok annotation (`@Data`, `@Builder`, `@RequiredArgsConstructor`, etc.) in the codebase. If unsure, grep for `import lombok.` — if you find any, Lombok is in use and the annotation is the right tool.

Don't mix styles within one project — if the surrounding files already use `@Slf4j`, follow that. If they declare the field manually and Lombok is *not* a dependency, declare the field manually too. Introducing Lombok purely to use `@Slf4j` is a project-level decision; ask before adding the dependency.

### 2. Parameterized messages, never string concatenation or `String.format`

```java
// good — placeholders are resolved lazily by the framework
log.info("Order {} for customer {} settled in {} ms", orderId, customerId, durationMs);

// bad — concatenation runs even when INFO is disabled
log.info("Order " + orderId + " for customer " + customerId + " settled in " + durationMs + " ms");

// bad — String.format runs eagerly too, and is slower
log.info(String.format("Order %s for customer %s settled in %d ms", orderId, customerId, durationMs));
```

For exceptions, **never attach the full stack trace at `ERROR`** (project preference). Log the message at `ERROR` so the production log stays scannable, and put the stack trace at `DEBUG` for when someone needs to investigate.

```java
// good — ERROR carries the human-readable message; DEBUG carries the stack
log.error("Exception occurred while persisting entity {}: {}", entityId, ex.getMessage());
log.debug(ex.getMessage(), ex);

// bad — stack trace dumped at ERROR floods the prod log
log.error("Exception occurred while persisting entity: {}", ex.getMessage(), ex);

// bad — Throwable in a {} placeholder gives you toString() with no stack at any level
log.error("Failed to settle order {} {}", orderId, ex);
```

The `log.debug(message, throwable)` form (Throwable as the last positional argument, no `{}` for it) is how SLF4J renders the stack trace. Pair the ERROR + DEBUG lines so they show up adjacent in the file and can be correlated by timestamp / MDC.

### 3. Guard with `isXxxEnabled()` whenever the argument is computed only for the log line

Parameterized logging defers `toString()` on the arguments themselves, but it does **not** defer the work of producing those arguments. Calls and calculations that exist solely to feed the log line still run at production runtime even when the level is disabled.

The rule: **if a value is computed only because a log call wants it, wrap the log call in `if (log.isXxxEnabled())`.** Don't try to judge whether the computation is "expensive enough" — `calculateEbitMargin()` looks fine today and quietly becomes a join across three tables next quarter, by which time nobody is touching the log call to add a guard.

Field reads and locals you already have for non-logging reasons need no guard — the work was done anyway.

```java
// no guard — userId is a method parameter, already in scope
log.debug("Resolved user {}", userId);

// no guard — result was computed because the caller needs it
Result result = service.execute(...);
log.debug("Got result {}", result);

// guard — calculateEbitMargin() exists only for this log line
if (log.isDebugEnabled()) {
    double ebitMargin = calculateEbitMargin();
    log.debug("EBIT margin: {}", ebitMargin);
}

// guard — serializing the request is purely for diagnosis
if (log.isTraceEnabled()) {
    log.trace("Request payload: {}", jsonMapper.writeValueAsString(request));
}
```

Log4j2's fluent `Supplier` API is an equivalent escape — the supplier only runs when the level is enabled:

```java
log.debug("EBIT margin: {}", () -> calculateEbitMargin());
```

The rule is "*computed only for the log line*", not "anywhere a log line touches a method". If you're already producing the value for other reasons, no guard. If you're producing it solely because the log call wants it, guard.

### 4. Use log levels deliberately

| Level | Use for | Examples |
|---|---|---|
| `ERROR` | A failure that requires human attention. The operation could not be completed and there's no automatic recovery. | Unhandled exception bubbling out of a request handler; failed write to a critical store after retries; data corruption detected. |
| `WARN` | Something unexpected but recoverable, or a degraded state. Worth investigating but not paging. | Retry succeeded after transient failure; deprecated config key used; fallback path taken; rate limit hit. |
| `INFO` | Significant business or lifecycle events. Sparse, durable, useful in production. | Service started/stopped; user logged in; order placed; scheduled job completed with summary. |
| `DEBUG` | Internal state useful for diagnosis. Off by default in production, enabled when investigating. | Query parameters and result counts; branch taken in a decision; cache hit/miss. |
| `TRACE` | Very fine-grained. Method entry/exit, loop iterations, raw payloads. Almost never on in production. | Per-row processing detail during a batch job. |

Common mistakes to avoid:
- `INFO` for things that fire on every request — that's `DEBUG`.
- `ERROR` for expected validation failures (a user typed a bad email is not an error, it's a 400). `WARN` or `DEBUG`, or no log at all.
- `WARN` for "I want to make sure someone notices this" — if it's actionable, make it `ERROR`; if it isn't, make it `INFO` or `DEBUG`. WARN-fatigue is real.

### 5. Never log sensitive data

Treat logs as if they will be shipped to a third-party log aggregator and read by anyone with prod access — because they usually are.

**Never log:**
- Passwords, password hashes, password reset tokens
- API keys, bearer tokens, JWTs, session cookies, OAuth refresh tokens
- Full credit card numbers, CVVs, full bank account numbers
- Personal identifiers in plain form when not needed: full SSN, government IDs, full date of birth
- Health data (PHI), and anything subject to GDPR/CCPA without a clear reason
- Full request/response bodies of authenticated endpoints (they often contain the above)
- Private keys, certificates, encryption keys
- Raw `Authorization` / `Cookie` / `Set-Cookie` headers

**Prefer when you must reference these:**
- Stable opaque IDs (`userId=12345`) over emails or names
- Last-4 of a card number with the rest masked: `****-****-****-1234`
- Hashes or fingerprints of tokens, not the tokens themselves
- Counts and shapes ("body had 17 fields, 4.2KB") instead of the body

If you're about to log an object whose contents you didn't author (a request DTO, an external API response, a `Map<String, Object>`), assume it contains secrets unless proven otherwise. Don't `log.debug("payload: {}", request)` blind.

If you spot existing code logging sensitive data, flag it — it's a security issue, not a style nit.

### 6. Log content that's actually useful

The bar for adding a log line: **will this help someone diagnose a problem or understand system behavior, without them having to read the source?** If not, don't add it.

**Don't log:**

```java
// noise — the method name and arguments are already in the stack trace if it fails
public void processOrder(Order order) {
    log.info("Entering processOrder with order: {}", order);
    // ...
    log.info("Exiting processOrder");
}

// noise — these tell you nothing on their own
log.debug("Starting...");
log.debug("Done");
log.info("In the if branch");
log.info("Got here");

// noise — logging that something obvious happened
log.info("Set userId to {}", userId);   // it's right there in the assignment
log.info("Returning result");
```

Method-entry/exit tracing is what `TRACE` and AOP / OpenTelemetry are for. Don't hand-roll it at `INFO` or `DEBUG`.

**Do log:**

```java
// decisions and outcomes, with the IDs needed to correlate
log.info("Settled order {} for customer {} in {} ms (items={}, total={})",
        orderId, customerId, durationMs, itemCount, total);

// branch taken when it isn't obvious from inputs
log.debug("Pricing {} via {} strategy in region {}",
        sku, strategy.name(), region);

// the *unhappy* path, with context
log.warn("Retrying call to {} after transient failure (attempt {} of {})",
        endpoint, attempt, maxAttempts);

log.error("Could not settle order {} after {} attempts; giving up: {}",
        orderId, maxAttempts, lastException.getMessage());
log.debug(lastException.getMessage(), lastException);
```

The pattern: **what happened + the IDs you'd grep for + the numbers a human cares about + the exception (if any)**. Stable identifiers (orderId, customerId, requestId) matter more than narrative — they're how anyone correlates across services.

### 7. Use MDC for cross-cutting context

For things that apply to *every* log line within a unit of work (request ID, tenant ID, user ID), use `MDC` (Mapped Diagnostic Context) rather than threading them into every message:

```java
import org.slf4j.MDC;

try (MDC.MDCCloseable ignored = MDC.putCloseable("requestId", requestId)) {
    // every log call inside this block automatically includes requestId
    handle(request);
}
```

This keeps individual log calls focused on what *that line* is saying, while the context propagates. Configure your appender's pattern to render MDC keys (e.g. `%X{requestId}`).

### 8. Use structured arguments for fields you'll query on

A plain log line like `log.info("Settled order {}", orderId)` produces a text message — fine for humans, but log aggregators that index by field can't extract `orderId` cleanly without parsing the message. When a value needs to be *queryable* (filter on it, group by it, alert on it), put it in a structured field, not just in the message text.

The mechanism depends on the stack:

**Logback + `logstash-logback-encoder`** (very common):

```java
import static net.logstash.logback.argument.StructuredArguments.kv;

log.info("Settled order {}", kv("orderId", orderId));
// Plain-text appender renders: "Settled order orderId=12345"
// JSON appender renders:       {"message":"Settled order 12345","orderId":12345,...}
```

`kv("name", value)` adds the field to the JSON output and substitutes `name=value` into the text rendering. `value("name", value)` substitutes only the value (no `name=`) into the text but still adds the JSON field.

**Log4j2** uses `ObjectMessage` or the fluent API:

```java
log.atInfo().log("Settled order {}", orderId);

// arbitrary kv pairs:
log.info(new ObjectMessage(Map.of("event", "order_settled", "orderId", orderId)));
```

**Default policy:**
- **MDC** (rule 7) for context that applies to *every* line in a unit of work — `requestId`, `tenantId`, `userId`.
- **Structured arguments** for per-event facts that the message itself is about — `orderId` on a "settled order" line.
- **Plain `{}` placeholders** when the value is purely human-readable narrative and won't be queried.

If the project uses only a plain-text appender, structured arguments degrade gracefully to `name=value` in the message — there's no downside to using them now and turning on JSON output later.

### 9. Audit logs are a different system from operational logs

When the requirement is "we must be able to prove later that X happened" — regulatory, security, financial reconciliation — the log is an *audit log*, not a diagnostic log. The rules above optimize for noise reduction and developer convenience; audit logging optimizes for completeness and durability, which means almost-opposite tradeoffs:

- **Guaranteed delivery.** No async/buffered appenders that can drop under load. A synchronous sink (DB, dedicated audit service, Kafka with `acks=all`).
- **Separate destination.** Don't mix audit events with operational logs. Operational logs are usually rotated or sampled on retention policies an auditor won't accept; mixing buries audit events in the volume.
- **Structured by design.** Every audit event has a fixed schema — `actor`, `action`, `target`, `timestamp`, `outcome`, `correlationId`. Free-text messages are useless for auditing. Use structured arguments (rule 8) or, better, a typed audit API.
- **Log success, not just failure.** Operational logs can skip the happy path; audit logs cannot. The point is the trail.
- **Sensitive data still doesn't go in.** Rule 5 still applies. Auditors do not need plaintext PANs or session tokens.
- **Don't sample or throttle.** Backpressure on operational logs is fine; audit events queue and persist, never drop.

Practical pattern: define an `AuditLogger` interface (or use an existing one in the project) that writes to the audit sink directly. Don't route audit events through SLF4J — the two concerns drift apart and end up in the wrong place.

If a project has retention or compliance requirements you didn't already know about (PCI, GDPR, SOX, HIPAA), ask before changing how audit-relevant events are captured — the rules above are defaults, but the specifics are usually dictated by the regulator.

## When reviewing existing code

Apply these rules in this order — fix the worst first:

1. `System.out.println` / `printStackTrace()` in production code → replace with SLF4J at appropriate level. If no framework exists, **ask** before doing anything else.
2. Sensitive data in logs → fix immediately, this is a security bug.
3. String concatenation / `String.format` inside log calls → switch to `{}` placeholders.
4. Stack traces logged at `ERROR` (`log.error("...", ex)` with Throwable attached) → split into `log.error("...: {}", ex.getMessage())` plus a follow-up `log.debug(ex.getMessage(), ex)` for the stack.
5. Wrong levels (validation `ERROR`, per-request `INFO`) → re-level.
6. Method-entry noise / "got here" logs → delete.
7. Unguarded expensive computations only used for logging → wrap in `isXxxEnabled()` or rework.

## When adding new code

Before writing a `log.x(...)` call, ask:
- Is the framework already in use here? (Check for an existing `Logger` field; match the project's convention.)
- What level is this? (Pick from the table above; default toward `DEBUG` if unsure rather than `INFO`.)
- What IDs go in the message so this is greppable later?
- Is anything I'm about to log sensitive?
- Does the argument require expensive computation? If yes, guard.

If the answer to "would I want this line during an incident" is no, don't write it.
