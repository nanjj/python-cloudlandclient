'''
Command line interface to cloudland.
'''

import argparse
import json
import logging
import os
import sys
import cloudlandclient
from client import CloudlandClient
import utils

logger = logging.getLogger(__name__)


class CloudlandShell:

    def get_base_parser(self):
        parser = argparse.ArgumentParser(
            prog='cloudland',
            description=__doc__.strip(),
            epilog='See "cloudland help COMMAND" '
                   'for help on a specific command.',
            add_help=False,
            formatter_class=HelpFormatter
        )

        parser.add_argument('--help',
                            action='store_true',
                            help=argparse.SUPPRESS)

        parser.add_argument('--version',
                            action='version',
                            version=cloudlandclient.__version__,
                            help="Shows the client version and exits.")

        parser.add_argument('--debug',
                            action='store_true',
                            help='Enable debug')

        parser.add_argument('--username',
                            default=os.environ.get('CLOUDLAND_USERNAME'),
                            help='Defaults to env[CLOUDLAND_USERNAME].')

        parser.add_argument('--password',
                            default=os.environ.get('CLOUDLAND_PASSWORD'),
                            help='Defaults to env[CLOUDLAND_PASSWORD].')

        parser.add_argument('--endpoint',
                            default=os.environ.get('CLOUDLAND_ENDPOINT'),
                            help='Defaults to env[CLOUDLAND_ENDPOINT].')

        return parser

    def get_subcommand_parser(self):
        parser = self.get_base_parser()
        self.subcommands = {}
        subparsers = parser.add_subparsers(metavar='<subcommand>')
        self._find_actions(subparsers, self)
        return parser

    @utils.arg('command', metavar='<subcommand>', nargs='?',
               help='Display help for <subcommand>.')
    def do_help(self, args):
        """Display help for <subcommand>."""
        if getattr(args, 'command', None):
            if args.command in self.subcommands:
                self.subcommands[args.command].print_help()
            else:
                raise Exception("'%s' is not a valid subcommand" %
                                args.command)
        else:
            self.parser.print_help()

    @utils.arg('image', help='Image to create the virtual machine.')
    @utils.arg('vlan', type=int,
               help='VLAN attched to the virtual machine to create.')
    @utils.arg('--name', metavar='<NAME>', required=False,
               help='Hostname of the virtual machine to create.')
    @utils.arg('--cpu', metavar='<CPU>', type=int, required=False,
               help='CPU number of the virtual machine to create.')
    @utils.arg('--memory', metavar='<MEMORY>', type=int,
               help='Memory size in Mega bytes.')
    @utils.arg('--increase',
               metavar='<DISK SIZE>', type=int,
               help=' Disk size to increase in Giga bytes.')
    def do_vm_create(self, args):
        """Create virtual machine."""
        body = self.client.vm_create(
            image=args.image,
            vlan=args.vlan,
            name=args.name,
            cpu=args.cpu,
            memory=args.memory,
            increase=args.increase)
        utils.pretty(head="VM|STATUS", body=body)

    def do_vm_list(self, args):
        """List virtual machines."""
        body = self.client.vm_list()
        head = 'VM|IMAGE|IP|NAME|VXLAN|STATUS|VNC'
        utils.pretty(head=head, body=body)

    @utils.arg('vm', metavar='<VM>',
               help='The virtual machine to be deleted')
    def do_vm_delete(self, args):
        '''Delete virtual machine.'''
        body = self.client.vm_delete(vm=args.vm)
        utils.pretty(head='VM|STATUS', body=body)

    def do_image_list(self, args):
        '''List images.'''
        body = self.client.image_list()
        utils.pretty(head='IMAGE|SIZE|OS|DESC|OWNER', body=body)

    @utils.arg('image', metavar='<IMAGE>',
               help='The image to be deleted.')
    def do_image_delete(self, args):
        '''Delete image.'''
        body = self.client.image_delete(image=args.image)
        utils.pretty(head='IMAGE|STATUS', body=body)

    @utils.arg('url', metavar='<IMAGE URL>',
               help='The url to the image binary.')
    @utils.arg('platform', metavar='<OS PLATFORM>',
               help='The OS platform of the image(linux or windows).')
    @utils.arg('--shared', type=bool,
               help='Share the image or not(true or false).')
    @utils.arg('--desc', help='Image description.')
    def do_image_create(self, args):
        '''Create image.'''
        body = self.client.image_create(
            url=args.url,
            platform=args.platform,
            shared=str(args.shared).lower(),
            desc=args.desc)
        utils.pretty(head='IMAGE|STATUS', body=body)

    @utils.arg('image', metavar='<IMAGE>',
               help='The image to be shown.')
    def do_image_show(self, args):
        '''Show image.'''
        body = self.client.image_show(image=args.image)
        body = dict(json.loads(body))
        # TODO remove below workaround once image show is ready.
        head = '|'.join(body.keys()).upper()
        body = '|'.join([v.strip() for v in body.values()]).replace(',', '')
        body = '["%s"]' % body
        utils.pretty(head=head, body=body)

    def do_vlan_list(self, args):
        '''List vlan.'''
        body = self.client.vlan_list()
        # NETWORK|NETMASK|GATEWAY|START_IP|END_IP
        utils.pretty(head='VLAN|DESC|OWNER',
                     body=body)

    @utils.arg('size', metavar='<VOLUME SIZE>', type=int,
               help='Volume size in G')
    @utils.arg('--image', metavar='<IMAGE>',
               help='Create volume from <IMAGE>. ')
    @utils.arg('--desc', metavar='<DESC>',
               help='Volume description.')
    def do_volume_create(self, args):
        '''Create volume.'''
        body = self.client.volume_create(
            size=args.size,
            image=args.image,
            desc=args.desc)
        utils.pretty(head='VOLUME|STATUS', body=body)

    def do_volume_list(self, args):
        '''List volume.'''
        body = self.client.volume_list()
        utils.pretty(
            head='VOLUME|SIZE|DESC|VM|DEVICE|BOOTABLE|STATUS', body=body)

    @utils.arg('volume', metavar='<VOLUME>',
               help='The volume to be deleted.')
    def do_volume_delete(self, args):
        '''Delete volume.'''
        body = self.client.volume_delete(args.volume)
        utils.pretty(head='VOLUME|STATUS', body=body)

    @utils.arg('volume', metavar='<VOLUME>',
               help='The volume to detach.')
    def do_volume_detach(self, args):
        '''Detach volume.'''
        body = self.client.volume_detach(args.volume)
        utils.pretty(head='VM|VOLUME|STATUS', body=body)

    @utils.arg('volume', metavar='<VOLUME>',
               help='The volume to attach.')
    @utils.arg('vm', metavar='<VM>',
               help='The VM to attach volume to')
    def do_volume_attach(self, args):
        '''Attach volume to VM.'''
        body = self.client.volume_attach(
            volume=args.volume, vm=args.vm)
        utils.pretty(head='VM|VOLUME|STATUS', body=body)

    @utils.arg('vlan', type=int, metavar='<VLAN>',
               help='VLAN number, for example, 5001.')
    @utils.arg('network', metavar='<NETWORK>',
               help='Network, for example, 172.16.1.0.')
    @utils.arg('netmask', metavar='<NETMASK>',
               help='Netmask, for example, 255.255.255.0.')
    @utils.arg('--gateway', metavar='<GATEWAY>',
               help='Gateway, for example, 172.16.1.1.')
    @utils.arg('--begin', metavar='<START IP>',
               help='Start IP, for example, 172.16.1.2.')
    @utils.arg('--end', metavar='<END IP>',
               help='End IP, for example, 172.16.1.10.')
    @utils.arg('--shared', type=bool, metavar='<SHARED>',
               help='Shared with others or not.')
    @utils.arg('--use-dhcp', type=bool, metavar='<USE_DHCP>',
               help='Use DHCP or not.')
    def do_vlan_create(self, args):
        '''Create VLAN.'''
        body = self.client.vlan_create(
            vlan=args.vlan,
            network=args.network,
            netmask=args.netmask,
            gateway=args.gateway,
            start_ip=args.begin,
            end_ip=args.end,
            shared=str(args.shared).lower(),
            use_dhcp=str(args.use_dhcp).lower()
        )
        utils.pretty(head='VLAN|STATUS', body=body)

    @utils.arg('vlan', type=int, metavar='<VLAN>',
               help='Existing VLAN number, for example, 5001.')
    def do_vlan_delete(self, args):
        '''Delete VLAN.'''
        body = self.client.vlan_delete(vlan=args.vlan)
        utils.pretty(head='VLAN|STATUS', body=body)

    @utils.arg('vlan', type=int, metavar='<VLAN>',
               help='VLAN to attach to VM.')
    @utils.arg('vm', metavar='<VM>',
               help='The virtual machine to be attached VLAN')
    def do_vlan_attach(self, args):
        '''Attach VLAN to VM.'''
        body = self.client.vlan_attach(
            vlan=args.vlan,
            vm=args.vm)
        utils.pretty(head='VM|VLAN|STATUS', body=body)

    def _find_actions(self, subparsers, actions_module):
        for attr in (a for a in dir(actions_module) if a.startswith('do_')):
            command = attr[3:].replace('_', '-')
            callback = getattr(actions_module, attr)
            desc = callback.__doc__ or ''
            help = desc.strip().split('\n')[0]
            arguments = getattr(callback, 'arguments', [])

            subparser = subparsers.add_parser(command,
                                              help=help,
                                              description=desc,
                                              add_help=False,
                                              formatter_class=HelpFormatter)
            subparser.add_argument('-h', '--help',
                                   action='help',
                                   help=argparse.SUPPRESS)
            self.subcommands[command] = subparser
            for (args, kwargs) in arguments:
                subparser.add_argument(*args, **kwargs)
            subparser.set_defaults(func=callback)

    def _setup_logging(self, debug):
        log_lvl = logging.DEBUG if debug else logging.ERROR
        logging.basicConfig(
            format="%(levelname)s (%(module)s:%(lineno)d) %(message)s",
            level=log_lvl)

    def main(self, argv):
        # Parse args once to find version
        parser = self.get_base_parser()
        (options, args) = parser.parse_known_args(argv)
        self.parser = self.get_subcommand_parser()
        if not args and options.help or not argv:
            self.do_help(options)
            return 0
        self._setup_logging(options.debug)

        args = self.parser.parse_args(argv)
        if args.func == self.do_help:
            self.do_help(args)
            return 0
        if args.endpoint and args.username and args.password:
            self.client = CloudlandClient(
                args.endpoint, args.username, args.password)
            if self.client.cookies:
                args.func(args)
                return 0
        print("Please check whether "
              "\n\t--username CLOUDLAND_USERNAME "
              "\n\t--password CLOUDLAND_PASSWORD "
              "\n\t--endpoint CLOUDLAND_ENDPOINT \n"
              "are set correctly.")


class HelpFormatter(argparse.HelpFormatter):
    def start_section(self, heading):
        # Title-case the headings
        heading = '%s%s' % (heading[0].upper(), heading[1:])
        super(HelpFormatter, self).start_section(heading)


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    CloudlandShell().main(args)


if __name__ == "__main__":
    sys.exit(main())
