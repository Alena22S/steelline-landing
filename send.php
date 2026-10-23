<?php
/**
 * Приём заявок с сайта: контакты + фото проёма → письмо на почту (через SMTP) + копия в журнал на сервере.
 *
 * Пароли здесь НЕ хранятся. Настройки читаются из файла ВНЕ папки сайта (её перезаписывает автопубликация):
 *   /opt/steelline-promo/config/mail.php   (= папка выше сайта / config / mail.php)
 * Шаблон — config/mail.example.php в репозитории.
 * Журнал заявок и счётчик частоты — /opt/steelline-promo/leads/
 */

// ---- Постоянные настройки (без секретов) ----
$MAX_FILES = 5;
$MAX_SIZE  = 10 * 1024 * 1024;                    // 10 МБ на файл
$ALLOWED   = ['image/jpeg', 'image/png', 'image/webp', 'image/heic', 'image/heif'];
$RATE_MAX  = 5;                                   // не больше 5 заявок…
$RATE_WIN  = 600;                                 // …за 10 минут с одного IP
$MIN_FILL  = 3;                                   // быстрее 3 секунд форму заполняют только боты
// ----------------------------------------------

header('Content-Type: application/json; charset=utf-8');

function reply($ok, $error = '', $code = 200) {
    http_response_code($code);
    echo json_encode($ok ? ['ok' => true] : ['ok' => false, 'error' => $error], JSON_UNESCAPED_UNICODE);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    reply(false, 'Неверный запрос.', 405);
}

$BASE     = dirname(__DIR__);                     // /opt/steelline-promo
$CFG_FILE = getenv('STEELLINE_MAIL_CONFIG') ?: $BASE . '/config/mail.php';
$cfg      = is_readable($CFG_FILE) ? require $CFG_FILE : null;
$LEADS    = (is_array($cfg) && !empty($cfg['leads_dir'])) ? rtrim($cfg['leads_dir'], '/') : $BASE . '/leads';

// Ловушки для ботов: скрытое поле и слишком быстрая отправка. Боту отвечаем «успешно», ничего не делая
if (!empty($_POST['website'])) {
    reply(true);
}
$started = isset($_POST['ts']) ? (int) $_POST['ts'] : 0;
if ($started > 0 && (time() - (int) floor($started / 1000)) < $MIN_FILL) {
    reply(true);
}

// Ограничение частоты по IP
$ip = $_SERVER['REMOTE_ADDR'] ?? '0.0.0.0';
if (is_dir($LEADS) && is_writable($LEADS)) {
    $rateFile = $LEADS . '/.rate-' . hash('sha256', $ip) . '.json';
    $now  = time();
    $hits = is_readable($rateFile) ? (json_decode((string) file_get_contents($rateFile), true) ?: []) : [];
    $hits = array_values(array_filter($hits, function ($t) use ($now, $RATE_WIN) { return $t > $now - $RATE_WIN; }));
    if (count($hits) >= $RATE_MAX) {
        reply(false, 'Слишком много заявок подряд. Попробуйте через несколько минут или позвоните нам.', 429);
    }
    $hits[] = $now;
    @file_put_contents($rateFile, json_encode($hits), LOCK_EX);
}

function field($key, $max) {
    $v = isset($_POST[$key]) ? trim((string) $_POST[$key]) : '';
    $v = str_replace(["\r", "\0"], '', $v);
    return mb_substr($v, 0, $max);
}
function line($key, $max) {                       // однострочные поля: без переводов строк
    return str_replace("\n", ' ', field($key, $max));
}

$name    = line('name', 80);
$phone   = line('phone', 30);
$email   = line('email', 120);
$comment = field('comment', 1000);
$source  = line('source', 40);
$page    = line('page', 300);
$bonus   = line('bonus', 4) === '20'; // в форме обещали забронировать скидку 20%
$consent = !empty($_POST['consent']);
$isSale     = ($source === 'sale');     // заявка на скидку (распродажа межкомнатных Aurum): имя, телефон, модель
$isBonus    = ($source === 'bonus');    // карточка «Вам доступна скидка 20%»
$isCallback = ($source === 'callback' || $isSale || $isBonus); // короткая форма: только имя и телефон
$isContact  = ($source === 'contact');  // «Записаться на подбор»: имя, телефон, комментарий — почта и фото необязательны

if ($isBonus) {
    // купон 20%: нужна только почта — на неё уходит купон
    if (!filter_var($email, FILTER_VALIDATE_EMAIL)) reply(false, 'Проверьте адрес почты.', 422);
} else {
    if (mb_strlen($name) < 2) reply(false, 'Укажите имя.', 422);
    if (strlen(preg_replace('/\D/', '', $phone)) !== 11) reply(false, 'Укажите телефон полностью.', 422);
}
if ($isCallback || $isContact) {
    if ($email !== '' && !filter_var($email, FILTER_VALIDATE_EMAIL)) $email = '';
} elseif (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    reply(false, 'Проверьте адрес почты.', 422);
}
if (!$consent) reply(false, 'Нужно согласие на обработку данных.', 422);

