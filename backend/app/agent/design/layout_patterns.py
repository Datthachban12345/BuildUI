"""Advisory layout knowledge, deliberately not renderable page templates.

Patterns describe goals and compositional options. They never prescribe a
section tree, so the model remains free to invent an appropriate layout.
"""
from dataclasses import dataclass
import re
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class LayoutPrior:
    name: str
    signals: Tuple[str, ...]
    goals: Tuple[str, ...]
    primitives: Tuple[str, ...]
    compositions: Tuple[str, ...]
    avoid: Tuple[str, ...]
    threshold: int = 2


PATTERNS: Tuple[LayoutPrior, ...] = (
    LayoutPrior("commerce", ("shop", "store", "cửa hàng", "bán", "sản phẩm", "giỏ hàng", "product", "ecommerce"),
        ("help people discover and compare offerings", "make value and purchase action visible"),
        ("Image", "Card", "Grid", "Badge", "Button"),
        ("editorial hero with one featured offering", "category-led discovery", "catalog grid with a contrasting feature"),
        ("empty product cards", "prices hidden only in dataModel", "identical cards without hierarchy")),
    LayoutPrior("portfolio", ("portfolio", "nhiếp ảnh", "photography", "studio", "designer", "creative", "nghệ sĩ"),
        ("lead with a memorable point of view", "show selected work without visual noise"),
        ("Image", "Heading", "Text", "Grid", "Card", "Button"),
        ("editorial split hero", "asymmetric work showcase", "case-study-led narrative"),
        ("generic feature-card grid", "invented testimonials or credentials")),
    LayoutPrior("studio-booking", ("đặt lịch", "booking", "studio ảnh", "salon", "dịch vụ", "appointment"),
        ("explain the experience before asking for details", "make the booking action easy"),
        ("Image", "Card", "Input", "Button", "Grid"),
        ("service-led landing page", "visual hero plus compact booking panel", "availability-first flow"),
        ("burying the form", "large pricing table when a short service list is enough")),
    LayoutPrior("saas", ("saas", "phần mềm", "ứng dụng", "platform", "subscription", "dashboard"),
        ("communicate product value quickly", "differentiate capabilities by user outcome"),
        ("Heading", "Text", "Card", "Grid", "MetricsCard", "Button"),
        ("product-led hero", "outcome-driven feature sections", "metrics plus workflow proof"),
        ("three vague benefits", "dashboard chrome without a real user task")),
    LayoutPrior("restaurant", ("nhà hàng", "restaurant", "café", "cafe", "menu", "thực đơn", "đặt bàn"),
        ("create appetite and atmosphere", "surface menu and reservation actions"),
        ("Image", "Card", "Grid", "Badge", "Button", "Input"),
        ("atmospheric hero", "menu-led editorial layout", "location and reservation split"),
        ("generic SaaS pricing", "dense data table for a short menu")),
    LayoutPrior("dashboard", ("dashboard", "analytics", "thống kê", "bảng điều khiển", "báo cáo"),
        ("prioritize scanning and task completion", "make important changes and next actions legible"),
        ("MetricsCard", "DataTable", "Card", "Grid", "Input", "Button"),
        ("summary metrics then detail", "task-focused workspace", "table with contextual actions"),
        ("marketing hero", "decorative cards without actionable data")),
)

GENERIC_PRIOR = LayoutPrior("creative", (),
    ("infer the audience and primary task from the brief", "create a distinct visual point of view"),
    ("Container", "Row", "Column", "Grid", "Heading", "Text", "Image", "Card", "Button"),
    ("invent a section sequence appropriate to the brief", "alternate density and alignment to create rhythm", "use a visual focal point when it clarifies the subject"),
    ("filler sections", "repeated cards", "forcing an irrelevant pattern"), threshold=0)


def select_pattern(prompt: str) -> Tuple[LayoutPrior, int]:
    text = prompt.lower()
    scores = [(sum(1 for signal in pattern.signals if signal in text), pattern) for pattern in PATTERNS]
    score, best = max(scores, key=lambda item: item[0], default=(0, GENERIC_PRIOR))
    if score < best.threshold:
        return GENERIC_PRIOR, score
    return best, score


def build_design_prior(prompt: str) -> str:
    pattern, score = select_pattern(prompt)
    return (
        f"Advisory design prior: {pattern.name} (signal confidence {score}).\n"
        "This is knowledge, NOT a fixed template. Do not copy a section tree or force its order. "
        "Invent a new composition when the brief benefits from it; retain only the goals, catalog limits, "
        "and anti-patterns.\n"
        f"Goals: {'; '.join(pattern.goals)}.\n"
        f"Useful catalog primitives: {', '.join(pattern.primitives)}.\n"
        f"Possible composition directions (choose, combine, or replace): {'; '.join(pattern.compositions)}.\n"
        f"Avoid: {'; '.join(pattern.avoid)}."
    )
