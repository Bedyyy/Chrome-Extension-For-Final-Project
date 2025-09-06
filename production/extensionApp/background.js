console.log("========================================");
console.log("Service Worker (background.js) Dimuat.");
console.log("Waktu:", new Date().toLocaleTimeString());
console.log("========================================");

let majesticMillionDomains = new Set();

async function loadMajesticMillionData() {
    console.log("[TAHAP 0] Memuat data Majestic Million...");
    try {
        const response = await fetch(chrome.runtime.getURL('majestic_million_new.csv'));
        const text = await response.text();
        const lines = text.split(/\r?\n/);

        if (lines.length < 2) {
            console.error("File majestic_million_new.csv kosong atau hanya berisi header.");
            return;
        }

        const header = lines[0].split(',');
        const domainIndex = header.findIndex(h => h.trim().toLowerCase() === 'domain');

        if (domainIndex === -1) {
            console.error("Kolom 'Domain' tidak ditemukan di header majestic_million_new.csv. Pastikan header dieja dengan benar.");
            return;
        }
        console.log(`> Kolom 'Domain' ditemukan pada indeks: ${domainIndex}`);

        for (let i = 1; i < lines.length; i++) {
            const line = lines[i];
            if (line) {
                const columns = line.split(',');
                if (columns.length > domainIndex && columns[domainIndex]) {
                    const domain = columns[domainIndex].trim();
                    if(domain) {
                        majesticMillionDomains.add(domain);
                    }
                }
            }
        }
        
        console.log(`[SELESAI TAHAP 0] ${majesticMillionDomains.size} domain dari Majestic Million dimuat ke memori.`);
        if (majesticMillionDomains.size === 0) {
            console.warn("Peringatan: Tidak ada domain yang berhasil dimuat. Periksa kembali format file CSV Anda.");
        }

    } catch (error) {
        console.error("Gagal memuat atau mem-parse majestic_million_new.csv:", error);
    }
}

loadMajesticMillionData();

async function buildCosmeticRules() {
    console.log("[TAHAP 1] Membangun aturan kosmetik dari easylist.txt...");
    try {
        const response = await fetch(chrome.runtime.getURL('easylist.txt'));
        const text = await response.text();
        const cosmeticRules = text.split(/\r?\n/).filter(line => line.includes('##'));
        await chrome.storage.local.set({ cosmeticRules: cosmeticRules });
        console.log(`[SELESAI TAHAP 1] ${cosmeticRules.length} aturan kosmetik disimpan.`);
    } catch (error) {
        console.error("Gagal membangun aturan kosmetik:", error);
    }
}

chrome.runtime.onInstalled.addListener(() => {
    buildCosmeticRules();
});

chrome.declarativeNetRequest.onRuleMatchedDebug.addListener((info) => {
    const tabId = info.request.tabId;
    if (tabId > 0) {
        const key = `ad_count_${tabId}`;
        chrome.storage.local.get(key, (result) => {
            const newCount = (result[key] || 0) + 1;
            chrome.storage.local.set({ [key]: newCount });
        });
    }
});

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'loading') {
        const key = `ad_count_${tabId}`;
        chrome.storage.local.get(key, (result) => {
            if(result[key] !== 0) {
                 chrome.storage.local.set({ [key]: 0 });
            }
        });
    }
});

