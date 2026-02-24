# VectixLogic Engineering Handbook

**Policy ID:** VL-TECH-016  
**Effective Date:** January 1, 2026  
**Focus:** Rust safety, Solidity gas optimization.  
**Version:** 2.0.1

---

## 1. Introduction to Rust at VectixLogic

Rust is the primary systems language for VectixLogic backend services, CLI tooling, and performance-critical paths in our pharmacy inventory and Solana integration layers. All new services that require memory safety, concurrency, or deterministic behavior must be implemented in Rust unless explicitly approved by the CTO.

**When to use Rust at VectixLogic:**
- Blockchain clients (Solana SDK wrappers, transaction builders)
- High-throughput APIs that serve the pharmacy inventory module
- Any component that handles PII or health data and must pass our security audit
- CLI tools used by engineers and pharmacy staff (e.g., batch import, audit export)

**When not to use Rust:**
- Rapid prototypes or internal scripts (Python is acceptable with approval)
- Frontend or mobile applications (use existing stack: TypeScript/React, etc.)

All Rust code must compile with the latest stable toolchain specified in `rust-toolchain.toml` at the repository root. Nightly features are prohibited except for documented exceptions in the blockchain team.

---

## 2. Memory Management and Ownership Rules

### 2.1 Ownership and Borrowing

Every value in Rust has a single owner. When passing data across function or module boundaries, prefer the following in order:

1. **Borrow when the caller retains ownership:** Use `&T` or `&mut T`. For large structs or hot paths, borrowing avoids allocation and satisfies the borrow checker.
2. **Clone only when necessary:** Use `.clone()` or `Arc<T>` when shared ownership across threads is required. Document why cloning was chosen in a comment if the type is large.
3. **Transfer ownership when the callee should own the data:** Use `T` by value. Common in constructors and when building intermediate data structures.

### 2.2 Lifetimes

Explicit lifetime annotations are required whenever a function returns a reference that depends on an input reference. Use descriptive names: `'ctx` for context, `'db` for database handles, `'req` for request-scoped data. Avoid `'a`, `'b` except in trivial generic code.

### 2.3 No Unsafe Without Review

Use of `unsafe` blocks must be documented with a safety comment explaining why the invariants are upheld. All `unsafe` code requires a second reviewer and an entry in the project's `SAFETY.md` (or equivalent) listing the justification and test coverage.

---

## 3. Error Handling with Result and Option

### 3.1 Result and Option Conventions

- Use `Result<T, E>` for operations that can fail. Use `Option<T>` for optional values (e.g., "may or may not exist").
- Never use `unwrap()` or `expect()` in library or production code paths. Use them only in tests, examples, or in `main()` after a documented decision.
- Prefer the `?` operator for propagation. Define project-specific error types that implement `From` for common dependencies (e.g., `sqlx::Error`, `serde_json::Error`) so that `?` works across layers.

### 3.2 Error Type Design

Use a single crate-level or module-level error enum that implements `std::error::Error` and `Display`. Use `thiserror` for derive-based implementations. Include context (e.g., `InventoryError::ExpiredBatch { batch_id, expiry_date }`) so that logs and user-facing messages are actionable.

### 3.3 Panics

Reserve panics for truly unreachable states (e.g., "invariant violated" after a defensive check). Do not panic on bad input; return `Result` or `Option` and let the caller decide.

---

## 4. Crate Dependency Management

### 4.1 Allowed Crates

Dependencies must be listed in the root `Cargo.toml` (workspace) or the specific crate's `Cargo.toml`. All new dependencies require a short justification in the PR description (e.g., "Add `tokio` for async runtime per VL-TECH-016").

### 4.2 Version Pinning

Use semantic versioning in `Cargo.toml`: specify a minimum compatible version (e.g., `serde = "1.0"`) and run `cargo update` in a controlled manner. Lock files (`Cargo.lock`) must be committed for binaries and applications; for libraries, document the minimum supported Rust version (MSRV) and dependency versions in the README.

### 4.3 Security and Audit

Run `cargo audit` in CI. Any high- or critical-severity finding must be resolved or explicitly accepted with a documented mitigation before merge. Use `cargo deny` (or equivalent) to forbid duplicate dependencies and disallowed licenses.

---

## 5. Testing and Benchmarking Protocols

### 5.1 Unit Tests

