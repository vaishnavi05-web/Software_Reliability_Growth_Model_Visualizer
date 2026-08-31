"""
Software Reliability Growth Models (SRGMs) Module
Provides mathematical formulations, parameter estimation via scipy optimization,
goodness-of-fit evaluation metrics, and failure intensity/reliability forecasting.
"""

import numpy as np
from scipy.optimize import curve_fit, minimize


# ==========================================
# 1. Model Formulations (Cumulative Failures & Failure Intensity)
# ==========================================

class GoelOkumotoModel:
    """
    Goel-Okumoto (GO) Non-Homogeneous Poisson Process (NHPP) Model
    Cumulative Failures: m(t) = a * (1 - exp(-b * t))
    Failure Intensity: lambda(t) = a * b * exp(-b * t)
    """
    name = "Goel-Okumoto (GO)"
    param_names = ["a (Expected Total Defects)", "b (Fault Detection Rate)"]

    @staticmethod
    def m(t, a, b):
        t = np.maximum(t, 0)
        return a * (1.0 - np.exp(-b * t))

    @staticmethod
    def failure_intensity(t, a, b):
        t = np.maximum(t, 0)
        return a * b * np.exp(-b * t)

    @staticmethod
    def initial_params(t_data, y_data):
        a_init = float(y_data[-1] * 1.3 + 1.0)
        b_init = 0.05
        return [a_init, b_init], [(0.1, 1e-6), (np.inf, 10.0)]


class JelinskiMorandaModel:
    """
    Jelinski-Moranda (JM) De-Eutrophiation / Reliability Model
    Continuous Approximation:
    Cumulative Failures: m(t) = N * (1 - exp(-phi * t))
    Failure Intensity: lambda(t) = N * phi * exp(-phi * t)
    """
    name = "Jelinski-Moranda (JM)"
    param_names = ["N (Initial Fault Content)", "phi (Fault Detection Proportionality)"]

    @staticmethod
    def m(t, N, phi):
        t = np.maximum(t, 0)
        return N * (1.0 - np.exp(-phi * t))

    @staticmethod
    def failure_intensity(t, N, phi):
        t = np.maximum(t, 0)
        return N * phi * np.exp(-phi * t)

    @staticmethod
    def initial_params(t_data, y_data):
        N_init = float(y_data[-1] * 1.2 + 2.0)
        phi_init = 0.03
        return [N_init, phi_init], [(0.1, 1e-6), (np.inf, 5.0)]


class MusaOkumotoModel:
    """
    Musa-Okumoto Logarithmic Poisson Model
    Cumulative Failures: m(t) = (1 / theta) * ln(1 + lambda0 * theta * t)
    Failure Intensity: lambda(t) = lambda0 / (1 + lambda0 * theta * t)
    """
    name = "Musa-Okumoto Logarithmic Poisson"
    param_names = ["lambda_0 (Initial Failure Rate)", "theta (Intensity Decay Parameter)"]

    @staticmethod
    def m(t, lambda0, theta):
        t = np.maximum(t, 0)
        arg = np.maximum(1.0 + lambda0 * theta * t, 1e-9)
        return (1.0 / np.maximum(theta, 1e-9)) * np.log(arg)

    @staticmethod
    def failure_intensity(t, lambda0, theta):
        t = np.maximum(t, 0)
        denom = np.maximum(1.0 + lambda0 * theta * t, 1e-9)
        return lambda0 / denom

    @staticmethod
    def initial_params(t_data, y_data):
        lambda0_init = float((y_data[1] - y_data[0]) / max((t_data[1] - t_data[0]), 1.0)) if len(y_data) > 1 else 1.0
        lambda0_init = max(lambda0_init, 0.5)
        theta_init = 0.01
        return [lambda0_init, theta_init], [(1e-4, 1e-6), (100.0, 5.0)]


class YamadaSShapedModel:
    """
    Yamada S-Shaped Reliability Growth Model (S-Shaped NHPP)
    Cumulative Failures: m(t) = a * (1 - (1 + b * t) * exp(-b * t))
    Failure Intensity: lambda(t) = a * (b^2) * t * exp(-b * t)
    """
    name = "Yamada S-Shaped Model"
    param_names = ["a (Expected Total Defects)", "b (Fault Isolation Rate)"]

    @staticmethod
    def m(t, a, b):
        t = np.maximum(t, 0)
        return a * (1.0 - (1.0 + b * t) * np.exp(-b * t))

    @staticmethod
    def failure_intensity(t, a, b):
        t = np.maximum(t, 0)
        return a * (b ** 2) * t * np.exp(-b * t)

    @staticmethod
    def initial_params(t_data, y_data):
        a_init = float(y_data[-1] * 1.25 + 1.0)
        b_init = 0.08
        return [a_init, b_init], [(0.1, 1e-6), (np.inf, 5.0)]


