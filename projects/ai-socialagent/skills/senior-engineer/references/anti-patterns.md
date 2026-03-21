# Anti-Patterns — When Engineering Goes Wrong

Patterns that feel productive but create more problems than they solve. Each entry explains what the pattern looks like, why it's tempting, and what to do instead.

---

## 1. Premature Abstraction

**Looks like:** A `BaseService<T>` class, a `createFactory()` function, or a `useGenericHandler` hook — all used exactly once.

**Why it's tempting:** It feels like you're "doing it right" and preparing for the future. DRY principle taken to an extreme.

**The reality:** Abstractions are bets on the future. Every abstraction you write today assumes tomorrow's requirements will follow the same shape. When they don't (and they usually don't), the abstraction becomes a constraint you fight against instead of a tool that helps.

**Instead:** Write the concrete implementation. When you have 3 concrete examples that share a clear pattern, *then* extract. The abstraction will be better because it's based on evidence, not speculation.

**The test:** Can you name 3 existing callers that would benefit? If not, it's premature.

---

## 2. Speculative Generality

**Looks like:** Config objects for things that never change. Feature flags for features that don't exist. Plugin architectures for apps with one plugin. "Just in case" parameters.

**Why it's tempting:** "It's only a little more work now and it'll save us time later."

**The reality:** Configuration has a cost: validation, documentation, testing, error messages for invalid values, migration when the schema changes. Every config option is a maintenance promise. Most never get used.

**Instead:** Hardcode it. When someone actually needs it to be configurable, add the configuration then. You'll know the actual requirements instead of guessing.

**The test:** Has anyone asked for this to be configurable? If no, hardcode.

---

## 3. Defensive Programming Against Yourself

**Looks like:** Runtime type checks on function parameters that TypeScript already validates. Null checks on values you just constructed. Try/catch around code that can't throw. Validation between internal modules that trust each other.

**Why it's tempting:** "Better safe than sorry." Defensive programming is a well-known best practice.

**The reality:** Defensive programming matters at system boundaries — user input, API responses, file reads, database queries. Between your own functions in the same codebase, it's noise. It obscures the real logic, makes the code harder to read, and creates a false sense of safety.

**Instead:** Trust your internal code. Validate at the boundaries. Use TypeScript's type system to catch the internal contract violations at compile time, not runtime.

**The test:** Is this data coming from outside the system? If no, skip the validation.

---

## 4. Test-Driven Paralysis

**Looks like:** Writing comprehensive test suites before the interface is stable. Mocking everything. Tests that assert implementation details rather than behavior. 100% coverage as a goal.

**Why it's tempting:** Tests are good, right? More tests = more safety. TDD is a best practice.

**The reality:** Tests are maintenance. Every test is a commitment to keep passing. When interfaces are still changing (early development, prototyping, design exploration), tests become anchors that slow down iteration. You spend more time updating tests than writing features.

**Instead:** Write tests when:
- The interface is stable and unlikely to change
- The logic is complex enough that manual testing is unreliable
- You're fixing a bug (write a test that reproduces it, then fix)
- External consumers depend on the behavior

Skip tests when:
- You're still designing the API
- The feature might be removed or rewritten
- The test would only assert that the framework works correctly

**The test:** Would rewriting this function require rewriting the test? If yes, the test is coupled to implementation, not behavior.

---

## 5. Over-Documented Code

**Looks like:** JSDoc on every function. Comments above every line. README files that restate what the code does. Inline explanations of standard library calls.

**Why it's tempting:** "Self-documenting code" feels like a myth, and documentation is universally praised.

**The reality:** Comments that explain *what* the code does become stale when the code changes. They're a maintenance burden that provides no value to competent readers. Worse, stale comments are actively misleading.

**Instead:** Write code that's clear enough to read without comments. Use comments only for:
- **Why** — "We use JSONB here because translations may expand to 3+ languages"
- **Non-obvious constraints** — "Must run before the auth middleware initializes"
- **Workarounds** — "Safari doesn't support X, so we do Y instead"
- **Business context** — "Legal requires session tokens to be stored this way"

**The test:** Does this comment say something the code doesn't? If no, delete it.

---

## 6. Backwards-Compatibility Theater

**Looks like:** Re-exporting removed types. Renaming old functions to `_deprecated_oldName`. Adding `// removed` comments where code used to be. Keeping unused parameters with underscore prefixes.

**Why it's tempting:** "Someone might depend on this." Breaking changes feel reckless.

**The reality:** If you control all the consumers and can verify nothing uses the old interface, keeping it around is pure noise. It confuses future readers ("is this used or not?") and makes the codebase appear larger than it is.

**Instead:** Delete it. If something breaks, you'll know immediately and the fix is to update the consumer. That's cheaper than maintaining dead code indefinitely.

**The test:** Can you grep the entire codebase for usages? If zero results, delete.

---

## 7. The God Commit

**Looks like:** "Update everything", "Big refactor", "WIP — Monday work". Commits that touch 30 files across 5 features.

**Why it's tempting:** You're in flow, changing things as you discover them. Committing feels like it would break the momentum.

**The reality:** Git history is a debugging tool. When you need to find which change broke something, a 30-file commit makes bisection useless. When you need to revert one change, you can't extract it from the blob.

**Instead:** Commit coherent units. One logical change per commit. If you've been working for hours without committing, stop and stage related changes into separate commits using `git add -p`.

**The test:** Can you describe what this commit does in one sentence? If not, split it.

---

## 8. Configuration-Driven Everything

**Looks like:** Admin UIs for values that change once a year. Database tables for things that could be an enum. YAML files for what could be a constant.

**Why it's tempting:** "Non-developers should be able to change this." Configurability feels like good product thinking.

**The reality:** Every configuration surface has a cost: UI to display it, validation to enforce it, documentation to explain it, migration when the schema changes, and error handling when the value is invalid. If the value changes less than once a quarter, a code change deployed in 5 minutes is simpler and safer.

**Instead:** Start with a constant. When someone actually needs to change it without a deploy, build the configuration then. You'll know the actual constraints (who needs access, what validation is needed, what the failure mode is).

**The test:** How often does this value change? If less than monthly, it's a constant.
