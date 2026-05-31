import re
from typing import Dict, List

class InputGuard:
    def __init__(self):
        self.jailbreak_patterns: List[str] = [
            # Classic overrides
            r"(?i)(ignore|disregard|forget|override).*?(previous|all|prior).*?(instructions|prompts|rules)",
            r"(?i)(new|updated|revised).*?(instructions|policy|guidelines)",
            # Persona / Roleplay
            r"(?i)(you are now|act as|roleplay as|become|pretend you are).*?(dan|developer|unrestricted|evil|grandma)",
            r"(?i)(developer mode|maintenance mode|jailbreak mode|test mode)",
            # Encoding / Obfuscation
            r"(?i)(base64|rot13|hex|encoded|decode this|translate to leetspeak)",
            r"(?i)[\[\(\{]system[\]\)\}]|[\[\(\{]assistant[\]\)\}]",
            # Hypothetical / Research framing
            r"(?i)(for research|academic|educational|fiction|hypothetical).*?(how to|steps to|guide)",
            # Policy manipulation
            r"(?i)(safety.*?(disabled|off|removed)|no (restrictions|limits|rules|ethics))",
            # Skeleton Key / Crescendo style
            r"(?i)(append.*?(warning|disclaimer)|safety.*?(acknowledged|noted))",
            # Token smuggling / Fragmentation
            r"(?i)[\*~!^<|>{}]{3,}",  # Heavy symbols
            # More from recent attacks
            r"(?i)(multi-turn|escalation|crescendo|policy puppetry)",
            # Add as many as needed...
        ]

    def analyze(self, text: str) -> Dict:
        text_lower = text.lower()
        matches = []
        
        for pattern in self.jailbreak_patterns:
            if re.search(pattern, text_lower):
                matches.append(pattern)

        risk_score = min(len(matches) * 0.2 + self._heuristic_score(text_lower), 1.0)

        return {
            "safe": risk_score < 0.5,
            "risk_score": risk_score,
            "detected_patterns": matches[:5],  # Limit for report size
            "reason": "Jailbreak patterns detected" if matches else None
        }
    
    def _heuristic_score(self, text: str) -> float:
        indicators = ["system prompt", "instructions", "bypass", "override", "secret", "password", "hack", "exploit", "vulnerability"]
        return sum(0.15 for word in indicators if word in text)