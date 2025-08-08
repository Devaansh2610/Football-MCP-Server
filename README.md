# ⚽️ Football Data Microservice with FastMCP

This project is a secure and modular **football data microservice** built using the `FastMCP` framework, designed for seamless integration with **LLM agents** like **Cursor Agent** and **Claude Desktop**.

Its purpose is to expose **structured, real-time football data** via conversational, callable tools optimized for **agentic workflows** — enabling natural language-driven data retrieval with ease and security.

---

## 🚀 Features

- 🔌 **FastMCP-powered** microservice with schema-compliant callable tools.
- 🧠 Seamless integration with LLM agents for natural language queries.
- ⚙️ Containerized with **Docker** for portability and security.
- 🔐 Dual-key access control for runtime protection.
- 📦 One-click launch support via `config.json` in Claude Desktop.

---

## 🧰 Tools Implemented

Each tool is an MCP-compliant function that supports schema-driven querying via LLMs and returns clean, interpretable JSON structures.

1. ### `get_league_id_by_name`
   - Retrieves a **league's unique ID** by name.
   - Simplifies API calls requiring numeric league identifiers.
   - Enables natural language-driven dynamic queries.

2. ### `get_standings`
   - Fetches **detailed standings** for multiple leagues and seasons.
   - Optional filtering by **team ID**.
   - Ideal for comparing team performance trends.

3. ### `get_player_id`
   - Resolves **player IDs** from partial names (first or last).
   - Returns matching profiles with metadata (ID, age, nationality, etc.).
   - Useful for handling incomplete queries from LLMs.

4. ### `get_player_profile`
   - Delivers **structured player bios** (birthplace, nationality, height, etc.).
   - Tailored for personalized insights in agentic systems.

5. ### `get_player_statistics`
   - Fetches comprehensive **player stats** across seasons.
   - Metrics include goals, assists, ratings, passes, duels, fouls, and more.
   - Allows optional filtering by league and season.

---

## 🧱 Architecture & Security

### 🔒 Secure, Containerized Deployment
- Built with **Docker** for consistent runtime, portability, and code protection.
- API keys and credentials are hidden from logs and external exposure.
- One-click launch via a custom `config.json` in Claude Desktop.

### 🔐 Dual-Key Access Control

To prevent misuse and unauthorized access:

- 🔑 **Internal Secret Key**: Embedded at build-time in the Docker `.env` file.
- 🔑 **External Key (Runtime)**: Must be supplied by the user via environment variable.

If the external key does **not match** the internal secret:
- 🚫 The container **exits immediately**.
- 🔐 Internal key is **never logged or exposed**.

This robust access control ensures secure deployments, even in shared or remote environments.

---

## 🔧 Tech Stack

- **FastMCP** – Modular conversational tools for LLMs
- **Docker** – Containerized deployment
- **Python** – Core logic and tooling
- **RAPID-API Football** – Real-time football data source
- **Claude Desktop / Cursor Agent** – LLM-based interfaces

---


