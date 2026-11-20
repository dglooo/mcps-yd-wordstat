# Директ и Wordstat: настройка и справка

## Настройка (один раз, делает владелец)
1. **Права ключа.** https://avadge.com/admin/tasks/keypolicy/ → строка ключа человека
   (нет строки → «Добавить», выбрать ключ). Галочки:
   | Право | Что даёт |
   |---|---|
   | `can_use_wordstat` | все `wordstat_*` |
   | `can_use_yandex_ads` | чтение `yd_*` |
   | `can_write_yandex_ads` | запись `yd_*` (нужно и `can_use_yandex_ads`) |

   По умолчанию все три выключены.
2. **OAuth-токен Директа, один на домен.** Покрывает Директ, Метрику и Аудитории кабинета.
   - Выпуск: приложение на https://oauth.yandex.ru с правом `direct:api`
     (плюс `metrika:read` / `metrika:write`, Аудитории — если нужны), затем
     `https://oauth.yandex.ru/authorize?response_type=token&client_id=<Client ID>` → токен `y0_…`.
   - Куда: https://avadge.com/management/seo → «Интеграции» → **сначала выбрать домен в переключателе
     сверху** → карточка «Яндекс Директ · токен домена» → вставить → сохранить.
     Токен ляжет на тот домен, который выбран в переключателе.
   - Запасной путь: https://avadge.com/admin/credentials/sitesecret/ (name `yandex_ads`, host = домен).
3. **Cookie Wordstat, у каждого человека свой.**
   - Войти в Яндекс, открыть https://wordstat.yandex.ru → F12 → Application → Cookies →
     `.yandex.ru` → скопировать значение `Session_id`. Подходит и полная строка cookie с `Session_id=`.
   - Передать: в сессии Claude «обнови cookie Wordstat: <значение>» → `wordstat_set_cookie(value)`.
     Запасной путь: https://avadge.com/admin/credentials/keysecret/ (name `wordstat`, ключ человека).
   - Протухает после выхода из Яндекса или запроса повторного входа. Тогда повторить.
   - Cookie даёт доступ к аккаунту Яндекса: не публиковать, не пересылать, не писать в заметки.

## Проверка
Только в **новой** сессии Claude: старая помнит прежний список инструментов.
- `call_tool("wordstat_top_requests", {"phrase": "купить bmw x5"})` → частотности;
- `call_tool("yd_campaigns_get", {"site": "<домен с токеном>"})` → список кампаний;
- любая запись `yd_*` → превью `confirm_required`, выполняется только повтором с `confirm=true`.

Что значат ответы:
- «нет права …» → шаг 1;
- «Токен … для домена X не задан» → шаг 2, токен лежит на другом домене или не внесён;
- «Cookie Wordstat не задан» → шаг 3.

## Ограничения
- `site` у `yd_*` по умолчанию `avadge.com`. На 20.11.2026 токен внесён только для `avadge-detailing.ru`.
- `wordstat_monthly_dynamics`: даты YYYY-MM-DD, минимум 3 полных месяца. Свежий месяц может запаздывать.
- `wordstat_top_requests` игнорирует даты: окно задаёт сайт Wordstat. Формат внутренних запросов Wordstat может смениться.
- `yd_audience_segment_upload`, `yd_videos_upload` выключены: они читают файлы с диска сервера.
- Описания `yd_*` английские: ищи `search_tools("campaigns")`, а не по-русски.
