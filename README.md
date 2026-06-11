# ARUM: _Latin for gold_

# The Scenario
AI-powered investment portfolio assistant for retail banking customers.
Three agents:

|--|--| 
| Agent | Role | 
| Lead Agent | Receives user query. Routes to sub-agents based on intrent. Orchestrates the response 
|Porfolio RAG Agent | Retrieves the authenticated user's protfolio data, transaction history, and account details from pgvector. Read-only | 
