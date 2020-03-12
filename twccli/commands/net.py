from twccli.twcc.services.compute import GpuSite, VcsSite, VcsSecurityGroup, VcsServerNet
from twccli.twcc.util import isNone
from twccli.twcc.services.compute import getServerId, getSecGroupList
import click


@click.command(help='Expose port perations for CCS (Container Compute Service)')
@click.option('-exp/-unexp', '--exposed-port/--unexposed-port', 'isAttach', is_flag=True,
              show_default=True,
              help='exposed/un-exposed port for continer services')
@click.option('-p', '--port', 'port', type=int,
              required=True,
              help='Port number in your CCS environment.')
@click.option('-s', '--site-id', 'siteId', type=int,
              required=True,
              help='Resource id for CCS.')
def ccs(siteId, port, isAttach):
    """Command line for network function of ccs
    Functions:
    expose/unbind port

    :param port: Port number for your VCS environment
    :type port: integer
    :param siteId: Resource id for VCS
    :type siteId: integer
    :param isAttach: exposed/un-exposed port for continer services
    :type isAttach: bool
    """
    b = GpuSite()
    tsite = b.queryById(siteId)
    if isAttach:
        b.exposedPort(siteId, port)
    else:
        b.unbindPort(siteId, port)


@click.command(help='Security Group operations for VCS (Virtual Compute Service)')
@click.option('-fip / -nofip', '--floating-ip / --no-floating-ip', 'fip',
              is_flag=True, default=True,  show_default=False,
              help='Configure your VCS environment with or without floating IP.')
@click.option('-p', '--port', 'port', type=int,
              help='Port number for your VCS environment.')
@click.option('-s', '--site-id', 'siteId', type=int,
              required=True,
              help='Resource id for VCS.')
@click.option('-cidr', '--cidr-network', 'cidr', type=str,
              help='Network range for security group.',
              default='192.168.0.1/24', show_default=True)
@click.option('-proto', '--protocol', 'protocol', type=str,
              help='Network protocol for security group.',
              default='tcp', show_default=True)
@click.option('-in/-out', '--ingress/--egress', 'isIngress',
              is_flag=True, default=True,  show_default=True,
              help='Applying security group directions.')
def vcs(siteId, port, cidr, protocol, isIngress, fip):
    """Command line for network function of vcs

    :param fip: Configure your VCS environment with or without floating IP
    :type fip: bool
    :param port: Port number for your VCS environment
    :type port: integer
    :param siteId: Resource id for VCS
    :type siteId: integer
    :param cidr: Network range for security group
    :type cidr: string
    :param protocol: Network protocol for security group
    :type protocol: string
    :param isIngress: Applying security group directions.
    :type isIngress: bool
    """
    if isNone(port):
        if fip: # @todo need to add check
            VcsServerNet().associateIP(siteId)
        else:
            VcsServerNet().deAssociateIP(siteId)


    else:
        avbl_proto = ['tcp', 'udp', 'icmp']

        secg_list = getSecGroupList(siteId)
        secg_id = secg_list['id']
        from netaddr import IPNetwork
        IPNetwork(cidr)

        if not protocol in avbl_proto:
            raise ValueError(
                "Protocol is not valid. available: {}.".format(avbl_proto))

        secg = VcsSecurityGroup()
        secg.addSecurityGroup(secg_id, port, cidr, protocol,
                          "ingress" if isIngress else "egress")


@click.group(help="NETwork related operations.")
def cli():
    pass


cli.add_command(ccs)
cli.add_command(vcs)


def main():
    cli()


if __name__ == "__main__":
    main()