// Купон 20%: код SL2026-ДДММ — день и месяц получения (по Екатеринбургу), срок — 7 дней с этой даты.
// По коду менеджер сразу видит, когда купон выдан и до какого числа действует.
$coupon = ''; $couponUntil = '';
if ($isBonus) {
    $tz = new DateTimeZone('Asia/Yekaterinburg');
    $issued = new DateTime('now', $tz);
    $coupon = 'SL2026-' . $issued->format('dm');
    $couponUntil = (clone $issued)->modify('+7 days')->format('d.m.Y');
}

// Метки рекламы и откуда пришёл посетитель (собирает script.js)
$trackKeys = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'yclid', 'gclid', 'referrer', 'landing'];
$track = [];
foreach ($trackKeys as $k) {
    $v = line($k, 300);
    if ($v !== '') $track[$k] = $v;
}

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

// ---- Копия заявки в журнал на сервере (без фото) — даже если письмо не уйдёт, заявка не потеряется ----
$logged = false;
if (is_dir($LEADS) && is_writable($LEADS)) {
    $entry = [
        'time' => date('c'), 'type' => $isSale ? 'sale' : ($isBonus ? 'bonus' : ($isCallback ? 'callback' : 'lead')), 'page' => $page, 'name' => $name, 'phone' => $phone, 'email' => $email,
        'comment' => $comment, 'photos' => count($attachments), 'source' => $source, 'track' => $track, 'coupon' => $coupon,
    ];
    $logFile = $LEADS . '/leads-' . date('Y-m') . '.jsonl';
    $logged  = @file_put_contents($logFile, json_encode($entry, JSON_UNESCAPED_UNICODE) . "\n", FILE_APPEND | LOCK_EX) !== false;
    if ($logged) @chmod($logFile, 0600);
}

if (!is_array($cfg)) {
    // Почта не настроена: заявка сохранена в журнал (если он доступен), посетителю — честное сообщение
    reply(false, $logged ? 'Заявка сохранена, но письмо пока не отправилось. Мы свяжемся с вами.' : 'Форма временно не работает.', 503);
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
    'model'         => 'страница модели в каталоге',
    'catalog-cta'   => 'каталог: «Не нашли подходящую модель?»',
    'catalog-empty' => 'каталог: «Таких моделей не нашлось»',
    'callback'      => 'кнопка «Заказать звонок»',
    'sale'          => 'межкомнатные: форма «Получите скидку 40%»',
    'bonus'         => 'карточка «Вам доступна скидка 20%»',
];
$trackNames = [
    'utm_source' => 'utm_source', 'utm_medium' => 'utm_medium', 'utm_campaign' => 'utm_campaign',
    'utm_content' => 'utm_content', 'utm_term' => 'utm_term', 'yclid' => 'yclid (Директ)', 'gclid' => 'gclid',
    'referrer' => 'Пришёл с', 'landing' => 'Страница входа',
];
$h = function ($s) { return htmlspecialchars($s, ENT_QUOTES, 'UTF-8'); };

$html  = '<h2 style="font-family:Arial,sans-serif;color:#061f3b">' . ($isSale ? 'Заявка на скидку −40% (межкомнатные Aurum, распродажа склада)' : ($isBonus ? 'Заявка на скидку 20% — перезвонить и закрепить скидку' : ($isCallback ? 'Заказ обратного звонка — перезвонить в течение часа' : ($isContact ? 'Запись на подбор' : 'Новая заявка с сайта')))) . '</h2>';
$html .= '<table cellpadding="6" style="font-family:Arial,sans-serif;font-size:14px;color:#061f3b">';
if ($name !== '') $html .= '<tr><td><b>Имя</b></td><td>' . $h($name) . '</td></tr>';
if ($phone !== '') $html .= '<tr><td><b>Телефон</b></td><td><a href="tel:+' . preg_replace('/\D/', '', $phone) . '">' . $h($phone) . '</a></td></tr>';
if ($coupon !== '') $html .= '<tr><td><b>Купон</b></td><td><b>' . $coupon . '</b> — скидка 20% на входную дверь, действует до ' . $couponUntil . ' включительно. Отправлен клиенту на почту.</td></tr>';
if ($email !== '') $html .= '<tr><td><b>Почта</b></td><td><a href="mailto:' . $h($email) . '">' . $h($email) . '</a></td></tr>';
if ($comment !== '') $html .= '<tr><td valign="top"><b>Комментарий</b></td><td>' . nl2br($h($comment)) . '</td></tr>';
if (!$isCallback && !$isContact) $html .= '<tr><td><b>Фото проёма</b></td><td>' . (count($attachments) ? count($attachments) . ' во вложении' : 'не приложены') . '</td></tr>';
if ($bonus) $html .= '<tr><td><b>Скидка</b></td><td><b>20% — обещана на сайте при заявке</b></td></tr>';
if ($page !== '') $html .= '<tr><td><b>Страница</b></td><td>' . $h($page) . '</td></tr>';
if (isset($sources[$source])) $html .= '<tr><td><b>Откуда</b></td><td>' . $sources[$source] . '</td></tr>';
foreach ($track as $k => $v) {
    $html .= '<tr><td><b>' . $h($trackNames[$k]) . '</b></td><td>' . $h($v) . '</td></tr>';
}
$html .= '</table>';

