#!/usr/bin/env python3

"""
get_course_info.py
    gets info associated with a given course ID, then saves it to a local DynamoDB

Usage:
    ./get_course_info [-s] [-w WORKERS]

Output:
    None

Creator:
    Jack Rundle
"""

from bs4 import BeautifulSoup
import requests

import asyncio
import concurrent.futures

from time import time
import sys

from config import Config


def wrapper(args):
    return get_course_info(*args)


def get_course_info(course_id, session):
    """gets tees for a courseId"""
    # load course's page
    s = time()
    url = f"{Config.URL}{Config.COURSE_ENDPOINT}?CourseID={course_id}"
    resp = session.get(url)

    timing = time() - s
    soup = BeautifulSoup(resp.text, "html.parser")

    # load course info
    course_info_table = soup.find(id="gvCourseTees")
    try:
        row = course_info_table.find_all("tr")[1].find_all("td")
        course, club = row[0].text.split(" - ")
        city = row[1].text
        state = row[1].text

        course_info = {
            "course_id": course_id,
            "club_name": course,
            "course_name": club,
            "city": city,
            "state": state
        }

    except (IndexError, AttributeError):
        return

    # load tee table
    tee_table = soup.find(id="gvTee")
    rows = tee_table.find_all("tr")[1:] if tee_table else []

    # extract tee info from each row
    tees = []
    for row in rows:
        color, gender, par, _, bogey, _, front, back = map(lambda info: info.text.strip(), row.find_all("td"))

        front, back = front.split('/'), back.split('/')

        tees.append({
            "tee_name": color,
            "gender": gender,
            "par": par,
            "front_cr": front[0].strip(),
            "front_sr": front[1].strip(),
            "back_cr": back[0].strip(),
            "back_sr": back[1].strip(),
            "bogey_rating": bogey
        })

    course_info["tees"] = tees

    save_course_info(course_info)
    return timing
    # return course_info


def save_course_info(info):
    # save to database
    print(info)
    """
    courses.insert_one(info["course"])
    tees.insert_many(info["tees"])
    """


def process(info_list, count):
    print(f"Average Load Time: {sum(info_list) / count:.2f}")


if __name__ == "__main__":
    use_concurrency = True
    workers = 30

    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]

        if arg == "-s":
            use_concurrency = False
        elif arg == "-w":
            if i + 1 != len(sys.argv):
                workers = int(sys.argv[i + 1])
                i += 1

        i += 1

    with requests.Session() as session:
        ids = []
        for line in sys.stdin.readlines():
            ids.append(line.rstrip())

        s = time()

        if use_concurrency:
            params = (
                (id, session) for id in ids
            )
            with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
                info_list = executor.map(wrapper, params)

        else:
            info_list = [
                get_course_info(id, session) for id in ids
            ]
        process(info_list, len(ids))
        print(f"    Total Time: {time() - s:.2f}")
