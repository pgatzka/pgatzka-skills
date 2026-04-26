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

### 3. Guard expensive computation with `isXxxEnabled()` — but only when the computation is actually expensive

Parameterized logging already defers `toString()` on the arguments themselves, so you don't need a guard for cheap arguments. You **do** need a guard when constructing the argument requires non-trivial work (a DB call, a heavy aggregation, JSON serialization of a big object, a method call that hits the network).

```java
// fine — calculateEbitMargin() is cheap; just log it
double ebitMargin = calculateEbitMargin();
log.debug("EBIT margin: {}", ebitMargin);
```

```java
// guard — calculateEbitMargin() is expensive (e.g. aggregates over many rows)
// without the guard, the calculation runs in production even when DEBUG is off
if (log.isDebugEnabled()) {
    double ebitMargin = calculateEbitMargin();
    log.debug("EBIT margin: {}", ebitMargin);
}
```

Rule of thumb: if the value being logged is a field access, a local variable you already have, or a trivially-computed expression, no guard. If logging would force you to compute something *only for the log line*, guard it — or pass a `Supplier` if using Log4j2's fluent API. Don't sprinkle `isDebugEnabled()` everywhere "just in case" — it's noise.

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
log.debug("Pricing {} via {} strategy (sku={}, region={})",
        sku, strategy.name(), sku, region);

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
