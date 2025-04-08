from datetime import datetime
import json
from unittest.mock import AsyncMock, Mock, patch

import pytest


# Mock the mycelium imports
class Message:
    def __init__(self, id, data):
        self.id = id
        self.data = data


class Topic:
    def __init__(self, name):
        self.name = name


class MyceliumClient:
    def __init__(self):
        self.published_messages = []
        self.subscriptions = {}

    def subscribe(self, topic: str):
        def decorator(func):
            self.subscriptions[topic] = func
            return func

        return decorator

    async def publish(self, topic: str, data: dict):
        self.published_messages.append(
            {"topic": topic, "data": data, "timestamp": datetime.now().isoformat()}
        )

    async def trigger_message(self, topic: str, message_data: dict):
        """Simulate receiving a message on a topic."""
        if topic in self.subscriptions:
            message = Message(id="test_msg_" + datetime.now().isoformat(), data=message_data)
            await self.subscriptions[topic](message)


# Use the mocks to patch the import in cartographer.py
with patch.dict("sys.modules", {"mycelium": Mock()}):
    from subsystems.ATLAS.core.cartographer import AtlasCartographer


@pytest.fixture
def mock_mycelium():
    """Fixture providing a mock Mycelium client."""
    return MyceliumClient()


@pytest.fixture
def test_config():
    """Fixture providing test configuration."""
    return {
        "max_depth": 3,
        "cache_duration": 60,
        "mycelium": {
            "topics": {
                "map_request": "test.atlas.map.request",
                "map_result": "test.atlas.map.result",
                "metadata_update": "test.atlas.metadata.update",
                "metadata_status": "test.atlas.metadata.status",
                "relationship_update": "test.atlas.relationship.update",
                "relationship_status": "test.atlas.relationship.status",
                "alert": "test.atlas.alert",
            }
        },
        "visualization": {  # Added based on likely config
            "default_format": "json",
            "formats": ["json", "mermaid", "dot"],
        },
        "mapping": {  # Added based on likely config
            "relationship_types": [
                "depends_on",
                "imports",
                "extends",
                "implements",
                "contains",
                "calls",
            ]
        },
    }


@pytest.fixture
def cartographer(mock_mycelium, test_config, tmp_path):
    """Fixture providing configured AtlasCartographer instance."""
    config_path = tmp_path / "test_config.json"
    with open(config_path, "w") as f:
        json.dump(test_config, f)
    # Mock internal data structures for consistent testing
    instance = AtlasCartographer(config_path=config_path, mycelium_client=mock_mycelium)
    instance.system_map = {}
    instance.relationships = {}
    instance.metadata = {}
    instance.analysis_cache = {}
    return instance


@pytest.mark.asyncio
async def test_map_request_handler(cartographer, mock_mycelium):
    """Test handling of map requests via Mycelium."""
    # Setup test data
    target = "test_component"
    cartographer.system_map = {target: {"type": "service"}, "related": {"type": "database"}}
    cartographer.relationships = {
        target: [{"source": target, "target": "related", "type": "depends_on"}]
    }
    cartographer.metadata = {target: {"version": "1.0"}, "related": {"version": "2.0"}}

    # Trigger map request
    await mock_mycelium.trigger_message(
        "test.atlas.map.request", {"target": target, "depth": 2, "include_metadata": True}
    )

    # Verify published result
    assert len(mock_mycelium.published_messages) == 1
    result = mock_mycelium.published_messages[0]
    assert result["topic"] == "test.atlas.map.result"
    assert result["data"]["target"] == target

    # Check map structure
    map_data = result["data"]["map"]
    assert target in map_data["nodes"]
    assert "related" in map_data["nodes"]
    assert len(map_data["relationships"]) == 1
    assert map_data["metadata"][target]["version"] == "1.0"