async function startAnalysis(targetUrl, source, tabId) {
    console.log(`\n[TAHAP 2] Analisis Dimulai untuk URL: ${targetUrl}`);
    console.log(`> Sumber: ${source}`);

    const loadingPageUrl = chrome.runtime.getURL('loading.html');
    if (tabId) {
        await chrome.tabs.update(tabId, { url: loadingPageUrl });
    } else {
        const newTab = await chrome.tabs.create({ url: loadingPageUrl });
        tabId = newTab.id;
    }
    console.log(`> Pengguna diarahkan ke loading.html pada Tab ID: ${tabId}`);

    try {
        const urlObject = new URL(targetUrl);
        let domain = urlObject.hostname;
        if (domain.startsWith('www.')) {
            domain = domain.substring(4);
        }

        if (majesticMillionDomains.has(domain)) {
            console.log(`> Domain "${domain}" ditemukan di Majestic Million. Dilewati ke API.`);
            const analysisResult = { prediction: 'safe', source: 'Majestic Million' };
            
            const resultKeyForPage = `analysis_result_${tabId}`;
            const resultKeyForPopup = `analysis_for_${targetUrl}`;
            await chrome.storage.local.set({
                [resultKeyForPage]: analysisResult,
                [resultKeyForPopup]: analysisResult
            });
            console.log(`[TAHAP 4 - Cepat] Hasil analisis disimpan ke storage.`);

            const resultUrl = chrome.runtime.getURL(`result.html?tabId=${tabId}&redirect=${encodeURIComponent(targetUrl)}&source=majestic`);
            chrome.tabs.update(tabId, { url: resultUrl });
            console.log("[TAHAP 5 - Cepat] Mengarahkan pengguna ke halaman hasil.");
            return;
        }
    } catch (e) {
        console.warn("URL tidak valid, tidak dapat melakukan pengecekan domain:", e.message);
    }

    const apiUrl = 'http://127.0.0.1:8000/predict/';
    let analysisResult = {};
    
    const controller = new AbortController();
    const timeoutId = setTimeout(() => {
        console.error("TIMEOUT 30 detik tercapai di background.js. Membatalkan fetch.");
        controller.abort();
    }, 30000);

    try {
        console.log("[TAHAP 3] Mengirim permintaan FETCH ke API...");
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: targetUrl }),
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        console.log("[SELESAI TAHAP 3] Respons FETCH diterima.");

        if (!response.ok) throw new Error(`API Response Not OK: ${response.status}`);
        analysisResult = await response.json();
        console.log("> Data JSON dari API berhasil di-parse:", analysisResult);

    } catch (error) {
        clearTimeout(timeoutId);
        if (error.name === 'AbortError') {
            analysisResult = { error: "TIMEOUT", message: "Permintaan ke API memakan waktu lebih dari 30 detik dan dibatalkan." };
        } else {
            analysisResult = { error: error.name, message: error.message };
        }
        console.error("> Terjadi kesalahan pada TAHAP 3:", analysisResult);
    }

    const resultKeyForPage = `analysis_result_${tabId}`;
    const resultKeyForPopup = `analysis_for_${targetUrl}`;
    await chrome.storage.local.set({
        [resultKeyForPage]: analysisResult,
        [resultKeyForPopup]: analysisResult
    });
    console.log(`[TAHAP 4] Hasil analisis disimpan ke storage.`);

    const resultUrl = chrome.runtime.getURL(`result.html?tabId=${tabId}&redirect=${encodeURIComponent(targetUrl)}&source=${source}`);
    chrome.tabs.update(tabId, { url: resultUrl });
    console.log("[TAHAP 5] Mengarahkan pengguna ke halaman hasil.");
}

chrome.runtime.onMessage.addListener((message, sender) => {
    if (message.url && sender.tab) {
        startAnalysis(message.url, "serp", sender.tab.id);
    } 
    else if (message.manualUrl) {
        startAnalysis(message.manualUrl, "popup", null);
    }
    return false;
});

chrome.runtime.onStartup.addListener(async () => {
    const { cosmeticRules } = await chrome.storage.local.get('cosmeticRules');
    
    console.log("Browser dimulai. Membersihkan storage dari sesi sebelumnya...");
    await chrome.storage.local.clear();
    console.log("Storage berhasil dibersihkan.");
    
    if (cosmeticRules) {
        await chrome.storage.local.set({ cosmeticRules });
        console.log("Aturan kosmetik dipulihkan.");
    }
});