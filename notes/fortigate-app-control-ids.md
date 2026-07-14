# FortiGate UTM Signature/ID Databases

Source: https://github.com/Jaimer/FortigateAppControlID

## What it is

A table of every application in FortiGate's Application Control feature, with:
- Application ID (numeric)
- Application name
- Category ID
- Category name
- Technology (Client-Server, Browser-Based, Peer-to-Peer, etc.)

## Where the data came from

The data is **not scraped from docs.fortinet.com** — it comes from the FortiGate device itself.
FortiOS ships with an internal signature database called the FNDB (Fortinet Network Database)
that backs the Application Control engine. You can dump it from the CLI:

```
get application name status
```

```
config application list
    edit "default"
            config entries
                edit 1
                    set category  // hit '?' here!
```

Jaimer almost certainly ran one of these commands on a live FortiGate (or FortiManager),
exported the output to CSV, and posted it to GitHub.

## Why this differs from web filter categories

- Web filter categories (`wfc/`) come from FortiGuard's cloud lookup table and are
  documented at docs.fortinet.com — scrape-able.
- App control IDs are device-local, baked into the firmware's FNDB — not scrape-able
  from any public Fortinet URL.

## How to replicate

You need either:
1. A live FortiGate to run the CLI dump against, or
2. The FNDB files extracted from a FortiOS firmware image.

There is no equivalent public documentation URL to scrape.

## Other UTM profiles with signature/ID databases

### DNS Filter

Uses the **exact same FortiGuard URL category IDs** as web filter.
In `config dnsfilter profile` → `config ftgd-dns` → `config filters` → `set category <ID>`.
Already covered by what `scrape_log_ref.py` scrapes — no separate data source needed.

### IPS (Intrusion Prevention)

Signatures are referenced by **name** (not numeric ID) in `config ips sensor` → `config entries`,
e.g. `"Adobe.Commerce.CVE-2026-34658.XSS"`.

Publicly scrape-able from the FortiGuard encyclopedia:
https://www.fortiguard.com/encyclopedia?type=ips

Hundreds of pages of entries. The key is the name string, not a numeric ID.

### Web Application Firewall (WAF)

Similar to IPS — named signatures, not numeric IDs. FortiGate's built-in WAF is limited;
FortiWeb has the full engine. FortiGuard encyclopedia:
https://www.fortiguard.com/encyclopedia?type=waf

### Internet Service Database (ISDB)

Uses numeric IDs (e.g. `set internet-service-id 65646` in firewall policy config).
FortiGuard publishes these. Device-local like FNDB but partially documented in the encyclopedia:
https://www.fortiguard.com/encyclopedia?type=internet-service

### AntiVirus / Botnet / C&C

No signature IDs in the config — fully managed by FortiGuard push. Not relevant for scraping.

## Summary table

| Feature | Key type | Source | Scrape-able from docs? |
|---|---|---|---|
| Web filter categories | Numeric ID | FortiGuard URL DB | Yes (already done) |
| DNS filter categories | Same numeric ID | Same table as above | Already covered |
| IPS signatures | Name string | FortiGuard IPS encyclopedia | Yes (paginated) |
| App control | Numeric ID | FNDB (device-local) | No |
| WAF signatures | Name string | FortiGuard WAF encyclopedia | Yes |
| ISDB | Numeric ID | FortiGuard / device-local | Partially |
| AV / Botnet / C&C | N/A | Fully managed | N/A |

Best new scrape target: **IPS signatures** — public, paginated, frequently referenced in configs.