MODEL_REGISTRY = {
    'goel_okumoto': GoelOkumotoModel,
    'jelinski_moranda': JelinskiMorandaModel,
    'musa_okumoto': MusaOkumotoModel,
    'yamada_sshaped': YamadaSShapedModel
}


# ==========================================
# 2. Benchmark Datasets
# ==========================================

SAMPLE_DATASETS = {
    "musa_dataset_1": {
        "title": "Musa Real Software Failure Data (Dataset 1)",
        "description": "Standard benchmark dataset collected by John Musa at Bell Labs (Real-time Command & Control System).",
        "time_unit": "Testing Hours",
        "data": [
            {"time": 10, "cumulative_failures": 7},
            {"time": 25, "cumulative_failures": 18},
            {"time": 45, "cumulative_failures": 29},
            {"time": 70, "cumulative_failures": 42},
            {"time": 100, "cumulative_failures": 58},
            {"time": 135, "cumulative_failures": 69},
            {"time": 175, "cumulative_failures": 81},
            {"time": 220, "cumulative_failures": 93},
            {"time": 270, "cumulative_failures": 102},
            {"time": 330, "cumulative_failures": 110},
            {"time": 400, "cumulative_failures": 118},
            {"time": 480, "cumulative_failures": 124},
            {"time": 570, "cumulative_failures": 129},
            {"time": 670, "cumulative_failures": 133},
            {"time": 780, "cumulative_failures": 136}
        ]
    },
    "ntds_dataset": {
        "title": "Navy Tactical Data System (NTDS)",
        "description": "Classic software reliability dataset from the U.S. Navy Tactical Data System module testing phase.",
        "time_unit": "Testing Days",
        "data": [
            {"time": 5, "cumulative_failures": 5},
            {"time": 12, "cumulative_failures": 10},
            {"time": 19, "cumulative_failures": 14},
            {"time": 27, "cumulative_failures": 18},
            {"time": 36, "cumulative_failures": 21},
            {"time": 46, "cumulative_failures": 24},
            {"time": 58, "cumulative_failures": 26},
            {"time": 71, "cumulative_failures": 28},
            {"time": 86, "cumulative_failures": 29},
            {"time": 104, "cumulative_failures": 30},
            {"time": 125, "cumulative_failures": 31}
        ]
    },
    "telecom_release": {
        "title": "Telecommunication Software System (Release 4)",
        "description": "System test execution failures of a major telecom switching control software platform.",
        "time_unit": "Execution Weeks",
        "data": [
            {"time": 1, "cumulative_failures": 4},
            {"time": 2, "cumulative_failures": 11},
            {"time": 3, "cumulative_failures": 22},
            {"time": 4, "cumulative_failures": 35},
            {"time": 5, "cumulative_failures": 48},
            {"time": 6, "cumulative_failures": 57},
            {"time": 7, "cumulative_failures": 65},
            {"time": 8, "cumulative_failures": 71},
            {"time": 9, "cumulative_failures": 76},
            {"time": 10, "cumulative_failures": 80},
            {"time": 11, "cumulative_failures": 83},
            {"time": 12, "cumulative_failures": 85}
        ]
    }
}


# ==========================================
# 3. Model Fitting & Metric Computation Engine
# ==========================================

