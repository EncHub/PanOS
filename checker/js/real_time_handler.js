document.addEventListener("DOMContentLoaded", () => {
    const resultsDiv = document.getElementById('results');

    const eventSource = new EventSource('test_handler.php');
    eventSource.onmessage = (event) => {
        const item = document.createElement('div');
        item.className = 'list-item';
        item.textContent = event.data;
        resultsDiv.appendChild(item);
    };

    eventSource.onerror = () => {
        eventSource.close();
    };
});
