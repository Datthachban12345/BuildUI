import asyncio
from backend.app.main import app, health_check
from backend.app.models.a2ui import (
    CreateSurfaceMessage,
    UpdateComponentsMessage,
    UpdateDataModelMessage,
    ComponentNode
)

def test_health_check():
    res = asyncio.run(health_check())
    assert res["status"] == "healthy"
    assert res["protocol"] == "A2UI v1.0"
    assert res["service"] == "a2ui-agent-harness"

def test_a2ui_model_validation():
    create_msg = CreateSurfaceMessage(
        surfaceId="test-surface",
        title="Test UI"
    )
    assert create_msg.type == "createSurface"
    assert create_msg.version == "1.0"

    comp = ComponentNode(
        id="btn-1",
        type="Button",
        props={"label": "Click Me", "variant": "primary"}
    )
    update_msg = UpdateComponentsMessage(
        surfaceId="test-surface",
        components=[comp]
    )
    assert update_msg.type == "updateComponents"
    assert len(update_msg.components) == 1
    assert update_msg.components[0].props["label"] == "Click Me"

    data_msg = UpdateDataModelMessage(
        surfaceId="test-surface",
        operation="merge",
        path="records",
        value=[{"id": 1, "name": "Item 1"}]
    )
    assert data_msg.type == "updateDataModel"
    assert data_msg.operation == "merge"
