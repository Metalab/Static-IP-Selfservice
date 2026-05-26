# Static-IP-Selfservice
Python Script to parse a wiki table and create a OpenWRT dhcp config

# OpenWrt DHCP Config Generator

## Description
This Python script automates the creation of static DHCP leases for OpenWrt routers. It acts as a web scraper and validator. The tool fetches an HTML table containing network data (Hostname, MAC, IPv4, IPv6) from a specified URL, parses the columns dynamically, and validates the data. 

Specifically, it checks:
* **MAC Addresses:** Ensures correct format and filters out multicast/broadcast addresses.
* **IPv4 Addresses:** Validates the IP format and ensures the IP belongs to a specified allowed subnet.
* **Hostnames:** Ensures DNS compliance (automatically replaces dots with hyphens) and ignores invalid entries.

Invalid entries are safely skipped, and the reasoning is logged to `stderr` using the Python `logging` module. 

## Important Variables to Set
Before running the script, ensure you configure the following global variables inside the `main()` function:

* `url` (string): The URL of the webpage containing the HTML table with the static IP definitions.
* `allowedNetwork` (string via `ipaddress.ip_network`): The allowed subnet in CIDR notation (e.g., `"192.168.0.0/16"`). Any parsed IPv4 address outside this network will be rejected.

## How to Run the Tool
### Prerequisites
Ensure you have Python 3 installed along with the required external libraries. You can install the dependencies via pip:
`pip install requests beautifulsoup4`

### Execution
Run the script directly from your terminal or command prompt:
`python main.py`

## Output
The script produces two types of output:

1. **The Configuration File:**
Upon successful execution, the tool generates a file named `dhcp_hosts.conf` in the same directory. The file contains the validated devices sorted alphabetically by their MAC addresses in the standard OpenWrt UCI format. 

**Example output:**
config host
    option name 'nas'
    option ip '192.168.50.10'
    list mac '9c:b6:d0:4f:8a:22'
    option dns '1'

2. **Standard Error (stderr):**
Any parsing failures (e.g., malformed MAC addresses, IPs outside the allowed network, or invalid hostnames) will not crash the script. Instead, they are logged as errors to the console (`stderr`) so the administrator can review what data was skipped and why.
