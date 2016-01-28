#!/usr/bin/env python

from pygerrit.rest import GerritRestAPI
import datetime
import humanize
from prettytable import PrettyTable

import warnings
warnings.filterwarnings("ignore")

GERRIT_TIMESTAMP_FMT = '%Y-%m-%d %H:%M:%S'
QUERY = 'projects:openstack/oslo+label:Code-Review=-2'

USERS = {}


def parse_gerrit_time(value):
    """Parses a Gerrit-formatted timestamp into a Python 'datetime'.
    From Gerrit API documentation:
    `Timestamps are given in UTC and have the format
    "yyyy-mm-dd hh:mm:ss.fffffffff" where "ffffffffff" indicates the
    nanoseconds.`
    Args:
    value: (str) the value to parse
    Return: A Python 'datetime' object parsed from 'value'
    """
    parts = value.split('.')
    dt = datetime.datetime.strptime(parts[0], GERRIT_TIMESTAMP_FMT)
    if len(parts) > 1:
        dt += datetime.timedelta(
            microseconds=int(float('0.%s' % parts[1]) * 1000000.0))
    return dt


def format_date(date):
    return "%s (%s)" % (
        humanize.naturaldate(parse_gerrit_time(date)),
        humanize.naturaldelta(parse_gerrit_time(date)),
    )


def get_user_name(uid):
    if uid in USERS:
        return USERS[uid]
    else:
        user = rest.get("accounts/%s/name" % uid)
        USERS[uid] = user
        return user


def format_dict(change):
    return [
        get_user_name(change['owner']['_account_id']),
        'https://review.openstack.org/#/c/%s' % change['_number'],
        change['subject'],
        format_date(change['created']),
        format_date(change['updated']),
        change['mergeable'],
    ]


def print_project():

    changes = rest.get("/changes/?q=%s" % QUERY)

    ct = PrettyTable([
        "Name",
        "Link",
        "Title",
        "Created",
        "Updated",
        "Mergeable"
    ])

    ct.align["Name"] = "l"
    ct.align["Title"] = "l"
    ct.align["Link"] = "l"
    ct.align["Created"] = "l"
    ct.align["Updated"] = "l"
    ct.align["Mergeable"] = "l"

    for change in changes:
        ct.add_row(format_dict(change))

    print('Changes -2\'d in olso repos')

    print(ct)

rest = GerritRestAPI(url='https://review.openstack.org')

print_project()
