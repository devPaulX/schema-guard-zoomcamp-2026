"""Exercise the actual dashboard in a headless browser with isolated SQLite data."""

import socket
import threading
import time
from urllib.error import URLError
from urllib.request import urlopen

import pytest
import uvicorn
from playwright.sync_api import expect, sync_playwright

from app.main import create_app


@pytest.fixture
def dashboard_url(tmp_path):
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    listener.listen(128)
    port = listener.getsockname()[1]
    server = uvicorn.Server(
        uvicorn.Config(create_app(tmp_path / "schemaguard.db"), log_level="error")
    )
    thread = threading.Thread(target=server.run, kwargs={"sockets": [listener]})
    thread.start()
    url = f"http://127.0.0.1:{port}"
    try:
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            try:
                with urlopen(f"{url}/api/health", timeout=1) as response:
                    if response.status == 200:
                        break
            except (OSError, URLError):
                time.sleep(0.05)
        else:
            pytest.fail("The temporary dashboard server did not start.")
        yield url
    finally:
        server.should_exit = True
        thread.join(timeout=10)
        listener.close()
        assert not thread.is_alive(), "The temporary dashboard server did not stop."


def test_contract_and_csv_upload_journey(dashboard_url, tmp_path):
    valid_csv = tmp_path / "valid.csv"
    invalid_csv = tmp_path / "invalid.csv"
    valid_csv.write_bytes(b"id,amount\n1,20\n2,30\n")
    invalid_csv.write_bytes(b"id,amount\n1,20\n2, \n")

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.goto(dashboard_url)
            page.locator("#contract-name").fill("browser smoke orders")
            page.locator("#required-columns").fill("id, amount")
            page.locator("#threshold").fill("0")
            page.get_by_role("button", name="Save contract").click()
            expect(page.locator("#contract-message")).to_contain_text("Saved contract")
            expect(page.locator("#contract-select")).to_have_value("1")

            page.locator("#csv-file").set_input_files(valid_csv)
            page.get_by_role("button", name="Run validation").click()
            expect(page.locator("#validation-result h3")).to_contain_text("PASS")
            expect(page.locator("#history-list .history-item")).to_have_count(1)
            expect(page.locator("#history-list .history-item").first).to_contain_text("valid.csv")

            page.locator("#csv-file").set_input_files(invalid_csv)
            page.get_by_role("button", name="Run validation").click()
            expect(page.locator("#validation-result h3")).to_contain_text("FAIL")
            expect(page.locator("#validation-result")).to_contain_text(
                "Column 'amount' has 50.00% missing values"
            )
            history = page.locator("#history-list .history-item")
            expect(history).to_have_count(2)
            expect(history.first).to_contain_text("invalid.csv")
            expect(history.first).to_contain_text("FAIL")
            expect(history.first).to_contain_text("Column 'amount' has 50.00% missing values")
            expect(history.nth(1)).to_contain_text("PASS")
        finally:
            browser.close()