@pytest.mark.asyncio
async def test_metadata_update_handler(cartographer, mock_mycelium):
    """Test handling of metadata updates via Mycelium."""
    component = "test_service"
    metadata = {"version": "1.1", "status": "active", "dependencies": ["db", "cache"]}

    # Trigger metadata update
    await mock_mycelium.trigger_message(
        "test.atlas.metadata.update", {"component": component, "metadata": metadata}
    )

    # Verify metadata was updated
    assert component in cartographer.metadata
    assert cartographer.metadata[component] == metadata

    # Check confirmation message
    assert len(mock_mycelium.published_messages) == 1
    status = mock_mycelium.published_messages[0]
    assert status["topic"] == "test.atlas.metadata.status"
    assert status["data"]["status"] == "success"
    assert status["data"]["component"] == component


@pytest.mark.asyncio
async def test_relationship_update_handler(cartographer, mock_mycelium):
    """Test handling of relationship updates via Mycelium."""
    source = "service_a"
    target = "service_b"
    rel_type = "calls"
    metadata = {"frequency": "high"}

    # Trigger relationship update
    await mock_mycelium.trigger_message(
        "test.atlas.relationship.update",
        {"source": source, "target": target, "type": rel_type, "metadata": metadata},
    )

    # Verify relationship was updated
    assert source in cartographer.relationships
    relationships = cartographer.relationships[source]
    assert len(relationships) == 1
    relationship = relationships[0]
    assert relationship["source"] == source
    assert relationship["target"] == target
    assert relationship["type"] == rel_type
    assert relationship["metadata"] == metadata

    # Check confirmation message
    assert len(mock_mycelium.published_messages) == 1
    status = mock_mycelium.published_messages[0]
    assert status["topic"] == "test.atlas.relationship.status"
    assert status["data"]["status"] == "success"
    assert status["data"]["source"] == source
    assert status["data"]["target"] == target


@pytest.mark.asyncio
async def test_map_request_depth_limit(cartographer, mock_mycelium):
    """Test that map depth is limited according to configuration."""
    target = "root"
    cartographer.system_map = {"root": {}, "level1": {}, "level2": {}, "level3": {}, "level4": {}}
    cartographer.relationships = {
        "root": [{"source": "root", "target": "level1", "type": "contains"}],
        "level1": [{"source": "level1", "target": "level2", "type": "contains"}],
        "level2": [{"source": "level2", "target": "level3", "type": "contains"}],
        "level3": [{"source": "level3", "target": "level4", "type": "contains"}],
    }

    # Request depth beyond limit
    await mock_mycelium.trigger_message(
        "test.atlas.map.request",
        {"target": target, "depth": 5},  # Config max is 3
    )

    # Verify depth was limited
    assert len(mock_mycelium.published_messages) == 2  # Map result and alert

    # Check alert
    alert = mock_mycelium.published_messages[0]
    assert alert["topic"] == "test.atlas.alert"
    assert alert["data"]["type"] == "map_depth_limited"

    # Check map result
    result = mock_mycelium.published_messages[1]
    map_data = result["data"]["map"]
    assert len(map_data["nodes"]) <= 4  # root + 3 levels


@pytest.mark.asyncio
async def test_map_request_error_handling(cartographer, mock_mycelium):
    """Test error handling in map request processing."""
    # Mock generate_map to raise an exception
    cartographer.generate_map = AsyncMock(side_effect=ValueError("Invalid target"))

    # Trigger map request
    await mock_mycelium.trigger_message("test.atlas.map.request", {"target": "nonexistent"})

    # Verify error response
    assert len(mock_mycelium.published_messages) == 1
    error_msg = mock_mycelium.published_messages[0]
    assert error_msg["topic"] == "test.atlas.map.result"
    assert error_msg["data"]["status"] == "error"
    assert "Invalid target" in error_msg["data"]["error"]


@pytest.mark.asyncio
async def test_metadata_update_error_handling(cartographer, mock_mycelium):
    """Test error handling in metadata update processing."""
    # Mock update_metadata to raise an exception
    cartographer.update_metadata = AsyncMock(side_effect=ValueError("Invalid metadata"))

    # Trigger metadata update
    await mock_mycelium.trigger_message(
        "test.atlas.metadata.update", {"component": "test", "metadata": {}}
    )

    # Verify error response
    assert len(mock_mycelium.published_messages) == 1
    error_msg = mock_mycelium.published_messages[0]
    assert error_msg["topic"] == "test.atlas.metadata.status"
    assert error_msg["data"]["status"] == "error"
    assert "Invalid metadata" in error_msg["data"]["error"]


