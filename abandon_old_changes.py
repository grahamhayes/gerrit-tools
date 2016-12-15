#!/usr/bin/env python

from pygerrit.rest import GerritRestAPI
import datetime
import humanize
from prettytable import PrettyTable
import os
import warnings
warnings.filterwarnings("ignore")
from requests.auth import HTTPBasicAuth, HTTPDigestAuth

GERRIT_TIMESTAMP_FMT = '%Y-%m-%d %H:%M:%S'
QUERY = 'status:open+(label:Code-Review<=-1+OR+label:Verified<=-1)+'
DAYS = 45
PROJECTS_LIST = [
    'designate',
    'designate-dashboard',
    'python-designateclient',
    'designate-specs'
]

USERS = {}

MSG = "As this review has not been updated for more than %s days, with a "\
      "negative vote, we are abandoning it for now. Feel free to reactivate "\
      "the review by pressing the restore button and leaving a 'recheck' "\
      "comment to get fresh test results." % DAYS


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


def process_project(project):

    changes = rest.get("/changes/?q=%sproject:openstack/%s" % (QUERY, project))

    cut_off_date = datetime.datetime.now() - datetime.timedelta(days=DAYS)

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
        if parse_gerrit_time(change['updated']) < cut_off_date:

            # rest.post("/changes/%s/abandon" % change['id'],
            #           data=MSG)

            ct.add_row(format_dict(change))

    print('Changes Abandoned in openstack/%s' % project)

    print(ct)
user = os.environ['GERRIT_USER']
pwd = os.environ['GERRIT_PWD']
auth = HTTPDigestAuth(user, pwd)

rest = GerritRestAPI(url='https://review.openstack.org', auth=auth)

for project in PROJECTS_LIST:
    process_project(project)
