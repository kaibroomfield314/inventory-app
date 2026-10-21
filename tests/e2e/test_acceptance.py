"""Browser acceptance tests for the deployed inventory application."""

import os
import uuid

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = os.environ.get("BASE_URL", "").rstrip("/")
EXPECTED_VERSION = os.environ.get("EXPECTED_VERSION", "")


@pytest.fixture(scope="module")
def browser():
    if not BASE_URL:
        pytest.fail("BASE_URL must point to the deployed staging or production site")
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1280,900")
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(30)
    yield driver
    driver.quit()


def test_homepage_lists_products(browser):
    browser.get(f"{BASE_URL}/")
    products = WebDriverWait(browser, 15).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".product"))
    )
    assert products, "Expected seeded products on homepage"


def test_search_filters_products(browser):
    browser.get(f"{BASE_URL}/")
    product_name = browser.find_element(By.CSS_SELECTOR, ".product h3 a").text
    search = browser.find_element(By.ID, "search")
    search.clear()
    search.send_keys(product_name)
    browser.find_element(By.ID, "search-form").submit()
    WebDriverWait(browser, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".product h3 a"))
    )
    assert all(
        product_name.lower() in item.text.lower()
        for item in browser.find_elements(By.CSS_SELECTOR, ".product h3 a")
    )


def test_product_detail_opens(browser):
    browser.get(f"{BASE_URL}/")
    link = browser.find_element(By.CSS_SELECTOR, ".product h3 a")
    name = link.text
    link.click()
    assert WebDriverWait(browser, 15).until(
        EC.visibility_of_element_located((By.ID, "product-name"))
    ).text == name
    assert "/products/" in browser.current_url


def test_health_endpoint(browser):
    if not EXPECTED_VERSION:
        pytest.fail("EXPECTED_VERSION is required to verify the deployed image")
    browser.get(f"{BASE_URL}/health")
    import json
    data = json.loads(browser.find_element(By.TAG_NAME, "body").text)
    assert data["status"] == "ok"
    assert data["database"] == "ok"
    assert data["version"] == EXPECTED_VERSION


@pytest.mark.writes
def test_admin_can_login_and_add_product(browser):
    password = os.environ.get("E2E_ADMIN_PASSWORD")
    if not password:
        pytest.fail("E2E_ADMIN_PASSWORD must be configured for staging write tests")
    browser.get(f"{BASE_URL}/admin/login")
    browser.find_element(By.ID, "username").send_keys("admin")
    browser.find_element(By.ID, "password").send_keys(password)
    browser.find_element(By.ID, "login-btn").click()
    WebDriverWait(browser, 15).until(EC.url_contains("/admin/"))
    assert browser.find_elements(By.LINK_TEXT, "Add product"), "Admin login failed"

    browser.find_element(By.LINK_TEXT, "Add product").click()
    name = f"E2E test product {uuid.uuid4().hex[:8]}"
    browser.find_element(By.ID, "name").send_keys(name)
    browser.find_element(By.ID, "price").send_keys("12.50")
    browser.find_element(By.ID, "stock").clear()
    browser.find_element(By.ID, "stock").send_keys("3")
    browser.find_element(By.ID, "save-btn").click()
    WebDriverWait(browser, 15).until(
        EC.text_to_be_present_in_element((By.TAG_NAME, "body"), name)
    )
    assert name in browser.page_source
