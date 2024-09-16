import json
import os
from typing import Any
import re
import time
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.chrome.service import Service as BraveService
from selenium.webdriver.chrome.service import Service as ChromiumService
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from selenium.webdriver.chrome import service
from webdriver_manager.opera import OperaDriverManager
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager

from bs4 import BeautifulSoup

# Configuration
DATA_FOLDER = '../data/'


# Initialize the Selenium WebDriver
def init_selenium_driver(browser_type: str):
    """Init the selenium driver according to the browser type the user has selected in the config"""
    browser_type = browser_type.lower()

    if browser_type == "chrome":
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

    elif browser_type == "chromium":
        driver = webdriver.Chrome(
            service=ChromiumService(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()))

    elif browser_type == "firefox":
        driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))

    elif browser_type == "brave":
        driver = webdriver.Chrome(service=BraveService(ChromeDriverManager(chrome_type=ChromeType.BRAVE).install()))

    elif browser_type == "edge":
        driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()))

    elif browser_type == "opera":
        webdriver_service = service.Service(OperaDriverManager().install())
        webdriver_service.start()

        driver = webdriver.Remote(webdriver_service.service_url, webdriver.DesiredCapabilities.OPERA)

    else:
        raise ValueError(f"Unsupported browser type: {browser_type}")

    return driver


def load_json_from_file(file_location: str) -> Any:
    if not os.path.exists(file_location):
        raise FileNotFoundError(f"{file_location} not found.")

    with open(file_location, 'r') as file:
        config = json.load(file)

    return config


def validate_alliance_name(alliance_name: str):
    if not alliance_name:
        raise ValueError("Alliance name not found in config.")


def validate_browser_type(browser_type: str) -> bool:
    """Checks that the browser type provided in the config is valid, raises an exception if not"""

    # Valid browser types
    supported_browsers = {'chrome', 'opera', 'chromium', 'firefox', 'brave', 'edge'}

    # Validate the browser type
    if browser_type.lower() not in supported_browsers:
        raise ValueError(
            f"Browser type is not supported: '{browser_type}'. Change it to one of the following: {supported_browsers}.")

    return True


def fetch_or_load_data(alliance_name: str, browser_type: str, load_from_cache_if_possible: bool = True) -> tuple[Any, bool]:
    """Fetch data from the site or return cached data if available"""
    file_path = os.path.join(DATA_FOLDER, f'{alliance_name}.json')

    if os.path.exists(file_path) and load_from_cache_if_possible:
        with open(file_path, 'r') as file:
            return json.load(file), True

    driver = init_selenium_driver(browser_type)
    all_coordinates = []
    page = 1
    while True:
        url = f'https://ikalogs.ru/tools/map/?server=2&world=57&state=&search=ally&allies[1]={alliance_name}&allies[2]=&allies[3]=&allies[4]=&nick={alliance_name}&ally=&island=&city=&x=&y=&page={page}&limit=100'
        driver.get(url)
        time.sleep(5)

        html_content = driver.page_source
        coordinates_list = parse_raw_data_into_coordinates_list(html_content)

        if not coordinates_list:
            break

        all_coordinates.extend(coordinates_list)
        page += 1

    driver.quit()
    save_data_to_file(alliance_name, all_coordinates)

    return all_coordinates, False


def parse_raw_data_into_coordinates_list(html_content) -> list:
    """Parse HTML content to extract coordinates"""
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.select_one('table.rich-table.map_results')

    if not table:
        return []

    rows = table.find_all('tr')
    coordinates_list = []

    for row in rows[1:]:
        cols = row.find_all('td')
        if len(cols) >= 9:
            coordinates = cols[4].text.strip()
            coord_match = re.match(r"\[(\d+):(\d+)\]", coordinates)
            if coord_match:
                x = int(coord_match.group(1))
                y = int(coord_match.group(2))
                coordinates_list.append((x, y))

    return coordinates_list


def save_data_to_file(alliance_name: str, coordinates_list: list):
    os.makedirs(DATA_FOLDER, exist_ok=True)
    file_path = os.path.join(DATA_FOLDER, f'{alliance_name}.json')

    with open(file_path, 'w') as file:
        json.dump(coordinates_list, file)
