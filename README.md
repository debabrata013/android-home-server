# Android Home Server

A lightweight Python-based mDNS server that makes an Android device accessible through a hostname on a local network using SSH.

Instead of remembering your Android device's changing IP address, connect using a hostname such as `android-server.local`.

Built using **Termux, Python, OpenSSH and Zeroconf**.

## Features

- **Automatic IP Detection:** Detects the IPv4 address assigned to the configured network interface.
- **mDNS Service Discovery:** Advertises the Android SSH service on the local network.
- **Hostname Resolution:** Makes the device discoverable using `android-server.local`.
- **IP Change Detection:** Periodically checks the network interface and updates the mDNS registration when the IP changes.
- **Logging:** Records server activity and errors.
- **Process Management:** Provides scripts to start and stop the server in the background.
- **Configurable:** Hostname, SSH port, network interface and check interval can be customized.

## Architecture

```text
              MacBook / Client
                     |
                     |
             mDNS Discovery
              UDP Port 5353
                     |
                     |
              Android Phone
                (Termux)
                     |
              Python mDNS Server
                  (Zeroconf)
                     |
             SSH Service Advertised
                TCP Port 8022
                     |
                OpenSSH Server
                     |
              Android Terminal
```

## Tech Stack

| Technology | Purpose |
|---|---|
| Android | Host device |
| Termux | Linux-like terminal environment |
| Python | mDNS server implementation |
| Zeroconf | mDNS service registration |
| OpenSSH | Remote SSH access |
| Git & GitHub | Version control |

## Project Structure

```text
android-home-server/
│
├── config/
│   └── config.json
│
├── logs/
│
├── scripts/
│   ├── start.sh
│   └── stop.sh
│
├── src/
│   ├── __init__.py
│   └── mdns_server.py
│
├── .gitignore
├── README.md
└── requirements.txt
```

## Prerequisites

- Android smartphone
- Termux installed
- Python 3
- OpenSSH
- MacBook or another SSH client on the same local network
- Network that supports multicast DNS traffic

## Installation

### 1. Update Termux packages

```bash
pkg update && pkg upgrade -y
```

### 2. Install required packages

```bash
pkg install python openssh git -y
```

### 3. Configure SSH

Set your Termux password:

```bash
passwd
```

Start the SSH server:

```bash
sshd
```

Termux OpenSSH normally listens on port `8022`.

### 4. Clone the repository

```bash
git clone https://github.com/debabrata013/android-home-server.git

cd android-home-server
```

### 5. Install Python dependencies

```bash
python -m pip install -r requirements.txt
```

## Configuration

Edit the configuration file:

```bash
vi config/config.json
```

Default configuration:

```json
{
  "hostname": "android-server.local.",
  "service_name": "Android-Termux",
  "service_type": "_ssh._tcp.local.",
  "ssh_port": 8022,
  "network_interface": "wlan1",
  "check_interval": 15
}
```

### Configuration Parameters

| Parameter | Description |
|---|---|
| hostname | Hostname advertised through mDNS |
| service_name | SSH service instance name |
| service_type | DNS-SD SSH service type |
| ssh_port | Termux SSH server port |
| network_interface | Android network interface to monitor |
| check_interval | IP address check interval in seconds |

**Note:** The network interface may differ between Android devices. Check your device using `ifconfig` and update the configuration accordingly.

## Usage

### Start the mDNS server

```bash
./scripts/start.sh
```

### Stop the mDNS server

```bash
./scripts/stop.sh
```

### Check running process

```bash
ps -ef | grep mdns_server
```

### View application logs

```bash
tail -f logs/mdns.log
```

### View console logs

```bash
tail -f logs/console.log
```

### Run directly for debugging

```bash
python src/mdns_server.py
```

Press `Ctrl + C` to stop the foreground process.

## Connecting from MacBook

Make sure the MacBook and Android device are connected to the same local network.

### 1. Discover SSH services

```bash
dns-sd -B _ssh._tcp local.
```

Look for the service instance:

```text
Android-Termux
```

### 2. Resolve the Android hostname

```bash
dns-sd -G v4 android-server.local
```

### 3. Connect using SSH

```bash
ssh -p 8022 u0_a515@android-server.local
```

Replace `u0_a515` with your Termux username if it differs.

## How It Works

1. The Python application reads its configuration from `config/config.json`.
2. It detects the IPv4 address assigned to the configured network interface.
3. The Zeroconf library registers an SSH service using mDNS.
4. Other devices on the same multicast-enabled network can discover the service.
5. The application periodically checks whether the IP address has changed.
6. If the address changes, the old registration is removed and a new registration is created.
7. The MacBook can use the advertised hostname to connect to the Android SSH server.

## Troubleshooting

### mDNS hostname is not resolving

Check whether the mDNS server is running:

```bash
ps -ef | grep mdns_server
```

Check the logs:

```bash
tail -f logs/mdns.log
```

Verify that both devices are on the same local network.

Some mobile hotspots and Wi-Fi networks block multicast traffic. In that case, mDNS discovery may not work even when the service registers successfully.

### SSH connection refused

Check whether OpenSSH is running:

```bash
pgrep -a sshd
```

Start SSH if required:

```bash
sshd
```

### Network interface not found

Check available interfaces:

```bash
ifconfig
```

Update `network_interface` in `config/config.json`.

## Security Considerations

- Use a strong Termux SSH password or configure SSH key-based authentication.
- Never commit passwords, private keys or access tokens to GitHub.
- Avoid exposing SSH to untrusted public networks.
- Use a private GitHub repository if you plan to add sensitive configuration.
- Keep Termux packages and Python dependencies updated.

## Limitations

- mDNS requires multicast DNS traffic (UDP port 5353).
- Some Android hotspots do not forward multicast packets between connected clients.
- Android battery optimization may terminate background processes.
- Termux does not provide a full traditional Linux server environment.
- The project advertises SSH; it does not itself run or configure the SSH daemon.

## Future Improvements

- Automatic SSH server startup.
- SSH key-based authentication setup.
- Better network interface detection.
- Network reconnection handling.
- Health checks and process monitoring.
- Android boot-time startup support.
- Docker-free lightweight service management.
- Automated testing and CI using GitHub Actions.

## Author

**Debabrata**

GitHub: [@debabrata013](https://github.com/debabrata013)

## License

This project is licensed under the MIT License.
