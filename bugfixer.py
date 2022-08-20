#!/usr/bin/python3

# parolottero-languages
# Copyright (C) 2020-2022 Salvo "LtWorf" Tomaselli
#
# parolottero-languages is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# author Salvo "LtWorf" Tomaselli <tiposchi@tiscali.it>


# This is copy pasted from typedload's example.py

from datetime import datetime
import json
from typing import *
import urllib.request
from pathlib import Path
import subprocess

import typedload.dataloader


def get_data() -> Any:
    """
    Use the github API to get issues information
    """
    url = 'https://api.github.com/repos/ltworf/parolottero-languages/issues'
    with open('.token', 'rt') as f:
        token = f.readline().strip()
    req = urllib.request.Request(url)
    req.add_header('Accept', 'application/vnd.github+json')
    req.add_header('Authorization', f'token {token}')
    with urllib.request.urlopen(req) as f:
        return json.load(f)


class User(NamedTuple):
    login: str


class Issue(NamedTuple):
    number: int
    title: str
    body: str
    user: User
    created_at: datetime
    updated_at: datetime

    @property
    def autoissue(self) -> bool:
        return \
            self.title.startswith('User report for ') and \
            'id: ' in self.body and \
            'Item count: ' in self.body and \
            'Language: ' in self.body

    def _prefix(self, prefix: str) -> Iterable[str]:
        for l in self.body.split('\n'):
            if l.startswith(prefix):
                yield l

    def diff(self) -> Iterable[str]:
        yield from self._prefix('+')
        yield from self._prefix('-')

    @property
    def language(self) -> str:
        return next(self._prefix('Language: ')).split(' ', 1)[-1]

    @property
    def extrafile(self) -> str:
        a = {
            'Sicilianu': 'extralist/sicilian.extra',
            'Italiano': 'extralist/italian.extra',
        }
        return Path(a[self.language])

    @property
    def machineid(self) -> str:
        return next(self._prefix('id: ')).split(' ', 1)[-1]

    def __str__(self) -> str:
        return f'#{self.number}: {self.language}\nAutomatic: {self.autoissue} From machine: {self.machineid}\n'


def interactive_fix_issue(issue: Issue) -> None:
    with issue.extrafile.open('rt') as f:
        extras = {i.strip() for i in f}

    print(f'===== Doing extra words for {issue.language}')
    for diff in issue.diff():
        reply = input(f'Is this valid [yN]? {diff}')
        if reply in {'y', 'Y', 'YES', 'yes'}:
            extras.add(diff)

    with issue.extrafile.open('wt') as f:
        wlist = list(extras)
        wlist.sort()
        for l in extras:
            print(l, file=f)

    subprocess.check_call(['git', 'add', issue.extrafile])
    subprocess.check_call(['git', 'commit', '-m', f'Fix user reported mistakes\nCloses: #{issue.number}', issue.extrafile])
    # TODO close the issue even if all changes are rejected


def main():
    data = get_data()


    # Github returns dates like this "2016-08-23T18:26:00Z", which are not supported by typedload
    # So we make a custom handler for them.
    loader = typedload.dataloader.Loader()
    loader.handlers.insert(0, (# Make the new handler first so it overrides the current handler for datetime
        lambda t: t == datetime,
        lambda l, v, t: datetime.fromisoformat(v[:-1])
    ))


    # We know what the API returns so we can load the json into typed data
    issues = loader.load(data, List[Issue])
    for i in issues:
        if i.autoissue:
            interactive_fix_issue(i)


if __name__ == '__main__':
    main()
