<?php
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json");

$dataDir = "../frontend/public/data/";

$type = $_GET['type'] ?? 'runners';

switch ($type) {
    case "races":
        $filePath = $dataDir . "cleaned_race.json";
        break;
    case "runners":
        $filePath = $dataDir . "cleaned_runner.json";
        break;
    default:
        echo json_encode(["error" => "Invalid type"]);
        exit;
}

if (file_exists($filePath)) {
    echo file_get_contents($filePath);
} else {
    echo json_encode(["error" => "File not found"]);
}
?>
