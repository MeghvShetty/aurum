# AURUM: _Latin for gold_

# The Scenario
AI-powered investment portfolio assistant for retail banking customers.
Three agents:
 
| Agent | Role | 
| ---|--- |
| Lead Agent | Receives user query. Routes to sub-agents based on intrent. Orchestrates the response 
|Porfolio RAG Agent | Retrieves the authenticated user's protfolio data, transaction history, and account details from pgvector. Read-only | 
| Advisory Agent | User-facing. Interprets retrieved data and delivers personalised investment guidance. | 


Ideal data 
> synthetic data per user profile which captures the following fields. Name, National Insurance number, account number, holdings, transcation history, portfolio value. Ten synthetic users seeded in pgvector.

One environment variable controls everything:
```.env
AIRS_ENABLED=true   # callbacks active
AIRS_ENABLED=false  # callbacks removed — direct to LLM
```


