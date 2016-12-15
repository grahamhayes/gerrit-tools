#!/usr/bin/env python

from pygerrit.rest import GerritRestAPI
import datetime
import humanize
from prettytable import PrettyTable
import pprint
import yaml

import warnings
warnings.filterwarnings("ignore")

GERRIT_TIMESTAMP_FMT = '%Y-%m-%d %H:%M:%S'
PROJECTS_LIST = [
    'designate',
    'designate-dashboard',
    'python-designateclient',
    'designate-specs'
]
rest = GerritRestAPI(url='https://review.openstack.org')
USERS = {}


def query_projects(query):
    changes = []
    for project in PROJECTS_LIST:
        changes = changes + rest.get(
            "/changes/?q=%s+project:openstack/%s" % (query, project))

    return changes


def get_all_minus_one_reviews():
    return query_projects("status:open+label:Code-Review=-1")


def get_all_minus_two_reviews():
    return query_projects("status:open+label:Code-Review=-2")


def get_user_name(uid):
    if uid in USERS:
        return USERS[uid]
    else:
        user = rest.get("accounts/%s/name" % uid)
        USERS[uid] = user
        return user


def get_detailed_change(change_id):
    return rest.get(
            "/changes/%s/detail" % change_id)


def populate_detailed_changes(changes):
    for index, change in enumerate(changes):
        changes[index] = get_detailed_change(change["id"])
    return changes


def populate_user(changes):
    for index, change in enumerate(changes):
        changes[index]["owner"]["name"] = get_user_name(
            change["owner"]["_account_id"])
    return changes

#pprint.pprint(populate_detailed_changes(get_all_minus_one_reviews()))
#pprint.pprint(populate_user(get_all_minus_two_reviews()))


print yaml.safe_dump(populate_detailed_changes(get_all_minus_one_reviews()), default_flow_style=False)