@pytest.mark.asyncio
async def test_relationship_update_error_handling(cartographer, mock_mycelium):
    """Test error handling in relationship update processing."""
    # Mock update_relationship to raise an exception
    cartographer.update_relationship = AsyncMock(
        side_effect=ValueError("Invalid relationship data")
    )

    # Trigger relationship update
    await mock_mycelium.trigger_message(
        "test.atlas.relationship.update", {"source": "a", "target": "b", "type": "invalid"}
    )

    # Verify error response
    assert len(mock_mycelium.published_messages) == 1
    error_msg = mock_mycelium.published_messages[0]
    assert error_msg["topic"] == "test.atlas.relationship.status"
    assert error_msg["data"]["status"] == "error"
    assert "Invalid relationship data" in error_msg["data"]["error"]


@pytest.mark.asyncio
async def test_alert_publishing(cartographer, mock_mycelium):
    """Test publishing alerts through Mycelium."""
    alert_type = "test_alert"
    message = "This is a test alert"
    details = {"component": "test", "severity": "low"}

    await cartographer._publish_alert(alert_type, message, details)

    assert len(mock_mycelium.published_messages) == 1
    alert = mock_mycelium.published_messages[0]
    assert alert["topic"] == "test.atlas.alert"
    assert alert["data"]["type"] == alert_type
    assert alert["data"]["message"] == message
    assert alert["data"]["details"] == details


@pytest.mark.asyncio
async def test_generate_map_empty(cartographer):
    """Test generating a map when no data exists."""
    map_data = await cartographer.generate_map("any_target", depth=1)
    assert not map_data["nodes"]
    assert not map_data["relationships"]
    assert not map_data["metadata"]


@pytest.mark.asyncio
async def test_generate_map_complex(cartographer):
    """Test generating a map with multiple levels and relationships."""
    # Setup complex map data directly in the cartographer instance
    cartographer.system_map = {
        "root": {"type": "system"},
        "svc_a": {"type": "service"},
        "svc_b": {"type": "service"},
        "db_a": {"type": "database"},
        "lib_c": {"type": "library"},
    }
    cartographer.relationships = {
        "root": [
            {"source": "root", "target": "svc_a", "type": "contains"},
            {"source": "root", "target": "svc_b", "type": "contains"},
        ],
        "svc_a": [
            {"source": "svc_a", "target": "db_a", "type": "uses"},
            {"source": "svc_a", "target": "lib_c", "type": "imports"},
        ],
        "svc_b": [{"source": "svc_b", "target": "db_a", "type": "uses"}],
    }
    cartographer.metadata = {
        "root": {"version": "1.0"},
        "svc_a": {"language": "python"},
        "svc_b": {"language": "python"},
        "db_a": {"engine": "postgres"},
        "lib_c": {"version": "2.1"},
    }

    # Generate map from root with sufficient depth
    map_data = await cartographer.generate_map("root", depth=3, include_metadata=True)

    # Verify nodes
    assert len(map_data["nodes"]) == 5
    assert "root" in map_data["nodes"]
    assert "svc_a" in map_data["nodes"]
    assert "svc_b" in map_data["nodes"]
    assert "db_a" in map_data["nodes"]
    assert "lib_c" in map_data["nodes"]

    # Verify relationships (total expected: 5)
    assert len(map_data["relationships"]) == 5  # There are 5 relationships total
    rel_targets = set(r["target"] for r in map_data["relationships"])
    assert "svc_a" in rel_targets
    assert "svc_b" in rel_targets
    assert "db_a" in rel_targets  # Should be included twice via svc_a and svc_b
    assert "lib_c" in rel_targets

    # Verify metadata inclusion
    assert len(map_data["metadata"]) == 5
    assert map_data["metadata"]["root"] == {"version": "1.0"}
    assert map_data["metadata"]["svc_a"] == {"language": "python"}
    assert map_data["metadata"]["db_a"] == {"engine": "postgres"}


