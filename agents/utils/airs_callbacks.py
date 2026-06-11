import os 
import logging 
from typing import Optional 

from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types 

logger = logging.getLogger(__name__)


"""
Palo Alto prisma SDK init - one at startup, only if enabled 
Toggle via getenv values 
"""

AIRS_ENABLED =os.getenv("AIRS_ENABLED", "true").lower()=="true"
if AIRS_ENABLED:
    try:
        import aisecurity
        from aisecurity.scan.inline.scanner import Scanner
        from aisecurity.scan.models import content
        from aisecurity.generated_openapi_client.models.ai_profile import AiProfile 

        aisecurity.init(api_key=os.getenv("PA_AI_SECURIY_API_KEY"))
        _scanner = Scanner()
        _ai_profile = AiProfile(
            profile_id=os.getenv("AIRS_PROFILE_NAME","Default")
        )
        logger.info("AIRS enable - scanner initialised")

    except Exception as e:
        logger.error(f"AIRS init failed: {e}. Defaulting to fail-closed.")
        AIRS_ENABLED = False 


 def before_model_callback(
    callback_context:CallbackContext,
        llm_request: LlmRequest,
):
    if not AIRS_ENABLED:
        return None

    prompt_text = _extract_prompt(llm_request)
    if not prompt_text:
        return None

    try:
        result = _scanner.sync_scan(
        ai_profile = _ai_profile,
        content = types.Content(prompt=prompt_text),
    )
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
            return result.category

  except Exception as e:
        # Fail-closed — do not allow unscanned content through
        logger.error(f"AIRS before_model_callback error: {e}")
        callback_context.state["airs_prompt_scan_error"] = str(e)
        return _blocked_response("security check unavailable")

    return None
