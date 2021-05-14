import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '../../src/')

from scapy.all import *
import scapy.contrib.coap as scapy_coap


import gen_rulemanager as RM
import compr_parser as parser
from compr_core import *
from protocol import SCHCProtocol
from scapy_connection import *
from gen_utils import dprint, sanitize_value


import sched
import protocol
import pprint
import binascii
import socket
import ipaddress
import time, datetime


class debug_protocol:
    def _log(*arg):
        print (arg)

# Create a Rule Manager and upload the rules.

rm = RM.RuleManager()
rm.Add(file="icmp.json")
rm.Print()

def processPkt(pkt):
    """ called when scapy receives a packet, since this function takes only one argument,
    schc protocol must be specified as a global variable.
    """

    scheduler.run(session=schc_protocol, display_period=10)

    # look for a tunneled SCHC pkt

    if pkt.getlayer(Ether) != None: #HE tunnel do not have Ethernet
        e_type = pkt.getlayer(Ether).type
        if e_type == 0x0800:
            ip_proto = pkt.getlayer(IP).proto
            if ip_proto == 17:
                udp_dport = pkt.getlayer(UDP).dport
                if udp_dport == socket_port: # tunnel SCHC msg to be decompressed
                    print ("tunneled SCHC msg")                    
                    schc_pkt, addr = tunnel.recvfrom(2000)
                    other_end = "udp:"+addr[0]+":"+str(addr[1])
                    print("other end =", other_end)
                    r = schc_protocol.schc_recv(other_end, schc_pkt)
                    print (r)
            elif ip_proto==41:
                schc_protocol.schc_send(bytes(pkt)[34:])
        
# look at the IP address to define sniff behavior

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.connect(("8.8.8.8", 80))
    ip_addr = s.getsockname()[0]

# Start SCHC Machine
POSITION = T_POSITION_CORE

device_id = None
socket_port = 0x5C4C
other_end = None # defined by the rule


tunnel = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tunnel.bind(("0.0.0.0", 0x5C4C))

config = {}
upper_layer = ScapyUpperLayer()
lower_layer = ScapyLowerLayer(position=POSITION, socket=tunnel, other_end=other_end)
system = ScapySystem()
scheduler = system.get_scheduler()
schc_protocol = protocol.SCHCProtocol(
    system=system,           # define the scheduler
    layer2=lower_layer,      # how to send messages
    role=POSITION)           # DEVICE or CORE
schc_protocol.set_position(POSITION)
schc_protocol.set_rulemanager(rm)


#sniff(prn=processPkt, iface=["he-ipv6", "ens3"]) # scappy cannot read multiple interfaces
sniff(prn=processPkt, iface="ens3") # scappy cannot read multiple interfaces




 
