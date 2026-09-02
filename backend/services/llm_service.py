import json
import logging
import os
import re

from groq import Groq

from models.schemas import Explanation

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a clinical laboratory explanation assistant.

Your job is to explain laboratory test results in clear, cautious, clinically relevant language.

IMPORTANT RULES:
1. Do not diagnose a disease.
2. Do not prescribe medication.
3. Do not recommend medication dosage.
4. Do not invent patient history.
5. Do not invent symptoms.
6. Do not invent reference ranges.
7. Do not change the provided severity.
8. The severity was determined deterministically before you received this request.
9. Explain why the result received this severity.
10. Use cautious language such as "may be associated with" or "can be seen with".
11. Explain what the test generally measures.
12. Suggest a reasonable next step.
13. Include an informational disclaimer.
14. Return ONLY valid JSON with keys: summary, why_flagged, clinical_significance, next_step, disclaimer."""

FALLBACK_EXPLANATION = Explanation(
    summary="AI explanation is temporarily unavailable.",
    why_flagged="The result was classified using the configured reference range.",
    clinical_significance=(
        "Please review the laboratory value and reference range with a qualified healthcare professional."
    ),
    next_step="Clinical review is recommended based on the severity of the result.",
    disclaimer="AI explanation unavailable. This application does not provide a diagnosis.",
)


class LLMService:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        self.client = Groq(api_key=api_key) if api_key else None

    def _build_user_prompt(
        self,
        test_name: str,
        value: float,
        unit: str,
        reference_range: str,
        severity: str,
        classification_reason: str,
    ) -> str:
        return f"""Test name: {test_name}
Value: {value}
Unit: {unit}
Reference range: {reference_range}
Deterministic severity: {severity}
Classification reason: {classification_reason}

Return JSON with:
{{
  "summary": "...",
  "why_flagged": "...",
  "clinical_significance": "...",
  "next_step": "...",
  "disclaimer": "..."
}}"""

    def _parse_response(self, content: str) -> Explanation | None:
        try:
            text = content.strip()
            json_match = re.search(r"\{[\s\S]*\}", text)
            if json_match:
                data = json.loads(json_match.group())
                return Explanation(**data)
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning("Failed to parse LLM response: %s", e)
        return None

    def generate_explanation(
        self,
        test_name: str,
        value: float,
        unit: str,
        reference_range: str,
        severity: str,
        classification_reason: str,
    ) -> Explanation:
        if not self.client:
            logger.warning("Groq client not configured - using fallback explanation")
            return FALLBACK_EXPLANATION

        user_prompt = self._build_user_prompt(
            test_name, value, unit, reference_range, severity, classification_reason
        )

        for attempt in range(2):
            try:
                logger.info("LLM request for %s (attempt %d)", test_name, attempt + 1)
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.3,
                    max_tokens=1024,
                )
                content = response.choices[0].message.content or ""
                parsed = self._parse_response(content)
                if parsed:
                    logger.info("LLM explanation generated for %s", test_name)
                    return parsed
                logger.warning("Malformed LLM response for %s on attempt %d", test_name, attempt + 1)
            except Exception as e:
                logger.error("LLM request failed for %s: %s", test_name, e)
                break

        logger.warning("LLM failure for %s - using fallback", test_name)
        return FALLBACK_EXPLANATION


llm_service = LLMService()
