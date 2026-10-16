from __future__ import annotations

import importlib
from urllib.parse import parse_qs, urlparse

import pytest

from app.governed_conversational_request_mode import (
    GovernedConversationalRequestMode,
)
from app.governed_information_sources import InformationSourceCapability
from app.governed_source_query import GovernedSourceQuery

MODULE = "app.wikimedia_commons_governed_source"


def _adapter_module():
    return importlib.import_module(MODULE)


def _query(**changes: object) -> GovernedSourceQuery:
    values = {
        "source_id": "wikimedia_commons",
        "topics": frozenset(),
        "query_text": "Patagonian glaciers",
        "limit": 100,
        "timeout_seconds": 7.5,
        "mode": GovernedConversationalRequestMode.OPEN_VISUAL_SUBJECT,
    }
    values.update(changes)
    return GovernedSourceQuery(**values)


def _sample_payload() -> bytes:
    return b"""{
      "query": {
        "pages": {
          "42": {
            "pageid": 42,
            "title": "File:Glacier.jpg",
            "imageinfo": [{
              "url": "https://upload.wikimedia.org/glacier.jpg",
              "thumburl": "https://upload.wikimedia.org/thumb/glacier.jpg",
              "descriptionurl": "https://commons.wikimedia.org/wiki/File:Glacier.jpg",
              "mime": "image/jpeg",
              "mediatype": "BITMAP",
              "timestamp": "2025-01-02T03:04:05Z",
              "user": "ExampleUploader",
              "extmetadata": {
                "Artist": {"value": "Example Artist"},
                "Credit": {"value": "Example Credit"},
                "LicenseShortName": {"value": "CC BY-SA 4.0"},
                "LicenseUrl": {
                  "value": "https://creativecommons.org/licenses/by-sa/4.0/"
                }
              }
            }]
          }
        }
      }
    }"""


def test_adapter_module_and_canonical_source_declaration_exist():
    module = _adapter_module()
    adapter_type = module.WikimediaCommonsGovernedSourceAdapter
    declaration = adapter_type.source_declaration
    assert adapter_type.SOURCE_ID == "wikimedia_commons"
    assert declaration.source_id == "wikimedia_commons"
    assert declaration.topics == frozenset()
    assert (
        InformationSourceCapability.OPEN_VISUAL_SUBJECT_QUERY
        in declaration.capabilities
    )


def test_request_is_bounded_file_namespace_imageinfo_query():
    module = _adapter_module()
    url = module.WikimediaCommonsGovernedSourceAdapter._build_url(_query())
    parsed = urlparse(url)
    parameters = parse_qs(parsed.query)
    assert parsed.scheme == "https"
    assert parsed.netloc == "commons.wikimedia.org"
    assert parsed.path == "/w/api.php"
    assert parameters["action"] == ["query"]
    assert parameters["format"] == ["json"]
    assert parameters["generator"] == ["search"]
    assert parameters["gsrsearch"] == ["Patagonian glaciers"]
    assert parameters["gsrnamespace"] == ["6"]
    assert parameters["gsrlimit"] == ["20"]
    assert parameters["prop"] == ["imageinfo"]
    assert parameters["iilimit"] == ["1"]
    assert parameters["iiurlwidth"] == ["640"]
    assert "url" in parameters["iiprop"][0]
    assert "extmetadata" in parameters["iiprop"][0]


def test_user_parameters_cannot_override_provider_policy():
    module = _adapter_module()
    query = _query(
        parameters={
            "action": "edit",
            "gsrnamespace": "0",
            "gsrlimit": "99",
            "prop": "revisions",
            "iiurlwidth": "9999",
        }
    )
    parameters = parse_qs(
        urlparse(module.WikimediaCommonsGovernedSourceAdapter._build_url(query)).query
    )
    assert parameters["action"] == ["query"]
    assert parameters["gsrnamespace"] == ["6"]
    assert parameters["gsrlimit"] == ["20"]
    assert parameters["prop"] == ["imageinfo"]
    assert parameters["iiurlwidth"] == ["640"]


def test_configured_user_agent_is_required_before_network_io():
    module = _adapter_module()
    adapter_type = module.WikimediaCommonsGovernedSourceAdapter
    with pytest.raises(ValueError):
        adapter_type(user_agent="   ")


def test_execute_propagates_timeout_and_projects_bounded_metadata():
    module = _adapter_module()
    observed: list[tuple[str, float]] = []

    def transport(url: str, timeout_seconds: float) -> bytes:
        observed.append((url, timeout_seconds))
        return _sample_payload()

    adapter = module.WikimediaCommonsGovernedSourceAdapter(
        user_agent="ROBY-XI.2/1.0 (contact: operator@example.invalid)",
        transport=transport,
    )
    items = adapter.execute(_query())
    assert observed and observed[0][1] == 7.5
    assert len(items) == 1
    item = items[0]
    assert item["source_id"] == "wikimedia_commons"
    assert item["external_id"] == "42"
    assert item["media_type"] == "image"
    assert item["preview_url"].startswith("https://")
    assert item["source_url"].startswith("https://commons.wikimedia.org/")
    assert item["uploader"] == "ExampleUploader"
    assert item["artist"] == "Example Artist"
    assert item["credit"] == "Example Credit"
    assert item["license_short_name"] == "CC BY-SA 4.0"
    assert item["license_url"].startswith("https://creativecommons.org/")


def test_non_https_or_non_image_preview_is_rejected():
    module = _adapter_module()
    adapter_type = module.WikimediaCommonsGovernedSourceAdapter
    payload = _sample_payload().replace(
        b"https://upload.wikimedia.org/thumb/glacier.jpg",
        b"http://upload.wikimedia.org/thumb/glacier.jpg",
    )
    adapter = adapter_type(
        user_agent="ROBY-XI.2/1.0 (contact: operator@example.invalid)",
        transport=lambda _url, _timeout: payload,
    )
    assert adapter.execute(_query()) == ()


def test_malformed_provider_payload_fails_closed():
    module = _adapter_module()
    adapter = module.WikimediaCommonsGovernedSourceAdapter(
        user_agent="ROBY-XI.2/1.0 (contact: operator@example.invalid)",
        transport=lambda _url, _timeout: b"{not-json",
    )
    with pytest.raises((ValueError, TypeError)):
        adapter.execute(_query())


def test_adapter_contract_does_not_introduce_parallel_authorities():
    forbidden = (
        "app.wikimedia_commons_source_registry",
        "app.wikimedia_commons_query_executor",
        "app.wikimedia_commons_source_selector",
        "app.wikimedia_commons_image_presenter",
        "app.wikimedia_commons_retry_manager",
    )
    for module_name in forbidden:
        with pytest.raises(ModuleNotFoundError):
            importlib.import_module(module_name)