Place unit tests in the same file as the code under test, in a `#[cfg(test)]` module. Use the AAA pattern: Arrange (set up data and mocks), Act (call the function), Assert (check return value and side effects). Mock external services (databases, APIs) using traits and test doubles; avoid real network or DB in unit tests.

### 5.2 Integration Tests

Place integration tests in the `tests/` directory at the crate root. Each test file compiles as a separate crate. Use a shared helper (e.g., `tests/common/mod.rs`) for setup and teardown. Integration tests may use test containers or in-memory backends (e.g., SQLite for DB tests) where appropriate.

### 5.3 Benchmarks

Use `criterion` for performance benchmarks. Benchmarks must be deterministic (no wall-clock timing of external services). Record baseline metrics in the repo (e.g., in `docs/benchmarks.md`) and flag regressions in CI when benchmarks exceed a stated threshold (e.g., 5% slowdown).

---

## 6. Naming Conventions (Rust)

- **Crates:** `snake_case` (e.g., `vectix_inventory`, `vectix_solana_client`).
- **Modules:** `snake_case`.
- **Types (structs, enums):** `PascalCase`.
- **Functions and variables:** `snake_case`. Use descriptive names; avoid single letters except for iterators (e.g., `i`, `n` in short loops).
- **Constants:** `SCREAMING_SNAKE_CASE`.
- **Lifetimes:** lowercase, often `'a`, `'ctx`, `'db` (as noted in Section 2.2).

---

## 7. Solidity and Smart Contract Standards

### 7.1 Gas Optimization Rules

- Prefer `calldata` for read-only external array/struct parameters; use `memory` only when the function must modify the data.
- Pack storage variables into fewer slots (e.g., group `uint128` or smaller types) to minimize SSTORE costs.
- Use events for data that does not need to be read on-chain; avoid storing redundant state.
- Prefer custom errors over `require` strings to reduce deployment and revert gas.
- Cache array length and storage reads in local variables when used multiple times in a function.

### 7.2 Security Checklist for Smart Contracts

Before any contract is deployed to mainnet or a long-lived testnet, the following must be completed:

| Check | Owner |
|-------|--------|
| No use of `tx.origin` for authorization | Developer |
| Reentrancy guards on all state-changing external calls | Developer |
| Integer overflow/underflow handled (Solidity 0.8+ or SafeMath) | Developer |
| Access control (e.g., OpenZeppelin `Ownable`/`AccessControl`) reviewed | Developer |
| External audit or internal security review completed | CTO |
| Upgrade path (proxy pattern) documented if applicable | Tech Lead |

### 7.3 Naming and Style (Solidity)

- Contract names: `PascalCase`.
- Functions: `camelCase`. Use `internal` or `private` by default; expose `external`/`public` only when required.
- State variables: `camelCase` with a leading underscore for `private` (e.g., `_owner`).
- Events: `PascalCase` (e.g., `BatchExpired`, `ReturnForCreditSubmitted`).
- Constants: `SCREAMING_SNAKE_CASE`.

---

## 8. Rust Safety: 10 AAA Code Examples

All examples follow **Arrange–Act–Assert**: set up inputs and mocks, call the function, assert on the outcome.

### Example 1: Parsing a batch ID (Result)

```rust
// Arrange: valid and invalid input
// Act: parse_batch_id
// Assert: Ok("B-123") or Err
fn parse_batch_id(s: &str) -> Result<String, ParseError> {
    if s.starts_with("B-") && s.len() >= 4 { Ok(s.to_string()) } else { Err(ParseError::InvalidFormat) }
}
#[test] fn test_parse_batch_id_valid() {
    let input = "B-123";                    // Arrange
    let result = parse_batch_id(input);     // Act
    assert!(result.is_ok());                // Assert
    assert_eq!(result.unwrap(), "B-123");
}
```

### Example 2: Optional quantity (Option)

```rust
// Arrange: Option<u32>
// Act: get_quantity
// Assert: Some(10) or None
fn get_quantity(record: &InventoryRecord) -> Option<u32> { record.quantity }
#[test] fn test_get_quantity_some() {
    let record = InventoryRecord { quantity: Some(10) };  // Arrange
    let q = get_quantity(&record);                         // Act
    assert_eq!(q, Some(10));                               // Assert
}
```

### Example 3: Borrowing to avoid clone

