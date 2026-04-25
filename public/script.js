document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const maxResultsSlider = document.getElementById('max-results');
    const maxValSpan = document.getElementById('max-val');
    const scrapeForm = document.getElementById('scrape-form');
    const statusIndicator = document.getElementById('scrape-status');
    const datasetSelect = document.getElementById('dataset-select');
    const refreshBtn = document.getElementById('refresh-btn');
    const downloadBtn = document.getElementById('download-btn');
    const searchInput = document.getElementById('search-input');
    const tableBody = document.getElementById('table-body');

    // Theme Toggle Elements
    const themeToggle = document.getElementById('theme-toggle');
    const moonIcon = document.getElementById('moon-icon');
    const sunIcon = document.getElementById('sun-icon');

    // Metrics Elements
    const metricTotal = document.getElementById('metric-total');
    const metricHQ = document.getElementById('metric-hq');
    const metricWA = document.getElementById('metric-wa');

    let currentDataset = [];
    let currentRawCSV = "";

    // -- THEME LOGIC --
    const applyTheme = (theme) => {
        if (theme === 'dark') {
            document.documentElement.setAttribute('data-theme', 'dark');
            moonIcon.style.display = 'none';
            sunIcon.style.display = 'block';
        } else {
            document.documentElement.removeAttribute('data-theme');
            moonIcon.style.display = 'block';
            sunIcon.style.display = 'none';
        }
    };

    const savedTheme = localStorage.getItem('theme') || 'light';
    applyTheme(savedTheme);

    themeToggle.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

        localStorage.setItem('theme', newTheme);
        applyTheme(newTheme);
    });

    // -- END THEME LOGIC --

    // Sync Slider Value
    maxResultsSlider.addEventListener('input', (e) => {
        maxValSpan.textContent = e.target.value;
    });

    // Configuration / API endpoint (works on same domain or specific host)
    // For Vercel production, you would point this to your Render/Railway backend.
    const API_BASE = "https://darion-lead-scraper.onrender.com";

    // Fetch available datasets
    async function fetchDatasets() {
        try {
            const res = await fetch(`${API_BASE}/api/leads`);
            const data = await res.json();

            datasetSelect.innerHTML = '';

            if (!data.datasets || data.datasets.length === 0) {
                datasetSelect.innerHTML = '<option value="">No data available</option>';
                return;
            }

            datasetSelect.innerHTML = '<option value="">Select a dataset...</option>';
            data.datasets.forEach(file => {
                const option = document.createElement('option');
                option.value = file;
                // Prettify name: leads_london.csv -> London
                let cleanName = file.replace('leads_', '').replace('.csv', '').split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
                option.textContent = cleanName;
                datasetSelect.appendChild(option);
            });

        } catch (error) {
            console.error('Error fetching datasets:', error);
            datasetSelect.innerHTML = '<option value="">Error loading datasets</option>';
        }
    }

    // Load Specific Dataset
    async function loadDataset(filename) {
        if (!filename) return;

        tableBody.innerHTML = `<tr><td colspan="7" class="empty-state">Loading data...</td></tr>`;

        try {
            const res = await fetch(`${API_BASE}/api/leads/${filename}`);
            const payload = await res.json();

            currentDataset = payload.data;
            updateMetrics(payload.metrics);
            renderTable(currentDataset);

            downloadBtn.disabled = false;
        } catch (error) {
            console.error('Error loading dataset:', error);
            tableBody.innerHTML = `<tr><td colspan="7" class="empty-state">Failed to load dataset.</td></tr>`;
        }
    }

    // Update Metrics Board
    function updateMetrics(metrics) {
        metricTotal.textContent = metrics.total;
        metricHQ.textContent = metrics.high_quality;
        metricWA.textContent = metrics.whatsapp;
    }

    // Render Table Data
    function renderTable(data) {
        if (!data || data.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="7" class="empty-state">No matching records found.</td></tr>`;
            return;
        }

        tableBody.innerHTML = '';

        data.forEach(row => {
            const tr = document.createElement('tr');

            // Score Badge
            const score = row.score || 0;
            let scoreClass = 'score-low';
            if (score >= 70) scoreClass = 'score-high';
            else if (score >= 50) scoreClass = 'score-med';

            // WA Badge
            const hasWA = row.has_whatsapp ? `<span class="wa-badge">✓ Yes</span>` : '<span style="color:var(--text-muted)">-</span>';

            // Website link
            const website = row.website ? `<a href="${row.website}" target="_blank" style="color:var(--primary)">Visit Site</a>` : '-';

            tr.innerHTML = `
                <td><span class="score-badge ${scoreClass}">${score}</span></td>
                <td style="font-weight: 500">${row.business_name || 'N/A'}</td>
                <td style="color:var(--text-muted)">${row.category || 'N/A'}</td>
                <td>${website}</td>
                <td>${row.phone_number || '-'}</td>
                <td>${hasWA}</td>
                <td style="color:var(--text-muted)">${row.rating || '-'} (${row.reviews_count || 0})</td>
            `;
            tableBody.appendChild(tr);
        });
    }

    // Handle Form Submission (Start Scraper)
    scrapeForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const city = document.getElementById('city').value;
        const category = document.getElementById('category').value;
        const maxResults = document.getElementById('max-results').value;

        // Show status
        statusIndicator.classList.remove('hidden');

        try {
            const res = await fetch(`${API_BASE}/api/scrape`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    city: city,
                    category: category,
                    max_results: parseInt(maxResults)
                })
            });

            if (res.ok) {
                // Background job started
                setTimeout(() => {
                    statusIndicator.classList.add('hidden');
                    alert("Scraping completed! Refreshing datasets.");
                    fetchDatasets();
                }, 10000); // Poll or assume finished soon for UX demo
            }
        } catch (error) {
            console.error('Error starting scrape:', error);
            alert('Failed to start scraper API.');
            statusIndicator.classList.add('hidden');
        }
    });

    // Event Listeners for UI
    datasetSelect.addEventListener('change', (e) => {
        loadDataset(e.target.value);
    });

    refreshBtn.addEventListener('click', () => {
        fetchDatasets();
        if (datasetSelect.value) {
            loadDataset(datasetSelect.value);
        }
    });

    searchInput.addEventListener('input', (e) => {
        const term = e.target.value.toLowerCase();
        if (!currentDataset.length) return;

        const filtered = currentDataset.filter(row => {
            const nameMatch = row.business_name && String(row.business_name).toLowerCase().includes(term);
            const webMatch = row.website && String(row.website).toLowerCase().includes(term);
            return nameMatch || webMatch;
        });

        renderTable(filtered);
    });

    // CSV Download mechanism (Client-side from loaded JSON)
    downloadBtn.addEventListener('click', () => {
        if (!currentDataset.length) return;

        const headers = Object.keys(currentDataset[0]);
        const csvRows = [headers.join(',')];

        currentDataset.forEach(row => {
            const values = headers.map(header => {
                const val = String(row[header] || '');
                return `"${val.replace(/"/g, '""')}"`;
            });
            csvRows.push(values.join(','));
        });

        const blob = new Blob([csvRows.join('\n')], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.setAttribute('hidden', '');
        a.setAttribute('href', url);
        a.setAttribute('download', datasetSelect.value || 'filtered_leads.csv');
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    });

    // Init
    fetchDatasets();
});
