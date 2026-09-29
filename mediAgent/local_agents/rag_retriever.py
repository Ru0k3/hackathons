"""
Simple local RAG retriever: builds a small bag-of-words index from example JSON files
and retrieves top-k documents by cosine similarity to the query.
No heavy dependencies required.
"""
import os
import json
import math
from typing import List, Dict


def _tokenize(text: str):
    if not text:
        return []
    # lowercase and split on non-alphanumeric
    import re
    tokens = re.findall(r"\w+", text.lower())
    return tokens


class SimpleRAG:
    def __init__(self, examples_dir: str = None):
        self.examples_dir = examples_dir or os.path.join(os.path.dirname(__file__), "..", "examples")
        self.docs = []  # list of dicts with keys: id, title, url, content, tf
        self.vocab = set()
        self._build_index()

    def _build_index(self):
        examples_dir = os.path.abspath(self.examples_dir)
        if not os.path.isdir(examples_dir):
            return
        for fname in os.listdir(examples_dir):
            if not fname.lower().endswith('.json'):
                continue
            path = os.path.join(examples_dir, fname)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                content = data.get('content', json.dumps(data))
                tokens = _tokenize(content)
                tf = {}
                for t in tokens:
                    tf[t] = tf.get(t, 0) + 1
                for t in tf:
                    self.vocab.add(t)
                self.docs.append({
                    'id': fname,
                    'title': data.get('title', fname),
                    'url': f'file://{path}',
                    'content': content,
                    'tf': tf,
                })
            except Exception:
                continue

    def _vec(self, tf: Dict[str, int]):
        # return a dict of normalized tf values
        norm = math.sqrt(sum(v * v for v in tf.values()))
        if norm == 0:
            return {}
        return {k: v / norm for k, v in tf.items()}

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict]:
        qtokens = _tokenize(query)
        qtf = {}
        for t in qtokens:
            qtf[t] = qtf.get(t, 0) + 1
        qvec = self._vec(qtf)
        if not qvec:
            return []

        scores = []
        for d in self.docs:
            dvec = self._vec(d.get('tf', {}))
            # cosine similarity
            score = 0.0
            for t, qv in qvec.items():
                score += qv * dvec.get(t, 0.0)
            scores.append((score, d))

        scores.sort(key=lambda x: x[0], reverse=True)
        top = [d for s, d in scores[:top_k] if s > 0]
        return top
