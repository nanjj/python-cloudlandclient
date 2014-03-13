'''
Command line interface to cloudland.
'''

import argparse
import json
import os
import sys
import cloudlandclient
from client import CloudlandClient
import utils


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

        parser.add_argument('-h', '--help',
                            action='store_true',
                            help=argparse.SUPPRESS)

        parser.add_argument('--version',
                            action='version',
                            version=cloudlandclient.__version__,
                            help="Shows the client version and exits.")

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
    @utils.arg('--memory', metavar='<MEMORY>', required=False,
               help='Memory of the virtual machine to create.')
    def do_vm_create(self, args):
        """Create virtual machine."""
        body = self.client.vm_create(
            image=args.image,
            vlan=args.vlan,
            name=args.name,
            cpu=args.cpu,
            memory=args.memory)
        utils.pretty(head="ID|STATUS", body=body)

    def do_vm_list(self, args):
        """List virtual machines."""
        body = self.client.vm_list()
        head = 'ID|IMAGE|IP|NAME|VXLAN|STATUS|VNC'
        utils.pretty(head=head, body=body)

    @utils.arg('vm_id', metavar='<VM ID>',
               help='ID of the virtual machine to be deleted')
    def do_vm_delete(self, args):
        '''Delete virtual machine.'''
        body = self.client.vm_delete(vm_id=args.vm_id)
        utils.pretty(head='ID|STATUS', body=body)

    def do_image_list(self, args):
        '''List images.'''
        body = self.client.image_list()
        utils.pretty(head='IMAGE', body=body)

    @utils.arg('name', metavar='<NAME>',
               help='NAME of the image to be shown.')
    def do_image_show(self, args):
        '''Show image.'''
        body = self.client.image_show(name=args.name)
        body = dict(json.loads(body))
        # TODO remove below workaround once image show is ready.
        head = '|'.join(body.keys()).upper()
        body = '|'.join([v.strip() for v in body.values()]).replace(',', '')
        body = '["%s"]' % body
        utils.pretty(head=head, body=body)

    def do_vlan_list(self, args):
        '''List vlan.'''
        body = self.client.vlan_list()
        utils.pretty(head='VLAN|NETWORK|NETMASK|GATEWAY|START_IP|END_IP|OWNER',
                     body=body)

    @utils.arg('vlan', type=int, metavar='<VLAN>',
               help='VLAN number, for example, 5001.')
    @utils.arg('network', metavar='<NETWORK>',
               help='Network, for example, 172.16.1.0.')
    @utils.arg('netmask', metavar='<NETMASK>',
               help='Netmask, for example, 255.255.255.0.')
    @utils.arg('--gateway', metavar='<GATEWAY>', required=False,
               help='Gateway, for example, 172.16.1.1.')
    @utils.arg('--begin', metavar='<START IP>', required=False,
               help='Start IP, for example, 172.16.1.2.')
    @utils.arg('--end', metavar='<END IP>', required=False,
               help='End IP, for example, 172.16.1.10.')
    @utils.arg('--shared', type=bool, metavar='<END IP>', required=False,
               help='End IP, for example, 172.16.1.10.')
    def do_vlan_create(self, args):
        '''Create VLAN.'''
        body = self.client.vlan_create(
            vlan=args.vlan,
            network=args.network,
            netmask=args.netmask,
            gateway=args.gateway,
            start_ip=args.begin,
            end_ip=args.end,
            shared=args.shared
        )
        utils.pretty(head='VLAN', body=body)

    @utils.arg('vlan', type=int, metavar='<VLAN>',
               help='Existing VLAN number, for example, 5001.')
    def do_vlan_delete(self, args):
        '''Delete VLAN.'''
        body = self.client.vlan_delete(vlan=args.vlan)
        utils.pretty(head='RESULT', body=body)

    @utils.arg('vlan', type=int, metavar='<VLAN>',
               help='VLAN to attach to VM.')
    @utils.arg('vm_id', metavar='<VM ID>',
               help='ID of the virtual machine to be attached VLAN')
    def do_vlan_attach(self, args):
        '''Attach VLAN to VM.'''
        body = self.client.vlan_attach(
            vlan=args.vlan,
            vm_id=args.vm_id)
        utils.pretty(head='RESULT', body=body)

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

    def main(self, argv):
        # Parse args once to find version
        parser = self.get_base_parser()
        (options, args) = parser.parse_known_args(argv)
        self.parser = self.get_subcommand_parser()
        if not args and options.help or not argv:
            self.do_help(options)
            return 0
        args = self.parser.parse_args(argv)
        if args.func == self.do_help:
            self.do_help(args)
            return 0
        if args.endpoint and args.username and args.password:
            self.client = CloudlandClient(
                args.endpoint, args.username, args.password)
        else:
            self.do_help(args)
            return 1
        args.func(args)


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
    main()
