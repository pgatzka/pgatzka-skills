---
name: spring-boot
description: "Use whenever writing or reviewing Spring Boot or Spring Framework configuration code — @Configuration classes, @Bean methods, @SpringBootApplication, application context wiring, application configuration files, build-file dependency declarations for Spring starters, Jackson ObjectMapper imports in Spring projects. Triggers on phrases like 'add a Bean', 'wire up this dependency', 'create a Configuration class', 'register this with Spring', 'application.properties', 'application.yaml', 'spring profile', 'spring-boot-starter-web', 'ObjectMapper', and on any Java file containing @Bean, @Configuration, @SpringBootApplication, or other Spring stereotype annotations, plus any edits to application.properties / application.yaml / application-*.yaml files, plus any pom.xml or build.gradle edits referencing spring-boot-starter-* dependencies, plus any Java import of com.fasterxml.jackson.* or tools.jackson.* in a Spring context. Five rules: @Bean methods are package-private (CGLIB proxy semantics), @Configuration classes are not final (same CGLIB constraint), application config uses YAML rather than .properties, on Spring Boot 4+ the MVC starter is spring-boot-starter-webmvc rather than the deprecated spring-boot-starter-web, and on Spring Boot 4+ Jackson imports come from tools.jackson.* (Jackson 3) rather than com.fasterxml.jackson.* (with com.fasterxml.jackson.annotation.* as the documented exception). The skill will grow as more conventions are added."
---

# Spring Boot

Personal conventions for Spring Boot / Spring Framework. Five rules so far, covering application context wiring (rules 1–2), application configuration (rule 3), starter dependencies (rule 4), and Jackson imports (rule 5). The skill will grow as more conventions are added.

## Rules

### 1. `@Bean` methods are package-private, not public

Inside an `@Configuration` class, every `@Bean` method should be **package-private** — drop the `public` modifier. The surrounding `@Configuration` class itself should also be package-private when component scanning is the only entry point that needs to find it.

```java
// good — package-private @Configuration and package-private @Bean methods
@Configuration
class PaymentConfig {

    @Bean
    PaymentClient paymentClient(PaymentProperties properties) {
        return new PaymentClient(properties.endpoint(), properties.timeout());
    }

    @Bean
    PaymentRetryPolicy retryPolicy() {
        return new ExponentialBackoffRetry(3, Duration.ofSeconds(1));
    }
}
```

```java
// bad — public on the class and the @Bean methods, with no reason
@Configuration
public class PaymentConfig {

    @Bean
    public PaymentClient paymentClient(PaymentProperties properties) {
        return new PaymentClient(properties.endpoint(), properties.timeout());
    }
}
```

**Why:**

- Spring uses CGLIB to subclass `@Configuration` classes at runtime so it can intercept `@Bean` method calls and ensure singleton semantics across calls between methods. CGLIB-generated proxies can override any **non-private** method — package-private and protected work as well as public.
- Public is misleading. `@Bean` methods aren't API; they're implementation detail of how the application context gets wired. Marking them public puts them in IDE autocomplete and reflection-based searches as if they were intended for direct calls. They aren't.
- Package-private is the most restrictive visibility that still works. Don't use `private` — Spring **cannot** proxy private methods, so internal calls between `@Bean` methods inside the same `@Configuration` would bypass the proxy and create separate instances each time, breaking singleton semantics.

The rule extends to the `@Configuration` class itself **when component scanning is the only entry point**. If the class is referenced explicitly via `@Import` from another package, it has to stay public — but that's the exception, not the default.

### 2. `@Configuration` classes are not `final`

Same CGLIB-proxying constraint as rule 1: Spring needs to subclass the `@Configuration` class to intercept `@Bean` method calls, and `final` blocks subclassing. With proxying enabled (the default), CGLIB will fail to start the application context.

```java
// good
@Configuration
class PaymentConfig { ... }

// bad — CGLIB cannot subclass; context startup fails
@Configuration
final class PaymentConfig { ... }
```

The `lombok` skill makes the same note about `@Value` in proxied contexts — both are instances of the same root cause: Spring's proxying requires non-final, non-private targets.

