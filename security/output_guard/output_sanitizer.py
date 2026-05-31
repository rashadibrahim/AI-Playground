from presidio_analyzer import AnalyzerEngine 
from presidio_anonymizer import AnonymizerEngine
from typing import Dict

class OutputGuard:
    def __init__(self):
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()
        self._replacement = "[REDACTED]"
    
    def sanitize(self, text: str) -> Dict:
        analyzer_results = self.analyzer.analyze(
            text=text,
            language="en",
            entities=[
                "PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "CREDIT_CARD",
                "IP_ADDRESS", "SSN", "LOCATION", "DATE_TIME", "URL"
            ]
        )
        print(f"Detected entities: {[r.entity_type for r in analyzer_results]} with confidence scores: {[r.score for r in analyzer_results]}")
        
        # Redact
        anonymized = self.anonymizer.anonymize(
            text=text,
            analyzer_results=analyzer_results,
            operators={"DEFAULT": {"type": "replace", 
                                  "new_value": self._replacement}}
        )
        
        return {
            "safe": True,
            "sanitized_text": anonymized.text,
            "redactions_count": len(analyzer_results),
            "entities_found": [r.entity_type for r in analyzer_results]
        }
        
        
        
