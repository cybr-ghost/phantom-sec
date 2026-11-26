# Phantom Sec - Tool Catalogue

This document describes planned tools and categories. Listing a tool here does not mean it has been implemented.

## 1. System information

- Operating system and kernel information
- CPU and memory information
- Storage usage analysis
- Running process overview
- Hardware inventory
- System resource monitor
- Installed software overview

## 2. Network diagnostics

- Network interface information
- Local IP configuration
- DNS lookup
- Connectivity checks
- Ping utility
- Traceroute utility
- Current network connection overview
- Local network device discovery on networks the operator owns or is authorized to assess

## 3. Defensive security

- Local security configuration checks
- Firewall status checker
- Listening service overview on the local system
- File integrity checker
- HTTP security header checker
- Local password-strength estimator that does not collect or transmit passwords
- Basic system audit reports

## 4. Responsible OSINT

- Domain information lookup
- DNS records lookup
- Public IP information
- Certificate transparency lookup
- Public website metadata
- Public organization information
- Search engine research helpers

OSINT features must not enable doxxing, private-person tracking, credential harvesting, or attempts to expose private information.

## 5. Web diagnostics

- HTTP response checker
- Website availability checker
- SSL/TLS certificate information
- Security header analysis
- Redirect checker
- robots.txt viewer
- Sitemap viewer

Active testing must be limited to systems the operator owns or has explicit permission to assess.

## 6. File analysis

- File hash calculator
- File metadata viewer
- File type identification
- Duplicate file finder
- Directory size analyzer
- Text and log viewer

File analysis should be read-only by default. Any operation that changes files must clearly explain its effect and ask for confirmation.

## 7. Reporting

- Text reports
- JSON reports
- CSV exports
- HTML reports
- Local scan history
- Result comparison

Reports should avoid including secrets or unnecessary personal data.

## 8. Module Workshop

- Module generator
- Module templates
- Metadata validator
- Dependency checker
- Documentation generator
- Module test runner
- Import and export manager

Community modules require review before being recommended or distributed. Untrusted modules must never execute automatically.

## 9. Possible future categories

- Wireless network diagnostics for authorized networks
- Cloud security configuration checks
- Container security checks
- Developer utilities
- Advanced system monitoring

## Catalogue rules

- Every tool must have a clear purpose and documentation.
- Avoid duplicate functionality.
- Show required permissions before execution.
- Network testing must be authorized and clearly scoped.
- Community modules must be reviewed before inclusion.
- Untrusted modules must never execute automatically.
- Tools should produce understandable results and useful reports.

## Initial development priority

1. System information
2. Network diagnostics
3. File analysis
4. Defensive security
5. Basic responsible OSINT
6. Reporting
