import requests
import time
from os import environ
from faker import Faker
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

sleep_time = environ.get('SLEEP_DEMO_TIME', 0)
fake = Faker()
sut_endpoint = environ.get('SUT_ENDPOINT', 'http://localhost:3000')


def test_add_item(desktop_web_driver):
    time.sleep(sleep_time)

    desktop_web_driver.get(sut_endpoint)

    text = fake.country()

    wait = WebDriverWait(desktop_web_driver, 30)
    input_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[data-testid="new-item-text"]')))
    input_field.send_keys(text)

    desktop_web_driver.find_element(By.CSS_SELECTOR, 'button[data-testid="new-item-button"]').click()

    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f'div[data-testid="{text}"]')))

    time.sleep(sleep_time)

    expected = desktop_web_driver.find_elements(By.CSS_SELECTOR, f'div[data-testid="{text}"]')
    assert len(expected) == 1


def test_toggle_item(desktop_web_driver):
    text = fake.country()

    create_item_with_api(text)

    time.sleep(sleep_time)

    desktop_web_driver.get(sut_endpoint)

    wait = WebDriverWait(desktop_web_driver, 30)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f'div[data-testid="{text}"]')))

    toggle_button = wait.until(
        AriaLabelInToggleButtonItemHasValue(f'div[data-testid="{text}"]', 'Mark item as complete'))
    toggle_button.click()

    desktop_web_driver.find_element(By.CSS_SELECTOR, f'div[data-testid="{text}"]')

    wait.until(AriaLabelInToggleButtonItemHasValue(f'div[data-testid="{text}"]', 'Mark item as incomplete'))

    time.sleep(sleep_time)


def test_remove_item(desktop_web_driver):
    text = fake.country()

    create_item_with_api(text)

    time.sleep(sleep_time)

    desktop_web_driver.get(sut_endpoint)


    wait = WebDriverWait(desktop_web_driver, 30)
    item = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f'div[data-testid="{text}"]')))

    item.find_element(By.CSS_SELECTOR, 'button[data-testid="remove-item"]').click()

    wait.until(EC.invisibility_of_element((By.CSS_SELECTOR, f'div[data-testid="{text}"]')))

    time.sleep(sleep_time)


def create_item_with_api(text):
    payload = {'name': text}
    response = requests.post(f'{sut_endpoint}/items', json=payload)
    assert response.status_code == 200
    response_body = response.json()
    assert response_body['name'] == text


class AriaLabelInToggleButtonItemHasValue:
    def __init__(self, item_locator, aria_label_value):
        self._item_locator = item_locator
        self._aria_label_value = aria_label_value

    def __call__(self, driver):
        item = driver.find_element(By.CSS_SELECTOR, self._item_locator)
        toggle_button = item.find_element(By.CSS_SELECTOR, 'button[data-testid="toggle-item"]')
        aria_label = toggle_button.get_attribute('aria-label')
        if aria_label == self._aria_label_value:
            return toggle_button
        else:
            return False
