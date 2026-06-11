from google.adk.agents import LlmAgent
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool
from utils.instruction_loader import load_instruction_from_file 


MODEL = "gemini-2.5-pro"


# Sub Agent 1 : Porfolio RAG Agent
portfolio_agent = LlmAgent(
    name = "Portfolio Agent",
    model= MODEL,
    instruction= load_instruction_from_file("portfolio-instruction.txt")

)

# Sub Agent 2 : Advisory Agent
advisory_agent = LlmAgent(
    name = "Advisory Agent",
    model = MODEL,
    instruction= load_instruction_from_file("advisory-instruction.txt")
) 

# Lead Agent 
lead_agent = LlmAgent(
    name = "AURUM",
    model= MODEL,
    instruction= load_instruction_from_file("lead-instruction.txt"),
    tools = [AgentTool(portfolio_agent),AgentTool(advisory_agent), google_search]

)

root_agent = lead_agent 
