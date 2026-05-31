import concurrent.futures
from typing import Dict, Any, Tuple
from .token_manager import TokenManager
from .input_guard.jailbreak_detector import InputGuard
from .content_guard.content_safety import ContentGuard
from .output_guard.output_sanitizer import OutputGuard

class SecurityLayer:
    def __init__(self):
        self.token_manager = TokenManager()
        self.input_guard = InputGuard()
        self.content_guard = ContentGuard()
        self.output_guard = OutputGuard()

    def process(self, user_input: str) -> Tuple[bool, str, Dict]:
        """Fast parallel input validation"""
        report: Dict[str, Any] = {"stage": "start", "checks": {}}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            token_future = executor.submit(self.token_manager.check_request, user_input)
            input_future = executor.submit(self.input_guard.analyze, user_input)
            
            token_result = token_future.result()
            input_result = input_future.result()
        
        report["checks"]["token"] = token_result
        report["checks"]["input"] = input_result
        
        if not token_result["allowed"]:
            return False, token_result["reason"], report
        
        if not input_result["safe"]:
            return False, "Input blocked: Potential security violation.", report
        
        report["stage"] = "input_passed"
        return True, "Input approved for processing.", report

    def validate_output(self, llm_response: str, original_input: str) -> Tuple[bool, str, Dict]:
        """Local content + output validation"""
        report = {}
        
        content_result = self.content_guard.analyze(llm_response, original_input)
        output_result = self.output_guard.sanitize(llm_response)
        
        report["content"] = content_result
        report["output"] = output_result
        
        final_safe = content_result["safe"] and output_result["safe"]
        clean_text = output_result["sanitized_text"]
        
        
        
        return final_safe, clean_text, report