@pytest.mark.asyncio
async def test_generate_map_no_metadata(cartographer):
    """Test generating a map without including metadata."""
    cartographer.system_map = {"comp_a": {"type": "module"}}
    cartographer.metadata = {"comp_a": {"version": "1.0"}}

    map_data = await cartographer.generate_map("comp_a", depth=1, include_metadata=False)

    assert "comp_a" in map_data["nodes"]
    assert not map_data["metadata"]  # Metadata should be empty


# --- Tests for Core Data Update Functionality ---


@pytest.mark.asyncio
async def test_update_metadata_existing(cartographer):
    """Test updating metadata for an existing component."""
    component = "comp_x"
    initial_metadata = {"version": "1.0", "status": "beta"}
    updated_metadata = {"version": "1.1", "status": "stable", "owner": "team_a"}

    # Set initial state
    cartographer.metadata[component] = initial_metadata

    # Perform update
    await cartographer.update_metadata(
        component, {"version": "1.1", "status": "stable", "owner": "team_a"}
    )

    # Verify update
    assert cartographer.metadata[component] == updated_metadata


@pytest.mark.asyncio
async def test_update_metadata_new(cartographer):
    """Test adding metadata for a new component."""
    component = "comp_new"
    metadata = {"language": "go", "created": "2024-03-21"}

    assert component not in cartographer.metadata

    # Add metadata
    await cartographer.update_metadata(component, metadata)

    # Verify addition
    assert component in cartographer.metadata
    assert cartographer.metadata[component] == metadata


@pytest.mark.asyncio
async def test_update_relationship_existing(cartographer):
    """Test updating an existing relationship (by adding metadata)."""
    source = "mod_a"
    target = "mod_b"
    rel_type = "imports"
    initial_relationship = {"source": source, "target": target, "type": rel_type}
    update_metadata = {"conditional": True}
    expected_relationship = {
        "source": source,
        "target": target,
        "type": rel_type,
        "metadata": update_metadata,
    }

    # Set initial state
    cartographer.relationships[source] = [initial_relationship]

    # Update with metadata
    await cartographer.update_relationship(source, target, rel_type, update_metadata)

    # Verify update (assuming update adds metadata or replaces if type matches)
    assert source in cartographer.relationships
    # This assumes update replaces or merges based on source/target/type.
    # If it simply appends, this test needs adjustment.
    found = False
    for rel in cartographer.relationships[source]:
        if rel["target"] == target and rel["type"] == rel_type:
            assert rel == expected_relationship
            found = True
            break
    assert found, "Relationship not updated correctly"


@pytest.mark.asyncio
async def test_update_relationship_new(cartographer):
    """Test adding a new relationship."""
    source = "mod_c"
    target = "mod_d"
    rel_type = "calls"
    metadata = {"async": True}
    expected_relationship = {
        "source": source,
        "target": target,
        "type": rel_type,
        "metadata": metadata,
    }

    assert source not in cartographer.relationships

    # Add relationship
    await cartographer.update_relationship(source, target, rel_type, metadata)

    # Verify addition
    assert source in cartographer.relationships
    assert len(cartographer.relationships[source]) == 1
    assert cartographer.relationships[source][0] == expected_relationship


@pytest.mark.asyncio
async def test_update_relationship_multiple(cartographer):
    """Test adding multiple relationships for the same source."""
    source = "mod_e"
    target1 = "mod_f"
    target2 = "mod_g"
    rel_type1 = "uses"
    rel_type2 = "signals"

    # Add first relationship
    await cartographer.update_relationship(source, target1, rel_type1)
    # Add second relationship
    await cartographer.update_relationship(source, target2, rel_type2)

    # Verify both exist
    assert source in cartographer.relationships
    assert len(cartographer.relationships[source]) == 2
    targets = {rel["target"] for rel in cartographer.relationships[source]}
    assert target1 in targets
    assert target2 in targets


# --- Tests for Cache Functionality ---


