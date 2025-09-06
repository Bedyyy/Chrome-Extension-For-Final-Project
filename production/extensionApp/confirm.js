document.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search);
    const targetUrl = params.get('redirect');
    const tabId = params.get('tabId');
    const resultKey = `analysis_result_${tabId}`;

    const backButton = document.getElementById('go-back');
    const continueButton = document.getElementById('proceed');

    continueButton.addEventListener('click', () => {
        if (targetUrl) {
            chrome.storage.local.remove(resultKey);
            window.location.href = targetUrl;
        }
    });

    backButton.addEventListener('click', () => {
        history.back();
    });
});