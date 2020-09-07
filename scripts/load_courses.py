#!/usr/bin/env python3

"""
load_courses.py
    fetches a list of ID's associated with every course in a given country

Usage:
    ./load_courses.py [COUNTRY_KEY]

Output:
    11318
    11385
    11323
    11399
    11328
    11364
    ...

Creator:
    Jack Rundle
"""

import selenium
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
from config import Config
import sys


def get_driver(url, path=Config.CHROME_DRIVER_PATH):
    """Create a Selenium webdriver objects pointing to a specified URL"""
    # make browser session hidden
    options = selenium.webdriver.ChromeOptions()
    options.add_argument('headless')

    driver = selenium.webdriver.Chrome(
        executable_path=path,
        options=options)

    driver.get(url)

    return driver


def get_state_options(driver, country_key="USA"):
    """returns a generator of states in a country"""
    # select option in Country dropdown
    country_selector = Select(driver.find_element_by_id("ddCountries"))
    country_selector.select_by_value(country_key)

    # find State dropdown
    state_selector = Select(driver.find_element_by_id("ddState"))

    options = [
        option.get_attribute("value") for option in state_selector.options
    ]

    return filter(lambda o: o.strip() != "", options)


def get_course_ids_for_state(driver, state_key):
    """search for courses in a given state"""
    # select option in State dropdown
    selector = Select(driver.find_element_by_id("ddState"))
    selector.select_by_value(state_key)
    driver.find_element_by_name("myButton").click()

    # load courses table
    soup = BeautifulSoup(driver.page_source, "html.parser")
    table = soup.find(id="gvCourses")
    rows = table.find_all("tr")[1:] if table else []

    # extract ids from table
    for row in rows:
        club, course, city, state = row.find_all("td")
        course_id = course.a["href"].split('=')[1]
        yield course_id


def dump_info(info, stream):
    for row in info:
        stream.write(row + '\n')


def main():
    driver = get_driver(Config.URL)

    country_key = "USA"
    if len(sys.argv) > 1:
        country_key = sys.argv[1]

    states = get_state_options(driver, country_key=country_key)
    if not states:
        print("Invalid Country Key.  Failed to load options.", file=sys.stderr)

    for i, state in enumerate(states):
        ids = get_course_ids_for_state(driver, state)
        dump_info(ids, sys.stdout)


if __name__ == "__main__":
    main()
