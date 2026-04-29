---
name: logging
description: "Use whenever writing, reviewing, or modifying code that emits logs in any language — adding log statements, replacing print/println/console.log, debugging that needs instrumentation, configuring a logging library, reviewing logs in PRs, designing a correlation-ID strategy, deciding what to put in audit logs vs. operational logs, sampling high-volume logs. Triggers on phrases like 'add logging', 'log this', 'instrument', 'why isn't this logged', 'trace id', 'correlation id', 'audit log', 'structured logging', and on any source file containing logger / log. / logging. / console.log / println / print / fmt.Println / slog. / pino / winston / structlog. Language-agnostic principles (parameterized messages, sensible levels, no sensitive data, structured output in production, correlation IDs, audit vs. operational, expensive-computation guards, sampling) with per-language notes for Java/Kotlin, Python, JavaScript/TypeScript, and Go. For Java specifics (SLF4J wiring, `@Slf4j`/Lombok, MDC syntax, no-stack-at-ERROR), defer to the `java-logging` skill."
---

# Logging

## Overview

Personal conventions for emitting logs. The 10 rules below are language-agnostic; the per-language notes show concrete idioms for Java/Kotlin, Python, JavaScript/TypeScript, and Go.

**Boundary with the `java-logging` skill:** this skill carries the *principles* (when to log, what level, what to include, how to structure output). The `java-logging` skill carries Java-specific *mechanics* (SLF4J wiring, `@Slf4j` with Lombok, MDC syntax, the no-stack-at-ERROR pattern with the exact split). On a Java task both apply — defer to `java-logging` for syntax, this skill for the principle behind the syntax. They're cross-referenced both ways.

## Rules

### 1. Use a real logger, not stdout

`System.out.println` (Java), `print` (Python), `console.log` (JS), `fmt.Println` (Go) are not logging — they're debugging exhaust. Production code uses the language's logging library so log output respects levels, can be redirected, and can be aggregated.

Exceptions: one-off scripts and CLI tools where stdout *is* the contract with the user. Even there, errors and diagnostics go to stderr, not stdout.

### 2. Parameterized messages, not string concatenation

```
✓ log.info("user {} logged in from {}", username, ip)        // Java SLF4J
✓ logger.info("user %s logged in from %s", username, ip)     // Python lazy
✓ log.info({ username, ip }, "user logged in")               // pino
✓ slog.Info("user logged in", "username", username, "ip", ip) // Go slog

✗ log.info("user " + username + " logged in from " + ip)
✗ logger.info(f"user {username} logged in from {ip}")        // Python f-string is eager
✗ log.info(`user ${username} logged in from ${ip}`)          // JS template literal is eager
```

Reasons:

- **Lazy evaluation** — when the level is disabled, the formatting cost is skipped. F-strings and template literals format at the call site whether the log fires or not.
- **Structured arguments** — modern aggregators index logs by their fields. A parameterized message keeps the message template stable and the values searchable.
- **Sensitive-data containment** — passing values as arguments lets a custom serializer redact them; pre-formatted strings can't be redacted retroactively.

### 3. Sensible log levels

| Level | Use for | Volume |
|---|---|---|
| **TRACE** | Per-loop-iteration / per-function-entry detail used only when chasing a specific bug. Off in prod. | Very high |
| **DEBUG** | Diagnostic detail: variable values, branch decisions, retries. On in dev / staging; off in prod by default. | High |
| **INFO** | Significant business events: request received, user logged in, job started/finished. On in prod. | Moderate |
| **WARN** | Something unexpected but recoverable: retry triggered, deprecated API called, fallback used. On in prod. | Low |
| **ERROR** | Something failed and the operation could not complete: unhandled exception, dependency unavailable, data corruption detected. On always; pages oncall in many setups. | Rare |

Don't use ERROR for "the user did something wrong" (validation failures, 4xx responses) — those are INFO or WARN. ERROR is for "the system did something wrong."

### 4. Guard computations done only for the log line

If an argument is computed *only* to be logged, the computation runs even when the level is disabled — unless you guard it.

