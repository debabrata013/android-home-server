import json
import logging
import signal
import socket
import struct
import fcntl
import time
from pathlib import Path

from zeroconf import Zeroconf, ServiceInfo, IPVersion


# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = BASE_DIR / "config" / "config.json"
LOG_FILE = BASE_DIR / "logs" / "mdns.log"

# Stop signal
running = True


def load_config():
    """Load project configuration from JSON."""
    with open(CONFIG_FILE, "r") as file:
        return json.load(file)


def setup_logging():
    """Write logs to both terminal and log file."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler()
        ]
    )


def get_interface_ip(interface):
    """Detect IPv4 address assigned to a network interface."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        request = struct.pack(
            "256s",
            interface[:15].encode("utf-8")
        )

        response = fcntl.ioctl(
            sock.fileno(),
            0x8915,  # SIOCGIFADDR
            request
        )

        return socket.inet_ntoa(response[20:24])

    finally:
        sock.close()


def register_mdns(config, ip):
    """Register SSH service with mDNS."""
    hostname = config["hostname"]
    service_type = config["service_type"]
    service_name = config["service_name"]
    ssh_port = config["ssh_port"]

    service_info = ServiceInfo(
        type_=service_type,
        name=f"{service_name}.{service_type}",
        addresses=[socket.inet_aton(ip)],
        port=ssh_port,
        server=hostname
    )

    zeroconf = Zeroconf(
        interfaces=[ip],
        ip_version=IPVersion.V4Only
    )

    zeroconf.register_service(service_info)

    logging.info("mDNS service registered successfully")
    logging.info("Hostname: %s", hostname)
    logging.info("IP address: %s", ip)
    logging.info("SSH port: %s", ssh_port)

    return zeroconf, service_info


def shutdown_handler(signum, frame):
    """Handle Ctrl+C and termination signals."""
    global running
    logging.info("Shutdown signal received")
    running = False


def main():
    global running

    config = load_config()
    setup_logging()

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    interface = config["network_interface"]
    interval = config["check_interval"]

    zeroconf = None
    service_info = None
    current_ip = None

    logging.info("Starting Android mDNS server")
    logging.info("Monitoring interface: %s", interface)

    try:
        while running:
            try:
                new_ip = get_interface_ip(interface)

                if new_ip != current_ip:
                    logging.info("Detected IP: %s", new_ip)

                    # Remove previous registration
                    if zeroconf and service_info:
                        zeroconf.unregister_service(service_info)
                        zeroconf.close()

                    # Register using the new IP
                    zeroconf, service_info = register_mdns(
                        config,
                        new_ip
                    )

                    current_ip = new_ip

            except Exception:
                logging.exception("Unable to register or detect IP")

            # Wait before checking the interface again
            for _ in range(interval):
                if not running:
                    break
                time.sleep(1)

    finally:
        if zeroconf and service_info:
            zeroconf.unregister_service(service_info)
            zeroconf.close()

        logging.info("mDNS server stopped")


if __name__ == "__main__":
    main()
