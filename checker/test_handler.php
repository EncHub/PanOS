<?php
header('Content-Type: application/json');
$data = json_decode(file_get_contents('php://input'), true);
$scriptType = $data['script'] ?? null;
$dir = $data['dir'] ?? null;

if (!$scriptType || !$dir || !is_dir($dir)) {
    http_response_code(400);
    echo json_encode(['error' => 'Неправильные параметры']);
    exit();
}

// Имитируем выполнение тестов с постепенным выводом
$targetsFile = $dir . 'targets.list';
$addresses = file($targetsFile, FILE_IGNORE_NEW_LINES);

foreach ($addresses as $address) {
    // Логика для тестирования адреса
    usleep(50000); // Имитация задержки
    echo "data: Тестирование $address завершено\n\n";
    ob_flush();
    flush();
}
?>
