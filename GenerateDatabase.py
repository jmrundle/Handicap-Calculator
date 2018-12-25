"""
    ********** OUTDATED ************
    CURRENT DATABASE USES DIFFERENT STRUCTURE AND IS
    A RESULT OF A VARIETY OF DIFFERENT PROGRAMS
    ********************************
    
    
    Generates a Courses database
        contains links, USGA course and slope ratings, and locations for every course in the US
    Will take probably 20 hrs to generate...  so just use the one I already (painstakingly) generated
"""

from selenium import webdriver
from selenium.webdriver.support.ui import Select
import requests
from bs4 import BeautifulSoup
import sqlite3
import time


class Generate:

    def __init__(self):
        self.connection = sqlite3.connect("Databases/Courses.db")
        self.cursor = self.connection.cursor()
        self.cursor.execute("PRAGMA EKY = 'password'")
        self.connection.execute('CREATE TABLE IF NOT EXISTS CourseNames(id INTEGER, name TEXT, state TEXT, city TEXT, latitude REAL, longitude REAL)')

        self.base_url = "https://ncrdb.usga.org/NCRDB/"

        self.browser = None  # selenium webdriver object

        self.get_browser()
        self.load_course_info()

        self.cursor.close()
        self.connection.close()

    def get_browser(self):
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        self.browser = webdriver.Chrome(
                        executable_path=r"C:\Users\Jack\Downloads\chromedriver_win32\chromedriver.exe",
                        chrome_options=options)
        self.browser.get(self.base_url)

    def load_course_info(self):
        html = BeautifulSoup(self.browser.page_source, 'lxml')
        # get list of state options
        states = list(map(lambda info: info.text, html.find_all('option')[1:]))

        for state in states:
            print(state)

            # search courses by state
            menu = self.browser.find_element_by_name("ddState")
            select = Select(menu)
            select.select_by_visible_text(state)
            menu.submit()

            html = BeautifulSoup(self.browser.page_source, 'lxml')
            courses = html.find_all('tr')[1:]

            for i, course in enumerate(courses):
                if (i+1) % 50 == 0 or i+1 == len(courses): print("{} / {}".format(i+1, len(courses)))

                # load each course info into sql database
                name, url, city, state = course.find_all('td')

                url = self.base_url + url.a["href"]
                id = int(url[57:])

                # format name in form 'Aaaa Bbbb CC'
                name = " ".join(list(map(lambda word: word[0].upper() + word[1:] if len(word) > 2 else word, name.text.split())))

                try:
                    # go to course url, and get tee info
                    teeInfo = ""
                    page = requests.get(url)
                    html = BeautifulSoup(page.text, 'lxml')
                    table = html.find("table", id="gvTee")
                    for row in table.find_all("tr")[1:]:
                        col, course_rating, slope_rating, *_, gender = map(lambda info: info.text, row.find_all("td"))
                        teeInfo += "{}:{}:{}:{}\n".format(col, course_rating, slope_rating, gender)

                    self.cursor.execute('INSERT INTO CourseNames(id, name, teeInfo, state, city) VALUES (?, ?, ?, ?, ?)',
                                        (id, name,  teeInfo, state.text, city.text))
                    self.connection.commit()

                except AttributeError:
                    pass

if __name__ == "__main__":
    start = time.time()
    jack = Generate()
    elapsed = time.time() - start
    print("Database Generation took {} hrs, {} min, {} sec".format(elapsed // 3600, elapsed // 60 - 60 * (elapsed // 3600), elapsed % 60))
