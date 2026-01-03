# 🐝 SwarmHealth — Sovereign Medical AI Infrastructure

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   Medical AI that never leaves your building.                               ║
║   No cloud. No vendor. No jeets.                                            ║
║                                                                              ║
║   💎 Diamond Hands Edition                                                  ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## 🏗️ Architecture

```
CLIENT → STINGER → QUEENBEE → BUMBLE70B → PDF → CLIENT
         (Gateway)  (Models)   (Reasoning)  (Report)
```

Every component has an ENS identity on Ethereum mainnet (Chain ID: 1):

| Component | ENS Domain | Role |
|-----------|-----------|------|
| SwarmOS | swarmos.eth | Root Identity |
| Stinger | stinger.swarmbee.eth | Gateway |
| QueenBee | queenbee.swarmbee.eth | Model Orchestrator |
| Bumble | bumble.swarmbee.eth | 70B Inference |
| SwarmPool | swarmpool.swarmbee.eth | Job Ledger |
| Merlin | merlin.swarmbee.eth | Air-Gapped Signer |

---

## 📦 Repository Structure

```
swarmhealth/
├── stinger-v2/           # Intelligent Medical AI Gateway
│   ├── stinger/          # Main Python package
│   ├── tests/            # E2E tests
│   ├── Dockerfile        # Production container
│   └── docker-compose.yml
│
├── trustcat-site/        # TrustCat.ai landing page
│   └── index.html        # Midnight blue edition
│
├── models/               # Model cards & configs
│   ├── queenbee-cardiac/
│   ├── queenbee-spine-detect/
│   ├── queenbee-ecg-classifier/
│   └── queenbee-ecg-transformer/
│
└── docs/                 # Documentation
    ├── validation/       # E2E validation results
    └── compliance/       # HIPAA, FDA, MDR mappings
```

---

## 🏆 Validated Models

| Model | Task | Performance | Dataset |
|-------|------|-------------|---------|
| queenbee-cardiac | MRI Segmentation | 79.5% Dice | ACDC |
| queenbee-spine-detect | X-ray Detection | 44.5% mAP@50 | VinDr-SpineXR |
| queenbee-ecg-classifier | ECG Classification | 58% F1 | PTB-XL |
| queenbee-ecg-transformer | ECG Foundation | 89.1% AUC | PTB-XL |

---

## 📊 E2E Validation Results

```
╔══════════════════════════════════════════════════════════════════════════════╗
║   MODALITY          SAMPLES    SUCCESS    NOTES                             ║
╠══════════════════════════════════════════════════════════════════════════════╣
║   🦴 Spine X-ray     40         97.5%     Production ready                  ║
║   ❤️  ECG            40         100%      89% AUC transformer               ║
║   📈 CGM             20         100%      Time series validated             ║
╠══════════════════════════════════════════════════════════════════════════════╣
║   📊 TOTAL          100         99%       PRODUCTION READY                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## 🚀 Quick Start

### Stinger V2 (Gateway)

```bash
cd stinger-v2
pip install -e ".[full]"
uvicorn stinger.main:app --host 0.0.0.0 --port 8100
```

### Docker Deployment

```bash
cd stinger-v2
docker-compose up -d
```

### API Usage

```bash
# Health check
curl http://localhost:8100/

# Analyze a study
curl -X POST http://localhost:8100/analyze \
  -F "file=@ecg_sample.xml" \
  -F "patient_id=TEST001"

# Get job status
curl http://localhost:8100/job/{job_id}
```

---

## 🔐 Security & Compliance

- **Air-Gapped Ready**: Full operation without internet
- **HIPAA Friendly**: Data never leaves your LAN
- **Cryptographic Proof**: Merkle trees + EIP-191 signatures
- **Audit Trail**: Every job recorded to SwarmPool ledger

### Compliance Mappings

| Standard | Coverage |
|----------|----------|
| HIPAA Security Rule | Full data residency |
| FDA 21 CFR Part 11 | Deterministic outputs, audit trails |
| EU MDR Article 14 | Traceable validation |

---

## 🏠 Infrastructure

```
╔══════════════════════════════════════════════════════════════════════════════╗
║   HARDWARE                                                                  ║
╠══════════════════════════════════════════════════════════════════════════════╣
║   RTX 5090:        48 cards                                                 ║
║   RTX 6000 Ada:    48 cards                                                 ║
║   RTX 3090:        200 cards                                                ║
║   Total:           296 GPUs                                                 ║
║   Network:         10G Fiber                                                ║
║   Power:           Solar + Battery                                          ║
║   Location:        Florida, USA                                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## 📜 License

Apache 2.0

---

## 🏢 Built by

**SudoHash LLC** — Florida, USA

- 🌐 [trustcat.ai](https://trustcat.ai)
- 🔗 [swarmos.eth.limo](https://swarmos.eth.limo)
- 📧 pilot@trustcat.ai
- 📞 561-532-7120

---

## 💎 Philosophy

```
Cloud AI asks you to trust.
We ask you to verify.

No shortcuts. No quick wins. No jeets.
Diamond hands.
```

---

**January 3, 2025** — The day sovereign medical AI became real.
