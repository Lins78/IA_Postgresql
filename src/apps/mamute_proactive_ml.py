"""
Modelo simples de aprendizado de máquina para o Mamute Proativo.
Esse módulo aprende correlações entre solicitações de usuário e ações de melhoria
para ajustar a confiança e sugerir ações mais relevantes.
"""

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

DEFAULT_MODEL_FILE = ".mamute_ml_state.json"


def _tokenize(text: str) -> List[str]:
    if not text:
        return []
    return re.findall(r"\b[\w]+\b", text.lower())


class MamuteProactiveML:
    """Modelo leve de recomendação/treinamento para IA proativa."""

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = Path(model_path) if model_path else Path(__file__).resolve().parents[2] / DEFAULT_MODEL_FILE
        self.action_token_counts: Dict[str, Dict[str, int]] = defaultdict(dict)
        self.action_totals: Dict[str, int] = {}
        self._load_state()

    def _load_state(self) -> None:
        if not self.model_path.exists():
            return

        try:
            content = self.model_path.read_text(encoding="utf-8")
            data = json.loads(content)
            self.action_token_counts = {
                action: {token: int(count) for token, count in tokens.items()}
                for action, tokens in data.get("action_token_counts", {}).items()
            }
            self.action_totals = {action: int(total) for action, total in data.get("action_totals", {}).items()}
        except Exception:
            self.action_token_counts = defaultdict(dict)
            self.action_totals = {}

    def _save_state(self) -> None:
        try:
            self.model_path.write_text(
                json.dumps({
                    "action_token_counts": self.action_token_counts,
                    "action_totals": self.action_totals,
                }, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        except Exception:
            pass

    def _action_score(self, action: str, tokens: List[str]) -> float:
        token_counts = self.action_token_counts.get(action, {})
        total = self.action_totals.get(action, 0)
        if total <= 0 or not token_counts:
            return 0.0

        score = 0.0
        for token in tokens:
            score += token_counts.get(token, 0)

        normalized = score / float(total)
        return min(1.0, max(0.0, normalized))

    def predict_scores(self, user_input: str, candidate_actions: List[str]) -> Dict[str, float]:
        """Retorna pontuações previstas para ações conhecidas."""
        tokens = _tokenize(user_input)
        return {
            action: self._action_score(action, tokens)
            for action in candidate_actions
        }

    def recommend_actions(
        self,
        user_input: str,
        top_n: int = 3,
        threshold: float = 0.2,
        candidate_actions: Optional[List[str]] = None,
    ) -> List[Tuple[str, float]]:
        """Recomenda ações com base nos dados aprendidos."""
        candidate_actions = candidate_actions or list(self.action_totals.keys())
        scores = self.predict_scores(user_input, candidate_actions)
        sorted_actions = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        return [(action, score) for action, score in sorted_actions if score >= threshold][:top_n]

    def train(self, user_input: str, action: str, success: bool = True) -> None:
        """Treina o modelo com um exemplo de melhoria aplicada."""
        if not user_input or not action:
            return

        tokens = _tokenize(user_input)
        if not tokens:
            return

        action_counts = self.action_token_counts.setdefault(action, {})
        for token in tokens:
            action_counts[token] = action_counts.get(token, 0) + 1

        self.action_totals[action] = self.action_totals.get(action, 0) + len(tokens)
        self._save_state()

    def get_known_actions(self) -> List[str]:
        return list(self.action_totals.keys())
