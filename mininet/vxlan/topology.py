#!/usr/bin/env python
import os
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel, info, debug
from mininet.topo import Topo
from mininet.node import Host, RemoteController, OVSSwitch

'''
Topology:
    red1  -`                             ,- red2
            +--- ovs1 -- tor -- ovs2 ---+
    blue1 -,                             `- blue2

IP of ovs1 is 192.168.10.1, ovs2 is 192.168.20.1
Use ovs as vtep
'''


class VXLANTopo(Topo):

    def __init__(self):
        Topo.__init__(self)
        tor = self.addSwitch('tor',
                             dpid='0000000000000010',
                             cls=OVSSwitch, failMode="standalone")
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        red1 = self.addHost('red1', ip='10.0.0.1/24')
        red2 = self.addHost('red2', ip='10.0.0.2/24')
        blue1 = self.addHost('blue1', ip='10.0.0.1/24')
        blue2 = self.addHost('blue2', ip='10.0.0.2/24')

        self.addLink(red1, s1)
        self.addLink(blue1, s1)

        self.addLink(red2, s2)
        self.addLink(blue2, s2)

        self.addLink(s1, tor, port1=10, port2=1)
        self.addLink(s2, tor, port1=10, port2=2)

if __name__ == '__main__':
    setLogLevel('debug')
    topo = VXLANTopo()

    net = Mininet(topo=topo, controller=None)

    net.start()
    c0 = net.addController(name='c0',
                           controller=RemoteController,
                           ip='127.0.0.1', port=6633)

    net.get('red1').setMAC('00:00:00:00:00:01')
    net.get('red2').setMAC('00:00:00:00:00:02')
    net.get('blue1').setMAC('00:00:00:00:00:01')
    net.get('blue2').setMAC('00:00:00:00:00:02')

    net.get('s1').start([c0])
    net.get('s2').start([c0])
    os.popen('ip addr add 192.168.10.1/16 dev s1-eth10')
    os.popen('ip addr add 192.168.20.1/16 dev s2-eth10')
    os.popen('ovs-vsctl set interface s1-eth10 type=vxlan option:remote_ip=192.168.20.1 option:key=flow')
    os.popen('ovs-vsctl set interface s2-eth10 type=vxlan option:remote_ip=192.168.10.1 option:key=flow')

    CLI(net)
    net.stop()
