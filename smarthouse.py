#!/usr/bin/env python
"""Usage: smarthouse.py
          smarthouse.py today
          smarthouse.py rest
          smarthouse.py week
"""

import docopt
import datetime
import json
import requests


def date_to_str(d):
    return d.strftime("%Y-%m-%d")


def date_to_human_str(d):
    return d.strftime("%d.%m.%Y (%A)")


def today():
    return datetime.datetime.now()


def last_monday():
    day = datetime.datetime.now()
    while day.weekday() != 0:
        day += datetime.timedelta(-1)

    return day


def next_friday():
    day = datetime.datetime.now()
    while day.weekday() != 4:
        day += datetime.timedelta(1)

    return day


def next_sunday():
    day = datetime.datetime.now()
    while day.weekday() != 6:
        day += datetime.timedelta(1)

    return day


def get_today_dates():
    return (today(), today())


def get_rest_week_dates():
    return (today(), next_friday())


def get_whole_week_dates():
    return (last_monday(), next_sunday())


def get_url(first, last):
    return "http://www.amica.fi/modules/json/json/Index?costNumber=3498&firstDay=" + date_to_str(first) + "&lastDay=" + date_to_str(last) + "&language=fi"


def str_to_date(s):
    return datetime.datetime.strptime(s, "%Y-%m-%dT00:00:00")


def print_red(s):
    print "\033[1;31m" + s + "\033[0m"


def print_green(s):
    print "\033[1;32m" + s + "\033[0m"


def print_data(data):
    for day in data["MenusForDays"]:
        menus = day["SetMenus"]

        if day["SetMenus"]:
            print_green(date_to_human_str(str_to_date(day["Date"])))
            print "-" * 20
            print

            for menu in menus:
                if not menu["Components"]:
                    continue

                if menu["Name"]:
                    print menu["Name"] + ":"
                else:
                    print "Unknown menu:"

                for component in menu["Components"]:
                    print component

                print
        else:
            print_red(date_to_human_str(str_to_date(day["Date"])) + " CLOSED")
            print "-" * 20
            print


if __name__ == "__main__":
    arguments = docopt.docopt(__doc__)

    if arguments["week"]:
        first, last = get_whole_week_dates()
    elif arguments["rest"]:
        first, last = get_rest_week_dates()
    else:
        first, last = get_today_dates()

    url = get_url(first, last)

    print "Fetching " + url
    print

    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()

        # Filter dates which are not requested, api seems to now days always return the whole week
        def is_before_date(menu):
            date = datetime.datetime.strptime(menu["Date"], "%Y-%m-%dT%H:%M:%S")
            return date <= last
        data["MenusForDays"] = filter(lambda x: is_before_date(x), data["MenusForDays"])

        print_data(data)
    else:
        print "Error fetching data!"
