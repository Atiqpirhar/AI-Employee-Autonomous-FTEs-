# AI Employee - Bronze Tier Implementation

> **Tagline:** Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.

A Personal AI Employee that proactively manages your personal and business affairs using **Qwen Code** as the reasoning engine and **Obsidian** as the management dashboard.

## Bronze Tier Deliverables ✅

- [x] Obsidian vault with `Dashboard.md` and `Company_Handbook.md`
- [x] One working Watcher script (Filesystem monitoring)
- [x] Qwen Code successfully reading from and writing to the vault
- [x] Basic folder structure: `/Inbox`, `/Needs_Action`, `/Done`
- [x] Orchestrator for triggering Qwen Code processing

---

## Quick Start

### Prerequisites

| Software | Version | Purpose |
|----------|---------|---------|
| [Qwen Code](https://github.com/QwenLM/qwen-code) | Latest | Primary reasoning engine |
| [Obsidian](https://obsidian.md/download) | v1.10.6+ | Knowledge base & dashboard |
| [Python](https://www.python.org/downloads/) | 3.13+ | Watcher scripts & orchestration |

### Setup (15 minutes)

1. **Clone or download this repository**

2. **Install Python dependencies**
   ```bash
   cd AI_Employee_Vault/scripts
   pip install watchdog
   ```

3. **Set up Qwen Code**
   ```bash
   # Install Qwen Code (if not already installed)
   npm install -g @alibaba/qwen-code
   
   # Set up your API key
   qwen setup-token
   # Or set environment variable:
   # export DASHSCOPE_API_KEY=your-api-key-here
   
   # Verify installation
   qwen --version
   ```

4. **Open the vault in Obsidian**
   - Launch Obsidian
   - Click "Open folder as vault"
   - Select the `AI_Employee_Vault` folder

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    AI Employee                          │
│                  (Bronze Tier)                          │
└─────────────────────────────────────────────────────────┘

┌─────────────────┐     ┌─────────────────────────────────┐
│   Drop Folder   │────▶│      Filesystem Watcher         │
│  (User drops    │     │  (Monitors for new files)       │
│   files here)   │     └─────────────────────────────────┘
└─────────────────┘                  │
                                     ▼
                          ┌─────────────────────────────────┐
                          │     Needs_Action Folder         │
                          │  (Action files created here)    │
                          └─────────────────────────────────┘
                                     │
                                     ▼
                          ┌─────────────────────────────────┐
                          │      QWEN CODE                  │
                          │   Read → Think → Plan → Write   │
                          └─────────────────────────────────┘
                                     │
                    ┌────────────────┴────────────────┐
                    ▼                                 ▼
        ┌─────────────────────┐         ┌─────────────────────┐
        │   Pending_Approval  │         │      Done Folder    │
        │  (Human reviews)    │         │   (Completed items) │
        └─────────────────────┘         └─────────────────────┘
                    │
                    ▼
        ┌─────────────────────┐
        │    Approved Folder  │
        │  (Human approved)   │
        └─────────────────────┘
                    │
                    ▼
        ┌─────────────────────┐
        │   Execute Action    │
        │   (Qwen processes)  │
        └─────────────────────┘
```

---

## Folder Structure

```
AI_Employee_Vault/
├── Dashboard.md              # Real-time status dashboard
├── Company_Handbook.md       # Rules of engagement
├── Business_Goals.md         # Your business objectives
├── Inbox/                    # Raw incoming items
├── Needs_Action/             # Items requiring processing
├── Plans/                    # Task breakdowns
├── Pending_Approval/         # Awaiting human approval
├── Approved/                 # Approved actions ready to execute
├── Rejected/                 # Rejected actions with reasons
├── Done/                     # Completed tasks
├── Accounting/               # Financial records
├── Briefings/                # CEO briefing reports
├── Logs/                     # Daily activity logs
├── Files/                    # Processed file attachments
├── Drop_Folder/              # Drop files here for processing
└── scripts/
    ├── base_watcher.py       # Base class for watchers
    ├── filesystem_watcher.py # Filesystem monitoring
    └── orchestrator.py       # Qwen Code trigger
```

---

## Usage

### Method 1: File Drop Processing

1. **Drop a file** into the `Drop_Folder/` directory
   - Any file type: PDF, DOCX, TXT, CSV, images, etc.

2. **The Filesystem Watcher** automatically:
   - Detects the new file
   - Copies it to `Files/` for safekeeping
   - Creates an action file in `Needs_Action/`

3. **Run the Orchestrator** to process:
   ```bash
   cd AI_Employee_Vault/scripts
   python orchestrator.py ..
   ```

4. **Qwen Code** will:
   - Read the action file
   - Process the dropped file
   - Create a summary and take actions
   - Move the file to `Done/` when complete

### Method 2: Manual Processing

1. Create a markdown file in `Needs_Action/`:
   ```markdown
   ---
   type: manual
   priority: normal
   ---
   
   # Task Description
   
   What needs to be done...
   
   ## Suggested Actions
   - [ ] Action 1
   - [ ] Action 2
   ```

2. Run the orchestrator:
   ```bash
   python orchestrator.py ..
   ```

### Continuous Mode

Run both watcher and orchestrator continuously:

```bash
# Terminal 1: Start the filesystem watcher
cd AI_Employee_Vault/scripts
python filesystem_watcher.py ..

# Terminal 2: Start the orchestrator (continuous mode)
cd AI_Employee_Vault/scripts
python orchestrator.py .. --continuous
```

---

## Human-in-the-Loop Workflow

For actions requiring approval:

1. **Claude creates** a file in `Pending_Approval/`:
   ```markdown
   ---
   type: approval_request
   action: summarize_document
   created: 2026-02-27T10:30:00Z
   ---
   
   ## Action Details
   Summarize the dropped PDF file
   
   ## To Approve
   Move this file to /Approved/
   
   ## To Reject
   Move this file to /Rejected/ with reason
   ```

2. **You review** the request

3. **To approve**: Move the file to `Approved/`

4. **To reject**: Move the file to `Rejected/` and add a reason

5. **Orchestrator** detects approved files and executes the action

---

## Example Workflow

### Processing an Invoice

1. **Drop the invoice PDF** into `Drop_Folder/invoice_jan.pdf`

2. **Watcher creates** action file:
   ```
   Needs_Action/FILE_invoice_jan_20260227_103000.md
   ```

3. **Run orchestrator**:
   ```bash
   python orchestrator.py ..
   ```

4. **Qwen Code**:
   - Reads the invoice
   - Extracts: vendor, amount, date, line items
   - Creates summary in action file
   - Logs to `Accounting/Transactions.md`
   - Moves to `Done/`

5. **Check Dashboard.md** for summary:
   ```
   ## Recent Activity
   - [2026-02-27 10:35] Processed: Invoice from Vendor ($500)
   ```

---

## Configuration

### Customize Company Handbook

Edit `Company_Handbook.md` to set your rules:

- Payment thresholds
- Communication style
- Priority keywords
- Known contacts
- Working hours

### Update Business Goals

Edit `Business_Goals.md` to define:

- Revenue targets
- Active projects
- Service rates
- Client list

---

## Troubleshooting

### Qwen Code not found

```bash
# Install Qwen Code
npm install -g @alibaba/qwen-code

# Or verify installation
qwen --version
```

### Watcher not detecting files

```bash
# Check if drop folder exists
ls -la AI_Employee_Vault/Drop_Folder/

# Run watcher with verbose logging
python filesystem_watcher.py .. 2>&1 | tee watcher.log
```

### Orchestrator timeout

- Large files may take time to process
- Check your API key and quota
- Try processing files individually

---

## Logs

Daily logs are stored in `Logs/YYYY-MM-DD.json`:

```json
{"timestamp": "2026-02-27T10:35:00", "action": "process_needs_action", "details": "Processed 1 items", "status": "success"}
```

View today's log:
```bash
cat Logs/$(date +%Y-%m-%d).json
```

---

## Next Steps (Silver Tier)

To upgrade to Silver tier:

1. Add Gmail Watcher for email monitoring
2. Add WhatsApp Watcher (Playwright-based)
3. Implement MCP server for sending emails
4. Add scheduled tasks (cron/Task Scheduler)
5. Create Plan.md generation workflow

---

## Security Notes

⚠️ **Important Security Practices:**

1. **Never commit** `.env` files or credentials
2. **Use environment variables** for API keys
3. **Review all approvals** before executing
4. **Check logs regularly** for unexpected activity
5. **Keep vault backed up** (use Git or cloud sync)

---

## License

This project is part of the Personal AI Employee Hackathon 0.

---

## Resources

- [Hackathon Document](../Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md)
- [Qwen Code Documentation](https://github.com/QwenLM/qwen-code)
- [Obsidian Help](https://help.obsidian.md/)
- [Wednesday Research Meetings](https://us06web.zoom.us/j/87188707642?pwd=a9XloCsinvn1JzICbPc2YGUvWTbOTr.1)

---

*Built for the Personal AI Employee Hackathon 0 - Bronze Tier*
