# AI Employee - How It Works Guide

## Quick Start: Which Commands to Run and Why

### Scenario 1: First Time Setup

```bash
# 1. Navigate to the scripts folder
cd C:\Users\Thinkpad\OneDrive\Documents\GitHub\AI-Employee-Autonomous-FTEs-\AI_Employee_Vault\scripts

# 2. Install Python dependencies
pip install watchdog

# 3. Verify Qwen Code is set up
qwen --version

# 4. If not set up, configure your API key
qwen setup-token
# or set environment variable:
# set DASHSCOPE_API_KEY=your-api-key-here
```

**Why?** This installs required packages and ensures Qwen Code can authenticate with the API.

---

### Scenario 2: Daily Usage (Continuous Mode)

Open **two terminal windows**:

**Terminal 1 - Filesystem Watcher:**
```bash
cd C:\Users\Thinkpad\OneDrive\Documents\GitHub\AI-Employee-Autonomous-FTEs-\AI_Employee_Vault\scripts
python filesystem_watcher.py ..
```
**Why?** This watches the `Drop_Folder/` for new files 24/7. When you drop a file, it automatically creates an action file in `Needs_Action/`.

**Terminal 2 - Orchestrator:**
```bash
cd C:\Users\Thinkpad\OneDrive\Documents\GitHub\AI-Employee-Autonomous-FTEs-\AI_Employee_Vault\scripts
python orchestrator.py .. --continuous
```
**Why?** This continuously checks for pending items and approved actions, then calls Qwen Code to process them.

---

### Scenario 3: One-Time Processing

```bash
# 1. Drop your file in the Drop_Folder
# Example: Drop_Folder/invoice.pdf

# 2. Wait 30 seconds for watcher to detect it
# (or run the watcher once)

# 3. Run the orchestrator once
cd C:\Users\Thinkpad\OneDrive\Documents\GitHub\AI-Employee-Autonomous-FTEs-\AI_Employee_Vault\scripts
python orchestrator.py ..
```

**Why?** If you just want to process a single file without running continuous background processes.

---

## Complete Workflow Example

### Step-by-Step: Processing an Invoice

#### Step 1: Drop the File
Place `invoice_january.pdf` in:
```
AI_Employee_Vault/Drop_Folder/invoice_january.pdf
```

#### Step 2: Watcher Detects (Automatic)
The Filesystem Watcher:
- Detects the new file every 30 seconds
- Calculates a hash to avoid duplicates
- Copies the file to `Files/` folder
- Creates an action file in `Needs_Action/`

**Output you'll see:**
```
2026-02-27 10:30:00 - FilesystemWatcher - INFO - Found 1 new item(s)
2026-02-27 10:30:00 - FilesystemWatcher - INFO - Created action file: FILE_invoice_january_20260227_103000.md
2026-02-27 10:30:00 - FilesystemWatcher - INFO - Processed file: invoice_january.pdf
```

#### Step 3: Orchestrator Processes
The Orchestrator:
- Scans `Needs_Action/` folder
- Builds a prompt for Qwen Code
- Calls Qwen Code with the action file content
- Qwen Code reads, analyzes, and takes actions

**Output you'll see:**
```
2026-02-27 10:31:00 - Orchestrator - INFO - === Orchestrator Run ===
2026-02-27 10:31:00 - Orchestrator - INFO - Found 1 item(s) in Needs_Action
2026-02-27 10:31:00 - Orchestrator - INFO - Calling Qwen Code: You are the AI Employee...
2026-02-27 10:31:30 - Orchestrator - INFO - === Orchestrator Run Complete ===
```

#### Step 4: Qwen Code Acts
Qwen Code will:
1. Read the action file
2. Read the invoice PDF from `Files/`
3. Extract: vendor, amount, date, line items
4. Update `Dashboard.md` with summary
5. Log to `Logs/2026-02-27.json`
6. Move action file to `Done/`

#### Step 5: Check Results
Open `Dashboard.md` in Obsidian to see:
```markdown
## Recent Activity
- [2026-02-27 10:31] Processed: Invoice from Vendor ($500)
```

---

## Architecture Components Explained

### 1. Filesystem Watcher (`filesystem_watcher.py`)

**What it does:**
- Monitors `Drop_Folder/` for new files
- Runs every 30 seconds (configurable)
- Creates markdown action files with metadata

**When to run:**
- Keep running in background for automatic processing
- Or run once when you have files to process

**Command:**
```bash
python filesystem_watcher.py ..
```

**Stop with:** `Ctrl+C`

---

### 2. Orchestrator (`orchestrator.py`)

**What it does:**
- Scans `Needs_Action/` for pending items
- Scans `Approved/` for approved actions
- Calls Qwen Code to process items
- Updates `Dashboard.md`
- Moves completed items to `Done/`

