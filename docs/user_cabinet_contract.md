Настройки уведомлений в кабинете пользователя

Страница кабинета доступна по адресу /users/profile/

В notifications передаются четыре значения:

weekly_reports
trend_notifications
limit_exceeded
new_features

weekly_reports trend_notifications и new_features берутся из NotificationSettings текущего пользователя.

Если настроек у пользователя ещё нет они создаются со значениями по умолчанию.

limit_exceeded в NotificationSettings не хранится.

Для сохранения настроек отправляется POST запрос на /users/profile/

В запросе передаются:

action со значением notifications
weekly_reports
trend_notifications
new_features

После успешного сохранения пользователь возвращается в кабинет и получает сообщение об успешном сохранении.

Если сохранить настройки не удалось пользователь возвращается в кабинет с сообщением об ошибке.

Сообщения передаются через общий Inertia flash.
