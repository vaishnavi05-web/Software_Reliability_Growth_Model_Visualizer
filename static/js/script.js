/**
 * Software Reliability Growth Model Visualizer - Client Logic
 */

let cumulativeChartInstance = null;
let intensityChartInstance = null;
let residualChartInstance = null;
let sampleDatasetsCache = {};

const MODEL_COLORS = {
    goel_okumoto: { border: '#6366f1', fill: 'rgba(99, 102, 241, 0.1)', name: 'Goel-Okumoto' },
    jelinski_moranda: { border: '#10b981', fill: 'rgba(16, 185, 129, 0.1)', name: 'Jelinski-Moranda' },
    musa_okumoto: { border: '#f59e0b', fill: 'rgba(245, 158, 11, 0.1)', name: 'Musa-Okumoto' },
    yamada_sshaped: { border: '#a855f7', fill: 'rgba(168, 85, 247, 0.1)', name: 'Yamada S-Shaped' }
};

document.addEventListener('DOMContentLoaded', () => {
    initThemeToggle();
    initSampleDataSelector();
    initFileUploadHandler();
    initToggleButtons();
    
    document.getElementById('btn-fit-models').addEventListener('click', handleFitModels);
    document.getElementById('btn-reset-data').addEventListener('click', handleReset);

    handleFitModels();
});

function initThemeToggle() {
    const btn = document.getElementById('btn-theme-toggle');
    btn.addEventListener('click', () => {
        document.body.classList.toggle('light-theme');
        const isLight = document.body.classList.contains('light-theme');
        btn.innerHTML = isLight ? '<i class="fa-solid fa-sun"></i>' : '<i class="fa-solid fa-moon"></i>';
    });
}

function switchTab(tabId) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));

    const activeBtn = Array.from(document.querySelectorAll('.tab-btn')).find(b => b.getAttribute('onclick').includes(tabId));
    if (activeBtn) activeBtn.classList.add('active');

    const targetPane = document.getElementById(tabId);
    if (targetPane) targetPane.classList.add('active');
}

function initToggleButtons() {
    const toggleBtns = document.querySelectorAll('.toggle-btn');
    toggleBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            toggleBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const radio = btn.querySelector('input[type="radio"]');
            if (radio) radio.checked = true;
        });
    });
}

async function initSampleDataSelector() {
    const select = document.getElementById('sample-dataset-select');
    try {
        const response = await fetch('/api/sample_data');
        const res = await response.json();
        if (res.status === 'success') {
            sampleDatasetsCache = res.datasets;
            for (const key in sampleDatasetsCache) {
                const opt = document.createElement('option');
                opt.value = key;
                opt.textContent = sampleDatasetsCache[key].title;
                select.appendChild(opt);
            }

            select.value = 'musa_dataset_1';
            loadSampleDataset('musa_dataset_1');

            select.addEventListener('change', (e) => {
                if (e.target.value) {
                    loadSampleDataset(e.target.value);
                }
            });
        }
    } catch (err) {
        console.error('Failed to load sample datasets:', err);
    }
}

function loadSampleDataset(key) {
    const ds = sampleDatasetsCache[key];
    if (!ds) return;

    let text = "Time, Cumulative Failures\n";
    ds.data.forEach(item => {
        text += `${item.time}, ${item.cumulative_failures}\n`;
    });

    document.getElementById('data-input-text').value = text.trim();
    handleFitModels();
}

function initFileUploadHandler() {
    const fileInput = document.getElementById('file-upload');
    const label = document.getElementById('file-drop-label');

    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (!file) return;

        label.textContent = file.name;
        const reader = new FileReader();
        reader.onload = (event) => {
            document.getElementById('data-input-text').value = event.target.result;
            document.getElementById('sample-dataset-select').value = '';
            handleFitModels();
        };
        reader.readAsText(file);
    });
}

function parseInputData() {
    const text = document.getElementById('data-input-text').value.trim();
    if (!text) return { t_data: [], y_data: [] };

    const lines = text.split('\n');
    const t_data = [];
    const y_data = [];

    lines.forEach(line => {
        const clean = line.trim();
        if (!clean || clean.toLowerCase().startsWith('time') || clean.startsWith('#')) return;

        const parts = clean.split(/[,;\t\s]+/).map(p => parseFloat(p.trim())).filter(p => !isNaN(p));
        if (parts.length >= 2) {
            t_data.push(parts[0]);
            y_data.push(parts[1]);
        }
    });

    return { t_data, y_data };
}

