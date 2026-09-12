from scapy.all import sniff


INTERFACE = "en0"
PACKET_COUNT = 20


def show_packet(packet):
    print(packet.summary())


def main():
    print("================================")
    print("Network Traffic Analyzer")
    print("================================")

    print(f"Interface: {INTERFACE}")
    print(f"Capturing {PACKET_COUNT} packets...")
    print()

    packets = sniff(
        iface=INTERFACE,
        count=PACKET_COUNT,
        prn=show_packet
    )

    print()
    print("Capture complete.")
    print(f"Total packets captured: {len(packets)}")


if __name__ == "__main__":
    main()