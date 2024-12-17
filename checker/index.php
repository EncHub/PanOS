<?php
$config = require 'config/config.php';

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_FILES['file'])) {
    $file = $_FILES['file'];

    // Проверка на размер файла
    if ($file['size'] > $config['max_file_size']) {
        die("Файл слишком большой.");
    }

    // Создание директорий
    $dateTimeDir = $config['upload_dir'] . date('Y-m-d_H-i-s') . '/';
    if (!is_dir($dateTimeDir)) {
        mkdir($dateTimeDir, 0755, true);
    }

    $targetPath = $dateTimeDir . 'targets.list';
    move_uploaded_file($file['tmp_name'], $targetPath);

    header("Location: menu.php?dir=" . urlencode($dateTimeDir));
    exit();
}
?>

<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Загрузка таргетов</title>
    <link rel="stylesheet" href="css/dark_macos.css">
</head>
<body>
    <h1>Загрузите список адресов</h1>
    <form method="POST" enctype="multipart/form-data">
        <input type="file" name="file" required accept=".txt">
        <button type="submit">Загрузить</button>
    </form>
</body>
</html>
