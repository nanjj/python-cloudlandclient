import requests
import utils


class CloudlandClient:
    def __init__(self, endpoint, username, password):
        self.endpoint = endpoint
        self.cookies = None
        self.login(username, password)

    def post(self, data):
        return requests.post(self.endpoint, data=data, cookies=self.cookies)

    def get(self, params):
        return requests.get(self.endpoint, params=params, cookies=self.cookies)

    def login(self, username, password):
        password = utils.sha1sum(password)
        data = {'username': username, 'sha1': password, 'op': 'login'}
        r = self.post(data)
        self.cookies = r.cookies

    def vm_create(self, image, vlan, name=None, cpu=None, memory=None):
        data = {'exec': 'launch_vm',
                'image': image,
                'vlan': vlan,
                'name': name,
                'cpu': cpu,
                'memory': memory}
        r = self.post(data=data)
        return r.text.strip()

    def vm_list(self):
        params = {'action': 'get_vm_list'}
        r = self.get(params=params)
        return r.text.strip()

    def vm_delete(self, vm_id):
        data = {'exec': 'clear_vm',
                'vm_ID': vm_id}
        r = self.post(data=data)
        return r.text.strip()

    def image_list(self):
        params = {'action': 'get_img_list'}
        r = self.get(params=params)
        return r.text.strip()

    def image_show(self, name):
        params = {'action': 'get_img',
                  'name': name}
        r = self.get(params=params)
        return r.text.strip()

    def vlan_list(self):
        params = {'action': 'get_vlan_list'}
        r = self.get(params=params)
        return r.text.strip()

    def vlan_create(self, vlan, network, netmask, gateway, start_ip, end_ip,
                    shared):
        data = {'exec': 'create_net',
                'vlan': vlan,
                'network': network,
                'netmask': netmask,
                'gateway': gateway,
                'start_ip': start_ip,
                'end_ip': end_ip,
                'shared': shared}
        r = self.post(data=data)
        return r.text.strip()

    def vlan_delete(self, vlan):
        data = {'exec': 'clear_net',
                'vlan': vlan}
        r = self.post(data=data)
        return r.text.strip()

    def vlan_attach(self, vlan, vm_id):
        data = {'exec': 'attach_nic',
                'vlan': vlan,
                'vm_ID': vm_id}
        r = self.post(data=data)
        return r.text.strip()
