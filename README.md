# ReproHum-0744-02

This repository contains tools and scripts for quantified reproducibility assessment of NLP results through human evaluation data analysis. The project implements methodologies described in Belz, Popovic & Mille (2022) "Quantified Reproducibility Assessment of NLP Results" (ACL'22).

## Overview

The project analyzes human evaluation data for different NLP systems, providing:

- Statistical reliability metrics (Fleiss Kappa, Krippendorff's Alpha)
- ANOVA and Tukey HSD tests for system comparisons
- Power analysis and effect size calculations
- Coefficient of variation (CV) analysis for reproducibility assessment

## Project Structure

```text
.
├── src/                      # Source code directory
│   ├── analyze_responses.py  # Main analysis script
│   ├── cv.py                # Coefficient of variation calculations
│   ├── statistical_power_analysis.py # Statistical power analysis
│   └── preprocess_responses.py # Data preprocessing
├── responses/               # Input data directory
├── results/                # Analysis output directory
│   ├── lab1/              # Primary results
│   └── original/          # Original data results
└── power_analysis.r       # R script for power analysis
```

## Prerequisites

- Docker (optional, for containerized environment)
- Python 3.x
- Required packages:
  - pandas
  - scipy
  - statsmodels
  - krippendorff

## Setup

Clone the repository and install the required packages. You can use a virtual environment or Docker for isolation.

```bash
docker build -t reprohum-0744-02 .
docker run -it --rm -v $(pwd):/app reprohum-0744-02
```

## Usage

1. Preprocess the response data (requires original responses, you can skip this version if you are loading the preprocessed data from this repository):

   ```bash
   python src/preprocess_responses.py
   ```

2. Run the analysis pipeline:

   ```bash
   python src/analyze_responses.py
   ```

3. Generate reproducibility metrics:

   ```bash
   python src/quantified_reproducibility.py
   ```

## Output

The analysis generates several outputs in the `results/lab1/` directory:

- Statistical test results (`anova_tukeyhsd.txt`)
- Inter-rater reliability metrics (`fleiss_kappa.txt`, `krippendorff_alpha.txt`)
- Dataset usage statistics (`tables/datasets_used.csv`)
- System comparison results (`tables/results.csv`)
- Detailed reliability data (`reliability_data.csv`)
- Coefficient of variation analysis (`cv_2_way.csv`, `cv_summary.csv`)
- Correlation analysis (`correlations.csv`)
- Best-Worst system results (`results.csv`)

## Citation

If you use this software in your research, please cite:

```bibtex
TBA
```

## License

This project is licensed under CC-BY-4.0. See the LICENSE file for details.
