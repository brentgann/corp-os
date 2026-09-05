# Pricing

> Personnel context on this exists — see `sensitive.md`.

### CL-0001 — Northwind named per-seat cost as their renewal obstacle
- **Statement**: Northwind's finance lead said per-seat pricing is the primary obstacle to renewing at current volume.
- **Kind**: fact
- **Jobs**: job-001
- **Confidence**: confirmed
- **Source**: raw/2026-08-12--meeting--northwind-qbr.md
- **Citation**: "At this seat count the math stops working for us." — Dana Okafor, 2026-08-12
- **Decay**: 90d
- **Verified**: 2026-08-12

### CL-0002 — Mid-market buyers are assumed to prefer predictable billing
- **Statement**: Mid-market buyers prefer predictable billing over usage-based pricing.
- **Kind**: assumption
- **Jobs**: job-001
- **Confidence**: needs_review
- **Source**: no source
- **Citation**: no source
- **Decay**: none

### CL-0004 — Northwind's renewal champion is leaving in March
- **Statement**: Dana Okafor, the Northwind-side champion for the renewal, has told us privately she is leaving the company in March.
- **Kind**: fact
- **Jobs**: job-001
- **Confidence**: confirmed
- **Source**: raw/2026-08-12--meeting--northwind-qbr.md
- **Citation**: "Between us — I'm out in March, so whatever we agree needs to survive me." — Dana Okafor, 2026-08-12
- **Sensitivity**: sensitive
- **Bearing**: load_bearing
- **Decay**: 90d
- **Verified**: 2026-08-12
- **Note**: Load-bearing, not incidental. Every plan that routes the renewal through Dana is wrong after March, so an answer about the renewal computed without this is not thinner — it is wrong. Stays in the scan path; `corp-os-redact` strips it at the export boundary.