The only situation where `final` is safe on a `@Configuration` class is `@Configuration(proxyBeanMethods = false)`, which disables CGLIB proxying for that class entirely. Even then, mixing `final` with no-proxy mode is fragile — if someone later removes the `proxyBeanMethods = false` setting without also removing `final`, the context silently breaks. Don't combine them without a real reason.

### 3. Prefer `application.yaml` over `application.properties`

Application configuration uses YAML (`application.yaml`, `application-<profile>.yaml`), not the legacy `.properties` format. Spring Boot supports both equivalently, but YAML is the better choice for new projects and the right default to push towards.

```yaml
# application.yaml — clean tree
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/app
    username: app
    password: ${DB_PASSWORD}
  jpa:
    hibernate:
      ddl-auto: validate
```

```properties
# application.properties — repeated prefixes, every key reads the full path
spring.datasource.url=jdbc:postgresql://localhost:5432/app
spring.datasource.username=app
spring.datasource.password=${DB_PASSWORD}
spring.jpa.hibernate.ddl-auto=validate
```

**Why:**

- **Hierarchical structure.** Nested config (`spring.datasource.{url, username, password}`) reads as a tree in YAML; in properties it's three lines with the prefix duplicated. The repetition isn't just aesthetic — misalignment between repeated prefixes (a typo in one of three `spring.datasource.` strings) is a real config bug that YAML structurally prevents.
- **Lists and maps are first-class.** YAML has native list and map syntax. Properties files require `foo[0]=`, `foo[1]=` indexed keys for lists, and there's no clean syntax for maps. A `@ConfigurationProperties` class with a `Map<String, X>` is dramatically nicer to populate from YAML.
- **Comments stay attached to structure.** Both formats support comments, but in YAML a comment sits visually with the sub-tree it documents. Properties comments tend to drift when keys move because they're not structurally bound to anything.
- **Single source of truth on the format question.** Mixing both formats in the same project is a real footgun — Spring's property-resolution order (`.properties` overrides `.yaml` at the same precedence) is well-defined but rarely top-of-mind. Picking one format and sticking to it removes the failure mode entirely.

**Filename:** `application.yaml` (not `application.yml`). Spring Boot accepts both extensions; `.yaml` matches the YAML spec's recommendation. Profile-specific files follow the same pattern: `application-dev.yaml`, `application-prod.yaml`, `application-test.yaml`.

**Exception — project consistency.** When the project already uses `.properties` everywhere, don't introduce a stray `application.yaml`. Mixing formats is the exact problem this rule is supposed to prevent. If a converting an existing project to YAML is the goal, that's a deliberate change with PR implications — ASK first.

### 4. On Spring Boot 4+, use `spring-boot-starter-webmvc` instead of `spring-boot-starter-web`

`spring-boot-starter-web` is **deprecated in Spring Boot 4** and will be removed in a future major version. Its replacement is `spring-boot-starter-webmvc`, which is what new and migrated projects should depend on.

Before applying this rule, **detect the project's Spring Boot version** from the parent POM (`<parent>` block in Maven), the Spring Boot Gradle plugin version (`id 'org.springframework.boot' version '...'`), or `spring-boot-dependencies` BOM. The rule applies as follows:

| Spring Boot version | Starter to use |
|---|---|
| 4.x and later | `spring-boot-starter-webmvc` |
| 3.x and earlier | `spring-boot-starter-web` *(no choice — `webmvc` starter does not exist yet)* |

```xml
<!-- Spring Boot 4+ — good -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-webmvc</artifactId>
</dependency>

<!-- Spring Boot 4+ — deprecated; remove and replace -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
</dependency>
```

```gradle
// Spring Boot 4+ — good
implementation 'org.springframework.boot:spring-boot-starter-webmvc'

// Spring Boot 4+ — deprecated; remove and replace
implementation 'org.springframework.boot:spring-boot-starter-web'
```

**Why the rename:** `spring-boot-starter-web` was an omnibus name that hid a specific stack choice (Spring MVC + Tomcat). The Spring team is making the stack explicit in the starter name so the alternatives — `spring-boot-starter-webflux` (reactive), and any future stacks — sit at the same naming level. `webmvc` is what `web` always was; the rename is purely about clarity.

