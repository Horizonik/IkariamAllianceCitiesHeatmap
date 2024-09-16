import json
import os
from typing import Any
import re
import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup

# Configuration
DATA_FOLDER = '../data/'
CONFIG_FILE = '../user_config.json'


# Initialize the Selenium WebDriver
def init_selenium_driver():
    service = FirefoxService(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service)
    return driver


def load_json() -> dict:
    if not os.path.exists(CONFIG_FILE):
        raise FileNotFoundError(f"{CONFIG_FILE} not found.")

    with open(CONFIG_FILE, 'r') as file:
        config = json.load(file)

    return config


def fetch_or_load_data(alliance_name: str) -> tuple[Any, bool]:
    """Fetch data from the site or return cached data if available"""
    file_path = os.path.join(DATA_FOLDER, f'{alliance_name}.json')

    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file), True

    driver = init_selenium_driver()
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
