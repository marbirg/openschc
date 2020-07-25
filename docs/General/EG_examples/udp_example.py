

from net_udp_core import  *

# --------------------------------------------------

compression_rule = {
    "RuleID": 12,
    "RuleIDLength": 4,
    "Compression": []
}

frag_rule_noack = {
    "RuleID" : 12,
    "RuleIDLength" : 6,
    "Fragmentation" : {
        "FRMode": "noAck",
        "FRDirection": "UP"
    }
}

rule_set = [compression_rule, frag_rule_noack]

rule_manager = gen_rulemanager.RuleManager()
rule_manager.Add(dev_info=rule_set)
rule_manager.Print()



# --------------------------------------------------
# Get UDP address and role from command line

parser = argparse.ArgumentParser()
parser.add_argument("role", choices=["device", "core-server"])
parser.add_argument("--core-ip", type=str)
parser.add_argument("--core-port", type=int)
#parser.add_argument("other_end_ip", help="IP address of the other end")
#parser.add_argument("other_end_port", help="Port number of the other end", type=int)
#parser.add_argument("core_port", help="core port", type=int)

args = parser.parse_args()

role = args.role
core_ip = args.core_ip
core_port = args.core_port



if role == "device":
    udp_src = None
    udp_dst = (core_ip, core_port)
else:
    assert role == "core-server"
    udp_src = ("", core_port)
    udp_dst = None

# --------------------------------------------------
# Actually run SCHC

config = {}
upper_layer = UdpUpperLayer()
lower_layer = UdpLowerLayer(udp_src, udp_dst)
system = UdpSystem()
scheduler = system.get_scheduler()
schc_protocol = protocol.SCHCProtocol(
    config, system, layer2=lower_layer, layer3=upper_layer, role=role, unique_peer=True)
schc_protocol.set_rulemanager(rule_manager)

if role == "device": # XXX: fix addresses mismatches
    coap_ip_packet = bytearray(b"""`\
    \x12\x34\x56\x00\x1e\x11\x1e\xfe\x80\x00\
    \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
    \x00\x00\x01\xfe\x80\x00\x00\x00\x00\x00\
    \x00\x00\x00\x00\x00\x00\x00\x00\x02\x16\
    2\x163\x00\x1e\x00\x00A\x02\x00\x01\n\xb3\
    foo\x03bar\x06ABCD==Fk=eth0\xff\x84\x01\
    \x82  &Ehello""")

    upper_layer.send_later(1, udp_dst, coap_ip_packet)

scheduler.run()

# --------------------------------------------------
