## Calibrating Classification with `--dry-run --explain`

The `--dry-run --explain` mode prints detailed classification scores without modifying files, ideal for testing new keyword rules or debugging misclassifications.

### Basic Usage

```bash
cd library_pipeline
python cli.py --dry-run --explain --file path/to/your/document.pdf
```

### Output Example

```
================================================================================
CLASSIFICATION ANALYSIS: document.pdf
================================================================================

Sources analyzed:
  title        (  128 chars): Deep Learning for Autonomous Systems
  filename     (  23 chars): dl_autonomy
  first_page   ( 1842 chars): Abstract. This paper presents...
  abstract     (  256 chars): This work investigates ...

────────────────────────────────────────────────────────────────────────────────
TYPE Classification:
────────────────────────────────────────────────────────────────────────────────
  Candidates:
    1. PAPER           score=  12.40  matched_terms=4
    2. REPORT          score=   2.10  matched_terms=1
    3. REVIEW          score=   0.85  matched_terms=1

  ✓ SELECTED: PAPER

────────────────────────────────────────────────────────────────────────────────
DOMAIN Classification:
────────────────────────────────────────────────────────────────────────────────
  Candidates:
    1. COMPUTE         score=  18.30  matched_terms=6
       → concepts: machine-learning, neural-networks, deep-learning
    2. FORMAL          score=   6.20  matched_terms=2
       → concepts: verification
    3. ROBOTICS        score=   4.80  matched_terms=1
       → concepts: autonomous-systems

  ✓ PRIMARY: COMPUTE
  ✓ SECONDARY: FORMAL, ROBOTICS

────────────────────────────────────────────────────────────────────────────────
Extracted Metadata:
────────────────────────────────────────────────────────────────────────────────
  Title:      Deep Learning for Autonomous Systems
  Author:     smith
  Year:       2024
  DOI:        (none)
  Concepts:   machine-learning, neural-networks, autonomous-systems

────────────────────────────────────────────────────────────────────────────────
Generated Filename:
────────────────────────────────────────────────────────────────────────────────
  PAPER_COMPUTE_2024_deep-learning-autonomous_smith.pdf
  ✓ Valid
```

### Workflow: Testing New Rules

1. **Identify misclassified documents:**
   ```bash
   python cli.py --dry-run --explain --file "01_input_pdfs/problematic.pdf"
   ```

2. **Review the scores:**
   - Is the correct TYPE in top 3?
   - Is the correct DOMAIN in top 3?
   - Are concepts reasonable?

3. **Adjust `config.yaml`:**
   - Add aliases for missed terms
   - Increase `weight` for correct labels
   - Check `fuzzy` thresholds if typos are involved

4. **Retest:**
   ```bash
   python cli.py --dry-run --explain --file "01_input_pdfs/problematic.pdf"
   ```

### Tuning Parameters

**To fix a missed TYPE or DOMAIN:**

```yaml
# Before
COMPUTE: ["machine learning", "deep learning"]

# After (add weight and concepts)
COMPUTE:
  - { term: "machine learning", weight: 1.5, concepts: ["ml"] }
  - { term: "deep learning", weight: 1.4, concepts: ["deep-learning"] }
  - { term: "neural network", aliases: ["neural networks", "nn"], concepts: ["neural-networks"] }
```

**To reduce false positives:**

- Add more specific terms instead of generic ones
- Lower `secondary_domains.min_relative_score` (currently 0.35) to be stricter
- Increase `fuzzy.threshold` (currently 0.88) to avoid weak fuzzy matches

**To debug scoring:**

- Check field weights in `classification.field_weights`
- Verify normalize() removes accents correctly
- Look at `classification_scores` in `03_metadata/` for actual vs predicted

### Tips

- **Batch test:** Create a small folder with 5–10 representative PDFs and test all with:
  ```bash
  for file in test_batch/*.pdf; do
    python cli.py --dry-run --explain --file "$file"
    echo "---"
  done
  ```
- **Compare before/after:** Run dry-run, adjust config, run dry-run again
- **Preserve fallbacks:** Keep "PAPER" and "META" at the end of config to catch unmatched documents
- **Document changes:** Add a comment in config.yaml explaining why weights were adjusted

### When to Use

- Before running full batch processing on 50+ PDFs
- After merging new keyword rules
- When validating config changes affect accuracy
- To understand why a specific PDF was classified unexpectedly
