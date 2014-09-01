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
import json
import requests
import sys
import os

from cloudlandclient.exc import SomeThingWrong


def download(url):
    filename = url.split('/')[-1]
    res = requests.get(url, stream=True)
    length = int(res.headers.get('content-length'))
    position = 0
    m = 1024*1024
    previous = 0
    current = 0
    with open(filename, 'wb') as f:
        for chunk in res.iter_content(chunk_size=4096):
            if chunk:
                f.write(chunk)
                f.flush()
                position = position + len(chunk)
                current = position/m
                if current > previous:
                    sys.stdout.write(
                        '\rDownloading %(filename)s, total %(length)sM, received %(position)sM' %
                        {'filename': filename,
                         'position': position/m,
                         'length': length/m})
                    sys.stdout.flush()
                    previous = current


def loads(body):
    if body:
        lines = list(json.loads(body))
    if not lines or lines.pop() != 0:
        raise SomeThingWrong(message=body)
    return lines


def dumps(data):
    return json.dumps(data)


def cut(lines, delim='|', field=1):
    result = []
    for line in lines:
        if line:
            result.append(line.split('|')[field-1])
    return result


def pretty(head, body):
    if head and body:
        x = PrettyTable(head.split('|'))
        if body:
            lines = loads(body)
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


def read_file(filename):
    if os.path.isfile(filename):
        with open(filename) as f:
            return f.read()
    return filename
