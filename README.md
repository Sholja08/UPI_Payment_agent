# UPI_Payment_agent

An AI-driven UPI payment support agent that automates user queries related to UPI transactions, mandates, and payment workflows using LLM-powered tool orchestration.

---

##  Features

-  Handles UPI-related user queries intelligently
-  Assists with transaction status, failures, and retries
-  Manages UPI mandates (create, view, cancel)
-  Uses LLM + tools architecture for decision-making
-  Secure tool execution via FastMCP servers

---

##  Tech Stack

- **Python**
- **LangGraph** – agent orchestration and state management
- **FastMCP** – secure tool server implementation
- **LLM Tools** – decision making and task routing

---

##  System Architecture

User Query
↓
LLM Agent (LangGraph)
↓
Tool Router
↓
FastMCP Tool Server
↓
UPI Actions / Responses

---

##  How It Works

1. User submits a UPI-related query
2. LangGraph agent analyzes intent
3. Relevant FastMCP tool is invoked
4. Tool processes the request securely
5. Agent returns a structured response

---

## Installation

```bash
git clone https://github.com/Sholja08/UPI_Payment_agent.git
cd UPI_Payment_agent
pip install -r requirements.txt


