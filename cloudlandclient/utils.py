# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from prettytable import PrettyTable
import hashlib


def pretty(head, body):
    if head and body:
        if body[0] != '[' or '!' in body:
            head = 'RESULT'
        x = PrettyTable(head.split('|'))
        body = body.replace('[', '').replace(
            ']', '').replace('"', '')
        if body:
            lines = body.split(',')
            for line in lines:
                if line:
                    try:
                        x.add_row(line.split('|'))
                    except Exception:
                        print body
                        raise
        print x


# Decorator for cli-args
def arg(*args, **kwargs):
    def _decorator(func):
        # Because of the semantics of decorator composition if we just append
        # to the options list positional options will appear to be backwards.
        func.__dict__.setdefault('arguments', []).insert(0, (args, kwargs))
        return func
    return _decorator


def sha1sum(data):
    if is_not_sha1sum(data):
        return hashlib.sha1(data).hexdigest()
    return data


def is_not_sha1sum(data):
    if data:
        data = data.lower()
        if len(data) != 40:
            return True
        for c in data:
            if c not in '0123456789abcdedf':
                return True
    return False