async function handleFitModels() {
    const { t_data, y_data } = parseInputData();

    if (t_data.length === 0 || y_data.length === 0) {
        alert('Please enter or select valid numerical failure data.');
        return;
    }

    const inputType = document.querySelector('input[name="input_type"]:checked').value;
    const forecastHorizon = parseFloat(document.getElementById('forecast-horizon').value) || 50;
    const targetIntensity = parseFloat(document.getElementById('target-intensity').value) || 0.01;

    const selectedModels = Array.from(document.querySelectorAll('input[name="model_select"]:checked')).map(cb => cb.value);

    if (selectedModels.length === 0) {
        alert('Please select at least one SRGM model to fit.');
        return;
    }

    const payload = {
        t_data,
        y_data,
        input_type: inputType,
        forecast_horizon: forecastHorizon,
        target_intensity: targetIntensity,
        selected_models: selectedModels
    };

    try {
        const response = await fetch('/api/fit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const res = await response.json();
        if (res.status === 'success') {
            renderDashboardResults(res.results, res.raw_input);
        } else {
            alert('Error: ' + res.message);
        }
    } catch (err) {
        console.error('Fit API Error:', err);
    }
}

function handleReset() {
    document.getElementById('sample-dataset-select').value = '';
    document.getElementById('data-input-text').value = '';
    document.getElementById('file-upload').value = '';
    document.getElementById('file-drop-label').textContent = 'Upload CSV / TXT Data File';
    
    if (cumulativeChartInstance) cumulativeChartInstance.destroy();
    if (intensityChartInstance) intensityChartInstance.destroy();
    if (residualChartInstance) residualChartInstance.destroy();

    document.getElementById('metric-best-model').textContent = '--';
    document.getElementById('metric-best-r2').textContent = 'R² Score: --';
    document.getElementById('metric-total-failures').textContent = '0';
    document.getElementById('metric-remaining-faults').textContent = '--';
    document.getElementById('metric-target-time').textContent = '--';
}

function renderDashboardResults(results, rawInput) {
    const models = results.models;
    const bestKey = results.best_model_key;
    const bestModel = models[bestKey];

    if (bestModel && bestModel.metrics) {
        document.getElementById('metric-best-model').textContent = bestModel.model_name;
        document.getElementById('metric-best-r2').textContent = `R² Score: ${bestModel.metrics.r2}`;
        document.getElementById('metric-total-failures').textContent = results.data_summary.total_observed_failures;
        document.getElementById('metric-max-time').textContent = `Testing Time: ${results.data_summary.max_time} units`;
        
        document.getElementById('metric-remaining-faults').textContent = bestModel.remaining_defects;
        document.getElementById('metric-target-time').textContent = typeof bestModel.target_time_required === 'number' 
            ? `${bestModel.target_time_required} units` 
            : bestModel.target_time_required;
    }

    renderCumulativeChart(models, rawInput);
    renderIntensityChart(models);
    renderResidualChart(models, rawInput);
    renderComparisonTable(models, bestKey);
}

function renderCumulativeChart(models, rawInput) {
    const ctx = document.getElementById('cumulative-chart').getContext('2d');
    if (cumulativeChartInstance) cumulativeChartInstance.destroy();

    const datasets = [];

    datasets.push({
        label: 'Observed Failures',
        data: rawInput.t_data.map((t, idx) => ({ x: t, y: rawInput.y_data[idx] })),
        borderColor: '#06b6d4',
        backgroundColor: '#06b6d4',
        pointRadius: 5,
        pointHoverRadius: 7,
        showLine: true,
        borderDash: [2, 2],
        fill: false
    });

    for (const key in models) {
        const m = models[key];
        if (m.error) continue;

        const palette = MODEL_COLORS[key] || { border: '#ffffff', fill: 'transparent' };

        datasets.push({
            label: `${m.model_name} (Fit)`,
            data: m.t_forecast.map((t, idx) => ({ x: t, y: m.m_forecast[idx] })),
            borderColor: palette.border,
            backgroundColor: palette.fill,
            borderWidth: 2.5,
            pointRadius: 0,
            tension: 0.3
        });
    }

    cumulativeChartInstance = new Chart(ctx, {
        type: 'scatter',
        data: { datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { labels: { color: '#94a3b8', font: { family: 'Inter' } } },
                tooltip: { mode: 'index', intersect: false }
            },
            scales: {
                x: {
                    type: 'linear',
                    title: { display: true, text: 'Testing Execution Time (t)', color: '#94a3b8' },
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#94a3b8' }
                },
                y: {
                    title: { display: true, text: 'Cumulative Failures m(t)', color: '#94a3b8' },
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#94a3b8' }
                }
            }
        }
    });
}

