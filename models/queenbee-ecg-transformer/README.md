# 🐝 QueenBee ECG Transformer

**89.1% AUC on PTB-XL** — Foundation model for 12-lead ECG analysis

## Model Details

| Property | Value |
|----------|-------|
| Model Type | Transformer (Self-Attention) |
| Parameters | ~15M |
| Model Size | 57MB |
| Input | 12-lead ECG (1000 samples @ 100Hz) |
| Output | 5 superclasses + 71 SCP codes |
| License | Apache 2.0 |

## Performance

### Superclass AUC

| Class | AUC | Description |
|-------|-----|-------------|
| NORM | 92.8% | Normal ECG |
| MI | 90.1% | Myocardial Infarction |
| STTC | 91.6% | ST/T Change |
| CD | 90.2% | Conduction Disturbance |
| HYP | 81.0% | Hypertrophy |

### Overall Metrics

| Metric | Value |
|--------|-------|
| Superclass Mean AUC | 89.1% |
| Superclass F1 | 64.6% |
| SCP Mean AUC | 84.9% |

## Training

| Property | Value |
|----------|-------|
| Dataset | PTB-XL (21,388 ECGs) |
| Train/Val/Test | 17,084 / 2,146 / 2,158 |
| Epochs | 50 (best @ epoch 10) |
| Training Time | ~18 minutes |
| Hardware | 2× RTX 5090 |
| Task | Multi-task (superclass + SCP) |

## Usage

```python
import torch
from queenbee_ecg import ECGTransformer

# Load model
model = ECGTransformer.from_pretrained("Trustcat/queenbee-ecg-transformer")
model.eval()

# Inference
ecg_signal = torch.randn(1, 12, 1000)  # [batch, leads, samples]
with torch.no_grad():
    predictions = model(ecg_signal)
    
# predictions contains superclass and SCP probabilities
```

## Intended Use

- **Primary**: Clinical decision support for ECG interpretation
- **Secondary**: Research, education, algorithm development
- **NOT for**: Standalone diagnosis without physician review

## Limitations

- Trained on PTB-XL dataset (German population)
- HYP class has lower performance (81% AUC) due to class imbalance
- Requires 10-second, 12-lead ECG at 100Hz
- Not FDA cleared

## Citation

```bibtex
@misc{queenbee-ecg-transformer-2025,
  title={QueenBee ECG Transformer: Foundation Model for 12-Lead ECG Analysis},
  author={TrustCat},
  year={2025},
  publisher={HuggingFace},
  url={https://huggingface.co/Trustcat/queenbee-ecg-transformer}
}
```

## ENS Identity

`queenbee.swarmbee.eth`

## License

Apache 2.0

---

💎 **Diamond Hands Edition** — January 3, 2025
