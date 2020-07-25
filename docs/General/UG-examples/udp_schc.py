#!/usr/bin/env python3

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

args = parser.parse_args()

role = args.role

core_ip = "127.0.0.1"
core_port = 48044

if args.core_ip != None:
    core_ip = args.core_ip
if args.core_port != None:
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

# --------------------------------------------------

if role == "device":
    import binascii

    coap_ip_packet = binascii.unhexlify(
    b'60123456001e111efe800000000000000000000000000001fe800000000000000000000000000002'
    b'16321633001e0000'
    b'410200010ab3666f6fff8401822020264568656c6c6f'
    )

    upper_layer.send_later(1, udp_dst, coap_ip_packet)

scheduler.run()

# --------------------------------------------------
