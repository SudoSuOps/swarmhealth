# Changelog

All notable changes to Stinger V2 will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-01-03

### 🎉 Initial Release — Diamond Hands Edition

The first public release of Stinger V2, the intelligent medical AI gateway.

#### Added

**Core Pipeline**
- Full end-to-end medical AI pipeline: Client → Stinger → QueenBee → Bumble70B → PDF → Client
- FastAPI-based gateway with async processing
- Background job processing with status tracking

**Input Parsers**
- DICOM parser with full metadata extraction
- ECG parser supporting HL7 aECG, SCP-ECG, and WFDB formats
- CGM parser for Dexcom, Libre, and CSV formats
- Automatic input type detection

**Intelligent Routing**
- ML-powered study classification (body region, modality, study type)
- Model orchestrator for multi-model coordination
- GPU load balancer for fleet distribution

**Gold Prompts (QueenBee)**
- 15 clinical-grade prompts following medical guidelines:
  - Spine (ACR guidelines)
  - Cardiac (ASE/SCMR guidelines)
  - Chest (Fleischner Society)
  - Neuro (ASNR guidelines)
  - ECG (AHA/ACC)
  - CGM (ADA Standards of Care)
  - And more...

**Inference (Bumble70B)**
- Integration with Meditron-70B medical reasoning model
- Support for text-only, image+text, and multimodal inference
- Batch inference capability

**Report Generation**
- Clinical-grade PDF reports with TrustCat branding
- Structured findings extraction
- Professional formatting with reportlab

**Cryptographic Proof**
- Merkle tree generation for job attestation
- EIP-191 compliant message signing (Ethereum compatible)
- IPFS pinning for decentralized storage

**Ledger (SwarmPool)**
- SQLite-based job ledger
- Epoch management with automatic sealing
- Full audit trail with cryptographic integrity

**ENS Identity**
- Full ENS domain integration
- Component identities: stinger.swarmbee.eth, queenbee.swarmbee.eth, etc.
- Ethereum mainnet (Chain ID: 1) compatibility

**Deployment**
- Docker and docker-compose support
- Kubernetes-ready configuration
- Systemd service files

#### Infrastructure

- Tested on 2x RTX 5090 (64GB VRAM)
- Full pipeline execution in ~2.3 minutes
- Air-gap ready architecture

#### Security

- LAN-only endpoints by default
- No external API dependencies
- Cryptographic signing for all outputs
- HIPAA-friendly data residency

---

## Models Trained (Same Day)

These QueenBee models were trained on the same infrastructure:

| Model | Task | Performance | Dataset |
|-------|------|-------------|---------|
| queenbee-cardiac | Segmentation | 79.5% Dice | ACDC |
| queenbee-spine | Detection | 44.5% mAP@50 | VinDr-SpineXR |
| queenbee-ecg | Classification | 58% F1 | PTB-XL |

---

## ENS Domains

| Domain | Role |
|--------|------|
| swarmos.eth | Root Identity |
| stinger.swarmbee.eth | Gateway |
| queenbee.swarmbee.eth | Prompt Orchestrator |
| bumble.swarmbee.eth | 70B Inference |
| swarmpool.swarmbee.eth | Job Ledger |
| merlin.swarmbee.eth | Air-Gapped Signer |

---

💎 **Diamond Hands. Full Stack. No Jeets.** 💎
