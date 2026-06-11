from google.adk.agents import LlmAgent
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool
from aurum.utils.instruction_loader import load_instruction_from_file 
from aurum.utils.airs_callbacks import before_model_callback

MODEL = "gemini-2.5-pro"


# Sub Agent 1 : Porfolio RAG Agent
portfolio_agent = LlmAgent(
    name = "Portfolio_Agent",
    model= MODEL,
    instruction= load_instruction_from_file("portfolio-instruction.txt"),
    before_model_callback=before_model_callback
)

# Sub Agent 2 : Advisory Agent
advisory_agent = LlmAgent(
    name = "Advisory_Agent",
    model = MODEL,
    instruction= load_instruction_from_file("advisory-instruction.txt"),
    before_model_callback=before_model_callback
) 

# Lead Agent 
lead_agent = LlmAgent(
    name = "AURUM",
    model= MODEL,
    instruction= load_instruction_from_file("lead-instruction.txt"),
    tools = [
        AgentTool(portfolio_agent),
        AgentTool(advisory_agent),
        ],
    before_model_callback=before_model_callback

)

root_agent = lead_agent 
