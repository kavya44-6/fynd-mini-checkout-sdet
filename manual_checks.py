import functools
import http.server
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

PROJECT_ROOT = Path(__file__).resolve().parent
EVIDENCE = PROJECT_ROOT / "evidence"
EVIDENCE.mkdir(exist_ok=True)


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):  # noqa: A002
        pass


def main():
    handler = functools.partial(QuietHandler, directory=str(PROJECT_ROOT))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    results = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            page.goto(f"http://127.0.0.1:{port}/", wait_until="domcontentloaded")

            # Manual check 1: empty cart must block checkout.
            page.get_by_test_id("customer-name").fill("Manual Tester")
            page.get_by_test_id("place-order").click()
            empty_msg = page.get_by_test_id("validation-message")
            empty_pass = (
                empty_msg.is_visible()
                and "cart is empty" in empty_msg.inner_text().lower()
                and page.get_by_test_id("confirmation").is_hidden()
            )
            page.screenshot(path=str(EVIDENCE / "manual_empty_cart_blocked.png"), full_page=True)
            results.append(("Manual empty cart blocked", empty_pass, empty_msg.inner_text()))

            # Reset for the next manual check.
            page.reload(wait_until="domcontentloaded")
            page.get_by_test_id("add-p1").click()
            page.get_by_test_id("customer-name").fill("Rapid Click Tester")

            # Manual check 2: rapid double-click / same-task duplicate click must not duplicate confirmation.
            page.evaluate(
                """() => {
                    const button = document.querySelector('[data-testid="place-order"]');
                    button.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
                    button.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
                }"""
            )
            reference_count = page.locator('[data-testid="order-reference"]').count()
            visible_reference_count = page.locator('[data-testid="order-reference"]:visible').count()
            double_pass = (
                page.get_by_test_id("confirmation").is_visible()
                and reference_count == 1
                and visible_reference_count == 1
                and page.locator('[data-testid="order-reference"]').inner_text().startswith("FYND-")
            )
            page.screenshot(path=str(EVIDENCE / "manual_rapid_double_click_one_confirmation.png"), full_page=True)
            results.append(("Manual rapid double-click creates one confirmation", double_pass, page.locator('[data-testid="order-reference"]').inner_text()))

            browser.close()
    finally:
        server.shutdown()
        server.server_close()

    lines = ["Manual check results"]
    for name, passed, detail in results:
        lines.append(f"{'PASS' if passed else 'FAIL'} - {name}: {detail}")

    output = "\n".join(lines) + "\n"
    (PROJECT_ROOT / "manual_results.txt").write_text(output, encoding="utf-8")
    print(output, end="")
    if not all(passed for _, passed, _ in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
