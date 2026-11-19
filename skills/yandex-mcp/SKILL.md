---
name: yandex-mcp
description: Яндекс Директ (кампании, группы, объявления, ключевые фразы, ставки, отчёты, Метрика и Аудитории кабинета) и Wordstat (частотность, динамика, подсказки) через MCP-сервер avadge — инструменты yd_* и wordstat_*, обновление cookie Wordstat (wordstat_set_cookie), запись в Директ только с подтверждением. Используй, когда просят посмотреть или поменять рекламу в Директе, снять частотность или динамику запроса в Wordstat, или когда wordstat_* просит cookie.
---

# Директ и Wordstat через avadge

MCP `avadge` показывает только `search_tools`, `describe_tool`, `call_tool`.
Порядок: `search_tools("кампании")` или `search_tools("yd_campaigns")` →
`describe_tool(name)` → `call_tool(name=…, arguments={…})`. По кругу не искать.

## Директ (`yd_*`)
- `site` в arguments = домен кабинета, по умолчанию `avadge.com`. Токен домена берётся из базы сайта.
- По умолчанию только чтение. Запись дают только ключу с правом `can_write_yandex_ads`.
- Запись в два шага: первый вызов возвращает превью (`confirm_required`). Покажи превью
  человеку. Повтори вызов с `confirm=true` только после его явного «да».
- Агентский кабинет: `client_login` в arguments.
- `seo_direct_*` — это ядро фраз SEO Hub, а не API Директа. Не путай.
- Метрика внутри `yd_*` использует токен Директа. Метрику SEO Hub она не заменяет.

## Wordstat (`wordstat_*`)
- `wordstat_top_requests(phrase, region)` — частотность и похожие запросы.
- `wordstat_monthly_dynamics(phrase, start_date, end_date)` — даты YYYY-MM-DD, минимум 3 полных месяца.
- `wordstat_suggest(phrase)` — подсказки.
- Cookie у каждого ключа свой. Ответ «cookie не задан» или ошибка входа в Яндекс → попроси у человека
  свежий `Session_id` (как его взять: references/direct-wordstat.md) →
  `call_tool(name="wordstat_set_cookie", arguments={"value": "…"})` → повтори вызов.
  Значение cookie не повторяй в ответе и не сохраняй в заметки.

## Ошибки
- 403 с именем права (`can_use_wordstat`, `can_use_yandex_ads`, `can_write_yandex_ads`) — у ключа нет права. Права выдаёт владелец в админке сайта, сам не обходи.
- «Токен Яндекс Директа для домена … не задан» — токен вносит владелец: панель → SEO Hub → Интеграции.
- «подсервер … недоступен» — скажи человеку и остановись, не повторяй вызов.
