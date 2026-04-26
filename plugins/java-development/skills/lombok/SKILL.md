---
name: lombok
description: Use whenever writing or reviewing Java code that contains boilerplate — getters/setters, constructors, equals/hashCode/toString, builders, logger fields, try-with-resources, null checks. Triggers on phrases like "use lombok", "lombokify", "remove this boilerplate", "add a builder", "add getters", and on any Java file containing manual accessor methods, manual builder classes, or `private static final Logger log = LoggerFactory.getLogger(...)`. Decision flow: detect Lombok in the project; if present, use it; if absent, ask the user before adding the dependency. Never silently introduce or remove Lombok.
---

# Lombok

[Project Lombok](https://projectlombok.org/) eliminates Java boilerplate via annotation-driven code generation. The point of this skill is twofold: (1) when Lombok is already in the project, use it consistently instead of hand-rolling boilerplate; (2) when it isn't, never sneak it in — the dependency choice is the user's, not yours.

## Decision flow

```
Is Lombok already a dependency in this project?
├── Yes → use Lombok-first patterns below. Refactor adjacent boilerplate when touching a file.
└── No  → ASK: "this project doesn't use Lombok. Want to add it and lombokify the existing boilerplate?"
         ├── Yes → add the dependency, then run the lombokify pass.
         └── No  → write boilerplate by hand. Don't import lombok.* anywhere.
```

The ask is mandatory. Don't introduce Lombok as a side-effect of "while I'm here" cleanup. Don't remove it without asking either.

### How to detect Lombok

In this priority order:

1. **Build file dependency** — search `pom.xml`, `build.gradle`, `build.gradle.kts` for `org.projectlombok` (group id) or `lombok` (artifact id). This is the authoritative signal.
2. **Existing imports** — `git grep "^import lombok\."` (or equivalent). If anything in the codebase imports a Lombok class, Lombok is in use.
3. **Generated `target/generated-sources/annotations` or IDE config** is weaker — only treat as a hint, confirm via 1 or 2.

If you find Lombok via the imports but *not* in the build file, something is broken — flag it to the user instead of guessing.

## When Lombok is present — use it

Use the annotation, not the boilerplate. Manual code generated for the same purpose adds noise, drifts from the rest of the file, and makes refactors (e.g. renaming a field) split-brain.

### Common replacements

| Hand-written boilerplate | Lombok equivalent | Notes |
|---|---|---|
| `getX()` / `setX()` pairs on plain fields | `@Getter` / `@Setter` (field- or class-level) | Use field-level when only some fields need it. |
| Manual `equals` + `hashCode` | `@EqualsAndHashCode` | For entities, use `onlyExplicitlyIncluded = true` and mark the id field with `@EqualsAndHashCode.Include`. |
| Manual `toString` | `@ToString` | Use `@ToString.Exclude` on lazy/circular fields (JPA relations, big payloads). |
| All-args / no-args / required-args constructors | `@AllArgsConstructor` / `@NoArgsConstructor` / `@RequiredArgsConstructor` | `@RequiredArgsConstructor` generates a ctor over `final` and `@NonNull` fields — the right default for constructor injection. |
| Hand-rolled builder class | `@Builder` (or `@SuperBuilder` for inheritance) | See pitfalls below before reaching for it on entities. |
| Immutable value class with all of the above | `@Value` | Makes the class `final`, all fields `private final`, generates getters + ctor + equals/hashCode/toString. No setters. |
| `private static final Logger log = LoggerFactory.getLogger(<Class>.class);` | `@Slf4j` (or matching annotation per logging API) | Covered in the `java-logging` skill. |
| `if (x == null) throw new NullPointerException(...)` at method entry | `@NonNull` on the parameter | Generates the same NPE; cleaner signature. |
| Manual try-with-resources around a single resource | `@Cleanup` on the local variable | Niche; usually plain try-with-resources is clearer. |

### `@Data` — use with caution

`@Data` bundles `@Getter`, `@Setter`, `@ToString`, `@EqualsAndHashCode`, and `@RequiredArgsConstructor`. Convenient for plain data carriers (DTOs, simple records-before-records). **Avoid `@Data` on:**

- **JPA entities.** The auto-generated `equals`/`hashCode`/`toString` walk every field, including lazy associations — this triggers `LazyInitializationException`s, infinite loops on bidirectional relations, and N+1 problems just from logging. Prefer `@Getter @Setter` plus manual `equals`/`hashCode` on the id (or `@EqualsAndHashCode(onlyExplicitlyIncluded = true)`).
- **Classes with mutable collections you don't want exposed.** `@Data` generates a setter that hands out the live reference.
- **Anything you'd otherwise make immutable.** Use `@Value` instead.

When in doubt on a domain class, prefer the explicit set: `@Getter`, `@Setter`, `@EqualsAndHashCode(of = "id")`, `@ToString(of = {"id", "name"})`.

### `@Builder` pitfalls

- On a class extending another, plain `@Builder` won't include the parent's fields. Use `@SuperBuilder` on both parent and child.
- For JPA entities with `@OneToMany`, the builder's collection field is `null` by default — initialize via `@Builder.Default` (e.g. `@Builder.Default private List<Item> items = new ArrayList<>();`) or use `@Singular` for a builder-side `addItem` API.
- `@Builder` on a constructor is often clearer than `@Builder` on a class — it makes the build target explicit.

### `@SneakyThrows` — almost never

`@SneakyThrows` swallows checked exceptions into the runtime layer at compile time. It can be useful for genuinely unrecoverable cases in tests or scripts. In production code it hides real failure modes from callers and the type system. Default: don't use it. If a caller can't handle `IOException`, wrap it explicitly in your own runtime exception.

### Constructor injection (Spring / similar)

```java
@RequiredArgsConstructor
@Service
public class OrderService {
    private final OrderRepository orderRepository;
    private final PaymentClient paymentClient;
    // Lombok generates the constructor; Spring autowires it.
}
```

This is the modern preferred pattern: no `@Autowired` field injection, no manual constructor, all collaborators `final`.

## When Lombok is absent — ask first

If the project doesn't use Lombok and a refactor would benefit from it:

1. Stop before adding any `import lombok.*` or modifying the build file.
2. Tell the user, concretely: "this project doesn't use Lombok. Adopting it would let me replace [N] manual getter/setter pairs, [M] hand-written builders, and the manual logger fields. Want me to add the dependency and lombokify? Or keep writing it by hand?"
3. **If yes** — add the dependency (see "Adding Lombok" below), then run the lombokify pass.
4. **If no** — write boilerplate by hand for this and future work. Do not bring up adoption again unsolicited.

Don't ask repeatedly. Once is enough; the answer applies to the whole project until the user says otherwise.

## Adding Lombok (only after explicit yes)

### Maven

```xml
<dependency>
    <groupId>org.projectlombok</groupId>
    <artifactId>lombok</artifactId>
    <scope>provided</scope>
</dependency>
```

Pin a recent version (check [latest](https://projectlombok.org/changelog) — current at time of writing is in the 1.18.x line). For Maven projects also configure the compiler plugin's `annotationProcessorPaths` if it doesn't pick up Lombok automatically.

### Gradle (Kotlin DSL)

```kotlin
compileOnly("org.projectlombok:lombok:1.18.x")
annotationProcessor("org.projectlombok:lombok:1.18.x")

testCompileOnly("org.projectlombok:lombok:1.18.x")
testAnnotationProcessor("org.projectlombok:lombok:1.18.x")
```

The `compileOnly` / `annotationProcessor` pair is required — `implementation` alone won't trigger the annotation processor.

### IDE setup

Mention to the user that IDEs need the Lombok plugin installed (IntelliJ: bundled since 2020.3; Eclipse: run `lombok.jar`). Without it, the IDE flags Lombok-generated code as missing.

## Lombokify pass

After adoption (or any time the user says "lombokify"), do a sweep across the relevant scope:

1. **Inventory the boilerplate.** For each file:
   - Manual `getX()` / `setX()` pairs whose body is just `return x;` / `this.x = ...;`.
   - Manual `equals` / `hashCode` / `toString` that don't have custom logic.
   - Manual constructors that just assign all parameters to fields.
   - Manual builder classes (often a static inner class).
   - `private static final Logger log = LoggerFactory.getLogger(...)`.
   - Manual null checks at method entry: `if (x == null) throw new NullPointerException(...)`.
2. **Pick the right annotation per case** using the table above. Don't reach for `@Data` reflexively — see its caveats.
3. **Verify behavior is preserved.** Lombok's generated code matches naming conventions, but custom logic does not. If a manual `equals` does anything non-default, *don't* replace it; leave a comment-free explicit method.
4. **Run the build and the tests.** Compilation is a real check (annotation processor failures are loud); tests catch behavioral drift in `equals`/`hashCode`/`toString`.
5. **Don't mix styles within a single file.** Either all accessors in a class are Lombok, or all are manual. Mixed files are confusing.

## Things to avoid

- **Don't use `@Data` on JPA entities** (see above).
- **Don't use `@SneakyThrows` to dodge checked exceptions** in production code.
- **Don't `delombok` and then re-lombokify** as a refactor strategy — diff churn for no value.
- **Don't add Lombok to a single file as a one-off.** It's a project-wide convention; either everywhere or nowhere.
- **Don't combine `@Data` with `@Builder` on classes with default field values** without `@Builder.Default` — defaults silently disappear in builder-constructed instances.

## Cross-references

- Logger fields: see the `java-logging` skill — when Lombok is present, `@Slf4j` is the default rather than a hand-declared `Logger` field.
