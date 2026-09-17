document.addEventListener('DOMContentLoaded', () => {
    // Updated UI Elements for Premium Design
    const mainCard = document.getElementById('mainCard');
    const uploadSection = document.getElementById('uploadSection');
    const dropZone = document.getElementById('dropZone');
    const csvInput = document.getElementById('csvInput');
    const uploadBtn = document.getElementById('uploadBtn');
    const batchLoader = document.getElementById('batchLoader');

    // File Status UI
    const fileStatus = document.getElementById('fileStatus');
    const fileNameDisplay = document.getElementById('fileName');
    const clearFileBtn = document.getElementById('clearFileBtn');
    const dropZoneContent = dropZone.querySelector('.upload-hint');

    // Results UI
    const batchResultSection = document.getElementById('batchResultSection');
    const statTotal = document.getElementById('statTotal');
    const statFraud = document.getElementById('statFraud');
    const fraudTable = document.getElementById('fraudTable').querySelector('tbody');
    const exportBtn = document.getElementById('exportBtn');
    let currentAnalysisData = null;

    let selectedFile = null;

    // --- Tab Switching ---
    const tabBatch = document.getElementById('tabBatch');
    const tabSingle = document.getElementById('tabSingle');
    const singleCard = document.getElementById('singleCard');
    // mainCard already defined above

    tabBatch.addEventListener('click', () => {
        tabBatch.classList.add('active');
        tabSingle.classList.remove('active');
        mainCard.classList.remove('hidden');
        singleCard.classList.add('hidden');
        // Hide result if open
        batchResultSection.classList.add('hidden');
    });

    tabSingle.addEventListener('click', () => {
        tabSingle.classList.add('active');
        tabBatch.classList.remove('active');
        singleCard.classList.remove('hidden');
        mainCard.classList.add('hidden');
        batchResultSection.classList.add('hidden');
    });

    // --- Single Check Logic ---
    const singleForm = document.getElementById('singleForm');
    const singleResult = document.getElementById('singleResult');
    const resultBadge = document.getElementById('resultBadge');
    const resConfidence = document.getElementById('resConfidence');
    const resMessage = document.getElementById('resMessage');
    const checkFraudBtn = document.getElementById('checkFraudBtn');

    singleForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Gather Data
        const payload = {
            transaction_type: document.getElementById('sf_type').value,
            amount: parseFloat(document.getElementById('sf_amount').value),
            merchant_category: document.getElementById('sf_category').value,
            sender_bank: document.getElementById('sf_sender_bank').value,
            receiver_bank: document.getElementById('sf_receiver_bank').value,
            device_type: document.getElementById('sf_device').value,
            network_type: document.getElementById('sf_network').value
        };

        // UI Loading
        checkFraudBtn.disabled = true;
        checkFraudBtn.innerHTML = '<div class="loader" style="display:block; width:20px; height:20px;"></div> Checking...';

        try {
            const response = await fetch('http://127.0.0.1:7012/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) throw new Error("API Error");

            const data = await response.json();

            // Display Result
            singleResult.classList.remove('hidden');
            const isFraud = data.prediction === "Fraudulent";
            const probPercent = (data.fraud_probability * 100).toFixed(2) + '%';

            resultBadge.textContent = isFraud ? "High Risk" : "Safe";
            resultBadge.className = isFraud ? "result-badge danger" : "result-badge success";

            resConfidence.textContent = probPercent;
            resMessage.textContent = isFraud
                ? "This transaction shows patterns associated with fraud."
                : "This transaction appears legitimate.";

        } catch (err) {
            alert("Error checking transaction: " + err.message);
        } finally {
            checkFraudBtn.disabled = false;
            checkFraudBtn.innerHTML = '<span>Check Risk</span><div class="shine"></div>';
        }
    });
    dropZone.addEventListener('click', () => csvInput.click());

    csvInput.addEventListener('change', (e) => {
        if (e.target.files.length) handleFile(e.target.files[0]);
    });

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
    });

    function handleFile(file) {
        if (file.type !== "text/csv" && !file.name.endsWith('.csv')) {
            alert("Please upload a Valid CSV file.");
            return;
        }
        selectedFile = file;

        // Update UI
        fileNameDisplay.textContent = file.name;
        fileStatus.classList.remove('hidden');
        dropZone.style.display = 'none'; // Hide big drop zone
        uploadBtn.disabled = false;
    }

    clearFileBtn.addEventListener('click', () => {
        selectedFile = null;
        csvInput.value = '';
        fileStatus.classList.add('hidden');
        dropZone.style.display = 'block'; // Show drop zone again
        uploadBtn.disabled = true;
    });

    // --- Upload Logic ---
    uploadBtn.addEventListener('click', async () => {
        if (!selectedFile) return;

        // UI Loading
        const btnSpan = uploadBtn.querySelector('span');
        btnSpan.style.display = 'none';
        batchLoader.style.display = 'block';
        uploadBtn.disabled = true;

        const formData = new FormData();
        formData.append('file', selectedFile);

        try {
            const response = await fetch('/upload_csv', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.detail || 'Upload failed');
            }

            const data = await response.json();

            setTimeout(() => {
                showBatchResult(data);
                resetUploadButton();
            }, 1000);

        } catch (error) {
            console.error(error);
            alert(`Error: ${error.message}`);
            resetUploadButton();
        }
    });

    function showBatchResult(data) {
        // Store data for export
        currentAnalysisData = data;

        // Transition: Hide upload card, show result card
        mainCard.classList.add('hidden');
        batchResultSection.classList.remove('hidden');

        // Update Stats
        statTotal.textContent = data.total_processed;
        statFraud.textContent = data.fraud_count;

        // Populate Table
        fraudTable.innerHTML = '';
        if (data.fraud_count === 0) {
            fraudTable.innerHTML = '<tr><td colspan="5" style="text-align:center; padding: 30px;">No Fraud Detected! ✅</td></tr>';
        } else {
            data.frauds.forEach(fraud => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${fraud['transaction id'] || '-'}</td>
                    <td>${fraud['transaction type']}</td>
                    <td>₹${fraud['amount (INR)']}</td>
                    <td>${fraud['sender_bank'] || '-'}</td>
                    <td style="color: var(--danger); font-weight: bold;">${fraud.fraud_prob}</td>
                `;
                fraudTable.appendChild(row);
            });
        }
    }

    // --- Export Logic ---
    // --- Export Logic ---
    exportBtn.addEventListener('click', () => {
        console.log("Export button clicked"); // Debug log

        if (!currentAnalysisData || !currentAnalysisData.frauds || currentAnalysisData.frauds.length === 0) {
            alert('No fraud data available to export.');
            return;
        }

        const headers = ["Transaction ID", "Type", "Amount", "Sender Bank", "Fraud Probability"];
        const rows = currentAnalysisData.frauds.map(fraud => [
            fraud['transaction id'] || '',
            fraud['transaction type'] || '',
            fraud['amount (INR)'] || '',
            fraud['sender_bank'] || '',
            fraud.fraud_prob || ''
        ]);

        // Join with commas and newlines
        const csvContent = [
            headers.join(","),
            ...rows.map(e => e.join(","))
        ].join("\n");

        // Use Blob for robust file download
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);

        const link = document.createElement("a");
        link.setAttribute("href", url);
        link.setAttribute("download", "fraud_analysis_report.csv");
        link.style.visibility = 'hidden';

        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url); // Clean up
    });

    resetBatchBtn.addEventListener('click', () => {
        batchResultSection.classList.add('hidden');
        mainCard.classList.remove('hidden');

        // Reset Upload State
        selectedFile = null;
        csvInput.value = '';
        fileStatus.classList.add('hidden');
        dropZone.style.display = 'block';
        uploadBtn.disabled = true;
        currentAnalysisData = null;
    });

    function resetUploadButton() {
        const btnSpan = uploadBtn.querySelector('span');
        btnSpan.style.display = 'block';
        batchLoader.style.display = 'none';
        uploadBtn.disabled = false;
    }

    // --- Helper Functions ---


});
