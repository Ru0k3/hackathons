# Medtriage MCP

> MedTriage MCP — AI-Powered Clinical Triage & Care Navigation
> MedTriage MCP is an MCP-based healthcare orchestration system that takes a patient from "something's wrong" to safely matched with the right doctor — closing the gap usually filled by guesswork.

![Model Context Protocol](https://img.shields.io/badge/Model%20Context%20Protocol-MCP-blue) ![Built with Nitrostack](https://img.shields.io/badge/Built%20with-Nitrostack-0A66FF) ![Status](https://img.shields.io/badge/status-live-brightgreen)

**Medtriage MCP** is an [MCP (Model Context Protocol)](https://nitrostack.ai) server that extends AI assistants — like Claude, Cursor, and any MCP-compatible client — with new, real-world capabilities. It is built and deployed on [Nitrostack](https://nitrostack.ai), the fastest way to build, deploy, and share MCP apps.

## Table of Contents

- [Overview](#overview)
- [What is MCP?](#what-is-mcp)
- [Features](#features)
- [Live Demo](#live-demo)
- [Getting Started](#getting-started)
- [Connect to an MCP Client](#connect-to-an-mcp-client)
- [Deploy Your Own MCP App](#deploy-your-own-mcp-app)
- [Explore More MCP Apps](#explore-more-mcp-apps)
- [FAQ](#faq)
- [Keywords](#keywords)
- [License](#license)

## Overview

MedTriage MCP is an MCP-based healthcare orchestration system that takes a patient from "something's wrong" to safely matched with the right doctor — closing the gap usually filled by guesswork.

* **Track 1 (Emergency Detection & Routing):** Symptoms are checked against red-flag patterns; genuine emergencies bypass normal flow entirely. Non-emergency cases get matched to an available specialist (searching nearby hospitals if needed), with real working hours confirmed, then booking and payment completed — no patient guesswork.
* **Track 2 (Medication Safety Auditing):** Before any prescription, MedTriage cross-checks it against the patient's active medications, allergies, and history using a real interaction dataset, flagging dangerous conflicts with severity and reasoning. It never recommends a drug — only guards against mistakes.
* **Track 3 (Rare Disease Registry Matching):** For unclear cases, it searches verified registries (FDA approvals, orphan drug data, published trials) for existing, documented treatments — never inventing new chemistry. No match means honest referral, not a guess.

A shared rule governs everything: ambiguity defaults to caution, not reassurance — directly responding to a documented 2026 Nature Medicine finding that a popular AI health tool under-triaged over half of true emergencies. MedTriage separates suggesting from guarding, using only real, cited data throughout.

## What is MCP?

The **Model Context Protocol (MCP)** is an open standard that lets AI assistants securely connect to external tools, data sources, and services. Instead of being limited to what it was trained on, an AI model can call **MCP servers** to fetch live data, run actions, and integrate with real systems.

This project is one such MCP server. Learn more about building and shipping MCP apps at [nitrostack.ai](https://nitrostack.ai).

## Features

- 🔌 **MCP-native** — works with any MCP-compatible client (Claude, Cursor, and more)
- 🛠️ **Tools, resources & prompts** — exposes structured capabilities to AI agents
- ⚡ **Deployed on Nitrostack** — reliable, hosted, and instantly shareable
- 🔐 **Secure by design** — secrets stay in environment variables, never in code
- 🧩 **Composable** — combine with other MCP apps to build powerful AI workflows

## Live Demo

🚀 **Live MCP endpoint:** https://medtriage-mc-zero-gravity-amrita-university-amritapuri-campus-1.app.nitrocloud.ai

Point your MCP client at the endpoint above to try it instantly. Prefer a hosted setup? Deploy your own in minutes on [Nitrostack](https://nitrostack.ai).

## Getting Started

### Prerequisites

- Node.js 18+ (or your project runtime)
- An MCP-compatible client (Claude Desktop, Cursor, etc.)

### Installation

```bash
git clone https://github.com/JayanthAmanchy/AgenticAIHackathon.git
cd medtriage-mcp
npm install
```

### Configuration

Copy the example environment file and add your own values:

```bash
cp .env.example .env
```

### Run

```bash
npm run dev
```

## Connect to an MCP Client

Add this server to your MCP client configuration. A typical entry looks like:

```json
{
  "mcpServers": {
    "medtriage-mcp": {
      "command": "node",
      "args": ["C:/Users/adith/nitroprojects/medtriage-mcp/dist/index.js"],
      "env": {}
    }
  }
}
```

Or for the remote live endpoint:

```json
{
  "mcpServers": {
    "medtriage-mcp": {
      "url": "https://medtriage-mc-zero-gravity-amrita-university-amritapuri-campus-1.app.nitrocloud.ai"
    }
  }
}
```

Restart your client and the tools from this MCP server will be available to your AI assistant.

## Deploy Your Own MCP App

Want to build and ship an MCP server like this one? **[Nitrostack](https://nitrostack.ai)** lets you create, deploy, and host MCP apps in minutes — no infrastructure to manage.

👉 **Start building:** [https://nitrostack.ai](https://nitrostack.ai)

## Explore More MCP Apps

- 🌙 Discover and share MCP projects with the community on [r/mcptothemoon](https://www.reddit.com/r/mcptothemoon/)
- 🧰 Browse a growing catalog of MCP apps on [Nitrostack](https://nitrostack.ai/apps)

## FAQ

### What is an MCP server?

An MCP server implements the Model Context Protocol to expose tools, resources, and prompts that AI assistants can call. It lets an AI model take real actions and access live data.

### What does Medtriage MCP do?

MedTriage MCP is an MCP-based healthcare orchestration system that takes a patient from "something's wrong" to safely matched with the right doctor, auditing medication safety, and checking rare disease registries using verified data sources.

### Which AI clients does this work with?

Any MCP-compatible client, including Claude Desktop and Cursor. New clients are adding MCP support regularly.

### How do I deploy my own MCP app?

Use [Nitrostack](https://nitrostack.ai) to build, deploy, and host MCP apps without managing infrastructure.

## Keywords

`HealthTech & Life Sciences` · `Medtriage MCP` · `MCP` · `Model Context Protocol` · `MCP server` · `MCP app` · `AI tools` · `AI agents` · `LLM tools` · `Claude MCP` · `Nitrostack` · `deploy MCP server` · `build MCP app`

## License

MIT © 2026

---

Built with ❤️ using the Model Context Protocol on [Nitrostack](https://nitrostack.ai). Share your MCP app on [r/mcptothemoon](https://www.reddit.com/r/mcptothemoon/).
