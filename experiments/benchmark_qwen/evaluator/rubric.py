from typing import Dict, Any, Tuple

class BenchmarkRubric:
    """
    Evaluator implementing the exact 100-point rubric requested by user:
    - Visual Design & Aesthetics: 25
    - Layout & Composition: 20
    - Typography & Color: 15
    - UX & Usability: 15
    - Responsive Design: 10
    - A2UI Validity: 10
    - Generation Cost & Latency: 5
    Total: 100
    """

    CRITERIA_WEIGHTS = {
        "visual_design": 25,
        "layout_composition": 20,
        "typography_color": 15,
        "ux_usability": 15,
        "responsive_design": 10,
        "a2ui_validity": 10,
        "cost_latency": 5,
    }

    @classmethod
    def evaluate_output(
        cls,
        a2ui_doc: Dict[str, Any],
        raw_error: str,
        latency_sec: float,
        cost_usd: float,
        prompt_category: str
    ) -> Dict[str, Any]:
        scores = {}
        notes = []

        # 1. A2UI Validity (Max 10)
        validity_score = 10
        if raw_error or not a2ui_doc:
            validity_score = 0
            notes.append(f"Validation failed: {raw_error}")
        else:
            if a2ui_doc.get("version") != "1.0":
                validity_score -= 4
                notes.append("Wrong version or missing 'version: 1.0'")
            if "createSurface" not in a2ui_doc:
                validity_score -= 6
                notes.append("Missing createSurface envelope")
        scores["a2ui_validity"] = max(0, validity_score)

        if scores["a2ui_validity"] == 0:
            # If payload is totally invalid JSON or missing, other structural scores collapse
            return {
                "scores": {k: 0 for k in cls.CRITERIA_WEIGHTS},
                "total_score": 0,
                "notes": notes,
                "latency_sec": latency_sec,
                "cost_usd": cost_usd
            }

        surface = a2ui_doc.get("createSurface", {})
        components = surface.get("components", [])
        data_model = surface.get("dataModel", {})

        # Component type extraction
        types = [c.get("component") for c in components if isinstance(c, dict)]
        type_set = set(types)

        # 2. Layout & Composition (Max 20)
        # Check presence of Container, Row/Grid hierarchy, section count
        layout_score = 20
        has_container = "Container" in type_set
        has_flow = ("Row" in type_set or "Column" in type_set or "Grid" in type_set)
        num_sections = len([c for c in components if c.get("component") in ("Container", "Grid", "Card")])

        if not has_container:
            layout_score -= 5
            notes.append("Missing standard Container wrapper")
        if not has_flow:
            layout_score -= 5
            notes.append("Missing Row/Grid flex layout")
        if num_sections < 3:
            layout_score -= 5
            notes.append(f"Too few sections ({num_sections}), shallow layout")
        scores["layout_composition"] = max(5, layout_score)

        # 3. Visual Design & Aesthetics (Max 25)
        # Evaluates card elevation, pill badges, Apple minimalist polish
        design_score = 25
        has_card = "Card" in type_set
        has_badge = "Badge" in type_set
        has_metrics = "MetricsCard" in type_set

        # Check for Apple light theme hints (zinc, white, subtle borders, rounded corners)
        classes_str = " ".join([c.get("props", {}).get("className", "") for c in components])
        has_light_theme = "zinc" in classes_str or "white" in classes_str or "neutral" in classes_str

        if not has_card and not has_metrics:
            design_score -= 5
            notes.append("Lacks elevated Cards or visual focal points")
        if not has_badge:
            design_score -= 3
            notes.append("Missing refined pill badge highlights")
        if not has_light_theme:
            design_score -= 4
            notes.append("Did not strictly apply clean Apple light palette")
        scores["visual_design"] = max(8, design_score)

        # 4. Typography & Color (Max 15)
        # Checks heading hierarchy (H1, H2, H3) and text clarity
        typo_score = 15
        headings = [c for c in components if c.get("component") == "Heading"]
        levels = {c.get("props", {}).get("level") for c in headings}

        if 1 not in levels:
            typo_score -= 4
            notes.append("Missing level 1 hero heading")
        if 2 not in levels and 3 not in levels:
            typo_score -= 3
            notes.append("Lacks secondary heading hierarchy")
        if "Text" not in type_set:
            typo_score -= 3
            notes.append("Missing descriptive Text elements")
        scores["typography_color"] = max(5, typo_score)

        # 5. UX & Usability (Max 15)
        # Checks actionable CTA buttons, forms/inputs, interactive DataTable
        ux_score = 15
        has_button = "Button" in type_set
        has_interactive = ("Input" in type_set or "DataTable" in type_set or has_button)

        if not has_button:
            ux_score -= 6
            notes.append("No call-to-action Button found")
        if not has_interactive:
            ux_score -= 5
            notes.append("No interactive inputs or data components")
        scores["ux_usability"] = max(4, ux_score)

        # 6. Responsive Design (Max 10)
        resp_score = 10
        if "Grid" not in type_set and "Row" not in type_set:
            resp_score -= 4
            notes.append("No responsive grid or flexible row")
        if "md:" not in classes_str and "cols" not in str(components):
            resp_score -= 2
            notes.append("Few explicit responsive breakpoint rules")
        scores["responsive_design"] = max(4, resp_score)

        # 7. Generation Cost & Latency (Max 5)
        # Latency under 4s is full points; cost under $0.005 is full points
        cost_latency_score = 5
        if latency_sec > 8.0:
            cost_latency_score -= 2
        elif latency_sec > 5.0:
            cost_latency_score -= 1

        if cost_usd > 0.03:
            cost_latency_score -= 2
        elif cost_usd > 0.01:
            cost_latency_score -= 1
        scores["cost_latency"] = max(1, cost_latency_score)

        total = sum(scores.values())

        return {
            "scores": scores,
            "total_score": total,
            "notes": notes,
            "latency_sec": round(latency_sec, 2),
            "cost_usd": round(cost_usd, 6),
            "component_count": len(components),
            "component_types": list(type_set)
        }