function renderIntensityChart(models) {
    const ctx = document.getElementById('intensity-chart').getContext('2d');
    if (intensityChartInstance) intensityChartInstance.destroy();

    const datasets = [];

    for (const key in models) {
        const m = models[key];
        if (m.error) continue;

        const palette = MODEL_COLORS[key] || { border: '#ffffff' };

        datasets.push({
            label: `${m.model_name} λ(t)`,
            data: m.t_forecast.map((t, idx) => ({ x: t, y: m.intensity_forecast[idx] })),
            borderColor: palette.border,
            borderWidth: 2,
            pointRadius: 0,
            tension: 0.3
        });
    }

    intensityChartInstance = new Chart(ctx, {
        type: 'scatter',
        data: { datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { labels: { color: '#94a3b8' } }
            },
            scales: {
                x: {
                    type: 'linear',
                    title: { display: true, text: 'Testing Time (t)', color: '#94a3b8' },
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#94a3b8' }
                },
                y: {
                    title: { display: true, text: 'Failure Intensity λ(t) (Failures / Unit Time)', color: '#94a3b8' },
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#94a3b8' }
                }
            }
        }
    });
}

function renderResidualChart(models, rawInput) {
    const ctx = document.getElementById('residual-chart').getContext('2d');
    if (residualChartInstance) residualChartInstance.destroy();

    const datasets = [];

    for (const key in models) {
        const m = models[key];
        if (m.error || !m.residuals) continue;

        const palette = MODEL_COLORS[key] || { border: '#ffffff' };

        datasets.push({
            label: `${m.model_name} Residuals`,
            data: rawInput.t_data.map((t, idx) => ({ x: t, y: m.residuals[idx] })),
            borderColor: palette.border,
            backgroundColor: palette.border,
            pointRadius: 4,
            showLine: true,
            borderWidth: 1.5
        });
    }

    residualChartInstance = new Chart(ctx, {
        type: 'scatter',
        data: { datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { labels: { color: '#94a3b8' } }
            },
            scales: {
                x: {
                    type: 'linear',
                    title: { display: true, text: 'Testing Time (t)', color: '#94a3b8' },
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#94a3b8' }
                },
                y: {
                    title: { display: true, text: 'Residual Error (y_actual - y_pred)', color: '#94a3b8' },
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#94a3b8' }
                }
            }
        }
    });
}

function renderComparisonTable(models, bestKey) {
    const tbody = document.querySelector('#comparison-table tbody');
    tbody.innerHTML = '';

    for (const key in models) {
        const m = models[key];
        const tr = document.createElement('tr');

        if (m.error) {
            tr.innerHTML = `
                <td><strong>${m.model_name}</strong></td>
                <td colspan="7" class="text-muted">Error fitting model: ${m.error}</td>
                <td><span class="badge-best" style="background: rgba(244, 63, 94, 0.2); color: #f43f5e;">Failed</span></td>
            `;
            tbody.appendChild(tr);
            continue;
        }

        const isBest = (key === bestKey);
        const paramsFormatted = Object.entries(m.parameters)
            .map(([k, v]) => `${k.split(' ')[0]}=${v}`)
            .join(', ');

        tr.innerHTML = `
            <td><strong>${m.model_name}</strong> ${isBest ? '<i class="fa-solid fa-star text-amber" style="color:#f59e0b;"></i>' : ''}</td>
            <td class="code-font" style="font-size:0.78rem;">${paramsFormatted}</td>
            <td><strong>${m.metrics.r2}</strong></td>
            <td>${m.metrics.rmse}</td>
            <td>${m.metrics.mse}</td>
            <td>${m.metrics.aic}</td>
            <td>${m.total_expected_defects}</td>
            <td>${m.remaining_defects}</td>
            <td>${isBest ? '<span class="badge-best"><i class="fa-solid fa-check"></i> Best Fit</span>' : '<span style="color:#94a3b8;">Evaluated</span>'}</td>
        `;

        tbody.appendChild(tr);
    }
}

function exportChart(chartId) {
    let canvas = document.getElementById(chartId);
    if (!canvas) return;

    const imageURI = canvas.toDataURL('image/png');
    const link = document.createElement('a');
    link.download = `${chartId}_export.png`;
    link.href = imageURI;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}