```rust
// Arrange: large struct
// Act: process by reference
// Assert: original unchanged
fn total_value(items: &[InventoryItem]) -> u64 {
    items.iter().map(|i| i.unit_price * i.quantity as u64).sum()
}
#[test] fn test_total_value_borrow() {
    let items = vec![InventoryItem { unit_price: 100, quantity: 2 }];  // Arrange
    let total = total_value(&items);                                     // Act
    assert_eq!(total, 200);                                              // Assert
    assert_eq!(items.len(), 1);  // items still owned by test
}
```

### Example 4: Error propagation with ?

```rust
// Arrange: Result from dependency
// Act: function that uses ?
// Assert: Err propagates
fn load_batch(db: &Db, id: &str) -> Result<Batch, DbError> {
    let row = db.query_one(id)?;   // Act; ? propagates Err
    Ok(Batch::from_row(row)?)
}
#[test] fn test_load_batch_missing() {
    let db = MockDb::empty();      // Arrange
    let r = load_batch(&db, "B-999");  // Act
    assert!(r.is_err());           // Assert
}
```

### Example 5: Lifetime in return reference

```rust
// Arrange: struct with reference
// Act: get_name
// Assert: same as input slice
fn get_name<'a>(batch: &'a Batch) -> &'a str { &batch.name }
#[test] fn test_get_name_lifetime() {
    let batch = Batch { name: String::from("Batch-A") };
    let name = get_name(&batch);   // Act
    assert_eq!(name, "Batch-A");   // Assert
}
```

### Example 6: Custom error with context

```rust
// Arrange: error condition
// Act: return InventoryError
// Assert: error variant and message
#[derive(thiserror::Error, Debug)]
enum InventoryError { #[error("batch {batch_id} expired {expiry_date}")] ExpiredBatch { batch_id: String, expiry_date: String } }
#[test] fn test_expired_batch_error() {
    let e = InventoryError::ExpiredBatch { batch_id: "B-1".into(), expiry_date: "2025-01-01".into() };
    assert!(e.to_string().contains("B-1"));
}
```

### Example 7: No unwrap in library code

```rust
// Arrange: may fail
// Act: use ? or match
// Assert: no panic
fn safe_get(batch: &Batch) -> Option<&str> {
    batch.nested.as_ref().map(|n| n.name.as_str())  // No .unwrap()
}
```

### Example 8: Integration test layout

```rust
// tests/inventory_test.rs
// Arrange: common setup in tests/common/mod.rs
// Act: call crate public API
// Assert: DB state or return value
#[test] fn test_receive_batch_integration() {
    let db = setup_test_db();           // Arrange
    let result = vectix_inventory::receive_batch(&db, "B-1", 100);  // Act
    assert!(result.is_ok());           // Assert
}
```

### Example 9: Criterion benchmark (deterministic)

```rust
// Arrange: fixed input
// Act: benchmarked function
// Assert: no assertion; criterion compares to baseline
fn bench_parse(c: &mut Criterion) {
    let input = "B-12345";  // Arrange
    c.bench_function("parse_batch_id", |b| b.iter(|| parse_batch_id(black_box(input))));  // Act
}
```

### Example 10: Reentrancy guard (Solidity pattern)

```rust
// Rust equivalent: use state machine or guard type so "Act" is single-step
// Arrange: guard taken
// Act: do one state transition
// Assert: state updated once
struct DispenseGuard { batch_id: String }
impl Drop for DispenseGuard { fn drop(&mut self) { /* release lock */ } }
```

---

## 9. Appendix: Rust Compiler Error Glossary