```
✓ if (log.isDebugEnabled()) log.debug("classpath: {}", expensiveDump());
✓ if logger.isEnabledFor(logging.DEBUG): logger.debug("classpath: %s", expensive_dump())
✓ if log.level === 'debug' { log.debug({ classpath: expensiveDump() }, '...') }

✗ log.debug("classpath: {}", expensiveDump())   // expensiveDump runs even at INFO
```

The strict version of this rule: *whenever* an argument exists only for the log line, guard it. Don't make exceptions for "cheap" computations — `calculateEbitMargin()` looks cheap until next quarter when it joins three tables.

### 5. Never log sensitive data

Categorical no:

- Passwords, password hashes, password reset tokens.
- Authentication tokens, session cookies, API keys, signed JWTs.
- Payment instrument data (PAN, CVV, expiry, IBAN).
- Personal identifying information beyond what your privacy policy explicitly permits.
- Full request/response bodies that may contain any of the above.

Treat the runner's environment and the log aggregator as semi-trusted. A log line that hits disk anywhere is forever, regardless of subsequent rotation or deletion.

### 6. Stack traces at ERROR — split level

When an exception occurs:

- **ERROR** carries the human-readable summary: what failed, what context (user, request id, key inputs).
- **DEBUG** (immediately after) carries the full stack trace.

Reason: ERROR is the level oncall reads at 3am. A stack trace is essential for the engineer fixing the bug at 10am — but at 3am it's noise that hides the *what* in 60 lines of *where*.

For Java specifics (`log.error("...: {}", ex.getMessage())` + `log.debug(ex.getMessage(), ex)`), see the `java-logging` skill. The principle generalizes — the syntax doesn't.

### 7. Structured output in production

Production logs go to an aggregator (ELK, Loki, Datadog, CloudWatch, Splunk). Plain-text "user X logged in from Y" is unsearchable except by full-text grep. Structured logs (JSON or key-value) are queryable: `level=info event=user_login user_id=42`.

- **Local dev**: human-readable formatting is fine and helps — pretty-printed text, colors, no JSON noise.
- **Production / staging**: JSON or your aggregator's preferred format. The library handles the switch via configuration; the call sites stay the same.

The mechanism that makes this work is rule 2: pass values as arguments, not concatenated into the message. Structured output is a serialization concern; the *call site* stays the same regardless of output format.

### 8. Correlation / trace IDs

Every log line emitted while handling a request shares a trace ID with every other log line in that flow. Without it, debugging a distributed system is grep-and-pray.

- **Origin** — the trace ID is generated at the system edge (load balancer, API gateway, mobile client) and propagated via header (`X-Request-ID`, `traceparent` for W3C Trace Context, OpenTelemetry baggage).
- **Storage** — the request handler puts the trace ID in the language's per-request context: MDC (Java), `contextvars` (Python), `AsyncLocalStorage` (Node), `context.Context` (Go). Logging libraries read from there and emit it on every line automatically.
- **Cross-service propagation** — outbound HTTP / message-queue clients copy the current trace ID into the next request's headers. Most modern observability libraries (OpenTelemetry instrumentation) do this for you.

If you're adding a feature and there's no existing trace-ID convention in the project, ASK rather than picking one — the choice has system-wide implications.

### 9. Audit vs. operational logs are different systems

Audit logs record security-relevant or compliance-relevant events: login attempts, permission changes, financial transactions, data exports. They're not the same as operational logs and shouldn't share the same sink.

| Operational logs | Audit logs |
|---|---|
| Aggregator (ELK, Loki, Datadog) | Append-only audit store (separate DB, S3 with object lock, dedicated audit service) |
| Days-to-weeks retention | Years (often regulatory minimum) |
| Lossy on rotation / sampling | Must not lose events |
| Read by engineers | Read by auditors, security, regulators |
| Mutable indices, schema can evolve | Immutable, schema is part of the contract |

Don't write `log.info("audit: user X exported customer data")` and call it audit logging. That's an operational log line — the next log rotation can lose it. Audit needs a separate sink with a delivery guarantee.

If the project doesn't have an audit log system and one is needed, raise it explicitly — building one is a real architectural decision, not a logging tweak.

### 10. Sampling for high-volume logs

When a log line fires hundreds or thousands of times per second, it can drown the aggregator and hide signal in noise. Sample:

