from design_agent_hub.tool_registry import list_tool_catalog, search_tool_catalog


def test_catalog_has_separate_builtin_mcp_and_api_hubs():
    catalog = list_tool_catalog()
    assert set(catalog["items"]) == {"builtin", "mcp", "api"}
    assert catalog["counts"]["builtin"] >= 10
    assert catalog["counts"]["mcp"] >= 10
    assert catalog["counts"]["api"] >= 10
    assert catalog["catalog_is_metadata_not_installation"] is True


def test_free_only_filters_integrations_requiring_external_api_keys():
    catalog = list_tool_catalog(free_only=True)
    assert catalog["counts"]["builtin"] >= 10
    for items in catalog["items"].values():
        assert all(not item.get("needs_external_api_key", False) for item in items)


def test_search_can_scope_to_one_hub():
    matches = search_tool_catalog("browser", "mcp")
    assert matches
    assert all(item["id"].startswith("mcp-") for item in matches)


def test_invalid_kind_returns_clear_error():
    result = list_tool_catalog("unknown")
    assert "error" in result
