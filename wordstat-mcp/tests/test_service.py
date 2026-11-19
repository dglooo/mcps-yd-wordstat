import os
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
import mcp_service as service


class ServiceTests(unittest.TestCase):
    @patch.dict(os.environ, {"YANDEX_SESSION_ID": "env-secret"})
    def test_request_cookie_overrides_env_and_is_not_shared(self):
        self.assertEqual(service.resolve_cookie({"x-yandex-cookie": "header-secret"}), "Session_id=header-secret")
        self.assertEqual(service.resolve_cookie({"cookie": "foo=bar; Session_id=other"}), "foo=bar; Session_id=other")
        self.assertEqual(service.resolve_cookie({}), "Session_id=env-secret")
        with self.assertRaises(service.WordstatError):
            service.resolve_cookie({"x-yandex-cookie": "foo=bar"})

    @patch.dict(os.environ, {"YANDEX_SESSION_ID": ""})
    def test_missing_and_invalid_cookie(self):
        for headers in ({}, {"x-yandex-cookie": "foo=bar"}, {"x-yandex-cookie": "secret\r\nother"}):
            with self.subTest(headers=headers), self.assertRaises(service.WordstatError):
                service.resolve_cookie(headers)

    def test_top_requests_filters_and_payload(self):
        response = {"table": {"tableData": {"popular": [
            {"text": "one", "value": "12"}, {"text": "related", "value": 3, "isAssociations": True}]}}}
        with patch.object(service, "_post", return_value=response) as post:
            result = service.top_requests("Session_id=secret", "test", "all")
        self.assertEqual(result["results"], [{"text": "one", "value": 12}])
        self.assertEqual(post.call_args.args[2]["searchValue"], "test")
        with patch.object(service, "_post", return_value={}):
            with self.assertRaises(service.WordstatError):
                service.top_requests("Session_id=secret", "test")

    def test_months_validated_and_converted(self):
        points = [{"year": 2026, "month": 0, "y": 42}]
        response = {"graph": {"images": {"timeSeries": {"preparedValues": {"absolute": points}}}}}
        with patch.object(service, "_post", return_value=response) as post:
            result = service.monthly_dynamics("Session_id=x", "test", "2026-01-01", "2026-03-31")
        self.assertEqual(result["points"][0]["month1"], 1)
        self.assertEqual(post.call_args.args[2]["startDate"], "01.01.2026")
        for start, end in [("2026-01-02", "2026-03-31"), ("2026-01-01", "2026-02-28")]:
            with self.subTest(start=start, end=end), self.assertRaises(service.WordstatError):
                service.monthly_dynamics("Session_id=x", "test", start, end)

    def test_redirect_does_not_forward_cookie(self):
        response = Mock(status_code=302)
        session = Mock()
        session.headers = {}
        session.post.return_value = response
        context = Mock()
        context.__enter__ = Mock(return_value=session)
        context.__exit__ = Mock(return_value=False)
        with patch.object(service.requests, "Session", return_value=context):
            with self.assertRaises(service.WordstatError):
                service.top_requests("Session_id=secret", "test")
        self.assertFalse(session.post.call_args.kwargs["allow_redirects"])
        self.assertEqual(session.headers["Cookie"], "Session_id=secret")

    def test_suggestions(self):
        response = Mock(status_code=200, text='suggest.apply(["abc",["abc one","abc two"],[]])')
        with patch.object(service.requests, "get", return_value=response):
            self.assertEqual(service.suggestions("abc")["suggestions"], ["abc one", "abc two"])


if __name__ == "__main__":
    unittest.main()