**Scope of this rule:**

- Only `spring-boot-starter-web` → `spring-boot-starter-webmvc` is affected. `spring-boot-starter-webflux`, `spring-boot-starter-actuator`, `spring-boot-starter-data-jpa`, and the rest are not deprecated.
- The rule applies to dependency declarations in `pom.xml`, `build.gradle`, `build.gradle.kts`, and equivalent build files. It does not change application code — `@RestController`, `@GetMapping`, etc. work identically with both starters.

**Migration guidance for existing 3.x projects on Spring Boot version bumps:** when bumping a project to Spring Boot 4+, the starter swap is part of the upgrade — flag it explicitly in the PR description. It's a one-line dependency change with no code-level fallout, but burying it inside a multi-file version bump makes the deprecation history harder to track later.

### 5. On Spring Boot 4+, Jackson imports come from `tools.jackson.*`

Spring Boot 4 ships **Jackson 3**, which renamed the entire Java package from `com.fasterxml.jackson.*` to `tools.jackson.*`. Existing imports of `com.fasterxml.jackson.databind.ObjectMapper` (and friends) won't compile on a Spring Boot 4 project — replace them with `tools.jackson.databind.ObjectMapper`.

| Spring Boot version | Jackson version | `ObjectMapper` import |
|---|---|---|
| 4.x and later | Jackson 3 | `tools.jackson.databind.ObjectMapper` |
| 3.x and earlier | Jackson 2.x | `com.fasterxml.jackson.databind.ObjectMapper` |

```java
// Spring Boot 4+ — good
import tools.jackson.databind.ObjectMapper;
import tools.jackson.databind.json.JsonMapper;

// Spring Boot 4+ — won't compile (Jackson 2 package no longer present)
import com.fasterxml.jackson.databind.ObjectMapper;
```

The rename is across-the-board: `tools.jackson.core.*`, `tools.jackson.databind.*`, `tools.jackson.dataformat.*`, etc. — a flat search-and-replace of `com.fasterxml.jackson.` → `tools.jackson.` covers most code.

**Documented exception — annotations stay on the old package.** The `com.fasterxml.jackson.annotation` package (containing `@JsonProperty`, `@JsonInclude`, `@JsonIgnore`, `@JsonCreator`, etc.) keeps its 2.x package name in Jackson 3. Only annotations defined inside `jackson-databind` and the format-specific modules move to the new `tools.jackson.*` namespace. So:

```java
// On Spring Boot 4+, both of these are correct simultaneously:
import tools.jackson.databind.ObjectMapper;          // databind class — new package
import com.fasterxml.jackson.annotation.JsonProperty; // annotation — old package, on purpose
```

A bulk search-and-replace of `com.fasterxml.jackson` will incorrectly rewrite `com.fasterxml.jackson.annotation` imports into the new namespace, breaking the build. When migrating, exclude the `annotation` sub-package from the rewrite (or do it module-by-module rather than via blanket sed).

**Detection:** the project's Spring Boot version (parent POM, Gradle plugin, or BOM) determines which Jackson is on the classpath. Don't pick the import path before checking the version — the Jackson 2 package isn't present in a Spring Boot 4 build, and the Jackson 3 package isn't present in a Spring Boot 3 build.

## Edge cases

- **`@Configuration(proxyBeanMethods = false)`** disables CGLIB proxying for that class. With proxying off, visibility doesn't matter for proxy reasons — but the *API-surface* argument still applies. Keep `@Bean` methods package-private anyway.
- **`@TestConfiguration`** follows the same rule. Test code that needs a specific bean pulls it from the application context, not by calling the `@Bean` method directly.
- **`@Configuration` classes in a shared library** intended for `@Import` from other modules' code may need to stay public *on the class*. The `@Bean` methods inside still stay package-private.

## When reviewing existing code

If you see `public @Bean` or `public @Configuration class` with no `@Import` from another package: flag it. The fix is removing the `public` modifier — no behavior change, smaller API surface.

If a `@Configuration` class is `final`: flag it harder. CGLIB will fail to start the context, so this usually only happens when `proxyBeanMethods = false` is also set, but mixing the two without intent is fragile.