// для заказа звонка — свой список получателей (с почтой салона), если он задан в настройках
$toList   = ($isCallback && !empty($cfg['to_callback'])) ? $cfg['to_callback'] : $cfg['to'];
$to       = array_values(array_filter((array) $toList, function ($a) { return filter_var($a, FILTER_VALIDATE_EMAIL); }));
$from     = $cfg['from_email'];
$fromName = $cfg['from_name'] ?? 'Сайт «Стальная линия»';
$subject  = ($isSale ? 'Заявка на скидку −40% (межкомнатные Aurum) — ' : ($isBonus ? 'Купон 20% ' . $coupon . ' — ' . $email . ' ' : ($isCallback ? 'Заказ обратного звонка — ' : ($isContact ? 'Запись на подбор с сайта — ' : 'Заявка на подбор двери с сайта — ')))) . $name;
$enc      = function ($s) { return '=?UTF-8?B?' . base64_encode($s) . '?='; };

$boundary = '=_' . bin2hex(random_bytes(12));
$msg  = 'Date: ' . date('r') . "\r\n";
$msg .= 'From: ' . $enc($fromName) . " <$from>\r\n";
$msg .= 'To: ' . implode(', ', $to) . "\r\n";
if ($email !== '') $msg .= "Reply-To: $email\r\n";
$msg .= 'Subject: ' . $enc($subject) . "\r\n";
$msg .= 'Message-ID: <' . bin2hex(random_bytes(16)) . '@' . substr(strrchr($from, '@'), 1) . ">\r\n";
$msg .= "MIME-Version: 1.0\r\n";
$msg .= "Content-Type: multipart/mixed; boundary=\"$boundary\"\r\n\r\n";
$msg .= "--$boundary\r\n";
$msg .= "Content-Type: text/html; charset=UTF-8\r\n";
$msg .= "Content-Transfer-Encoding: base64\r\n\r\n";
$msg .= chunk_split(base64_encode($html)) . "\r\n";
foreach ($attachments as $file) {
    $msg .= "--$boundary\r\n";
    $msg .= "Content-Type: {$file['mime']}; name=\"{$file['name']}\"\r\n";
    $msg .= "Content-Transfer-Encoding: base64\r\n";
    $msg .= "Content-Disposition: attachment; filename=\"{$file['name']}\"\r\n\r\n";
    $msg .= chunk_split(base64_encode($file['data'])) . "\r\n";
}
$msg .= "--$boundary--\r\n";

/** Отправка через SMTP с SSL (порт 465) и AUTH LOGIN. Возвращает '' или текст ошибки (для журнала сервера). */
function smtp_send(array $cfg, $from, array $to, $msg) {
    $host = $cfg['smtp_host'];
    $port = (int) ($cfg['smtp_port'] ?? 465);
    $ctx  = stream_context_create(['ssl' => ['verify_peer' => true, 'verify_peer_name' => true]]);
    $fp   = @stream_socket_client("ssl://$host:$port", $errno, $errstr, 20, STREAM_CLIENT_CONNECT, $ctx);
    if (!$fp) return "connect: $errstr ($errno)";
    stream_set_timeout($fp, 20);

    $read = function () use ($fp) {
        $data = '';
        while (($line = fgets($fp, 515)) !== false) {
            $data .= $line;
            if (strlen($line) < 4 || $line[3] === ' ') break;
        }
        return $data;
    };
    $cmd = function ($line, $expect) use ($fp, $read) {
        if ($line !== null) fwrite($fp, $line . "\r\n");
        $resp = $read();
        return ((int) substr($resp, 0, 3) === $expect) ? '' : trim($resp);
    };

    $steps = [
        [null, 220],
        ['EHLO ' . (gethostname() ?: 'localhost'), 250],
        ['AUTH LOGIN', 334],
        [base64_encode($cfg['smtp_user']), 334],
        [base64_encode($cfg['smtp_pass']), 235],
        ["MAIL FROM:<$from>", 250],
    ];
    foreach ($to as $rcpt) $steps[] = ["RCPT TO:<$rcpt>", 250];
    $steps[] = ['DATA', 354];
    foreach ($steps as $i => $s) {
        $err = $cmd($s[0], $s[1]);
        if ($err !== '') { fclose($fp); return ($i === 4 ? 'auth' : 'smtp') . ": $err"; }
    }
    // точка в начале строки внутри письма удваивается (правило SMTP)
    $body = preg_replace('/^\./m', '..', $msg);
    $err  = $cmd($body . "\r\n.", 250);
    $cmd('QUIT', 221);
    fclose($fp);
    return $err === '' ? '' : "data: $err";
}

