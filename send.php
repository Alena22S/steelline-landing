<?php
/**
 * Приём заявок с сайта: контакты + фото проёма → письмо на почту салона.
 * Работает на любом PHP-хостинге с настроенной функцией mail() (Beget, Timeweb, REG.RU и т.п.).
 */

// ---- Настройки ----
$TO        = 'astroom@steelline.store';          // куда приходят заявки
$FROM      = 'no-reply@steelline.store';          // адрес отправителя на домене сайта
$SUBJECT   = 'Заявка на подбор двери с сайта';
$MAX_FILES = 5;
$MAX_SIZE  = 10 * 1024 * 1024;                    // 10 МБ на файл
$ALLOWED   = ['image/jpeg', 'image/png', 'image/webp', 'image/heic', 'image/heif'];
// -------------------

header('Content-Type: application/json; charset=utf-8');

function reply($ok, $error = '', $code = 200) {
    http_response_code($code);
    echo json_encode($ok ? ['ok' => true] : ['ok' => false, 'error' => $error], JSON_UNESCAPED_UNICODE);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    reply(false, 'Неверный запрос.', 405);
}

// Ловушка для ботов: настоящий посетитель это поле не заполняет
if (!empty($_POST['website'])) {
    reply(true);
}

function field($key, $max) {
    $v = isset($_POST[$key]) ? trim((string) $_POST[$key]) : '';
    $v = str_replace(["\r", "\0"], '', $v);
    return mb_substr($v, 0, $max);
}

$name    = field('name', 80);
$phone   = field('phone', 30);
$email   = field('email', 120);
$comment = field('comment', 1000);
$source  = field('source', 40);
$consent = !empty($_POST['consent']);

if (mb_strlen($name) < 2) reply(false, 'Укажите имя.', 422);
if (strlen(preg_replace('/\D/', '', $phone)) !== 11) reply(false, 'Укажите телефон полностью.', 422);
if (!filter_var($email, FILTER_VALIDATE_EMAIL)) reply(false, 'Проверьте адрес почты.', 422);
if (!$consent) reply(false, 'Нужно согласие на обработку данных.', 422);

// ---- Фото ----
$attachments = [];
if (!empty($_FILES['photos']) && is_array($_FILES['photos']['name'])) {
    $count = count($_FILES['photos']['name']);
    if ($count > $MAX_FILES) reply(false, "Можно приложить до $MAX_FILES фото.", 422);

    $finfo = new finfo(FILEINFO_MIME_TYPE);
    for ($i = 0; $i < $count; $i++) {
        $err = $_FILES['photos']['error'][$i];
        if ($err === UPLOAD_ERR_NO_FILE) continue;
        if ($err !== UPLOAD_ERR_OK) reply(false, 'Не удалось загрузить фото. Попробуйте файл поменьше.', 422);

        $tmp  = $_FILES['photos']['tmp_name'][$i];
        $size = $_FILES['photos']['size'][$i];
        if ($size > $MAX_SIZE) reply(false, 'Фото больше 10 МБ.', 422);

        $mime = $finfo->file($tmp);
        if (!in_array($mime, $ALLOWED, true)) reply(false, 'Можно загрузить только фотографии.', 422);

        $ext  = ['image/jpeg' => 'jpg', 'image/png' => 'png', 'image/webp' => 'webp', 'image/heic' => 'heic', 'image/heif' => 'heif'][$mime];
        $attachments[] = [
            'name' => 'proem-' . ($i + 1) . '.' . $ext,
            'mime' => $mime,
            'data' => file_get_contents($tmp),
        ];
    }
}

// ---- Письмо ----
$sources = [
    'header'    => 'кнопка в шапке',
    'hero'      => 'первый экран',
    'tech-card' => 'блок «Инженерия»',
    'doors'     => 'блок «Какая дверь подойдёт»',
    'contact'   => 'кнопка «Записаться на подбор»',
    'idea'      => 'блок «Дверь под вашу идею»',
    'sticky'    => 'закреплённая кнопка (телефон)',
];
$h = function ($s) { return htmlspecialchars($s, ENT_QUOTES, 'UTF-8'); };

$html  = '<h2 style="font-family:Arial,sans-serif;color:#061f3b">Новая заявка с сайта</h2>';
$html .= '<table cellpadding="6" style="font-family:Arial,sans-serif;font-size:14px;color:#061f3b">';
$html .= '<tr><td><b>Имя</b></td><td>' . $h($name) . '</td></tr>';
$html .= '<tr><td><b>Телефон</b></td><td><a href="tel:+' . preg_replace('/\D/', '', $phone) . '">' . $h($phone) . '</a></td></tr>';
$html .= '<tr><td><b>Почта</b></td><td><a href="mailto:' . $h($email) . '">' . $h($email) . '</a></td></tr>';
if ($comment !== '') $html .= '<tr><td valign="top"><b>Комментарий</b></td><td>' . nl2br($h($comment)) . '</td></tr>';
$html .= '<tr><td><b>Фото проёма</b></td><td>' . (count($attachments) ? count($attachments) . ' во вложении' : 'не приложены') . '</td></tr>';
if (isset($sources[$source])) $html .= '<tr><td><b>Откуда</b></td><td>' . $sources[$source] . '</td></tr>';
$html .= '</table>';

$boundary = '=_' . bin2hex(random_bytes(12));
$encSubject = '=?UTF-8?B?' . base64_encode($SUBJECT . ' — ' . $name) . '?=';

$headers  = 'From: =?UTF-8?B?' . base64_encode('Сайт «Стальная линия»') . "?= <$FROM>\r\n";
$headers .= "Reply-To: $email\r\n";
$headers .= "MIME-Version: 1.0\r\n";
$headers .= "Content-Type: multipart/mixed; boundary=\"$boundary\"";

$body  = "--$boundary\r\n";
$body .= "Content-Type: text/html; charset=UTF-8\r\n";
$body .= "Content-Transfer-Encoding: base64\r\n\r\n";
$body .= chunk_split(base64_encode($html)) . "\r\n";

foreach ($attachments as $file) {
    $body .= "--$boundary\r\n";
    $body .= "Content-Type: {$file['mime']}; name=\"{$file['name']}\"\r\n";
    $body .= "Content-Transfer-Encoding: base64\r\n";
    $body .= "Content-Disposition: attachment; filename=\"{$file['name']}\"\r\n\r\n";
    $body .= chunk_split(base64_encode($file['data'])) . "\r\n";
}
$body .= "--$boundary--";

if (!mail($TO, $encSubject, $body, $headers, '-f' . $FROM)) {
    reply(false, 'Не получилось отправить заявку.', 500);
}

reply(true);
