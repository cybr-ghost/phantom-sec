# Usage Guide

Start with `phantom-sec` or `python -m phantom_sec` to open the interactive module menu.

## Catalogue and local system
- `phantom-sec list`: list built-in modules.
- `phantom-sec run system.info`: operating system and runtime information.
- `phantom-sec run system.memory`: memory counters where supported.
- `phantom-sec run system.process-count`: process count only.
- `phantom-sec run system.environment`: local environment summary.
- `phantom-sec run system.hostname`: local hostname.
- `phantom-sec run system.disk --path ~`: disk usage.

## File analysis
- `phantom-sec run file.sha256 --path ./some-file`: SHA-256 hash.
- `phantom-sec run file.metadata --path ./some-file`: basic metadata.
- `phantom-sec run file.directory-size --path ./some-folder`: directory size.

## Network diagnostics
- `phantom-sec run network.interfaces`: local interface names.
- `phantom-sec run network.dns --domain example.com`: DNS lookup.
- `phantom-sec run network.reverse-dns --address 1.1.1.1`: reverse DNS lookup.

## Module Workshop and reports
- `phantom-sec create-module demo.sample "Sample Module" --output module.json`: create metadata template only.
- `phantom-sec validate-module module.json`: validate metadata only.
- `phantom-sec history --limit 20`: view local run history.
- `phantom-sec export-history json --output history.json`: export history as JSON.
- `phantom-sec export-history csv --output history.csv`: export history as CSV.

History is stored locally in `~/.local/share/phantom-sec/phantom-sec.sqlite3`. It may contain file paths and result data, so review exports before sharing them. No third-party plugin code is executed.
