# Spatial AI Architecture Decision Tree and Scoping Template

## Executive Summary
Choosing the wrong spatial AI architecture will waste time and tokens. This template provides a framework to evaluate options and define critical safety boundaries for your project based on three core architectural patterns:

* **Map Applications:** Visual interfaces.
* **Model Context Protocol (MCP):** Direct, deterministic database connection.
* **Agentic Workflows:** Multistep planning and reasoning.

---

## Part 1: The Architecture Decision Tree

To choose the right tool for your project, navigate this simple decision tree based on two key questions:

**Question One: What is the primary interface?**

* **Option A: Visual Interface** (Users need to explore data, toggle layers, or understand spatial relationships visually.)
    * 👉 **Decision: Map Application**
    * *Why?* Chat windows are not able to convey spatial context and arrangement.
* **Option B: Text Interface** (Like a chatbot or an API.)
    * ⬇️ **Next Step: Move to Question Two.**

**Question Two: Is the task Retrieval or Reasoning?**

* **Option A: Retrieval** (The user is asking for existing facts, e.g., "How many parks are in Buenos Aires?")
    * 👉 **Decision: Model Context Protocol (MCP)**
    * *Why?* MCP is fast, cheap, and deterministic, and it connects the LLM directly to the database to fetch the truth.
* **Option B: Reasoning** (The task requires multiple steps, calculations, or creating new data.)
    * 👉 **Decision: Agentic Workflow**
    * *Why?* Retrieval isn't enough here; the AI needs to plan, run spatial joins, and evaluate the results.

> **Note to Developers:** In production, these approaches are **not mutually exclusive**. Most robust projects are *Hybrid*. You might build a **Map Application** (the interface) that uses an **Agent** in the background (the worker) to analyze data fetched via **MCP** (the connector).

---

## Part 2: Scoping Template – Boundaries, Controls, and Review

Building a spatial AI tool is like giving a high-speed sports car to a student driver; it has incredible potential, but without guardrails, it will be difficult to control. Use this template to define your safety rules:

| Category | Control Area | Requirement / Implementation Detail |
| :--- | :--- | :--- |
| **1. BOUNDARIES** | **Define AOI (Area of Interest)** | *Define the Bounding Box or geographic limitation.*<br/>How will you enforce this? Will you prompt the user for an area, or reject requests lacking a specific location?<br/>*(Note: Skipping this allows the AI to query the whole planet, burning tokens and crashing databases.)*<br/><br/>**[Enter Implementation Plan Here]** |
| **2. CONTROLS** | **Database Permissions (Hard Rules)** | *Establish data access rules the AI cannot break.*<br/>Implement strict **Read-Only Access**. List the exact permissions of the database user the LLM connects to (e.g., ensure no permission for `DROP TABLE` or `DELETE` records).<br/><br/>**[Enter Permitted Actions / Restrictions Here]** |
| **2. CONTROLS** | **Query Row Limits** | *Prevent the AI from returning overwhelming datasets that exceed context window limits.*<br/>What is the specific numeric `LIMIT` you will enforce on *every* LLM-generated SQL query?<br/><br/>**[Enter Row Limit (e.g., 500) Here]** |
| **3. REVIEW** | **Observability & Logging** | *Maintain a detailed audit trail.*<br/>How will you log the direct output and the internal "thought process" of the LLM for audit and future review?<br/><br/>**[Enter Logging Strategy Here]** |
| **3. REVIEW** | **"Red Team" Step** | *Automated review of LLM reasoning.*<br/>How will you deploy an automated step within your workflows to review and summarize potential issues with results or logic before the user sees them?<br/><br/>**[Enter Red Team Workflow Detail Here]** |
| **3. REVIEW** | **User Feedback Loop (UI)** | *Gather signals to refine system prompts.*<br/>Detail how the UI will allow users to quickly signal a poor map result (e.g., a simple Thumbs Up / Thumbs Down button on the map result).<br/><br/>**[Enter Feedback UI Plan Here]** |