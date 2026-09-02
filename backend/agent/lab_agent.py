import logging

from mcp.client import mcp_client
from models.schemas import (
    AnalysisResult,
    AnalyzeLabsResponse,
    Explanation,
    LabResult,
    ReferenceRange,
    SummaryCounts,
)
from services.llm_service import llm_service

logger = logging.getLogger(__name__)

SEVERITY_ORDER = {"CRITICAL": 0, "WARNING": 1, "NORMAL": 2, "UNKNOWN": 3}


class LabAgent:
    """Laboratory analysis agent: CLASSIFY → ROUTE → EXPLAIN."""

    async def analyze(self, labs: list[LabResult]) -> AnalyzeLabsResponse:
        logger.info("Agent: analyzing %d lab results", len(labs))
        classified = await self._classify_all(labs)
        routed = self._route(classified)
        explained = self._explain_all(routed)
        summary = self._build_summary(explained)
        return AnalyzeLabsResponse(
            success=True,
            total_results=len(explained),
            summary=summary,
            results=explained,
        )

    async def _classify_all(self, labs: list[LabResult]) -> list[dict]:
        results = []
        for lab in labs:
            result = await self._classify_one(lab)
            results.append(result)
        return results

    async def _classify_one(self, lab: LabResult) -> dict:
        validation = await mcp_client.validate_lab_result(
            lab.test_name, lab.value, lab.unit
        )

        if not validation.get("valid"):
            raise ValueError(validation.get("message", "Invalid lab result"))

        ref = await mcp_client.reference_range_lookup(lab.test_name, lab.unit, lab.value)

        if not ref.get("found"):
            if ref.get("unit_mismatch"):
                raise ValueError(ref.get("message", "Unit mismatch"))
            return {
                "test_name": lab.test_name,
                "value": lab.value,
                "unit": lab.unit,
                "reference_range": None,
                "severity": "UNKNOWN",
                "classification_reason": "No configured reference range was found for this test.",
            }

        classify_value = ref.get("converted_value", lab.value)

        classification = await mcp_client.classify_lab_result(
            lab.test_name,
            classify_value,
            ref["unit"],
            ref["low"],
            ref["high"],
            ref.get("critical_low"),
            ref.get("critical_high"),
        )

        reference_range = ReferenceRange(
            low=ref["low"],
            high=ref["high"],
            unit=ref["unit"],
            source=ref["source"],
        )

        display_value = lab.value
        display_unit = lab.unit
        if ref.get("converted_value") is not None and ref["converted_value"] != lab.value:
            display_value = ref["converted_value"]
            display_unit = ref["unit"]

        return {
            "test_name": lab.test_name,
            "value": display_value,
            "unit": display_unit,
            "reference_range": reference_range,
            "severity": classification["classification"],
            "classification_reason": classification["reason"],
        }

    def _route(self, results: list[dict]) -> list[dict]:
        indexed = list(enumerate(results))
        indexed.sort(key=lambda x: (SEVERITY_ORDER.get(x[1]["severity"], 99), x[0]))
        return [r for _, r in indexed]

    def _explain_all(self, results: list[dict]) -> list[AnalysisResult]:
        explained = []
        for r in results:
            ref_str = "Reference range unavailable"
            if r["reference_range"]:
                ref = r["reference_range"]
                ref_str = f"{ref.low} - {ref.high} {ref.unit}"

            explanation = llm_service.generate_explanation(
                r["test_name"],
                r["value"],
                r["unit"],
                ref_str,
                r["severity"],
                r["classification_reason"],
            )

            explained.append(
                AnalysisResult(
                    test_name=r["test_name"],
                    value=r["value"],
                    unit=r["unit"],
                    reference_range=r["reference_range"],
                    severity=r["severity"],
                    classification_reason=r["classification_reason"],
                    explanation=explanation,
                )
            )
        return explained

    def _build_summary(self, results: list[AnalysisResult]) -> SummaryCounts:
        counts = SummaryCounts()
        for r in results:
            sev = r.severity.upper()
            if sev == "CRITICAL":
                counts.critical += 1
            elif sev == "WARNING":
                counts.warning += 1
            elif sev == "NORMAL":
                counts.normal += 1
            else:
                counts.unknown += 1
        return counts


lab_agent = LabAgent()
