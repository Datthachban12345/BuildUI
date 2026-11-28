"""Small injectable memory of validated design lessons.

The store keeps summaries, not whole surfaces, so retrieval inspires rather
than clones previous output. A process-local default avoids introducing a new
persistence dependency before the agent contract is stable.
"""
from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class DesignMemory:
    domain: str
    composition: str
    strengths: str
    score: float


class DesignMemoryStore:
    def __init__(self, limit: int = 32) -> None:
        self.limit = limit
        self._items: List[DesignMemory] = []

    def add(self, item: DesignMemory) -> None:
        if item.score < 7.0:
            return
        self._items = [existing for existing in self._items
                       if not (existing.domain == item.domain and existing.composition == item.composition)]
        self._items.insert(0, item)
        del self._items[self.limit:]

    def retrieve(self, domain: str, limit: int = 2) -> List[DesignMemory]:
        domain = domain.lower()
        ranked = sorted(self._items, key=lambda item: (domain in item.domain.lower(), item.score), reverse=True)
        return ranked[:limit]

    def inspiration(self, domain: str, limit: int = 2) -> str:
        items = self.retrieve(domain, limit)
        if not items:
            return "No prior design reference is available; compose from first principles."
        return "\n".join(
            f"Prior lesson (adapt, do not copy): {item.composition}; strengths: {item.strengths}."
            for item in items
        )


DEFAULT_DESIGN_MEMORY = DesignMemoryStore()
