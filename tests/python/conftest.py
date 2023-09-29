import pytest
import requests
from os import environ
from datetime import datetime
from selenium import webdriver
from selenium.common.exceptions import WebDriverException

import urllib3
urllib3.disable_warnings()


def edge_options(platform_name):
    options = webdriver.EdgeOptions()
    options.set_capability('platformName', platform_name)
    return options


def firefox_options(platform_name):
    options = webdriver.FirefoxOptions()
    options.set_capability('platformName', platform_name)
    return options


def chrome_options(platform_name):
    options = webdriver.ChromeOptions()
    options.set_capability('platformName', platform_name)
    return options

def safari_options(platform_name):
    options = webdriver.SafariOptions()
    options.set_capability('platformName', platform_name)
    return options

selenium_endpoint = environ.get('SE_ENDPOINT', 'localhost:4444')
tunnel_name = environ.get('SAUCE_TUNNEL_NAME')
build_tag = f'dockercon23_{datetime.now().strftime("%d.%m.%Y-%H:%M")}'

desktop_browsers = []

if tunnel_name is not None:
    desktop_browsers.append(safari_options('macOS 13'))
    for platform in ['Windows 11', 'macOS 13']:
        desktop_browsers.append(chrome_options(platform))
    #     desktop_browsers.append(edge_options(platform))
        # desktop_browsers.append(firefox_options(platform))

# platform = 'Linux'
# desktop_browsers.append(edge_options(platform))
# desktop_browsers.append(chrome_options(platform))
# desktop_browsers.append(firefox_options(platform))


@pytest.fixture(params=desktop_browsers)
def desktop_web_driver(request):
    test_name = request.node.name
    options = request.param
    grid_url = "http://{}/wd/hub".format(selenium_endpoint)

    options.set_capability('se:name', test_name)
    options.set_capability('se:recordVideo', True)
    if tunnel_name is not None:
        options.set_capability('sauce:build', build_tag)
        options.set_capability('sauce:name', test_name)
        options.set_capability('sauce:tunnelIdentifier', tunnel_name)

    browser = webdriver.Remote(
        command_executor=grid_url,
        options=options,
        keep_alive=True
    )

    browser.maximize_window()

    if browser is None:
        raise WebDriverException("Never created!")

    yield browser

    # Teardown starts here
    if 'sauce' in selenium_endpoint:
        # report results
        # use the test result to send the pass/fail status to Sauce Labs
        sauce_result = "failed" if request.node.rep_call.failed else "passed"
        browser.execute_script("sauce:job-result={}".format(sauce_result))
    browser.quit()


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    # this sets the result as a test attribute for Sauce Labs reporting.
    # execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()

    # set an report attribute for each phase of a call, which can
    # be "setup", "call", "teardown"
    setattr(item, "rep_" + rep.when, rep)


def pytest_sessionstart(session):
    """
    Called after the Session object has been created and
    before performing collection and entering the run test loop.
    """
    print("Cleaning database...")
    sut_endpoint = environ.get('SUT_ENDPOINT', 'http://localhost:3000')
    response = requests.delete(f'{sut_endpoint}/items')
    assert response.status_code == 200
