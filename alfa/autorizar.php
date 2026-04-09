<?php
require_once '../config.php';

if (!isset($_SESSION['usuario_id']) || $_SESSION['rol'] !== 'empresa') {
    header("Location: ../login.php");
    exit;
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $reporte_id = $_POST['reporte_id'] ?? 0;
    
    if ($reporte_id) {
        $stmt = $pdo->prepare("UPDATE reportes SET estado = 'autorizado' WHERE id = ?");
        $stmt->execute([$reporte_id]);
    }
}

header("Location: dashboard.php");
exit;
?>
