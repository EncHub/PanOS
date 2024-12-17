<?php
$dir = isset($_GET['dir']) ? $_GET['dir'] : die("Директория не указана.");
$targetsFile = $dir . 'targets.list';

if (!file_exists($targetsFile)) {
    die("Файл со списком адресов не найден.");
}

$addresses = file($targetsFile, FILE_IGNORE_NEW_LINES);
?>

<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Тестирование</title>
    <link rel="stylesheet" href="css/dark_macos.css">
    <script src="js/real_time_handler.js" defer></script>
</head>
<body>
    <div class="sidebar">
        <button id="startTest">Начать Тест</button>
        <button id="stopTest">Остановить Тест</button>
        <a href="index.php">Назад</a>
    </div>

    <div class="content">
        <h2>Загруженные адреса</h2>
        <div class="scroll-list">
            <?php foreach ($addresses as $address): ?>
                <div class="list-item"><?= htmlspecialchars($address) ?></div>
            <?php endforeach; ?>
        </div>

        <h2>Результаты тестирования</h2>
        <div id="results" class="scroll-list"></div>
    </div>

    <!-- Модальное окно -->
    <div id="modal" class="modal">
        <div class="modal-content">
            <h3>Выберите скрипт</h3>
            <select id="scriptType">
                <option value="python">Python скрипт</option>
                <option value="bash">Bash</option>
            </select>
            <button id="runTest">Поехали</button>
        </div>
    </div>

    <script>
        document.getElementById('startTest').addEventListener('click', () => {
            document.getElementById('modal').style.display = 'block';
        });

        document.getElementById('runTest').addEventListener('click', () => {
            const scriptType = document.getElementById('scriptType').value;
            document.getElementById('modal').style.display = 'none';
            fetch('test_handler.php', {
                method: 'POST',
                body: JSON.stringify({ script: scriptType, dir: '<?= $dir ?>' })
            });
        });
    </script>
</body>
</html>
