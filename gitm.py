#!/usr/bin/python3

import os
from os.path import *
import re
import json
import yaml
import ago
import sys
import argparse
import inspect
from datetime import datetime
from prettytable import PrettyTable
from git.exc import InvalidGitRepositoryError, GitCommandError
from munch import Munch
import git
from git.repo.base import Repo

args = None


def warn(a):
    print(a, file=sys.stderr)


def log(*_args, **kwargs):
    global args
    if args.verbose:
        print("%s:%d" % (inspect.stack()[1].filename,
                         inspect.stack()[1].lineno),
              str(*_args).rstrip(), file=sys.stderr, **kwargs)


def git_get(g):
    m = Munch()
    r = Repo(g)
    m.time_sec = r.head.commit.committed_date
    m.datetime = r.head.commit.committed_datetime
    m.sha = r.commit('HEAD').hexsha
    m.hash = r.git.rev_parse('--short', 'HEAD')
    m.msg = r.head.object.message.split('\n')[0]
    m.count = int(r.git.rev_list('--count', 'HEAD'))
    cr = r.config_reader()
    if islink(g + '/.git/config'):
        m.linked = dirname(relpath(realpath(g + '/.git/config')))

    if cr.has_option('core', 'worktree'):
        m.worktree = cr.get_value('core', 'worktree')
    m.revision = r.git.describe('--always')
    m.branches = r.branches
    if not r.head.is_detached:
        m.branch = r.active_branch.name
    if r.remotes:
        m.remote = r.remotes[0].name
        m.url = r.remotes[0].url
    return m


def short(s):
    if len(s) > 16:
        return s[:15] + '…'
    return s


def git_tree(*argv):

    parser = argparse.ArgumentParser()
    parser.add_argument('--table', nargs='?', default=argparse.SUPPRESS)
    parser.add_argument('--sha', nargs='?', default=argparse.SUPPRESS,
                        help='print sha hashes in format of sha1sum utility')
    parser.add_argument('--csv', nargs='?', default=argparse.SUPPRESS)
    parser.add_argument('--json', nargs='?', default=argparse.SUPPRESS)
    parser.add_argument('--export', nargs='?', default=argparse.SUPPRESS)
    parser.add_argument('--compare', nargs='?', default=argparse.SUPPRESS)
    parser.add_argument('--import', nargs='?', default=argparse.SUPPRESS)
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('--standalone_remote', action='store_true')
    parser.add_argument('d', nargs='?', default='.')
    parser.add_argument('rest', nargs='?')
    global args
    args = parser.parse_args()
    status = {}

    if 'csv' in args:
        if not args.csv:
            args.csv = "status.csv"
        if args.csv == '-':
            csv = sys.stdout
        else:
            csv = open(args.csv, "w")

    def print_csv(p, st):
        print("%s, %s, %d, %s, %s, %s, %s"
              % (p, st.datetime, st.count, st.sha, '"%s"' % (st.msg),
                  st.get('worktree', st.get('linked', 'standalone')),
                  st.get('remote', '') + ' ' + st.get('url', 'local')))

    def print_sha(p, st):
        print("%s  %s" % (st.sha, p))

    def table_add_row(p, st):
        r = {}
        r['dir'] = p
        r.update(dict(st))
        r['msg'] = short(r['msg'])
        r['ago'] = ago.human(datetime.fromtimestamp(int(st.time_sec)),
                             precision=2, past_tense='{}', future_tense='{}')
        if 'branch' in r:
            r['branch'] = short(r['branch'])
        tab.add_row([r[f] if f in r else '' for f in fields])

    def git_import(d, s):
        if 'import' not in args:
            return
        if not exists(d + '/.git'):
            Repo.clone_from(s.url, d)
        r = Repo(d)
        if 'branch' in s:
            r.git.checkout(s.branch)
        if s.sha != r.commit('HEAD').hexsha:
            r.git.checkout(s.sha)
        s.state = 'imported'
        # assure same
        if s.sha == r.commit('HEAD').hexsha:
            s.state += ' same'

    def git_compare(d, s):
        same = False
        s = Munch(s)
        if not exists(d + '/.git'):
            s.state = 'absent'
            log(d)
        else:
            r = Repo(d)
            if s.sha != r.commit('HEAD').hexsha:
                s.state = 'different'
            elif (not r.head.is_detached
                    and r.active_branch.name == s.get('branch', '')):
                print(d, r.active_branch.name, s.get('branch', ''))
                s.state = 'same'
                same = True
            else:
                s.state = 'same detached'
        if not same:
            git_import(d, s)
        out(d, s)
        status[d] = s

    compare = out = tab = None

    if 'compare' in args:
        if not args.compare:
            args.compare = "status.yaml"
            if not isfile(args.compare):
                args.compare = "status.json"
        log(args.compare)
        with open(args.compare) as f:
            if args.compare.endswith('.yaml'):
                compare = Munch(yaml.load(f))
            if args.compare.endswith('.json'):
                compare = Munch(json.load(f))
    else:
        if isfile('status.yaml'):
            with open('status.yaml') as f:
                compare = Munch(yaml.load(f))

    out = print_sha if 'sha' in args else out
    out = print_csv if 'csv' in args else out

    if not out:  # default output is table
        fields = ("dir ago count hash msg branch remote url linked state"
                  .split())
        tab = PrettyTable(fields, border=False, header=False, align="l")
        tab.align = "l"
        out = table_add_row

    if 'compare' in args and compare and 'status' in compare:
        for d, s in compare['status'].items():
            try:
                git_compare(d, s)
            except (InvalidGitRepositoryError, GitCommandError,
                    ValueError) as e:
                warn('Error: ' + str(e) +
                     (': ' + d if d not in str(e) else ''))

    def scan(d):
        for path, dirs, files in os.walk(d):
            (dir, base) = split(path)
            p = re.sub(r'^\.\/', '', path)
            log(p)
            if base in ['.git', 'tmp']:
                dirs[:] = []  # prune
                continue
            if not ('.git' in files or '.git' in dirs):
                continue

            try:
                st = git_get(p)
                # Get only remote and standalone if requested
                if (args.standalone_remote and
                        ('remote' not in st
                            or 'linked' in st
                            or 'worktree' in st)):
                    continue
                status[p] = dict(st)
                if compare and p not in compare.status:
                    # only here and not in compare
                    st.state = 'undesired'
                    out(p, st)
                if not compare:
                    out(p, st)
            except (InvalidGitRepositoryError, GitCommandError, ValueError) as e:
                warn('Error: ' + str(e) + (': ' + p if p not in str(e) else ''))

    if isdir(args.d):
        scan(args.d)
    elif args.rest:
        print(args.d, args.rest)
        print("git -C " + dirname(args.rest) + args.d + basename(args.rest))
        os.system("git -C " + dirname(args.rest) + " " + args.d + " " + basename(args.rest))
    else:
        if compare and 'status' in compare:
            for d, s in compare['status'].items():
                print(d)
                os.system("git -C " + d + " " + args.d + " ")
        status = compare.status

    if tab:
        print(tab)
    if 'json' in args:
        if not args.json:
            args.json = "status.json"
        if args.json == '-':
            f = sys.stdout
        else:
            f = open(args.json, "w")
        f.write(json.dumps({'status': status}, indent=4, default=str) + "\n")

    if 'export' in args:
        if not args.export:
            args.export = "status.yaml"
        if args.export == '-':
            f = sys.stdout
        else:
            f = open(args.export, "w")
        f.write(yaml.dump({'status': status},
                default_flow_style=False, default_style=''))
    return ''


if __name__ == "__main__":
    git_tree()
