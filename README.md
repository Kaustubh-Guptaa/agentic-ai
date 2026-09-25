# 🤖 Agentic AI - Data Agent

A multi-agent system for intelligent data processing and analysis using LangGraph. Implements and end-to-end agentic architecture with specialized sub-agents for SQL operations and ETL workflows.

---

## 🎯 Overview

**Agentic AI Data Agent** is an intelligent system that processes natural language queries and routes them to specialized agents for execution. The main agent acts as an intelligent router that understands user intent and delegates tasks to either the **SQL Analyst Agent** (for database queries) or the **ETL Analyst Agent** (for data extraction and transformation operations).

This project showcases modern AI engineering practices including:
- Multi-agent orchestration with LangGraph
- Intelligent routing based on natural language understanding
- Safety validation for SQL queries
- Tool-based agent architecture
- Dynamic LLM selection based on task complexity

---

## 🏗️ Architecture

The system follows a hierarchical agent architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                    Data Agent (Router)                      │
│         Routes user queries to appropriate sub-agents       │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
         ▼                       ▼
    ┌──────────────┐        ┌──────────────┐
    │ SQL Analyst  │        │ ETL Analyst  │
    │   Agent      │        │   Agent      │
    └──────────────┘        └──────────────┘
         │                       │
         ├─► Query Curation      ├─► Extract Load
         ├─► Schema Context      ├─► Transform Load
         ├─► SQL Generation      └─► Code Execution
         ├─► Safety Validation   
         ├─► Query Execution     
         └─► Answer Generation   
```

### State Flow

1. **User Input** → Natural language query
2. **Router Node** → Classifies query as SQL or ETL
3. **Agent Dispatch** → Routes to appropriate sub-agent
4. **Processing** → Each agent processes the task
5. **Output** → Returns structured result to user

---

## ✨ Features

### Core Capabilities

- **Intelligent Query Routing**: Automatically classifies user queries as SQL or ETL operations
- **SQL Analysis Agent**:
  - Natural language to SQL query conversion
  - Automatic schema context gathering
  - SQL safety validation (prevents harmful operations)
  - Query execution on PostgreSQL database
  - Intelligent query refinement

- **ETL Agent**:
  - API data extraction (JSON to structured formats)
  - Data transformation using Pandas
  - Multi-format support (CSV, JSON, Parquet)
  - Dynamic code generation based on user requirements
  - Safe code execution

- **Multi-LLM Support**:
  - Low-complexity queries: Faster, cost-effective LLM
  - Medium-complexity queries: Balanced LLM
  - High-complexity queries: Premium LLM (Claude)

- **Safety & Validation**:
  - SQL query safety checking
  - Protection against database modifications (INSERT, UPDATE, DELETE, DROP, etc.)
  - Input validation and sanitization
  - Structured output validation using Pydantic

---