@pytest.mark.asyncio
@patch("subsystems.ATLAS.core.cartographer.datetime")  # Patch datetime to control time
async def test_cache_hit(mock_dt, cartographer):
    """Test that a cached map result is returned within cache duration."""
    target = "cached_target"
    depth = 1
    cache_key = f"{target}:{depth}:True"
    initial_time = datetime(2024, 1, 1, 12, 0, 0)
    map_result = {"nodes": {"cached_target": {}}, "relationships": [], "metadata": {}}

    # Mock time
    mock_dt.now.return_value = initial_time

    # Prime the cache
    cartographer.analysis_cache[cache_key] = {"result": map_result, "timestamp": initial_time}

    # Mock time slightly later, but within cache duration (60s)
    mock_dt.now.return_value = initial_time.replace(second=30)

    # Spy on the actual map generation logic to ensure it's NOT called
    cartographer._build_map_recursive = AsyncMock(return_value=map_result)

    # Generate map
    result = await cartographer.generate_map(target, depth, include_metadata=True)

    # Assert result is from cache and internal method wasn't called
    assert result == map_result
    cartographer._build_map_recursive.assert_not_called()


@pytest.mark.asyncio
@patch("subsystems.ATLAS.core.cartographer.datetime")  # Patch datetime to control time
async def test_cache_miss_expired(mock_dt, cartographer):
    """Test that the cache is missed when duration expires."""
    target = "expired_target"
    depth = 1
    cache_key = f"{target}:{depth}:True"
    initial_time = datetime(2024, 1, 1, 12, 0, 0)
    cached_map_result = {"nodes": {"expired_target": {}}, "relationships": [], "metadata": {}}
    fresh_map_result = {
        "nodes": {"expired_target": {}, "new_node": {}},
        "relationships": [],
        "metadata": {},
    }

    # Mock time
    mock_dt.now.return_value = initial_time

    # Prime the cache
    cartographer.analysis_cache[cache_key] = {
        "result": cached_map_result,
        "timestamp": initial_time,
    }

    # Mock time later, outside cache duration (60s)
    mock_dt.now.return_value = initial_time.replace(minute=1, second=1)

    # Mock the actual map generation logic to ensure it IS called
    cartographer._build_map_recursive = AsyncMock(return_value=fresh_map_result)

    # Generate map
    result = await cartographer.generate_map(target, depth, include_metadata=True)

    # Assert result is the fresh one and internal method was called
    assert result == fresh_map_result
    cartographer._build_map_recursive.assert_called_once()


@pytest.mark.asyncio
async def test_cache_invalidation_on_metadata_update(cartographer):
    """Test that cache is invalidated when metadata is updated."""
    target = "invalidate_meta_target"
    depth = 1
    cache_key = f"{target}:{depth}:True"
    map_result = {"nodes": {target: {}}, "relationships": [], "metadata": {}}

    # Prime the cache
    cartographer.analysis_cache[cache_key] = {"result": map_result, "timestamp": datetime.now()}
    assert cache_key in cartographer.analysis_cache

    # Update metadata for the target component
    await cartographer.update_metadata(target, {"new_data": "value"})

    # Verify cache for that target is cleared
    assert cache_key not in cartographer.analysis_cache


@pytest.mark.asyncio
async def test_cache_invalidation_on_relationship_update(cartographer):
    """Test that cache is invalidated when relationships are updated."""
    source = "invalidate_rel_source"
    target = "invalidate_rel_target"
    depth = 2
    cache_key = f"{source}:{depth}:True"
    map_result = {"nodes": {source: {}, target: {}}, "relationships": [], "metadata": {}}

    # Prime the cache
    cartographer.analysis_cache[cache_key] = {"result": map_result, "timestamp": datetime.now()}
    assert cache_key in cartographer.analysis_cache

    # Update relationship involving the source component
    await cartographer.update_relationship(source, target, "connects")

    # Verify cache for that source is cleared
    assert cache_key not in cartographer.analysis_cache


# --- Tests for Config Loading ---


def test_config_loading_defaults(tmp_path):
    """Test that default config values are used when file is missing."""
    analyzer = AtlasCartographer(config_path=tmp_path / "nonexistent_config.json")
    # Check a few default values assumed from the mock config
    assert analyzer.config["max_depth"] > 0  # Should have a default
    assert analyzer.config["cache_duration"] > 0  # Should have a default
    assert "map_request" in analyzer.config["mycelium"]["topics"]


