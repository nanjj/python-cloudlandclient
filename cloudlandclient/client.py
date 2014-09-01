import logging
import requests
import utils
import tempfile
import time
import os.path as path
import pickle

logger = logging.getLogger(__name__)


class CloudlandClient:
    def __init__(self, endpoint, username, password):
        self.endpoint = endpoint
        self.cookies = None
        self.login(username, password)

    def post(self, data):
        logger.info(data)
        result = requests.post(self.endpoint, data=data, cookies=self.cookies)
        logger.info(result.text)
        return result

    def get(self, params):
        logger.info(params)
        result = requests.get(
            self.endpoint, params=params, cookies=self.cookies)
        logger.info(result.text)
        return result

    @property
    def cpath(self):
        return path.join(tempfile.gettempdir(), 'cloudland.cookies')

    def load_cookies(self):
        cpath = self.cpath
        if not path.isfile(cpath):
            return None
        with open(cpath, 'r') as cfile:
            cookies = pickle.load(cfile)
        if cookies:
            for cookie in cookies:
                if cookie.is_expired():
                    logger.info('Cookie %s is expired.' % cookie)
                    return None
        return cookies

    def dump_cookies(self):
        cookies = self.cookies
        for cookie in cookies:
            cookie.expires = time.time() + 6000 - 10
        logger.info(self.cpath)
        with open(self.cpath, 'w+') as cfile:
            pickle.dump(cookies, cfile)

    def test_cookies(self, cookies):
        result = False
        self.cookies = cookies
        if cookies:
            if 'You need to login before proceed!' not in self.vm_list():
                result = True
        return result

    def login(self, username, password):
        cookies = self.load_cookies()
        if self.test_cookies(cookies):
            return
        password = utils.sha1sum(password)
        data = {'username': username, 'sha1': password, 'op': 'login'}
        r = self.post(data)
        if 'You need to login before proceed!' not in r.text:
            self.cookies = r.cookies
            self.dump_cookies()

    def vm_create(self, image, vlan,
                  name=None, cpu=None, memory=None, increase=None, metadata={}):
        data = {'exec': 'launch_vm',
                'image': image,
                'vlan': vlan,
                'name': name,
                'cpu': cpu,
                'memory': memory,
                'disk_inc': increase,
                'metadata': utils.dumps(metadata)}
        r = self.post(data=data)
        return r.text.strip()

    def vm_list(self):
        params = {'action': 'get_vm_list'}
        r = self.get(params=params)
        return r.text.strip()

    def vm_delete(self, vm):
        data = {'exec': 'clear_vm',
                'vm_ID': vm}
        r = self.post(data=data)
        return r.text.strip()

    def image_list(self):
        params = {'action': 'get_img_list'}
        r = self.get(params=params)
        return r.text.strip()

    def image_show(self, image):
        params = {'action': 'get_img',
                  'name': image}
        r = self.get(params=params)
        return r.text.strip()

    def image_delete(self, image):
        data = {'exec': 'delete_img',
                'img_name': image}
        r = self.post(data=data)
        return r.text.strip()

    def image_create(self, url, platform, shared=True, desc=None):
        data = {'exec': 'upload_img',
                'img_url': url,
                'platform': platform,
                'shared': shared,
                'img_desc': desc}
        r = self.post(data=data)
        return r.text.strip()

    def vlan_list(self):
        params = {'action': 'get_link_list'}
        r = self.get(params=params)
        return r.text.strip()

    def vlan_create(self, vlan, network, netmask, gateway, start_ip, end_ip,
                    shared, use_dhcp):
        data = {'exec': 'create_net',
                'vlan': vlan,
                'network': network,
                'netmask': netmask,
                'gateway': gateway,
                'start_ip': start_ip,
                'end_ip': end_ip,
                'shared': shared,
                'use_dpcp': use_dhcp}
        r = self.post(data=data)
        return r.text.strip()

    def vlan_delete(self, vlan):
        data = {'exec': 'clear_net',
                'vlan': vlan}
        r = self.post(data=data)
        return r.text.strip()

    def vlan_attach(self, vlan, vm):
        data = {'exec': 'attach_nic',
                'vlan': vlan,
                'vm_ID': vm}
        r = self.post(data=data)
        return r.text.strip()

    def volume_list(self):
        params = {'action': 'get_vol_list'}
        r = self.get(params=params)
        return r.text.strip()

    def volume_delete(self, volume):
        data = {'exec': 'delete_vol',
                'vol_name': volume}
        r = self.post(data=data)
        return r.text.strip()

    def volume_create(self, size, image, desc):
        data = {'exec': 'create_vol',
                'vol_size': size,
                'img_name': image,
                'vol_desc': desc}
        r = self.post(data=data)
        return r.text.strip()

    def volume_attach(self, volume, vm):
        data = {'exec': 'attach_vol',
                'vol_name': volume,
                'vm_ID': vm}
        r = self.post(data=data)
        return r.text.strip()

    def volume_detach(self, volume):
        data = {'exec': 'detach_vol',
                'vol_name': volume}
        r = self.post(data=data)
        return r.text.strip()

    def snapshot_list(self):
        params = {'action': 'get_snapshot_list'}
        r = self.get(params=params)
        return r.text.strip()

    def snapshot_delete(self, snapshot):
        data = {'exec': 'delete_snapshot',
                'snapshot': snapshot}
        r = self.post(data=data)
        return r.text.strip()

    def snapshot_create(self, vm, desc):
        data = {'exec': 'create_snapshot',
                'vm_ID': vm,
                'snap_desc': desc}
        r = self.post(data=data)
        return r.text.strip()

    def snapshot_download(self, snapshot):
        data = {'exec': 'download_snapshot',
                'snapshot': snapshot}
        r = self.post(data=data)
        return r.text.strip()
