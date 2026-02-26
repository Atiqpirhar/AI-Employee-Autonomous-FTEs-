# AI Employee Autonomous FTEs - Project Context

## Project Overview

This is a **hackathon/educational project** focused on building "Digital FTEs" (Full-Time Equivalents) - autonomous AI agents that act as personal/business employees. The project provides a comprehensive blueprint for creating local-first, agent-driven automation systems powered by **Claude Code** and **Obsidian**.

### Core Concept

A Digital FTE is an AI agent built to work 24/7 managing personal and business affairs:
- **Availability**: 168 hours/week (vs human's 40 hours)
- **Cost**: $500-$2,000/month (vs human's $4,000-$8,000+)
- **Use Cases**: Email triage, WhatsApp monitoring, bank transaction auditing, social media posting, invoice management

### Architecture: Perception → Reasoning → Action

| Layer | Component | Purpose |
|-------|-----------|---------|
| **Perception (Watchers)** | Python scripts | Monitor Gmail, WhatsApp, filesystems for triggers |
| **Reasoning** | Claude Code | AI reasoning engine with Ralph Wiggum persistence loop |
| **Memory/GUI** | Obsidian vault | Dashboard.md, Company_Handbook.md, task tracking |
| **Action (Hands)** | MCP Servers | Model Context Protocol for external system interaction |

## Key Technologies

| Technology | Purpose |
|------------|---------|
| **Claude Code** | Primary reasoning engine (with Ralph Wiggum loop for persistence) |
| **Obsidian** | Local Markdown knowledge base & dashboard |
| **Python 3.13+** | Watcher scripts & orchestration |
| **Node.js v24+** | MCP servers & automation |
| **Playwright MCP** | Browser automation for web tasks |
| **MCP Servers** | External system integration (email, browser, calendar, etc.) |

## Project Structure

```
AI-Employee-Autonomous-FTEs-/
├── Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md  # Main blueprint document
├── skills-lock.json          # Skill dependencies tracking
├── .Qwen/skills/             # Qwen skill configurations
│   └── browsing-with-playwright/
│       ├── SKILL.md          # Playwright MCP skill documentation
│       ├── references/
│       │   └── playwright-tools.md  # MCP tool reference
│       └── scripts/
│           ├── mcp-client.py      # Universal MCP client (HTTP + stdio)
│           ├── start-server.sh    # Start Playwright MCP server
│           ├── stop-server.sh     # Stop Playwright MCP server
│           └── verify.py          # Server health check
└── .git/
```

## Building and Running

### Prerequisites Setup

```bash
# 1. Install required software
# - Claude Code (Pro subscription or free tier)
# - Obsidian v1.10.6+
# - Python 3.13+
# - Node.js v24+ LTS

# 2. Create Obsidian vault
mkdir AI_Employee_Vault
cd AI_Employee_Vault
mkdir -p Inbox Needs_Action Done Plans Pending_Approval Accounting Briefings

# 3. Verify Claude Code
claude --version

# 4. Set up Python environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install playwright

# 5. Install Playwright browsers
playwright install
```

### Playwright MCP Server

```bash
# Start the server (keeps browser context alive)
bash .Qwen/skills/browsing-with-playwright/scripts/start-server.sh

# Or manually
npx @playwright/mcp@latest --port 8808 --shared-browser-context &

# Verify server is running
python .Qwen/skills/browsing-with-playwright/scripts/verify.py

# Stop the server
bash .Qwen/skills/browsing-with-playwright/scripts/stop-server.sh
```

### MCP Client Usage

```bash
# List available tools
python mcp-client.py list -u http://localhost:8808

# Call a tool
python mcp-client.py call -u http://localhost:8808 -t browser_navigate \
  -p '{"url": "https://example.com"}'

# Take a screenshot
python mcp-client.py call -u http://localhost:8808 -t browser_take_screenshot \
  -p '{"type": "png", "fullPage": true}'

# Get page snapshot (for element interaction)
python mcp-client.py call -u http://localhost:8808 -t browser_snapshot -p '{}'
```

### Watcher Scripts (Perception Layer)

Create watcher scripts following the base pattern:

```python
# base_watcher.py template
import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod

class BaseWatcher(ABC):
    def __init__(self, vault_path: str, check_interval: int = 60):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.check_interval = check_interval
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def check_for_updates(self) -> list:
        '''Return list of new items to process'''
        pass

    @abstractmethod
    def create_action_file(self, item) -> Path:
        '''Create .md file in Needs_Action folder'''
        pass

    def run(self):
        while True:
            try:
                items = self.check_for_updates()
                for item in items:
                    self.create_action_file(item)
            except Exception as e:
                self.logger.error(f'Error: {e}')
            time.sleep(self.check_interval)
```

### Ralph Wiggum Persistence Loop

Keep Claude working autonomously until task completion:

```bash
# Start Ralph loop
/ralph-loop "Process all files in /Needs_Action, move to /Done when complete" \
  --completion-promise "TASK_COMPLETE" \
  --max-iterations 10
```

## Development Conventions

### File Organization (Obsidian Vault)

| Folder | Purpose |
|--------|---------|
| `/Inbox` | Raw incoming items |
| `/Needs_Action` | Items requiring Claude's attention |
| `/In_Progress/<agent>/` | Claimed tasks (prevents double-work) |
| `/Done` | Completed tasks |
| `/Plans` | Plan.md files with task breakdowns |
| `/Pending_Approval` | Human-in-the-loop approval requests |
| `/Approved` | Approved actions ready for execution |
| `/Rejected` | Rejected actions |
| `/Accounting` | Bank transactions, invoices |
| `/Briefings` | CEO Briefing reports |

### Human-in-the-Loop Pattern

For sensitive actions, Claude writes approval request files:

```markdown
---
type: approval_request
action: payment
amount: 500.00
recipient: Client A
reason: Invoice #1234 payment
created: 2026-01-07T10:30:00Z
expires: 2026-01-08T10:30:00Z
status: pending
---

## Payment Details
- Amount: $500.00
- To: Client A (Bank: XXXX1234)
- Reference: Invoice #1234

## To Approve
Move this file to /Approved folder.
```

### Agent Skills

All AI functionality should be implemented as [Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview):
- Modular, reusable components
- Clear input/output schemas
- Documented in SKILL.md format

## Hackathon Tiers

| Tier | Time | Deliverables |
|------|------|--------------|
| **Bronze** | 8-12h | Obsidian vault, 1 watcher, basic Claude integration |
| **Silver** | 20-30h | 2+ watchers, MCP server, HITL workflow, scheduling |
| **Gold** | 40+h | Full integration, Odoo accounting, Ralph Wiggum loop, audit logging |
| **Platinum** | 60+h | Cloud deployment, domain specialization, vault sync, production-ready |

## Key Patterns

### Claim-by-Move Rule
First agent to move an item from `/Needs_Action` to `/In_Progress/<agent>/` owns it; other agents must ignore it.

### Single-Writer Rule
Only Local agent writes to Dashboard.md to prevent conflicts.

### Cloud/Local Separation (Platinum)
- **Cloud owns**: Email triage, draft replies, social post drafts (draft-only)
- **Local owns**: Approvals, WhatsApp session, payments/banking, final send/post actions

## Security Rules

- Vault sync includes only markdown/state files
- Secrets never sync (`.env`, tokens, WhatsApp sessions, banking credentials)
- Cloud agents work in draft-only mode; Local executes final actions

## Testing Practices

1. **Verify MCP server** before browser operations:
   ```bash
   python scripts/verify.py
   ```

2. **Test watcher scripts** individually before integration

3. **Use human-in-the-loop** for all sensitive actions during development

4. **Log all actions** to audit files for debugging

## Resources

- [Claude Code Documentation](https://claude.com/product/claude-code)
- [Obsidian Documentation](https://obsidian.md/help)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Playwright MCP](https://github.com/microsoft/playwright-mcp)
- [Ralph Wiggum Pattern](https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum)

## Weekly Research Meetings

- **When**: Wednesdays at 10:00 PM
- **Zoom**: https://us06web.zoom.us/j/87188707642?pwd=a9XloCsinvn1JzICbPc2YGUvWTbOTr.1
- **YouTube**: https://www.youtube.com/@panaversity
