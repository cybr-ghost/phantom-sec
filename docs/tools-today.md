# Tools Available Today

This page lists the tools included in the current Phantom Sec preview. The catalogue is designed to grow; each tool has a unique ID and a distinct purpose. Use `phantom-sec gui` to search and launch them from the desktop interface.

## Computer information

| Tool ID | What it does |
|---|---|
| `system.info` | Basic operating system and runtime information. |
| `system.uptime` | Shows uptime on Linux and Windows. |
| `system.overview` | Combines local system, uptime, memory, storage, process-count, interface, and basic firewall information into one read-only snapshot. |
| `system.firewall` | Checks UFW/firewalld on Linux or Windows Defender Firewall profiles without changing settings. |
| `system.memory` | Memory counters on supported systems. |
| `system.battery` | Read battery charge and charging status where available. |
| `system.process-count` | Counts running processes on Linux and Windows without collecting command lines. |
| `system.environment` | A small summary of the local environment. |
| `system.disk` | Disk usage for a selected path. |
| `system.hostname` | The local computer's hostname. |

## File information

| Tool ID | What it does |
|---|---|
| `file.sha256` | Calculates a file's SHA-256 hash. |
| `file.metadata` | Shows basic file metadata. |
| `file.directory-size` | Calculates the size of a directory. |
| `file.permissions` | Shows permission bits for a local file or folder without changing them. |
| `file.type-signature` | Identifies common file formats from their leading bytes. It does not execute or validate files. |
| `file.text-profile` | Reports UTF-8 encoding, line count and newline style without displaying text contents. Files are limited to 10 MiB. |
| `file.duplicate-finder` | Finds byte-identical files under a selected folder, ignores symbolic links and never deletes files. |

## Network basics

| Tool ID | What it does |
|---|---|
| `network.interfaces` | Lists local network interface names. |
| `network.dns` | Looks up a hostname. |
| `network.reverse-dns` | Looks up a hostname for an IP address when available. |

## Network intelligence and website security

| Tool ID | What it does |
|---|---|
| `network.subnet-calculator` | Calculates IPv4 and IPv6 network boundaries locally without sending traffic. |
| `web.url-analyzer` | Inspects URL structure and basic indicators locally without opening the URL. |
| `web.tls-inspector` | Connects to the supplied hostname on port 443 and reads its public TLS certificate. |
| `web.security-headers` | Sends an HTTP HEAD request and checks common browser security headers. |

## Domain intelligence

| Tool ID | What it does |
|---|---|
| `domain.dns-records` | Queries common public DNS record types. |
| `domain.rdap` | Looks up public domain registration events, status and nameservers. |
| `domain.certificate-transparency` | Searches public certificate-transparency logs for a domain. |

## Important limits

Domain intelligence tools contact public DNS or RDAP/Certificate Transparency services. They do not access accounts or private registration records.

The firewall check supports UFW and firewalld on Linux, and reads Windows Defender Firewall profile status on Windows. Windows file permission output is limited to access checks for the current process; Windows ACL details are not decoded. If a check cannot confirm status, it reports that limitation rather than guessing.

The system overview is a quick informational snapshot, not a security audit. It does not scan networks, change settings, inspect process command lines, or claim that a device is secure.

Broader OSINT helpers, additional website checks, and a reviewed community module process are not included yet. TLS and HTTP checks contact the supplied hostname. Use them only where you have permission.
