# Results

Date: 2026-11-25
Environment: Python 3.12, Playwright Chromium, local `http.server` serving the project folder.

## Automated browser checks

Command:

```bash
python -m unittest discover -s tests -v
```

Output:

```text
test_missing_required_name_blocks_checkout_and_preserves_input (test_checkout.CheckoutTest.test_missing_required_name_blocks_checkout_and_preserves_input) ... ok
test_quantity_change_updates_exact_total (test_checkout.CheckoutTest.test_quantity_change_updates_exact_total) ... ok
test_successful_checkout_produces_confirmation (test_checkout.CheckoutTest.test_successful_checkout_produces_confirmation) ... ok

----------------------------------------------------------------------
Ran 3 tests in 1.316s

OK
```

Covered risks:

- Successful checkout shows one confirmation and a `FYND-XXXXXXXX` reference.
- Missing/blank required name blocks checkout, shows a clear message, and preserves the entered input.
- Changing quantity updates exact line totals and the exact order total.

## Manual checks

Command:

```bash
python manual_checks.py
```

Output:

```text
Manual check results
PASS - Manual empty cart blocked: Your cart is empty. Add at least one item before checkout.
PASS - Manual rapid double-click creates one confirmation: FYND-NWWZRYA9
```

Evidence screenshots:

- `evidence/manual_empty_cart_blocked.png`
- `evidence/manual_rapid_double_click_one_confirmation.png`

## Defect log

No unresolved defects found in the final implementation.

Resolved during development before submission:

| Severity | Area | Steps | Expected | Actual before fix | Fix | Status |
|---|---|---|---|---|---|---|
| Medium | Quantity entry | Add an item, type a new quantity in the quantity field | Line total and order total update immediately | Totals waited for blur/change event, so an automated customer-visible input did not update totals immediately | Listen to `input` events for quantity fields and re-render totals | Fixed and regression-tested |
