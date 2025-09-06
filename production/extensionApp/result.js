document.addEventListener("DOMContentLoaded", async () => {
    const params = new URLSearchParams(window.location.search);
    const tabId = params.get("tabId");
    const targetUrl = params.get("redirect");
    const source = params.get("source");

    const container = document.getElementById("result-container");

    if (!tabId) {
        container.innerHTML = "<h1>Error: Tab ID tidak ditemukan.</h1>";
        return;
    }

    const resultKey = `analysis_result_${tabId}`;
    const storedData = await chrome.storage.local.get(resultKey);
    
    if (storedData && storedData[resultKey]) {
        const result = storedData[resultKey];
        const isPhishing = result.prediction === 'phishing';
        renderPage(isPhishing, targetUrl, source, tabId, resultKey);
    } else {
        container.innerHTML = "<h1>Error: Tidak ditemukan hasil analisis.</h1>";
    }
});


function renderPage(isPhishing, targetUrl, source, tabId, resultKey) {
    const container = document.getElementById("result-container");
    let cardHtml = '';

    if (isPhishing) {
        cardHtml = `
            <div class="main-card is-danger">
                <img src="https://img.icons8.com/plasticine/100/error.png" alt="Phishing Detected" class="card-icon"/>
                <h1 class="card-title is-danger">Bahaya Phishing</h1>
                <p class="card-subtitle">
                    Sistem mendeteksi bahwa situs: 
                    <span class="url-display">${targetUrl}</span> 
                    adalah halaman <strong>phishing</strong>.
                </p>
                <p class="card-text">
                    Kami sangat menyarankan Anda untuk tidak melanjutkan demi keamanan data pribadi Anda.
                </p>
                <div class="button-group">
                    <button id="back" class="button btn-primary">Kembali</button>
                    <button id="continue" class="button btn-danger">Tetap Lanjutkan</button>
                </div>
            </div>
        `;
    } else {
        cardHtml = `
            <div class="main-card is-safe">
                <img src="https://img.icons8.com/plasticine/100/checked-2.png" alt="Site is Safe" class="card-icon"/>
                <h1 class="card-title is-safe">Situs Aman</h1>
                <p class="card-subtitle">
                    Situs tujuan Anda telah dianalisis dan dinyatakan aman untuk dikunjungi.
                </p>
                <p class="card-text">
                    URL: <span class="url-display">${targetUrl}</span>
                </p>
                <div class="button-group">
                    <button id="back" class="button btn-secondary">Kembali</button>
                    <button id="continue" class="button btn-primary">Lanjutkan ke Situs</button>
                </div>
            </div>
        `;
    }

    container.innerHTML = cardHtml;

    const continueButton = document.getElementById("continue");
    const backButton = document.getElementById("back");

    if (isPhishing) {
        continueButton.addEventListener("click", () => {
            const confirmUrl = `confirm.html?redirect=${encodeURIComponent(targetUrl)}&tabId=${tabId}&source=${source}`;
            window.location.href = confirmUrl;
        });
    } else {
        continueButton.addEventListener("click", () => {
            chrome.storage.local.remove(resultKey);
            window.location.href = targetUrl;
        });
    }

    backButton.addEventListener("click", () => {
        chrome.storage.local.remove(resultKey);

        if (source === 'popup') {
            window.close();
        } else if (source === 'majestic') {
            if (history.length > 1){
                history.back();
            } else {
                window.close();
            }
        } else {
            history.go(-2); 
        }
    });
}