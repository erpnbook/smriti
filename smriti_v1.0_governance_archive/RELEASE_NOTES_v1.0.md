# SMRITI Retail OS — Release Notes v1.0 GA

This document describes the General Availability (GA) release of SMRITI Retail OS v1.0. This release establishes a secure, inventory-first retail operating system built on top of ERPNext.

**Founder & Product Architect:**
Jawahar R. Mallah

**Organization:**
AITDL (AI Technology & Development Lab)

---

## 🚀 Key Release Highlights

### 1. SMRITI UI/UX Branding Integrity (Rule 7 Enforcement)
- Standardizes user experiences across Navy Blue (`#1A2B5C`) and Royal Blue (`#2563EB`) interfaces.
- Blocks and redirects all native Frappe `/desk` and setup wizard routes to `/app/smriti-dashboard` to keep back-office interfaces hidden from cashiers and managers.

### 2. POS Register & Barcode Billing
- Dynamic barcode scanning checkout interface at `/app/barcode#pos-dark`.
- Features split payment checkouts (Cash, Card, UPI, Credit) and draft cart hold/recall operations.
- Enforces shift opening and shift closing cash drawer reconciliations.

### 3. GPG Backup Encryption & Security Center
- Adds symmetric AES-256 backup encryption via GPG, eliminating process-sniffing exploits.
- Implements a dual-custodian key split protocol, sending mid-split recovery keys to authorized custodian emails.
- Securely wipes decrypted backup remnants on disk using the UNIX `shred` utility.
- Custom POS manager overrides rate-limited to 5 attempts per 10 minutes.

### 4. Go-Live Readiness checklist
- Dashboard interface located at `/smriti-go-live` verifying 14 readiness checks before store launch.
- Real-time scoring and blocker identification.

---

## 📋 Release Certification Details

- **Unit Tests Status**: 277/277 backend unit tests passing successfully.
- **Health Check Status**: 10/10 checks passing on production database schemas.
- **Go-Live Readiness**: Verified at 93% Readiness Score.

---

## ⚠️ Known Limitations & Workarounds
- **Offline Limits**: Register operations require a local network connection tomariadb to sync transactions. Offline sales buffering is queued for a future v1.1 release.
- **License Binding**: Key activations are locked to unique Installation UUIDs by default. Moving hosts requires key regeneration.
