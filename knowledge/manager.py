"""
knowledge/manager.py
====================
Knowledge query manager — replaces the missing knowledge_base.knowledge_manager.
"""
from __future__ import annotations
from typing import List, Dict, Any, Optional
from knowledge.classical_texts import search_knowledge, ALL_KNOWLEDGE


class KnowledgeManager:
    def search(self, keyword: str, category: Optional[str] = None) -> List[Dict]:
        return search_knowledge(keyword, category)

    def get_categories(self) -> List[str]:
        return list(ALL_KNOWLEDGE.keys())

    def smart_search(self, query: str) -> Dict[str, Any]:
        """Search across all categories and return structured result."""
        results = search_knowledge(query)
        return {
            "query":   query,
            "results": results[:10],
            "total":   len(results),
        }


knowledge_manager = KnowledgeManager()
