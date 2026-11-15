from backend.app.models.a2ui import (
    CreateSurfaceMessage,
    UpdateComponentsMessage,
    UpdateDataModelMessage,
    ComponentNode
)

def run():
    create_msg = CreateSurfaceMessage(surfaceId="test-surface", title="Test UI")
    assert create_msg.type == "createSurface"
    assert create_msg.version == "1.0"

    comp = ComponentNode(id="btn-1", type="Button", props={"label": "Click Me", "variant": "primary"})
    update_msg = UpdateComponentsMessage(surfaceId="test-surface", components=[comp])
    assert update_msg.type == "updateComponents"
    assert len(update_msg.components) == 1

    data_msg = UpdateDataModelMessage(surfaceId="test-surface", operation="merge", path="records", value=[{"id": 1}])
    assert data_msg.type == "updateDataModel"
    print("Backend tests passed successfully: 100%")

if __name__ == "__main__":
    run()
