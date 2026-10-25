"""Mocked Hudson Rock responses; no network is used."""

from types import SimpleNamespace
from unittest.mock import Mock

from anubis.scanners import hudson_rock


def make_scanner(domains=None):
  return SimpleNamespace(domains=domains or [], options={"--verbose": True},
                         handle_exception=Mock())


def mock_response(monkeypatch, payload):
  get = Mock(return_value=SimpleNamespace(json=lambda: payload))
  monkeypatch.setattr(hudson_rock.requests, "get", get)
  return get


def test_extracts_in_scope_hosts_from_all_urls(monkeypatch):
  # Same shape as the live API: data.all_urls is a list of {url, type, ...}
  get = mock_response(monkeypatch, {"data": {"all_urls": [
    {"url": "https://sso.example.com/adfs/ls", "type": "Employee"},
    {"url": "https://sso.example.com", "type": "Employee"},
    {"url": "http://www.example.com:8080/login", "type": "User"},
    {"url": "https://example.com/", "type": "User"},
    {"url": "https://notexample.com/", "type": "User"},
    {"url": "https://example.com.evil.test/", "type": "User"},
    {"url": '"https://auth.example.com/oauth2",', "type": "User"},
    {"url": "https://[bad/", "type": "User"},
    {"type": "User"},
  ]}})
  scanner = make_scanner(["www.example.com"])

  hudson_rock.search_hudsonrock(scanner, "example.com")

  get.assert_called_once()
  assert scanner.domains == ["www.example.com", "sso.example.com"]
  scanner.handle_exception.assert_not_called()


def test_missing_data_adds_nothing(monkeypatch):
  mock_response(monkeypatch, {"error": "rate limited"})
  scanner = make_scanner()

  hudson_rock.search_hudsonrock(scanner, "example.com")

  assert scanner.domains == []
  scanner.handle_exception.assert_not_called()


def test_request_error_is_handled(monkeypatch):
  error = hudson_rock.requests.RequestException("synthetic failure")
  monkeypatch.setattr(hudson_rock.requests, "get", Mock(side_effect=error))
  scanner = make_scanner()

  hudson_rock.search_hudsonrock(scanner, "example.com")

  assert scanner.domains == []
  scanner.handle_exception.assert_called_once_with(error,
                                                   "Error searching HudsonRock")