$error = $to ? smtp_send($cfg, $from, $to, $msg) : 'no recipients';
if ($error !== '') {
    error_log('steelline send.php: ' . $error);
    reply(false, $logged ? 'Заявка сохранена, но письмо не отправилось. Мы свяжемся с вами.' : 'Не получилось отправить заявку.', 500);
}

// ---- Купон 20%: письмо клиенту ----
if ($isBonus && $coupon !== '') {
    $catalog = 'https://promo.steelline.store/prototype-catalog/catalog.html';
    $ch  = '<div style="font-family:Arial,sans-serif;color:#061f3b;max-width:560px;margin:0 auto;padding:8px">';
    $ch .= '<h2 style="margin:0 0 12px;font-size:22px">Ваш купон на скидку 20%</h2>';
    $ch .= '<p style="margin:0 0 16px;font-size:15px;line-height:1.5;color:#5e6c66">Спасибо за интерес к входным дверям «Стальная линия». Назовите этот код менеджеру при оформлении заказа:</p>';
    $ch .= '<div style="margin:0 0 8px;padding:18px;border-radius:12px;background:#eef4fc;border:1px dashed #1e67b9;text-align:center;font-size:28px;font-weight:bold;letter-spacing:2px">' . $coupon . '</div>';
    $ch .= '<p style="margin:0 0 20px;font-size:14px;color:#5e6c66;text-align:center">Действует до <b>' . $couponUntil . '</b> включительно</p>';
    $ch .= '<p style="margin:0 0 6px;font-size:14px;font-weight:bold">Условия акции</p>';
    $ch .= '<ul style="margin:0 0 20px;padding-left:20px;font-size:14px;line-height:1.55;color:#5e6c66">'
         . '<li>Скидка 20% на входные двери «Стальная линия» по персональному купону.</li>'
         . '<li>Купон действует 7 дней с момента получения.</li>'
         . '<li>Один купон — на один заказ.</li>'
         . '<li>Скидка не суммируется с другими акциями и не действует на межкомнатные двери.</li></ul>';
    $ch .= '<p style="margin:0 0 24px"><a href="' . $catalog . '" style="display:inline-block;padding:14px 24px;border-radius:8px;background:#1e67b9;color:#fff;text-decoration:none;font-weight:bold">Смотреть входные двери</a></p>';
    $ch .= '<p style="margin:0;font-size:13px;line-height:1.5;color:#5e6c66">Интерьерный центр ASTROOM, Екатеринбург, ул. Цвиллинга, 1, 6 этаж, галерея А<br>'
         . '<a href="tel:+79222077552" style="color:#061f3b">+7 (922) 207-75-52</a> · ежедневно с 10:00 до 20:00</p></div>';
    $cmsg  = 'Date: ' . date('r') . "\r\n";
    $cmsg .= 'From: ' . $enc($fromName) . " <$from>\r\n";
    $cmsg .= "To: $email\r\n";
    $cmsg .= 'Subject: ' . $enc('Ваш купон на скидку 20% — «Стальная линия»') . "\r\n";
    $cmsg .= 'Message-ID: <' . bin2hex(random_bytes(16)) . '@' . substr(strrchr($from, '@'), 1) . ">\r\n";
    $cmsg .= "MIME-Version: 1.0\r\n";
    $cmsg .= "Content-Type: text/html; charset=UTF-8\r\n";
    $cmsg .= "Content-Transfer-Encoding: base64\r\n\r\n";
    $cmsg .= chunk_split(base64_encode($ch));
    $cerr = smtp_send($cfg, $from, [$email], $cmsg);
    if ($cerr !== '') {
        error_log('steelline send.php coupon: ' . $cerr);
        reply(false, 'Заявка принята, но купон не отправился на почту — менеджер пришлёт его сам.', 500);
    }
}

reply(true);
