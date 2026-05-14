# FortiGate Application Control IDs

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
get application list
diagnose application list
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
