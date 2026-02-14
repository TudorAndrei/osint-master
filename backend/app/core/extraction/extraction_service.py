"""LLM extraction service powered by LangExtract."""

from typing import cast

import langextract as lx
import logfire

from app.config import settings
from app.core.cleaning_service import CleaningService

ALLOWED_EXTRACTION_CLASSES = {
    "Person",
    "Company",
    "Organization",
    "Security",
    "Email",
    "Ownership",
    "Directorship",
    "Employment",
    "Associate",
    "Family",
    "Membership",
    "Representation",
    "Payment",
    "UnknownLink",
}


class ExtractionService:
    """Run LangExtract and map outputs into FTM entities."""

    def __init__(self) -> None:
        if not settings.gemini_api_key:
            msg = "GEMINI_API_KEY is required for extraction"
            raise RuntimeError(msg)
        self.cleaning_service = CleaningService()

    @logfire.instrument("extract entities from document", extract_args=False)
    def extract_entities(self, text: str, document_type: str) -> list[dict]:  # noqa: C901
        prompt = self._prompt_for(document_type)
        examples = self._examples()

        result = lx.extract(
            text_or_documents=text,
            prompt_description=prompt,
            examples=examples,
            model_id=settings.extract_model_id,
            api_key=settings.gemini_api_key,
        )

        entities: list[dict] = []
        for extraction in getattr(result, "extractions", []):
            extraction_class = str(getattr(extraction, "extraction_class", "")).strip()
            extraction_text = str(getattr(extraction, "extraction_text", "")).strip()
            attributes = getattr(extraction, "attributes", {}) or {}
            char_interval = getattr(extraction, "char_interval", None)
            confidence = getattr(extraction, "confidence", None)

            if extraction_class not in ALLOWED_EXTRACTION_CLASSES:
                continue
            schema = extraction_class

            properties: dict[str, list[str]] = {}
            for key, value in attributes.items():
                if value is None:
                    continue
                if isinstance(value, list):
                    properties[key] = [str(item) for item in value]
                else:
                    properties[key] = [str(value)]

            if confidence is not None:
                properties["confidence"] = [str(confidence)]

            if char_interval is not None:
                start = getattr(char_interval, "start_pos", None)
                end = getattr(char_interval, "end_pos", None)
                if start is not None:
                    properties["charStart"] = [str(start)]
                if end is not None:
                    properties["charEnd"] = [str(end)]

            if extraction_text and "name" not in properties:
                properties["name"] = [extraction_text]

            if properties:
                cleaned_properties = self.cleaning_service.clean_properties(
                    cast("dict[str, object]", properties)
                )
                entities.append(
                    {
                        "schema": schema,
                        "properties": cleaned_properties,
                    }
                )

        return entities

    @staticmethod
    def _prompt_for(document_type: str) -> str:
        base = (
            "Extract entities from text in order of appearance. "
            "Output Person, Company, Organization, Security, Email, Ownership, "
            "Directorship, Employment, Associate, Family, Membership, Representation, "
            "Payment, and UnknownLink entities. "
            "Use exact text spans when possible. "
            "For relation entities, extract FTM-compliant attributes when explicit: "
            "startDate/endDate/date, role/status, summary/description, sourceUrl, percentage, "
            "amount/currency, and relationship details. "
            "Use relationship endpoints: Ownership(owner, asset), "
            "Directorship(director, organization), Employment(employee, employer), "
            "Associate(person, associate), Family(person, relative), "
            "Membership(member, organization), Representation(agent, client), "
            "Payment(payer, beneficiary), "
            "UnknownLink(subject, object). "
            "When multiple mentions describe one relationship, "
            "attach relationGroup with the same value."
        )
        if document_type == "sec_filing":
            return (
                f"{base} Prioritize issuers, executives, directors, securities, and subsidiaries "
                "mentioned in SEC filing sections."
            )
        if document_type == "email":
            return (
                f"{base} Prioritize sender/recipient people and organizations found in headers "
                "and message body."
            )
        return base

    @staticmethod
    def _examples() -> list[object]:
        return [
            lx.data.ExampleData(
                text=(
                    "John Doe, CEO of Acme Corp (ticker: ACME), sent an email to jane@contoso.com."
                ),
                extractions=[
                    lx.data.Extraction(
                        extraction_class="Person",
                        extraction_text="John Doe",
                        attributes={"position": "CEO"},
                    ),
                    lx.data.Extraction(
                        extraction_class="Company",
                        extraction_text="Acme Corp",
                        attributes={"ticker": "ACME"},
                    ),
                    lx.data.Extraction(
                        extraction_class="Email",
                        extraction_text="jane@contoso.com",
                        attributes={"email": "jane@contoso.com"},
                    ),
                    lx.data.Extraction(
                        extraction_class="Employment",
                        extraction_text="John Doe, CEO of Acme Corp",
                        attributes={
                            "employee": "John Doe",
                            "employer": "Acme Corp",
                            "role": "CEO",
                        },
                    ),
                ],
            ),
            lx.data.ExampleData(
                text=(
                    "The Bezos Family Trust owns 9.8% of Amazon.com as of 2023-12-31, "
                    "with Jeffrey P. Bezos acting as trustee."
                ),
                extractions=[
                    lx.data.Extraction(
                        extraction_class="Organization",
                        extraction_text="Bezos Family Trust",
                        attributes={"relationGroup": "ownership_1"},
                    ),
                    lx.data.Extraction(
                        extraction_class="Company",
                        extraction_text="Amazon.com",
                        attributes={"relationGroup": "ownership_1"},
                    ),
                    lx.data.Extraction(
                        extraction_class="Ownership",
                        extraction_text="owns 9.8% of Amazon.com",
                        attributes={
                            "owner": "Bezos Family Trust",
                            "asset": "Amazon.com",
                            "percentage": "9.8%",
                            "date": "2023-12-31",
                            "relationGroup": "ownership_1",
                        },
                    ),
                    lx.data.Extraction(
                        extraction_class="Representation",
                        extraction_text="Jeffrey P. Bezos acting as trustee",
                        attributes={
                            "agent": "Jeffrey P. Bezos",
                            "client": "Bezos Family Trust",
                            "role": "trustee",
                            "relationGroup": "ownership_1",
                        },
                    ),
                ],
            ),
        ]
