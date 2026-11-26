# Mini Checkout and Browser Test Suite

A plain single-page checkout for the SDET hackathon brief. It uses two synthetic products with fixed prices, updates line totals and the order total as quantities change, blocks invalid checkout attempts, and shows one confirmation with an order reference after a successful order.

## Project structure

```text
.
├── index.html          # Single-page checkout
├── styles.css          # Plain interface styling
├── app.js              # Cart, validation, confirmation, duplicate-submit guard
├── tests/
│   └── test_checkout.py
├── manual_checks.py    # Manual evidence script for empty cart and rapid double-click
├── TEST_PLAN.md
├── RESULTS.md
└── evidence/           # Generated screenshots from manual checks
```

## Run the page

Open `index.html` directly in a browser, or serve the folder locally:

```bash
python -m http.server 8000
# then open http://localhost:8000
```

## Run browser tests

Install Python dependencies if needed:

```bash
python -m pip install playwright
python -m playwright install chromium
```

Run the automated checks from the project root:

```bash
python -m unittest discover -s tests -v
```

Generate manual evidence screenshots:

```bash
python manual_checks.py
```

## Implemented behavior

- Add/remove two fixed-price products and change quantities.
- Exact line totals and order total update immediately.
- Checkout is blocked for an empty cart.
- Checkout is blocked when the required name field is blank/whitespace.
- Validation messages are clear and entered values are preserved on failed validation.
- One confirmation is shown with reference format `FYND-XXXXXXXX`.
- A `placingOrder` guard plus disabled submit button prevents duplicate confirmations from rapid double-clicks.

## Defect policy

The brief says to report real defects only. Current result: no reproducible defects found in the implemented scope.
