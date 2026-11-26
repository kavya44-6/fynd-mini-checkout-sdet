# Test Plan: Mini Checkout

## Scope

Key checkout risks for a small store release:

1. Customers must see correct line totals and the order total.
2. Customers must know which required field is missing.
3. Customers must receive one clear confirmation with a reference.
4. Invalid checkout attempts must not destroy entered cart or field data.
5. Rapid repeated submission must not create duplicate confirmations.

## Prioritized test cases

| Priority | Area | Test idea | Expected result |
|---|---|---|---|
| P0 | Happy path | Add items, enter name, place order | Confirmation is visible with one `FYND-...` reference |
| P0 | Validation | Add item but leave name blank/whitespace | Checkout blocked; clear name error; entered value preserved |
| P0 | Totals | Change quantity | Line total and order total update to exact values |
| P1 | Empty cart | Click Place Order with no items | Checkout blocked with clear empty-cart message |
| P1 | Duplicate submit | Rapid double-click Place Order | Only one confirmation/reference is produced |

## Automated checks

Automated with Playwright in `tests/test_checkout.py`. Each test starts from a clean browser context/page. Assertions target visible customer-facing elements and exact total text rather than fixed sleeps.

Covered automatically:

- Successful checkout produces a confirmation.
- Missing required name blocks checkout and preserves entered input.
- Quantity change updates the exact line total and order total.

## Manual checks executed

| Manual check | Steps | Expected | Actual | Status |
|---|---|---|---|---|
| Empty cart blocked | Load page, leave cart empty, enter name, click Place Order | Checkout blocked; empty-cart message shown; no confirmation | Blocked with `Your cart is empty. Add at least one item before checkout.`; no confirmation | Pass |
| Rapid double-click | Add one item, enter name, double-click Place Order quickly | One confirmation only; one reference | One confirmation shown; one reference captured | Pass |

## Evidence

Screenshots are generated under `evidence/` by `manual_checks.py`.

## Defects found

None in the implemented scope. If a future change introduces a failure, record steps, expected vs actual, and evidence here.
