"""
Software Reliability Growth Model Visualizer - Flask Application
"""

import os
from flask import Flask, render_template, request, jsonify
import numpy as np

from models.reliability_model import (
    MODEL_REGISTRY,
    SAMPLE_DATASETS,
    fit_all_models,
    fit_single_model
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, 
            template_folder=os.path.join(BASE_DIR, 'templates'), 
            static_folder=os.path.join(BASE_DIR, 'static'))


@app.route('/')
def index():
    """Render main application view."""
    return render_template('index.html')


@app.route('/api/sample_data', methods=['GET'])
def get_sample_datasets():
    """Return available benchmark datasets."""
    return jsonify({
        "status": "success",
        "datasets": SAMPLE_DATASETS
    })


@app.route('/api/fit', methods=['POST'])
def fit_models():
    """
    Fit SRGM models based on incoming dataset.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No JSON payload received"}), 400

        t_raw = data.get('t_data', [])
        y_raw = data.get('y_data', [])
        input_type = data.get('input_type', 'cumulative')
        forecast_horizon = float(data.get('forecast_horizon', 10))
        target_intensity = float(data.get('target_intensity', 0.01))
        selected_models = data.get('selected_models', list(MODEL_REGISTRY.keys()))

        if not t_raw or not y_raw or len(t_raw) != len(y_raw):
            return jsonify({
                "status": "error",
                "message": "Invalid input data. Ensure time and failure arrays are equal length non-empty lists."
            }), 400

        t_arr = np.array(t_raw, dtype=float)
        y_arr = np.array(y_raw, dtype=float)

        if input_type == 'intervals':
            t_arr = np.cumsum(t_arr)
            y_arr = np.arange(1, len(t_arr) + 1, dtype=float)

        sort_indices = np.argsort(t_arr)
        t_arr = t_arr[sort_indices]
        y_arr = y_arr[sort_indices]

        fit_results = fit_all_models(
            t_data=t_arr.tolist(),
            y_data=y_arr.tolist(),
            forecast_horizon=forecast_horizon,
            target_intensity=target_intensity
        )

        if selected_models:
            filtered_models = {k: v for k, v in fit_results['models'].items() if k in selected_models}
            fit_results['models'] = filtered_models

        return jsonify({
            "status": "success",
            "results": fit_results,
            "raw_input": {
                "t_data": t_arr.tolist(),
                "y_data": y_arr.tolist()
            }
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Server processing error: {str(e)}"
        }), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    print(f"Starting Software Reliability Growth Model Visualizer on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=True)
