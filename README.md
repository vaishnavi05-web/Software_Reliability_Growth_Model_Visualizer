# Software Reliability Growth Model (SRGM) Visualizer

A comprehensive Web application built for **Software Engineering & Quality Assurance (SEQA)** and **Testing & Quality Assurance (TAE)** to fit, evaluate, visualize, and forecast **Software Reliability Growth Models (SRGMs)**.

---

## 📌 Features

- **4 Core Reliability Growth Models**:
  1. **Goel-Okumoto (GO) Model**: Non-Homogeneous Poisson Process (NHPP) exponential defect detection curve.
  2. **Jelinski-Moranda (JM) Model**: Classic hazard rate model based on fault count.
  3. **Musa-Okumoto Logarithmic Model**: Logarithmic NHPP model with decreasing failure intensity per defect repair.
  4. **Yamada S-Shaped Reliability Model**: S-Shaped NHPP model accounting for testing learning curves and ramp-up phases.
- **Robust Non-Linear Optimization**: Automatically fits parameters ($a, b, \phi, \lambda_0, \theta$) using SciPy `curve_fit` and fallback optimization methods.
- **Quantitative Evaluation Metrics**: Calculates $R^2$ (Coefficient of Determination), RMSE, MSE, and Akaike Information Criterion (AIC).
- **Interactive Visualizations (Chart.js)**:
  - Cumulative Failure Growth Plot $m(t)$ with future forecast projections.
  - Failure Intensity Rate decay curve $\lambda(t)$.
  - Modeling Residual Error plot ($y_i - \hat{y}_i$).
- **Reliability Target Calculator**: Estimates remaining software defects and testing time required to reach target failure rate threshold $\lambda_{\text{target}}$.
- **Preloaded Benchmark Datasets**: Includes John Musa's Bell Labs Dataset 1, Navy Tactical Data System (NTDS) dataset, and Telecom system release dataset.
- **Custom Input & File Upload**: Upload custom CSV/TXT failure datasets or paste cumulative / inter-failure timing data directly.
- **Modern Glassmorphic UI**: High-contrast visual design, theme toggle (Dark/Light mode), dynamic metric cards, and PNG chart export.

---

## 📁 Directory Structure

```
Software_Reliability_Growth_Model_Visualizer/
├── app.py                      # Flask Server API Endpoints
├── requirements.txt            # Python Dependencies
├── README.md                   # Technical Documentation & User Manual
│
├── models/
│   └── reliability_model.py    # Math formulations, fitting engine & datasets
│
├── templates/
│   └── index.html              # HTML5 Web Interface
│
└── static/
    ├── css/
    │   └── style.css           # Glassmorphism design system styling
    │
    └── js/
        └── script.js           # Client AJAX engine & Chart.js renderer
```

---

## 📐 Supported SRGM Models & Mathematics

| Model | Cumulative Failure Function $m(t)$ | Failure Intensity $\lambda(t)$ | Parameters |
| :--- | :--- | :--- | :--- |
| **Goel-Okumoto (GO)** | $m(t) = a(1 - e^{-bt})$ | $\lambda(t) = a b e^{-bt}$ | $a$: Total expected defects, $b$: Fault detection rate |
| **Jelinski-Moranda (JM)** | $m(t) = N(1 - e^{-\phi t})$ | $\lambda(t) = N \phi e^{-\phi t}$ | $N$: Initial fault content, $\phi$: Exposure factor |
| **Musa-Okumoto** | $m(t) = \frac{1}{\theta} \ln(1 + \lambda_0 \theta t)$ | $\lambda(t) = \frac{\lambda_0}{1 + \lambda_0 \theta t}$ | $\lambda_0$: Initial failure rate, $\theta$: Decay factor |
| **Yamada S-Shaped** | $m(t) = a(1 - (1 + bt)e^{-bt})$ | $\lambda(t) = a b^2 t e^{-bt}$ | $a$: Total expected defects, $b$: Isolation rate |

---

## 🚀 Quick Start Guide

### 1. Prerequisites
Ensure you have **Python 3.8+** installed on your system.

### 2. Install Dependencies
Open terminal/command prompt in this folder and run:

```bash
pip install -r requirements.txt
```

### 3. Run the Application
Start the Flask web server:

```bash
python app.py
```

### 4. Access Visualizer
Open your browser and navigate to:
```
http://127.0.0.1:5000
```
