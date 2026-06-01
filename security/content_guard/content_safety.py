from detoxify import Detoxify
from typing import Dict
import re

class ContentGuard:
    def __init__(self):
        self.toxicity_threshold = 0.5 
        self.hallucination_threshold = 0.5
        self.model = Detoxify('original')  
    
    def analyze(self, text: str, original_query: str = "") -> Dict:
        try:
            results = self.model.predict(text)
            
            max_score = max(results.values())
            toxicity_score = float(max_score)
            
            hallucination_risk = self._hallucination_risk(text, original_query)

            safe = (toxicity_score < self.toxicity_threshold and 
                   hallucination_risk < self.hallucination_threshold)
            
            return {
                "safe": safe,
                "toxicity_score": round(toxicity_score, 3),
                "hallucination_risk": round(hallucination_risk, 3),
                "category_scores": {k: round(float(v), 3) for k, v in results.items()},
                "recommendation": "Content appears harmful" if not safe else "Content passed local checks"
            }
        except Exception as e:
            return {"safe": False, "error": str(e)}

    def _hallucination_risk(self, response: str, query: str) -> float:
        if not query:
            return 0.5
        query_words = set(re.findall(r'\b\w+\b', query.lower()))
        resp_words = set(re.findall(r'\b\w+\b', response.lower()))
        if not query_words:
            return 0.5
        overlap = len(query_words.intersection(resp_words)) / len(query_words)
        return 1.0 - overlap  