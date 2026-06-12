import os
import logging
from typing import Optional
from dotenv import load_dotenv

from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types

logger = logging.getLogger(__name__)
load_dotenv()


AIRS_ENABLED = os.getenv("AIRS_ENABLED", "true").lower() == "true"


if AIRS_ENABLED:
    try:
        import aisecurity
        from aisecurity.scan.inline.scanner import Scanner
        from aisecurity.scan.models.content import Content
        from aisecurity.generated_openapi_client.models.ai_profile import AiProfile
        from aisecurity.generated_openapi_client.models.metadata import Metadata


        aisecurity.init(
            api_key=os.getenv("PANW_AI_SEC_API_KEY"),
            api_endpoint=os.getenv("AIRS_API_ENDPOINT")
            )
            
        _scanner   = Scanner()
        _ai_profile = AiProfile(
            profile_name=os.getenv("AIRS_PROFILE_NAME", "Default")
        )
        logger.info("AIRS enabled — scanner initialised")
    except Exception as e:
        logger.error(f"AIRS init failed: {e}. Defaulting to fail-closed.")
        AIRS_ENABLED = False


def _extract_prompt(llm_request: LlmRequest) -> str:
    for content in reversed(llm_request.contents or []):
        if content.role == "user":
            return " ".join(
                p.text for p in (content.parts or []) if getattr(p, "text")
            )
    return ""


def _extract_response(llm_response: LlmResponse) -> str:
    if llm_response.content and llm_response.content.parts:
        return " ".join(
            p.text for p in llm_response.content.parts if getattr(p, "text")
        )
    return ""


def _blocked_response(reason: str) -> LlmResponse:
    return LlmResponse(
        content=types.Content(
            role="model",
            parts=[types.Part(
                text=f"I cannot process that request. [AIRS: {reason}]"
            )],
        )
    )


def before_model_callback(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
) -> Optional[LlmResponse]:
    """Scan prompt before it reaches the LLM. Fail-closed on error."""

    if not AIRS_ENABLED:
        return None

    prompt_text = _extract_prompt(llm_request)
    if not prompt_text:
        return None

    try:
        result = _scanner.sync_scan(
            ai_profile=_ai_profile,
            content=Content(prompt=prompt_text),
            metadata= Metadata(
                app_name="AURUM",
                ai_model=os.getenv("MODEL", "gemini-2.5-pro"),
                app_user=callback_context.state.get("user_id", "demo-user"),
            ),
        )

        # Persist to session state for audit trail
        callback_context.state["airs_prompt_scan"] = {
            "agent":    callback_context.agent_name,
            "action":   result.action,
            "category": result.category,
            "scan_id":  result.scan_id,
        }

        if result.action == "block":
            logger.warning(
                f"AIRS blocked prompt | agent={callback_context.agent_name} "
                f"category={result.category} scan_id={result.scan_id}"
            )
            return _blocked_response(result.category)

    except Exception as e:
        # Fail-closed — do not allow unscanned content through
        logger.error(f"AIRS before_model_callback error: {e}")
        callback_context.state["airs_prompt_scan_error"] = str(e)
        return _blocked_response("security check unavailable")

    return None


def after_model_callback(
    callback_context: CallbackContext,
    llm_response: LlmResponse,
) -> Optional[LlmResponse]:
    """Scan model response before it leaves the agent. Fail-closed on error."""

    if not AIRS_ENABLED:
        return None

    response_text = _extract_response(llm_response)
    if not response_text:
        return None

    try:
        result = _scanner.sync_scan(
            ai_profile=_ai_profile,
            content=Content(response=response_text),
            metadata=Metadata(
            app_name="AURUM",
            ai_model=os.getenv("MODEL", "gemini-2.5-pro"),
            app_user=callback_context.state.get("user_id", "demo-user"),
    ),
        )

        callback_context.state["airs_response_scan"] = {
            "agent":    callback_context.agent_name,
            "action":   result.action,
            "category": result.category,
            "scan_id":  result.scan_id,
        }

        if result.action == "block":
            logger.warning(
                f"AIRS blocked response | agent={callback_context.agent_name} "
                f"category={result.category} scan_id={result.scan_id}"
            )
            return _blocked_response(result.category)

    except Exception as e:
        logger.error(f"AIRS after_model_callback error: {e}")
        callback_context.state["airs_response_scan_error"] = str(e)
        return _blocked_response("security check unavailable")

    return None
