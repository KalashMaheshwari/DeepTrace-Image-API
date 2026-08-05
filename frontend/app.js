document.addEventListener('DOMContentLoaded', () => {
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('file-input');
    const imagePreviewContainer = document.getElementById('image-preview-container');
    const imagePreview = document.getElementById('image-preview');
    const removeImageBtn = document.getElementById('remove-image-btn');
    const analyzeBtn = document.getElementById('analyze-btn');
    const btnText = analyzeBtn.querySelector('.btn-text');
    const loader = analyzeBtn.querySelector('.loader');
    const resultsSection = document.getElementById('results-section');
    const errorMessage = document.getElementById('error-message');

    let selectedFile = null;
    const API_URL = 'http://localhost:8000/api/v1/analyze'; // Assuming default FastAPI port

    // -- Drag and Drop Events --
    dropzone.addEventListener('click', (e) => {
        if (e.target !== removeImageBtn && !removeImageBtn.contains(e.target)) {
            fileInput.click();
        }
    });

    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
    });

    dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('dragover');
    });

    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleFile(e.target.files[0]);
        }
    });

    // -- File Handling --
    function handleFile(file) {
        if (!file.type.startsWith('image/')) {
            showError("Please upload a valid image file.");
            return;
        }
        
        hideError();
        selectedFile = file;
        
        const reader = new FileReader();
        reader.onload = (e) => {
            imagePreview.src = e.target.result;
            imagePreviewContainer.classList.remove('hidden');
            analyzeBtn.disabled = false;
            resultsSection.classList.add('hidden'); // Hide previous results
        };
        reader.readAsDataURL(file);
    }

    removeImageBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        selectedFile = null;
        fileInput.value = '';
        imagePreviewContainer.classList.add('hidden');
        imagePreview.src = '';
        analyzeBtn.disabled = true;
        resultsSection.classList.add('hidden');
        hideError();
    });

    // -- Analysis API Call --
    analyzeBtn.addEventListener('click', async () => {
        if (!selectedFile) return;

        setLoadingState(true);
        hideError();
        resultsSection.classList.add('hidden');

        const formData = new FormData();
        formData.append('file', selectedFile);

        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'Analysis failed. Make sure the backend is running.');
            }

            const data = await response.json();
            displayResults(data);
        } catch (error) {
            showError(error.message);
        } finally {
            setLoadingState(false);
        }
    });

    // -- UI Updates --
    function setLoadingState(isLoading) {
        analyzeBtn.disabled = isLoading;
        if (isLoading) {
            btnText.classList.add('hidden');
            loader.classList.remove('hidden');
        } else {
            btnText.classList.remove('hidden');
            loader.classList.add('hidden');
        }
    }

    function showError(msg) {
        errorMessage.textContent = msg;
        errorMessage.classList.remove('hidden');
    }

    function hideError() {
        errorMessage.classList.add('hidden');
    }

    function displayResults(data) {
        // Verdict
        const verdictPanel = document.getElementById('verdict-panel');
        const verdictText = document.getElementById('verdict-text');
        const verdictSubtext = document.getElementById('verdict-subtext');
        const circlePath = document.getElementById('confidence-circle-path');
        const scoreVal = document.getElementById('confidence-score');

        // Reset classes
        verdictPanel.classList.remove('status-authentic', 'status-synthetic');
        
        if (data.is_synthetic) {
            verdictPanel.classList.add('status-synthetic');
            verdictText.textContent = "SYNTHETIC / MANIPULATED";
            verdictSubtext.textContent = "High probability of AI generation or deepfake manipulation.";
        } else {
            verdictPanel.classList.add('status-authentic');
            verdictText.textContent = "AUTHENTIC MEDIA";
            verdictSubtext.textContent = "No significant traces of manipulation detected.";
        }

        // Animate Circle
        const score = Math.round(data.confidence_score);
        scoreVal.textContent = score;
        circlePath.setAttribute('stroke-dasharray', `${score}, 100`);

        // Heatmap
        document.getElementById('heatmap-image').src = data.visual_explainability.heatmap_overlay_base64;

        // Breakdown
        const breakdown = data.analysis_breakdown.neural_model_probabilities;
        document.getElementById('raw-prob').textContent = breakdown.raw_fake_probability;
        document.getElementById('heuristic-penalty').textContent = breakdown.heuristic_risk_penalty;
        document.getElementById('threshold-val').textContent = breakdown.threshold_applied;

        // Metadata Table
        const meta = data.analysis_breakdown.forensic_metadata;
        const metaList = document.getElementById('metadata-list');
        metaList.innerHTML = '';
        
        const metaItems = [
            { label: 'Resolution', value: meta.dimensions },
            { label: 'Format', value: meta.format },
            { label: 'EXIF Headers', value: meta.has_exif_headers ? 'Present' : 'Missing', warn: !meta.has_exif_headers },
            { label: 'Software Signature', value: meta.software_signature || 'None', warn: meta.editing_software_detected }
        ];

        metaItems.forEach(item => {
            const li = document.createElement('li');
            li.className = 'metadata-item';
            
            const valClass = item.warn ? 'metadata-value text-warning' : 'metadata-value';
            
            li.innerHTML = `
                <span class="metadata-label">${item.label}</span>
                <span class="${valClass}">${item.value}</span>
            `;
            metaList.appendChild(li);
        });

        // Show Results
        resultsSection.classList.remove('hidden');
        
        // Scroll to results slightly
        setTimeout(() => {
            resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);
    }
});
