# 🐝 QueenBee ECG Classifier

**58% F1 Score** — 1D ResNet for ECG classification (baseline)

## Model Details

| Property | Value |
|----------|-------|
| Model Type | 1D ResNet |
| Parameters | 8.7M |
| Model Size | 100MB |
| Task | 5-class ECG classification |
| License | Apache 2.0 |

## Performance

| Class | Precision | Recall | F1 | Support |
|-------|-----------|--------|-----|---------|
| NORM | 0.82 | 0.80 | 0.81 | 963 |
| MI | 0.75 | 0.52 | 0.62 | 544 |
| STTC | 0.50 | 0.70 | 0.58 | 284 |
| CD | 0.52 | 0.64 | 0.57 | 245 |
| HYP | 0.29 | 0.34 | 0.31 | 122 |

### Overall

| Metric | Value |
|--------|-------|
| Accuracy | 67% |
| Macro F1 | 58% |
| Weighted F1 | 68% |

## Training

| Property | Value |
|----------|-------|
| Dataset | PTB-XL |
| Train/Val/Test | 17,084 / 2,146 / 2,158 |
| Epochs | 18 (early stopping) |
| Training Time | ~3 minutes |
| Hardware | 2× RTX 5090 |

## Note

This is a baseline model. For better performance, use `queenbee-ecg-transformer` (89.1% AUC).

## ENS Identity

`queenbee.swarmbee.eth`

## License

Apache 2.0

---

💎 **Diamond Hands Edition** — January 3, 2025
