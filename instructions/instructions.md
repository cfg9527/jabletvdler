# OpenCode Agent Ironclad Behavioral Guardrails (Google + Planning + Graphify + ECC)

You are an advanced engineering AI agent deployed within the OpenCode ecosystem. You must strictly adhere to the following three-stage pipeline established by the Commander. "Hallucinating", "forgetting", "guessing", or "blindly refactoring" is strictly prohibited.

---

## Stage 1: Planning-with-files (Establish the Rules)
1. Upon receiving any development or refactoring task, you are **ABSOLUTELY FORBIDDEN** from modifying code immediately.
2. You must first read `docs/design/design.md` (following the Google design.md specification to align with the long-term architectural goals).
3. Use the `write_file` tool to create or update a milestone checklist and test specifications inside `tasks/current_plan.md` (Switching into TDD / Test-Driven Development mode).
4. Before modifying any file, you must update the progress status in this file (e.g., change `[ ] Step 1` to `[x] Step 1 Completed`). Do not blindly jump ahead.

---

## Stage 2: Graphify (Understand the Whole Picture)
1. Before editing or adding any file, you must invoke the local `graphify query` or `graphify explain` commands.
2. Analyze the upstream/downstream dependencies and the exact **Blast Radius** of the target code at the AST (Abstract Syntax Tree) level.
3. You must explicitly output the following statement in your Thinking Process:
   > "Checked via Graphify: Modifying File A will affect Module B and Function C. I have added corresponding defensive interface compatibility tests into `current_plan.md`."
4. Proceed with code modification only after understanding the structural map. Never fix A while breaking B.

---

## Stage 3: ECC Boundary (Automated Verification & Self-Correction)
1. Once code generation is complete, you are **ABSOLUTELY FORBIDDEN** from declaring the task finished or submitting it to the Commander.
2. You must automatically use the `run_terminal_command` tool to execute the automated ECC validation script at the project root (Command: `./ecc_check.sh`).
3. **Forced Self-Correction Loop**:
   - If the tests, Linter checks, or security scans return a non-zero exit code (`Exit Code != 0`), the submission is rejected as unqualified.
   - You must autonomously read the terminal's Error Log and debug the code right where it failed.
   - Repeat the "Modify -> Test" cycle until `./ecc_check.sh` passes successfully with all green lights and zero vulnerabilities before reporting back to the Commander.

---

## The Commander's Ultimate Expectation
Your objective is not to maximize raw coding speed, but to ensure that every output is fully **Production-ready** without accumulating hidden technical debt. Be auditable, verifiable, and capable of resuming tasks across multiple conversational rounds. This is the hallmark of true engineering discipline.

---

# Best Practice Guide: Test Script Step Structure
This document outlines a standardized, highly readable, and maintainable structure for designing and updating test scripts after editing source code (`.py` files).

---

## 1. Core Philosophy: The AAA Pattern
Every effective test case should tell a clear story. To achieve this, we adhere to the **AAA (Arrange, Act, Assert)** pattern, which aligns closely with the **Given-When-Then** structure used in behavioral testing.

By separating these three concerns, your test scripts become self-documenting, easier to debug, and highly resilient to code modifications.

```
+-------------------------------------------------------+
|                       ARRANGE                         |
|  (Set up preconditions, mock data, and environments)  |
+---------------------------+---------------------------+
                            |
                            v
+-------------------------------------------------------+
|                         ACT                           |
|      (Execute the specific function under test)       |
+---------------------------+---------------------------+
                            |
                            v
+-------------------------------------------------------+
|                        ASSERT                         |
|    (Verify the actual outcome against expectations)   |
+-------------------------------------------------------+
```

---

## 2. Step-by-Step Structure

### Phase 1: Arrange (Given)
* **Purpose:** Set up the system under test to the exact state required for the specific scenario.
* **Key Actions:**
  * Initialize target objects or classes.
  * Prepare mock inputs, sample payloads, or test data.
  * Configure environment variables, temporary database states, or mock external services.
* **Best Practice:** Keep this section clean. If setup exceeds 5-10 lines, abstract it into a reusable testing fixture (e.g., `pytest.fixture`).

### Phase 2: Act (When)
* **Purpose:** Trigger the exact code behavior or modification you introduced in your `.py` file.
* **Key Actions:**
  * Call the target method, function, or API endpoint.
  * Pass the parameters prepared in the *Arrange* step.
  * Capture the return value or the resulting exception.
* **Best Practice:** The *Act* phase should ideally be **1 to 2 lines long**. If you find yourself calling multiple sequential functions, you might be testing too many things at once.

### Phase 3: Assert (Then)
* **Purpose:** Verify that the executed action behaved exactly as intended.
* **Key Actions:**
  * Compare the returned data with expected values (`assert actual == expected`).
  * Check for changes in system state or side effects (e.g., verifying a file was written).
  * Validate that correct exceptions were raised under failure states.
* **Best Practice:** Provide explicit, descriptive assertion error messages. This helps diagnose regressions immediately when automated pipelines fail.

---

## 3. Standard Code Template (Python with `pytest`)

Below is a robust example demonstrating how to structure both successful paths and exception paths after modifying a hypothetical shopping cart module.

```python
import pytest
from shopping_cart import calculate_discount, InvalidCouponError

# Example 1: Happy Path / Successful Scenario
def test_calculate_discount_with_valid_coupon():
    # ---------------------------------------------------------
    # [Arrange] Prepare inputs and expected outcomes
    # ---------------------------------------------------------
    cart_total = 100.0
    coupon_code = "SUMMER20"
    expected_discount = 20.0

    # ---------------------------------------------------------
    # [Act] Execute the target function under test
    # ---------------------------------------------------------
    actual_discount = calculate_discount(cart_total, coupon_code)

    # ---------------------------------------------------------
    # [Assert] Verify that the outcome matches the design
    # ---------------------------------------------------------
    assert actual_discount == expected_discount, (
        f"Expected discount to be {expected_discount}, but got {actual_discount} instead."
    )


# Example 2: Unhappy Path / Exception Handling Scenario
def test_calculate_discount_with_invalid_coupon():
    # [Arrange] Prepare invalid inputs that trigger a failure
    cart_total = 100.0
    invalid_coupon = "EXPIRED_CODE"

    # [Act] & [Assert] Capture and verify the expected exception
    with pytest.raises(InvalidCouponError) as exc_info:
        calculate_discount(cart_total, invalid_coupon)

    assert "Coupon has expired" in str(exc_info.value), "Error message did not match expectations."
```

---

## 4. Post-Edit Checklist: Updating Your Test Scripts
When you modify a `.py` file, follow this mental workflow to update its corresponding test script:

1. **Map the Changes:** Did your code change introduce a new logical branch, a new parameter, or a modified return type?
2. **Review Edge Cases:** Ensure you add test cases for extreme inputs (e.g., `None`, empty strings, negative values, out-of-bound integers) that your code edits might impact.
3. **Ensure Test Isolation:** Confirm that your test does not leave residual state behind. Use teardown blocks or fixtures to clean up any temporary directories, mock servers, or database changes.
4. **Run and Validate:** Run the test suite locally to verify that your new test fails if you revert your code changes (proving the test is valid), and passes when the code is applied.
