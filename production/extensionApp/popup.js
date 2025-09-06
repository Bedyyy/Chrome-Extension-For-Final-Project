document.addEventListener('DOMContentLoaded', async () => {
    const currentUrlEl = document.getElementById('current-url');
    const statusEl = document.getElementById('analysis-status');
    const adCountEl = document.getElementById('ad-count');
    const manualInputEl = document.getElementById('manual-url-input');
    const manualCheckButton = document.getElementById('manual-check-button');

    statusEl.textContent = 'BELUM DIANALISIS';
    statusEl.className = 'status neutral';

    try {
        const [activeTab] = await chrome.tabs.query({ active: true, currentWindow: true });

        if (activeTab && activeTab.url) {
            currentUrlEl.textContent = activeTab.url;

            const analysisKey = `analysis_for_${activeTab.url}`;
            const storedAnalysis = await chrome.storage.local.get(analysisKey);
            
            if (storedAnalysis[analysisKey]) {
                const result = storedAnalysis[analysisKey];

                if (result.error) {
                    statusEl.textContent = 'ANALISIS GAGAL';
                    statusEl.className = 'status error';
                    console.error("Hasil analisis mengandung error:", result.message);
                } else if (result.prediction === 'phishing') {
                    statusEl.textContent = 'PHISHING';
                    statusEl.className = 'status phishing';
                } else if (result.prediction === 'safe') {
                    statusEl.textContent = 'AMAN';
                    statusEl.className = 'status safe';
                }
            }

            const adCountKey = `ad_count_${activeTab.id}`;
            const storedAdCount = await chrome.storage.local.get(adCountKey);
            if (storedAdCount[adCountKey]) {
                adCountEl.textContent = storedAdCount[adCountKey];
            }
        } else {
            currentUrlEl.textContent = "Tidak dapat mengakses URL tab ini.";
        }
    } catch (error) {
        console.error("Gagal mendapatkan info tab aktif:", error);
        currentUrlEl.textContent = "Error.";
        statusEl.textContent = 'ERROR';
        statusEl.className = 'status error';
    }

    manualCheckButton.addEventListener('click', () => {
        const urlToCheck = manualInputEl.value.trim();
        if (urlToCheck) {
            chrome.runtime.sendMessage({ manualUrl: urlToCheck });
            window.close();
        }
    });
});