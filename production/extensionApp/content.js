const injectElementHidingStyles = async () => {
  const { cosmeticRules } = await chrome.storage.local.get('cosmeticRules');
  if (!cosmeticRules || cosmeticRules.length === 0) return;

  const style = document.createElement('style');
  const currentHostname = window.location.hostname;
  let finalCssRules = '';

  for (const rule of cosmeticRules) {
    const parts = rule.split('##');
    if (parts.length < 2) continue;

    const domains = parts[0];
    const selector = parts[1];

    const appliesToCurrentDomain = () => {
      if (domains === '') return true;
      return domains.split(',').some(domain => {
        const cleanDomain = domain.startsWith('~') ? domain.substring(1) : domain;
        return currentHostname.endsWith(cleanDomain);
      });
    };

    if (appliesToCurrentDomain()) {
      finalCssRules += `${selector} { display: none !important; }\n`;
    }
  }
  
  if (finalCssRules) {
    style.textContent = finalCssRules;
    (document.head || document.documentElement).appendChild(style);
  }
};

injectElementHidingStyles();

const searchEngineUrls = [
    'google.com/search',
    'bing.com/search',
    'search.yahoo.com/search',
    'duckduckgo.com'
];

const currentUrl = window.location.href;
const isSearchPage = searchEngineUrls.some(engineUrl => currentUrl.includes(engineUrl));

if (isSearchPage) {
    document.addEventListener("click", (event) => {
        const link = event.target.closest("a");

        if (link && link.href) {
            event.preventDefault();

            let finalUrl = link.href;

            try {
                const urlObject = new URL(link.href);
                const params = new URLSearchParams(urlObject.search);
                const hostname = urlObject.hostname;

                if (hostname.includes("google.com") && params.has('url')) {
                    finalUrl = params.get('url');
                }
                else if (hostname.includes("bing.com") && params.has('u')) {
                    const actualUrlBase64 = params.get('u');
                    if (actualUrlBase64.startsWith('a1')) {
                        finalUrl = atob(actualUrlBase64.substring(2));
                    }
                }
                else if (hostname.includes("yahoo.com") && params.has('ru')) {
                    finalUrl = decodeURIComponent(params.get('ru'));
                }

            } catch (e) {
                console.error("Gagal membersihkan URL, menggunakan URL asli:", e);
                finalUrl = link.href;
            }
            
            console.log("URL yang dikirim untuk analisis:", finalUrl);
            chrome.runtime.sendMessage({ url: finalUrl });
        }
    }, true);
}