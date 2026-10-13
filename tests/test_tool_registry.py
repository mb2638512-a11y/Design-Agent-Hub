from design_agent_hub.tool_registry import list_tool_catalog, search_tool_catalog


def test_catalog_has_separate_builtin_mcp_and_api_hubs():
    catalog = list_tool_catalog()
    assert set(catalog["items"]) == {"builtin", "mcp", "api"}
    assert catalog["counts"]["builtin"] >= 10
    assert catalog["counts"]["mcp"] >= 10
    assert catalog["counts"]["api"] >= 10
    assert catalog["catalog_is_metadata_not_installation"] is True


def test_no_key_filter_excludes_integrations_that_need_external_keys():
    catalog = list_tool_catalog(no_key_only=True)
    assert catalog["counts"]["builtin"] >= 10
    for items in catalog["items"].values():
        assert all(not item.get("needs_external_api_key", False) for item in items)


def test_search_can_scope_to_one_hub():
    matches = search_tool_catalog("browser", "mcp")
    assert matches
    assert all(item["id"].startswith("mcp-") for item in matches)


def test_invalid_kind_returns_clear_error():
    assert "error" in list_tool_catalog("unknown")
