# Как получить Session_id для Wordstat

1. Откройте https://wordstat.yandex.ru и войдите в Яндекс.
2. Откройте инструменты разработчика браузера (F12), затем Application → Cookies.
3. Найдите `Session_id` для `.yandex.ru` и скопируйте значение.
4. Передайте значение через `YANDEX_SESSION_ID` или заголовок `X-Yandex-Cookie`, как описано в [README.md](README.md).

Cookie даёт доступ к вашей сессии Яндекса. Не публикуйте её и обновите, если Яндекс запросит повторный вход.