| Code | Name | Meaning | Typical fix |
|------|------|---------|-------------|
| **E0382** | use of moved value | Value was moved and used again. | Clone, use reference, or restructure. |
| **E0499** | cannot borrow as mutable more than once | Multiple `&mut` to same value in scope. | Narrow scope, use interior mutability, or split logic. |
| **E0502** | cannot borrow as immutable (already borrowed as mutable) | `&` and `&mut` overlap. | Reorder or limit borrow scope. |
| **E0507** | cannot move out of borrowed content | Moving from behind a reference. | Clone, or take reference instead of ownership. |
| **E0515** | cannot return reference to local variable | Returning `&` to a local. | Return owned value or use `'static`/leak. |
| **E0373** | closure may outlive current function | Closure captures reference that may not live long enough. | Add lifetime, use `move`, or `Arc`. |
| **E0597** | borrowed value does not live long enough | Reference outlives its referent. | Extend lifetime of owned value or shorten use. |
| **E0308** | mismatched types | Expected one type, got another. | Add conversion, fix generic params, or change return type. |
| **E0277** | trait not implemented | Type does not implement required trait. | Implement trait or use type that does. |
| **E0282** | type annotations needed | Compiler cannot infer type. | Add type annotation (e.g., on variable or turbofish). |
| **E0433** | unresolved import | Import path wrong or not in scope. | Fix path or add dependency to `Cargo.toml`. |
| **E0583** | file not found for module | `mod.rs` or file missing. | Create file or fix `mod` declaration. |
| **E0554** | invalid feature flag | Use of non-existent or unstable feature. | Remove feature or enable in `Cargo.toml`/toolchain. |
| **E0658** | unstable feature | Nightly-only feature on stable. | Use stable alternative or document nightly exception. |
| **E0689** | wrong number of generic arguments | Too many or too few type/const params. | Match trait or struct definition. |
| **E0046** | missing items in trait impl | Trait method not implemented. | Implement all required methods. |
| **E0596** | cannot borrow as mutable | Value is not mutable or already borrowed. | Use `&mut` where allowed, or `RefCell`/`Mutex`. |
| **E0594** | cannot assign to immutable | Assigning to non-`mut` binding. | Add `mut` or use interior mutability. |
| **E0716** | temporary value dropped while borrowed | Reference to temp (e.g., expression result). | Bind temp to a variable with sufficient lifetime. |
| **E0759** | variable does not need to be mutable | `mut` unused. | Remove `mut` (clippy/style). |

---

## 10. Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0.0 | 2024-02-01 | CTO | Initial engineering handbook. |
| 1.1.0 | 2024-05-01 | CTO | Rust ownership and error handling. |
| 1.2.0 | 2024-08-01 | CTO | Solidity gas and security checklist. |
| 1.3.0 | 2024-11-01 | CTO | Crate deps and cargo audit. |
| 1.4.0 | 2025-02-01 | CTO | AAA testing and benchmarks. |
| 1.5.0 | 2025-05-01 | CTO | Naming conventions. |
| 1.6.0 | 2025-08-01 | CTO | 10 Rust AAA examples added. |
| 1.7.0 | 2025-11-01 | CTO | Rust compiler error glossary. |
| 2.0.0 | 2025-12-01 | CTO | Header standardized. |
| 2.0.1 | 2026-01-01 | CTO | Corpus release. |

---

## 11. Appendix: Definitions

| Term | Definition |
|------|------------|
| **AAA** | Arrange–Act–Assert; test structure: set up, execute, verify. |
| **Borrow checker** | Rust compiler logic enforcing ownership and borrowing rules. |
| **Result** | `Result<T, E>`; type for fallible operations. |
| **Option** | `Option<T>`; type for optional value. |
| **Unsafe** | `unsafe` block; requires manual invariant guarantee and review. |
| **Criterion** | Rust benchmarking crate; deterministic benchmarks. |
| **MSRV** | Minimum Supported Rust Version. |
| **cargo audit** | Tool to check dependencies for known vulnerabilities. |
| **Reentrancy** | Multiple concurrent calls into state-changing code; guarded in Solidity. |
| **calldata** | Solidity: read-only external input; cheaper than memory. |
| **SSTORE** | Solidity opcode for storage write; gas cost. |
| **thiserror** | Crate for deriving `Error` and `Display` for error enums. |
| **TDD** | Test-Driven Development; tests before implementation. |
| **Integration test** | Test in `tests/` that uses crate as a dependency. |
| **Unit test** | Test in `#[cfg(test)]` next to code under test. |

---

## 12. Related Documents

- **VL-SEC-002:** Data Security (keys, MFA; no secrets in code).
- **VL-AI-005:** AI-generated code peer review (merge to main).
- **VL-EXE-020:** Company Vision (technical excellence).
- **.cursorrules:** Project TDD and AAA standards.

---

## 13. Quick Reference

- **Rust:** [The Rust Book](https://doc.rust-lang.org/book/) and internal `docs/rust-style.md`.
- **Solidity:** [Solidity Style Guide](https://docs.soliditylang.org/en/latest/style-guide.html) and VectixLogic blockchain repo `CONTRIBUTING.md`.
- **Questions:** #engineering-standards on Slack or the CTO.

*This document is the single source of truth for Rust and Solidity at VectixLogic. Exceptions require CTO approval and must be documented.*
