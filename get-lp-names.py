#!/usr/bin/env python

from prettytable import PrettyTable
import sys
from launchpadlib.launchpad import Launchpad


launchpad = Launchpad.login_anonymously('just testing', 'production')

issues = {}

table = PrettyTable()

table.field_names = ["Number", "Bug", "Link"]

for line in sys.stdin:
    print "looking up %s" % line

    try:
        bug_number = int(line)
        issues[line] = launchpad.bugs[line]
    except Exception:
        pass


for k, v in issues.iteritems():
    table.add_row([k, v.title, v.web_link])

print table
