import functools
import http.server
import re
import threading
import unittest
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):  # noqa: A002 - keep test output clean
        pass


class CheckoutTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.handler = functools.partial(QuietHandler, directory=str(PROJECT_ROOT))
        cls.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), cls.handler)
        cls.port = cls.server.server_address[1]
        cls.base_url = f"http://127.0.0.1:{cls.port}/"
        cls.server_thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.server_thread.start()

        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self):
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        self.page.goto(self.base_url, wait_until="domcontentloaded")

    def tearDown(self):
        self.context.close()

    def add_product(self, product_id):
        self.page.get_by_test_id(f"add-{product_id}").click()

    def test_successful_checkout_produces_confirmation(self):
        self.add_product("p1")
        self.add_product("p2")
        self.page.get_by_test_id("customer-name").fill("Asha Khan")
        self.page.get_by_test_id("place-order").click()

        confirmation = self.page.get_by_test_id("confirmation")
        expect(confirmation).to_be_visible()
        expect(self.page.get_by_test_id("confirmation-message")).to_contain_text("Asha Khan")
        expect(self.page.get_by_test_id("order-reference")).to_have_text(re.compile(r"^FYND-[0-9A-Z]{8}$"))
        expect(self.page.get_by_test_id("validation-message")).to_be_hidden()

    def test_missing_required_name_blocks_checkout_and_preserves_input(self):
        self.add_product("p1")
        name_input = self.page.get_by_test_id("customer-name")
        name_input.fill("   ")
        self.page.get_by_test_id("place-order").click()

        expect(self.page.get_by_test_id("confirmation")).to_be_hidden()
        expect(self.page.get_by_test_id("validation-message")).to_be_visible()
        expect(self.page.get_by_test_id("validation-message")).to_contain_text("Please enter your name")
        self.assertEqual(name_input.input_value(), "   ")
        expect(self.page.get_by_test_id("order-total")).to_have_text("₹799.00")

    def test_quantity_change_updates_exact_total(self):
        self.add_product("p1")
        self.add_product("p2")
        self.page.get_by_test_id("qty-p2").fill("3")

        expect(self.page.get_by_test_id("line-total-p1")).to_have_text("₹799.00")
        expect(self.page.get_by_test_id("line-total-p2")).to_have_text("₹4,497.00")
        expect(self.page.get_by_test_id("order-total")).to_have_text("₹5,296.00")


if __name__ == "__main__":
    unittest.main()
