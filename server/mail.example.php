<?php
/**
 * ШАБЛОН настроек почты для send.php. Сам файл с паролем в репозиторий НЕ кладём.
 *
 * На сервере скопировать в /opt/steelline-promo/config/mail.php (ВНЕ папки site/),
 * вписать пароль приложения и закрыть доступ:
 *   sudo install -d -m 750 -o deploy -g www-data /opt/steelline-promo/config
 *   sudo install -m 640 -o deploy -g www-data mail.example.php /opt/steelline-promo/config/mail.php
 *   sudo install -d -m 770 -o deploy -g www-data /opt/steelline-promo/leads
 * (www-data — пользователь, от которого работает PHP; на сервере может называться иначе)
 */
return [
    // Ящик, через который сайт отправляет письма (Яндекс: smtp.yandex.ru, порт 465)
    'smtp_host'  => 'smtp.yandex.ru',
    'smtp_port'  => 465,
    'smtp_user'  => 'segimova.alena@yandex.ru',
    'smtp_pass'  => 'ПАРОЛЬ_ПРИЛОЖЕНИЯ',          // id.yandex.ru → Безопасность → Пароли приложений → Почта
    'from_email' => 'segimova.alena@yandex.ru',     // должен совпадать с smtp_user
    'from_name'  => 'Сайт «Стальная линия»',

    // Куда приходят заявки
    'to' => [
        'alena.segimova22@mail.ru',
        'segimova.alena@yandex.ru',
        'astroom@steelline.store',
    ],

    // Заказ обратного звонка — свой список (необязательно; если нет — берётся 'to')
    'to_callback' => [
        'alena.segimova22@mail.ru',
        'segimova.alena@yandex.ru',
        'astroom@steelline.store',
    ],

    // Журнал заявок и счётчик частоты (папка вне site/, PHP должен иметь право записи)
    'leads_dir' => '/opt/steelline-promo/leads',
];