- **Rate-limit at the call site** — emit only every Nth occurrence, or first-N-per-window. Best for hot paths where the *fact* of the event matters more than every instance.
- **Configure aggregator-side sampling** — many aggregators (Datadog, Honeycomb) support sampling rules so the call site stays unchanged. Better for cases where you want full fidelity for errors and sampled fidelity for info.
- **Always log at full fidelity for ERRORs** — don't sample errors. Their volume is supposed to be low; if it isn't, that's the signal you need.

This rule rarely matters at small scale; codify it before reach scale rather than after the aggregator bill arrives.

## Per-language notes

### Java / Kotlin

See the `java-logging` skill for the Java-specific mechanics — SLF4J as the API, Logback / Log4j2 as the implementation, `@Slf4j` if Lombok is on the classpath, MDC for correlation IDs, the exact ERROR-message + DEBUG-stack split syntax, the per-tool guard idiom, audit logger as a separate logger name. The `java-logging` skill is where the syntax lives; this skill is where the *why* lives.

### Python

- **stdlib `logging`** for most projects. Configure via `logging.dictConfig` or `basicConfig`; don't use the root logger directly in libraries.
- **`structlog`** for native structured output. Drops in alongside stdlib `logging` and produces structured records (JSON in prod, pretty-printed in dev) without changing call sites.
- **Lazy formatting** — `logger.info("user %s logged in", username)`, not `logger.info(f"user {username} logged in")`. F-strings format eagerly even when the level is disabled.
- **Correlation IDs** — `contextvars.ContextVar` for async-safe per-request state, then a logging filter that copies it onto each record. Frameworks (FastAPI, Django, Starlette) usually have a middleware for this.
- **Don't propagate to the root logger from library code** — `logger.propagate = False` on library loggers, or namespace your logger (`logging.getLogger("mylib")`) so consumers can configure it independently.

### JavaScript / TypeScript

- **`console.log` is fine for CLI tools and one-off scripts.** Not for services. The fields aren't structured, levels are missing, and stdout/stderr split is inconsistent across runtimes.
- **`pino`** is the modern default for Node services — fast, structured by default (JSON), level-aware, ergonomic. `pino-pretty` for local dev.
- **`winston`** if you need transports the box doesn't have (file rotation, syslog, custom destinations) and don't want to wire them yourself.
- **Pass objects, not pre-formatted strings:** `log.info({ userId, ip }, 'user logged in')`. The first argument is the structured payload, the second is the message template — pino's argument order is the opposite of most other libraries; check before guessing.
- **Correlation IDs** — `AsyncLocalStorage` (Node 16+) for per-request state. Express / Fastify / NestJS each have request-scoped DI mechanisms that integrate with it.
- **Browser code** — `console.*` is the only practical option, but in production add a remote-log shipping layer (Sentry, LogRocket) for errors. Don't ship every `console.debug` to the network.

### Go

- **`log/slog`** (Go 1.21+) is the right default for new code. Structured by default, level-aware, built into the standard library.
  ```go
  slog.Info("user logged in", "user_id", id, "ip", ip)
  ```
- **The plain `log` package is unstructured** — fine for tiny CLI tools, not for services. Don't use it in new server code.
- **`zap` and `zerolog`** are mature third-party alternatives, both faster than slog at the high end. Fine to use; use them consistently across the project.
- **Correlation IDs** — `context.Context` is the canonical place. Use a logging handler that reads the trace ID off the context (slog has `WithGroup` / `Logger.With` for adding base fields per logger; per-request fields go via `Logger.WithContext` patterns or a custom handler).
- **Don't return errors *and* log them** — pick one. Logging an error and then returning it produces duplicate log lines as it bubbles up the call stack. The convention: errors are logged where they're handled, not where they're discovered.

### Other languages (Rust, .NET, Elixir, Ruby, …)

ASK before guessing the equivalent of any rule above. The principles (structured output, correlation IDs, levels, lazy evaluation, sensitive-data discipline) are universal; the libraries vary too much for cross-language extrapolation to be safe. Get the project's logging library from the dependency manifest (`Cargo.toml`, `*.csproj`, `mix.exs`, `Gemfile`) and confirm with the user before writing log statements that don't match the project's existing style.
