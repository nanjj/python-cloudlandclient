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

def download(url):
    filename = url.split('/')[-1]
    res = requests.get(url, stream=True)
    length = int(res.headers.get('content-length'))
    position = 0
    m=1024*1024
    with open(filename, 'wb') as f:
        for chunk in res.iter_content(chunk_size=2048):
            if chunk:
                f.write(chunk)
                f.flush()
                position = position + len(chunk)
                sys.stdout.write(
                    '\rDownloading %(filename)s, size %(length)sM, received %(position)sM...' %
                    {'filename': filename,
                     'position': (position/m),
                     'length': length/m})


def loads(body):
    if body:
        return list(json.loads(body))
    return []

def pretty(head, body):
    if head and body:
        x = PrettyTable(head.split('|'))
        if body:
            lines = loads(body)
            code = lines.pop()
            if code != 0:
                print('\n'.join(lines))
                return
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