def calculate_metrics(y_true, y_pred, num_params):
    """
    Computes standard SEQA metrics: MSE, RMSE, R-Squared (R2), and AIC.
    """
    y_true = np.array(y_true, dtype=float)
    y_pred = np.array(y_pred, dtype=float)
    n = len(y_true)

    residuals = y_true - y_pred
    mse = np.mean(residuals ** 2)
    rmse = np.sqrt(mse)

    ss_res = np.sum(residuals ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    r2 = 1.0 - (ss_res / max(ss_tot, 1e-9))
    r2 = max(min(r2, 1.0), -1.0)

    aic = n * np.log(max(mse, 1e-9)) + 2 * num_params

    return {
        "mse": round(float(mse), 4),
        "rmse": round(float(rmse), 4),
        "r2": round(float(r2), 4),
        "aic": round(float(aic), 4)
    }


def fit_single_model(model_key, t_data, y_data, forecast_horizon=10, target_intensity=0.01):
    """
    Fits a specific SRGM model to cumulative failure data (t_data, y_data).
    """
    if model_key not in MODEL_REGISTRY:
        raise ValueError(f"Unknown model key: {model_key}")

    model_cls = MODEL_REGISTRY[model_key]
    t_arr = np.array(t_data, dtype=float)
    y_arr = np.array(y_data, dtype=float)

    p0, (bounds_lower, bounds_upper) = model_cls.initial_params(t_arr, y_arr)

    try:
        popt, _ = curve_fit(
            model_cls.m,
            t_arr,
            y_arr,
            p0=p0,
            bounds=(bounds_lower, bounds_upper),
            maxfev=5000
        )
    except Exception:
        def loss_fn(params):
            preds = model_cls.m(t_arr, *params)
            return np.sum((y_arr - preds) ** 2)

        res = minimize(loss_fn, p0, method='Nelder-Mead')
        popt = res.x

    y_pred = model_cls.m(t_arr, *popt)
    metrics = calculate_metrics(y_arr, y_pred, len(popt))

    t_max = t_arr[-1]
    t_ext = np.linspace(0, t_max + forecast_horizon, 100)
    m_ext = model_cls.m(t_ext, *popt)
    intensity_ext = model_cls.failure_intensity(t_ext, *popt)

    total_est_defects = float(popt[0]) if model_key != 'musa_okumoto' else None
    current_failures = y_arr[-1]
    remaining_defects = max(round(total_est_defects - current_failures, 2), 0.0) if total_est_defects is not None else "N/A (Infinite capacity log model)"

    current_intensity = float(model_cls.failure_intensity(t_max, *popt))
    target_time_req = "Achieved" if current_intensity <= target_intensity else "N/A"

    if current_intensity > target_intensity:
        search_grid = np.linspace(t_max, t_max + 1000, 2000)
        grid_intensities = model_cls.failure_intensity(search_grid, *popt)
        under_target = search_grid[grid_intensities <= target_intensity]
        if len(under_target) > 0:
            target_time_req = round(float(under_target[0] - t_max), 2)
        else:
            target_time_req = "> 1000 additional units"

    params_dict = {}
    for idx, p_name in enumerate(model_cls.param_names):
        params_dict[p_name] = round(float(popt[idx]), 6)

    return {
        "model_key": model_key,
        "model_name": model_cls.name,
        "parameters": params_dict,
        "metrics": metrics,
        "current_intensity": round(current_intensity, 4),
        "total_expected_defects": round(total_est_defects, 2) if total_est_defects else "Unbounded",
        "remaining_defects": remaining_defects,
        "target_time_required": target_time_req,
        "t_fitted": t_arr.tolist(),
        "y_fitted": y_pred.tolist(),
        "t_forecast": t_ext.tolist(),
        "m_forecast": m_ext.tolist(),
        "intensity_forecast": intensity_ext.tolist(),
        "residuals": (y_arr - y_pred).tolist()
    }


def fit_all_models(t_data, y_data, forecast_horizon=10, target_intensity=0.01):
    """
    Fits all registered models against dataset and ranks them by R-Squared / RMSE.
    """
    results = {}
    for key in MODEL_REGISTRY:
        try:
            results[key] = fit_single_model(key, t_data, y_data, forecast_horizon, target_intensity)
        except Exception as e:
            results[key] = {
                "model_key": key,
                "model_name": MODEL_REGISTRY[key].name,
                "error": str(e)
            }
    
    valid_results = [r for r in results.values() if "metrics" in r]
    sorted_by_fit = sorted(valid_results, key=lambda x: (x["metrics"]["r2"], -x["metrics"]["rmse"]), reverse=True)
    
    best_model_key = sorted_by_fit[0]["model_key"] if sorted_by_fit else None

    return {
        "models": results,
        "best_model_key": best_model_key,
        "data_summary": {
            "num_points": len(t_data),
            "max_time": float(t_data[-1]),
            "total_observed_failures": float(y_data[-1])
        }
    }
