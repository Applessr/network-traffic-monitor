from scapy.all import (
    IP,
    IPv6,
    ARP,
    TCP,
    UDP,
    ICMP
)


def analyze_packet(packet):

    # -------------------------
    # Timestamp
    # -------------------------
    timestamp = packet.time

    # -------------------------
    # Source / Destination IP
    # -------------------------
    if packet.haslayer(IP):
        source = packet[IP].src
        destination = packet[IP].dst

    elif packet.haslayer(IPv6):
        source = packet[IPv6].src
        destination = packet[IPv6].dst

    elif packet.haslayer(ARP):
        source = packet[ARP].psrc
        destination = packet[ARP].pdst

    else:
        source = ""
        destination = ""

    # -------------------------
    # Protocol
    # -------------------------
    if packet.haslayer(TCP):
        protocol = "TCP"

    elif packet.haslayer(UDP):
        protocol = "UDP"

    elif packet.haslayer(ICMP):
        protocol = "ICMP"

    elif packet.haslayer(ARP):
        protocol = "ARP"

    else:
        protocol = "Other"

    # -------------------------
    # Packet Size
    # -------------------------
    packet_size = len(packet)

    return {
        "timestamp": timestamp,
        "source_ip": source,
        "destination_ip": destination,
        "protocol": protocol,
        "packet_size": packet_size
    }