**Modes:**
- **Single run:** `python orchestrator.py ..`
- **Continuous:** `python orchestrator.py .. --continuous`

**When to run:**
- **Continuous mode:** For 24/7 autonomous operation
- **Single run:** For manual, on-demand processing

**Command:**
```bash
# Continuous (recommended for autonomous operation)
python orchestrator.py .. --continuous

# Single run (for manual processing)
python orchestrator.py ..
```

**Stop with:** `Ctrl+C`

---

### 3. Base Watcher (`base_watcher.py`)

**What it is:**
- Abstract base class for all watchers
- Provides common functionality (logging, file naming, etc.)

**When to use:**
- When creating custom watchers (Gmail, WhatsApp, etc.)
- Not needed for basic file drop workflow

---

## Folder Structure and Purpose

```
AI_Employee_Vault/
│
├── Drop_Folder/          ← YOU PUT FILES HERE
├── Needs_Action/         ← Watcher creates action files here
├── Files/                ← Copies of dropped files
├── Done/                 ← Completed tasks
├── Pending_Approval/     ← Awaiting your review
├── Approved/             ← You approved these
├── Rejected/             ← You rejected these
├── Logs/                 ← Daily activity logs
├── Dashboard.md          ← Status overview
├── Company_Handbook.md   ← Your rules
└── Business_Goals.md     ← Your objectives
```

---

## Human-in-the-Loop Workflow

### For Actions Requiring Approval

**Step 1:** Qwen Code creates approval request
```
Pending_Approval/PAYMENT_vendor_20260227.md
```

**Step 2:** You review the file in Obsidian

**Step 3a:** To Approve
```bash
# Move file to Approved folder
mv Pending_Approval/PAYMENT_vendor_20260227.md Approved/
```

**Step 3b:** To Reject
```bash
# Move file to Rejected folder with reason
mv Pending_Approval/PAYMENT_vendor_20260227.md Rejected/
echo "Reason: Duplicate invoice" >> Rejected/PAYMENT_vendor_20260227.md
```

**Step 4:** Orchestrator detects and executes (or skips if rejected)

---

## Common Use Cases

### Use Case 1: Process a Document

```bash
# 1. Drop document
cp my_document.pdf AI_Employee_Vault/Drop_Folder/

# 2. Wait for watcher (or run manually)
python filesystem_watcher.py ..

# 3. Run orchestrator
python orchestrator.py ..
```

**Result:** Document summarized in `Done/` folder

---

### Use Case 2: Batch Processing

```bash
# 1. Drop multiple files
cp *.pdf AI_Employee_Vault/Drop_Folder/

# 2. Run watcher to detect all
python filesystem_watcher.py ..

# 3. Run orchestrator in continuous mode
python orchestrator.py .. --continuous
```

**Result:** All files processed sequentially

---

### Use Case 3: Autonomous Operation

**Terminal 1:**
```bash
python filesystem_watcher.py ..
```

**Terminal 2:**
```bash
python orchestrator.py .. --continuous
```

**Result:** 24/7 autonomous processing of any dropped files

---

## Troubleshooting

### "Qwen Code not found"

```bash
# Install Qwen Code
npm install -g @alibaba/qwen-code

# Verify
qwen --version
```

### "API key not set"

```bash
# Set API key
qwen setup-token

# Or use environment variable
set DASHSCOPE_API_KEY=sk-your-api-key-here
```

### Watcher not detecting files

```bash
# Check if drop folder exists
dir AI_Employee_Vault\Drop_Folder

# Run watcher with verbose output
python filesystem_watcher.py .. 2>&1
```

### Orchestrator not processing

```bash
# Check if items exist in Needs_Action
dir AI_Employee_Vault\Needs_Action

# Run with debug output
python orchestrator.py .. -v
```

---

## Configuration Options

### Change Watcher Check Interval

```python
# In filesystem_watcher.py, change:
super().__init__(vault_path, check_interval=30)  # 30 seconds
```

### Change Orchestrator Check Interval

```bash
# Continuous mode with custom interval (60 seconds)
python orchestrator.py .. --continuous --interval 60
```

---

## Best Practices

1. **Review logs daily:** Check `Logs/YYYY-MM-DD.json`

2. **Clean up Done folder weekly:** Move old files to archive

3. **Update Company Handbook:** Refine rules as you learn

4. **Monitor API usage:** Check your DashScope quota

5. **Backup your vault:** Use Git or cloud sync

---

## Next Steps (Silver Tier)

After mastering Bronze tier:

1. Add Gmail Watcher for email monitoring
2. Add WhatsApp Watcher for messaging
3. Implement MCP servers for sending emails
4. Set up scheduled tasks (cron/Task Scheduler)

---

*For more details, see README.md*
