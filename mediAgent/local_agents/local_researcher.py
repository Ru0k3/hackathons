"""
Local Researcher Agent - non-LLM fallback for offline or testing
This agent searches local example JSON files and returns basic extracted content.
"""
import json
import os
from typing import List, Dict, Callable


class LocalResearcherAgent:
    def __init__(self, examples_dir: str = None, status_callback: Callable[[str], None] = None):
        self.examples_dir = examples_dir or os.path.join(os.path.dirname(__file__), "..", "examples")
        self.status_callback = status_callback

        try:
            from local_agents.rag_retriever import SimpleRAG
        except Exception:
            try:
                from rag_retriever import SimpleRAG
            except Exception:
                SimpleRAG = None

    def _log(self, msg: str):
        if self.status_callback:
            self.status_callback(msg)

    def search_web(self, query: str, status_callback: Callable[[str], None] = None) -> List[Dict]:
        # Simple local search: return any example files that contain any query token in their content
        self._log(f"(local) Searching local examples for: {query}")
        results = []
        examples_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "examples"))
        if not os.path.isdir(examples_dir):
            self._log(f"(local) examples dir not found: {examples_dir}")
            return results

        # If RAG retriever available, use it for better relevance; otherwise fallback to token search
        try:
            from local_agents.rag_retriever import SimpleRAG as _R
        except Exception:
            _R = None

        if _R:
            try:
                retriever = _R(examples_dir)
                top = retriever.retrieve(query, top_k=5)
                for d in top:
                    results.append({'title': d.get('title'), 'url': d.get('url'), 'content': d.get('content')})
                self._log(f"(local) RAG found {len(results)} sources")
                return results
            except Exception as e:
                self._log(f"(local) RAG retrieval failed: {e}")

        tokens = [t.lower() for t in query.split() if t]
        for fname in os.listdir(examples_dir):
            if not fname.lower().endswith('.json'):
                continue
            path = os.path.join(examples_dir, fname)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                text = json.dumps(data).lower()
                if any(tok in text for tok in tokens):
                    results.append({
                        'title': data.get('title', fname),
                        'url': f'file://{path}',
                        'content': data.get('content', json.dumps(data))
                    })
            except Exception as e:
                self._log(f"(local) failed to read {fname}: {e}")

        self._log(f"(local) Found {len(results)} local sources")
        return results

    def analyze_sources(self, sources: List[Dict], topic: str, status_callback: Callable[[str], None] = None) -> str:
        self._log(f"(local) Analyzing {len(sources)} sources for topic: {topic}")
        summaries = []
        for idx, s in enumerate(sources, 1):
            content = s.get('content', '')
            preview = content[:1000]
            summaries.append(f"Source {idx}: {s.get('title', 'N/A')}\nPreview:\n{preview}\n")

        analysis = f"Local analysis for '{topic}'\n\n" + "\n---\n".join(summaries)
        return analysis

    def research(self, topic: str, status_callback: Callable[[str], None] = None) -> Dict:
        self._log(f"(local) Starting research on: {topic}")
        sources = self.search_web(topic, status_callback)
        if not sources:
            return {'topic': topic, 'sources': [], 'analysis': 'No local sources found.', 'success': False}

        analysis = self.analyze_sources(sources, topic, status_callback)
        return {'topic': topic, 'sources': sources, 'analysis': analysis, 'success': True}
