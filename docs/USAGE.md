# Usage Guide

Start with `phantom-sec` or `python -m phantom_sec` to see the module catalogue.

## Commands
- `phantom-sec list`: list available built-in modules.
- `phantom-sec run system.info`: show basic platform information.
- `phantom-sec run system.hostname`: show the local hostname.
- `phantom-sec run system.disk --path ~`: show disk usage.
- `phantom-sec run file.sha256 --path ./some-file`: hash a local file.
- `phantom-sec run file.directory-size --path ./some-folder`: calculate regular-file sizes.
- `phantom-sec run network.dns --domain example.com`: resolve a hostname.
- `phantom-sec validate-module module.json`: validate metadata only.

File analysis is read-only. Directory size traversal skips symlinks and ignores files that cannot be inspected. DNS lookup uses the system resolver. No port scanning, exploitation, credential collection, or third-party plugin execution is provided.
