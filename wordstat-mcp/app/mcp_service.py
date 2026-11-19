"""Wordstat website integration used by the MCP server."""
import calendar
import os
import re
from datetime import date
from http.cookies import SimpleCookie, CookieError

import requests


class WordstatError(Exception):
    pass


def resolve_cookie(headers):
    """Use the request cookie, when provided, otherwise the container setting."""
    raw = headers.get("x-yandex-cookie") or headers.get("cookie")
    if raw is None:
        raw = os.getenv("YANDEX_SESSION_ID", "")
    raw = raw.strip()
    if not raw:
        raise WordstatError("Передайте Session_id в X-Yandex-Cookie или задайте YANDEX_SESSION_ID.")
    if "\r" in raw or "\n" in raw:
        raise WordstatError("Некорректный заголовок cookie.")
    if "=" not in raw:
        return f"Session_id={raw}"
    try:
        cookie = SimpleCookie()
        cookie.load(raw)
    except CookieError:
        raise WordstatError("Некорректный заголовок cookie.") from None
    if "Session_id" not in cookie or not cookie["Session_id"].value:
        raise WordstatError("В cookie отсутствует Session_id.")
    return raw


def _post(cookie, endpoint, payload):
    try:
        with requests.Session() as session:
            session.headers.update({"Cookie": cookie, "Content-Type": "application/json",
                                    "Origin": "https://wordstat.yandex.ru",
                                    "Referer": "https://wordstat.yandex.ru/",
                                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/125.0.0.0 Safari/537.36"})
            response = session.post(endpoint, json=payload, timeout=40, allow_redirects=False)
            if response.status_code in (301, 302, 303, 307, 308, 401, 403):
                raise WordstatError("Яндекс отклонил запрос или перенаправил на авторизацию; проверьте cookie.")
            if response.status_code != 200:
                raise WordstatError(f"Wordstat вернул HTTP {response.status_code}.")
            data = response.json()
            if not isinstance(data, dict):
                raise WordstatError("Wordstat вернул неожиданный формат ответа.")
            return data
    except requests.RequestException:
        raise WordstatError("Не удалось выполнить запрос к Wordstat.") from None
    except ValueError:
        raise WordstatError("Wordstat вернул некорректный JSON.") from None


def top_requests(cookie, phrase, region="all"):
    payload = {"currentDevice": "desktop,phone,tablet", "dbname": "rus",
               "filters": {"region": region, "tableType": "popular"}, "searchValue": phrase}
    data = _post(cookie, "https://wordstat.yandex.ru/wordstat/api/getTable", payload)
    try:
        popular = data["table"]["tableData"]["popular"]
        if not isinstance(popular, list):
            raise TypeError
        rows = [{"text": item["text"], "value": int(item["value"])}
                for item in popular if not item.get("isAssociations") and item.get("value")]
    except (KeyError, TypeError, ValueError):
        raise WordstatError("Wordstat вернул неожиданный формат таблицы.") from None
    return {"phrase": phrase, "period": "окно по умолчанию на сайте Wordstat", "results": rows}


def monthly_dynamics(cookie, phrase, start_date, end_date, region="all"):
    try:
        start, end = date.fromisoformat(start_date), date.fromisoformat(end_date)
    except ValueError:
        raise WordstatError("Даты должны быть в формате YYYY-MM-DD.") from None
    months = (end.year - start.year) * 12 + end.month - start.month + 1
    if start.day != 1 or end.day != calendar.monthrange(end.year, end.month)[1] or months < 3:
        raise WordstatError("Укажите период от трёх полных месяцев: с первого до последнего дня месяца.")
    payload = {"currentDevice": "desktop,phone,tablet", "currentGraphType": "month", "dbname": "rus",
               "filters": {"region": region, "tableType": "popular"}, "searchValue": phrase,
               "startDate": start.strftime("%d.%m.%Y"), "endDate": end.strftime("%d.%m.%Y"),
               "text": {key: {"title": "", "disclaimer": ""} for key in ("graph", "map", "table")}}
    data = _post(cookie, "https://wordstat.yandex.ru/wordstat/api/getGraph", payload)
    try:
        points = data["graph"]["images"]["timeSeries"]["preparedValues"]["absolute"]
        if not isinstance(points, list):
            raise TypeError
        points = [{**point, "month1": point["month"] + 1} for point in points]
    except (KeyError, TypeError):
        raise WordstatError("Wordstat вернул неожиданный формат графика.") from None
    return {"phrase": phrase, "start_date": start_date, "end_date": end_date, "points": points,
            "note": "Яндекс публикует месячные данные с задержкой; последний месяц может отсутствовать."}


def suggestions(phrase):
    try:
        response = requests.get(
            "https://suggest.yandex.ru/suggest-ya.cgi",
            params={"part": phrase, "uil": "ru", "srv": "suggest-home", "nouserita": "1"},
            headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) Chrome/125.0.0.0 Safari/537.36",
                     "Accept-Language": "ru-RU,ru;q=0.9"}, timeout=8)
        if response.status_code != 200:
            raise WordstatError(f"Яндекс Подсказки вернули HTTP {response.status_code}.")
        match = re.search(r'\["[^"]*",\[([^\]]*)\]', response.text)
        if not match:
            raise WordstatError("Яндекс Подсказки вернули неожиданный формат ответа.")
        return {"phrase": phrase, "suggestions": re.findall(r'"([^"]+)"', match.group(1))}
    except requests.RequestException:
        raise WordstatError("Не удалось получить подсказки Яндекса.") from None
