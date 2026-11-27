import json
import pytest
from pathlib import Path
from backend.app.agent.validators.a2ui_validator import A2UIValidator
from backend.app.agent.planners.ui_planner import UIPlanner
from backend.app.agent.generators.a2ui_generator import A2UIGenerator

def test_a2ui_validator_valid():
    msg = {
        "version": "1.0",
        "createSurface": {
            "surfaceId": "test-surface",
            "catalogId": "astryx-web-v1",
            "title": "Test Title",
            "components": [
                {"id": "root", "component": "Container", "children": ["t1"]},
                {"id": "t1", "component": "Heading", "props": {"level": 1, "text": "Hello World"}}
            ],
            "dataModel": {"count": 0}
        }
    }
    valid, err = A2UIValidator.validate_message(msg)
    assert valid is True
    assert err is None

def test_a2ui_validator_reject_unsupported_component():
    msg = {
        "version": "1.0",
        "createSurface": {
            "surfaceId": "test-surface",
            "catalogId": "astryx-web-v1",
            "components": [
                {"id": "malicious", "component": "UnregisteredScriptTag", "props": {}}
            ]
        }
    }
    valid, err = A2UIValidator.validate_message(msg)
    assert valid is False
    assert "not permitted by Astryx Catalog" in err

def test_a2ui_validator_reject_duplicate_ids():
    msg = {
        "version": "1.0",
        "createSurface": {
            "surfaceId": "test-surface",
            "catalogId": "astryx-web-v1",
            "components": [
                {"id": "c1", "component": "Heading"},
                {"id": "c1", "component": "Text"}
            ]
        }
    }
    valid, err = A2UIValidator.validate_message(msg)
    assert valid is False
    assert "Duplicate component id" in err

def test_ui_planner():
    # Phase 3 intent scheme: generate_new / edit_section / change_theme / chat_inquiry
    intent1 = UIPlanner.classify_intent("Tạo một website bán trà sữa", has_existing_surface=False)
    assert intent1 == "generate_new"

    intent2 = UIPlanner.classify_intent("Đổi theme sang tím", has_existing_surface=True)
    assert intent2 == "change_theme"

    intent3 = UIPlanner.classify_intent("Sửa tiêu đề hero cho sang trọng hơn", has_existing_surface=True)
    assert intent3 == "edit_section"

    intent4 = UIPlanner.classify_intent("Website này trông thế nào?", has_existing_surface=True)
    assert intent4 == "chat_inquiry"

    steps = UIPlanner.create_generation_plan("Tạo portfolio chụp ảnh tối giản")
    assert len(steps) >= 4
    assert not any("bảng giá" in step.lower() or "form liên hệ" in step.lower() for step in steps)

def test_deterministic_generator_validity():
    landing_msg = A2UIGenerator.generate_deterministic("Tạo landing page cho studio ảnh")
    valid, err = A2UIValidator.validate_message(landing_msg)
    assert valid is True, f"Validation failed: {err}"

    analytics_msg = A2UIGenerator.generate_deterministic("Tạo dashboard thống kê dữ liệu")
    valid, err = A2UIValidator.validate_message(analytics_msg)
    assert valid is True, f"Validation failed: {err}"

def test_fixture_integrity():
    fixture_dir = Path(__file__).resolve().parent.parent / "fixtures" / "a2ui"
    with open(fixture_dir / "landing_page_fixture.json", "r", encoding="utf-8") as f:
        landing_fixture = json.load(f)
    valid, err = A2UIValidator.validate_message(landing_fixture)
    assert valid is True, f"Landing fixture invalid: {err}"

    with open(fixture_dir / "data_table_fixture.json", "r", encoding="utf-8") as f:
        data_fixture = json.load(f)
    valid, err = A2UIValidator.validate_message(data_fixture)
    assert valid is True, f"Data table fixture invalid: {err}"

if __name__ == "__main__":
    test_a2ui_validator_valid()
    test_a2ui_validator_reject_unsupported_component()
    test_a2ui_validator_reject_duplicate_ids()
    test_ui_planner()
    test_deterministic_generator_validity()
    test_fixture_integrity()
    print("ALL HARNESS & VALIDATOR UNIT TESTS PASSED: 100%!")
