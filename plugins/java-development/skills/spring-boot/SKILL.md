---
name: spring-boot
description: "Use whenever writing or reviewing Spring Boot or Spring Framework configuration code — @Configuration classes, @Bean methods, @SpringBootApplication, application context wiring. Triggers on phrases like 'add a Bean', 'wire up this dependency', 'create a Configuration class', 'register this with Spring', and on any Java file containing @Bean, @Configuration, @SpringBootApplication, or other Spring stereotype annotations. Currently enforces one rule: @Bean methods are package-private, not public, because Spring's CGLIB proxy works fine with package-private visibility and public exposes implementation-of-context-wiring as if it were API. The skill is expected to grow as more conventions are added."
---

# Spring Boot

Personal conventions for Spring Boot / Spring Framework application context wiring. Currently one rule; the skill will grow as more conventions are added.

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

**Don't use `final` on `@Configuration` classes either.** Same CGLIB-proxying constraint: the proxy needs to subclass, and `final` blocks subclassing. The `lombok` skill makes the same note about `@Value` in proxied contexts — same root cause.

## Edge cases

- **`@Configuration(proxyBeanMethods = false)`** disables CGLIB proxying for that class. With proxying off, visibility doesn't matter for proxy reasons — but the *API-surface* argument still applies. Keep `@Bean` methods package-private anyway.
- **`@TestConfiguration`** follows the same rule. Test code that needs a specific bean pulls it from the application context, not by calling the `@Bean` method directly.
- **`@Configuration` classes in a shared library** intended for `@Import` from other modules' code may need to stay public *on the class*. The `@Bean` methods inside still stay package-private.

## When reviewing existing code

If you see `public @Bean` or `public @Configuration class` with no `@Import` from another package: flag it. The fix is removing the `public` modifier — no behavior change, smaller API surface.

If a `@Configuration` class is `final`: flag it harder. CGLIB will fail to start the context, so this usually only happens when `proxyBeanMethods = false` is also set, but mixing the two without intent is fragile.