def test_config_loading_from_file(test_config, tmp_path):
    """Test that config values are loaded correctly from the file."""
    config_path = tmp_path / "test_config.json"
    with open(config_path, "w") as f:
        json.dump(test_config, f)

    analyzer = AtlasCartographer(config_path=config_path)

    assert analyzer.config["max_depth"] == test_config["max_depth"]
    assert analyzer.config["cache_duration"] == test_config["cache_duration"]
    assert analyzer.config["mycelium"]["topics"] == test_config["mycelium"]["topics"]


# --- Tests for Malformed Mycelium Messages (Error Handling) ---


@pytest.mark.asyncio
async def test_metadata_update_malformed(cartographer, mock_mycelium):
    """Test handling malformed metadata update message."""
    # Missing 'component' key
    await mock_mycelium.trigger_message(
        "test.atlas.metadata.update", {"metadata": {"key": "value"}}
    )
    assert len(mock_mycelium.published_messages) == 1
    error_msg = mock_mycelium.published_messages[0]
    assert error_msg["topic"] == "test.atlas.metadata.status"
    assert error_msg["data"]["status"] == "error"
    assert "Missing 'component'" in error_msg["data"]["error"]

    # Missing 'metadata' key
    mock_mycelium.published_messages.clear()
    await mock_mycelium.trigger_message("test.atlas.metadata.update", {"component": "test"})
    assert len(mock_mycelium.published_messages) == 1
    error_msg = mock_mycelium.published_messages[0]
    assert error_msg["topic"] == "test.atlas.metadata.status"
    assert error_msg["data"]["status"] == "error"
    assert "Missing 'metadata'" in error_msg["data"]["error"]


@pytest.mark.asyncio
async def test_relationship_update_malformed(cartographer, mock_mycelium):
    """Test handling malformed relationship update message."""
    # Missing 'source' key
    await mock_mycelium.trigger_message(
        "test.atlas.relationship.update", {"target": "b", "type": "calls"}
    )
    assert len(mock_mycelium.published_messages) == 1
    error_msg = mock_mycelium.published_messages[0]
    assert error_msg["topic"] == "test.atlas.relationship.status"
    assert error_msg["data"]["status"] == "error"
    assert "Missing 'source'" in error_msg["data"]["error"]

    # Missing 'target' key
    mock_mycelium.published_messages.clear()
    await mock_mycelium.trigger_message(
        "test.atlas.relationship.update", {"source": "a", "type": "calls"}
    )
    assert len(mock_mycelium.published_messages) == 1
    error_msg = mock_mycelium.published_messages[0]
    assert error_msg["topic"] == "test.atlas.relationship.status"
    assert error_msg["data"]["status"] == "error"
    assert "Missing 'target'" in error_msg["data"]["error"]

    # Missing 'type' key
    mock_mycelium.published_messages.clear()
    await mock_mycelium.trigger_message(
        "test.atlas.relationship.update", {"source": "a", "target": "b"}
    )
    assert len(mock_mycelium.published_messages) == 1
    error_msg = mock_mycelium.published_messages[0]
    assert error_msg["topic"] == "test.atlas.relationship.status"
    assert error_msg["data"]["status"] == "error"
    assert "Missing 'type'" in error_msg["data"]["error"]


# Add tests for visualization formats if generate_map supports it
# Example (assuming generate_map returns serialized format based on 'format' arg):
# @pytest.mark.asyncio
# async def test_generate_map_mermaid_format(cartographer):
#     cartographer.system_map = {"a": {}, "b": {}}
#     cartographer.relationships = {"a": [{"source": "a", "target": "b", "type": "connects"}]}
#
#     mermaid_output = await cartographer.generate_map("a", depth=2, format="mermaid")
#
#     assert isinstance(mermaid_output, str)
#     assert "graph TD" in mermaid_output
#     assert "a --> b" in mermaid_output

# --- Final Review ----
# Review coverage and add any missing edge cases.
