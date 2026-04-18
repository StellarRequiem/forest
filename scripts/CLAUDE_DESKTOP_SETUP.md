# Claude Desktop — MCP Setup Guide
## What's already configured (zero setup needed)

These 5 servers are live the moment you restart Claude Desktop:

| Server | What it gives Claude | Status |
|---|---|---|
| **filesystem** | Read/write any file under /Users/llm01 | ✅ Auto |
| **git** | Git log, diff, commit, branch across all repos | ✅ Auto |
| **memory** | Persistent knowledge graph that survives across sessions | ✅ Auto |
| **fetch** | Fetch any URL and convert to clean markdown | ✅ Auto |
| **sequential-thinking** | Multi-step reasoning chains for complex problems | ✅ Auto |

---

## Step 1 — Add your GitHub Token (5 minutes)

**Why:** Lets Claude read your repos, create issues, review PRs, check Actions runs.

1. Go to: https://github.com/settings/tokens/new
2. Note: "Claude Desktop MCP"
3. Expiration: 90 days (or No expiration)
4. Check these boxes:
   - ✅ `repo` (full repo access)
   - ✅ `read:org`
   - ✅ `workflow`
5. Click **Generate token** — copy the `ghp_...` string immediately
6. Open this file in any text editor:
   ```
   ~/Library/Application Support/Claude/claude_desktop_config.json
   ```
7. Find this line:
   ```
   "GITHUB_PERSONAL_ACCESS_TOKEN": "REPLACE_WITH_YOUR_GITHUB_TOKEN"
   ```
8. Replace `REPLACE_WITH_YOUR_GITHUB_TOKEN` with your actual `ghp_...` token
9. Save the file
10. Quit and relaunch Claude Desktop

**Test it:** Ask Claude "list my GitHub repos" — it should show StellarRequiem/forest etc.

---

## Step 2 — Add Brave Search API Key (10 minutes)

**Why:** Gives Claude real-time web search that's private (no Google tracking).

1. Go to: https://brave.com/search/api/
2. Click **Get Started Free** (free tier = 2,000 queries/month)
3. Sign up / log in
4. Go to: https://api-dashboard.search.brave.com/app/keys
5. Click **Create Key** → name it "Claude Desktop"
6. Copy the API key
7. Open:
   ```
   ~/Library/Application Support/Claude/claude_desktop_config.json
   ```
8. Find this line:
   ```
   "BRAVE_API_KEY": "REPLACE_WITH_YOUR_BRAVE_API_KEY"
   ```
9. Replace with your actual key
10. Save and relaunch Claude Desktop

**Test it:** Ask Claude "search the web for latest Ollama models 2026"

---

## Step 3 — Restart Claude Desktop

After editing the config:
1. Quit Claude Desktop completely (Cmd+Q, not just close window)
2. Relaunch it
3. Open a new chat — you should see MCP tools available in the tool picker

---

## On "OpenClaw" — Clarification Needed

I wasn't sure which tool you meant by "openclaw." Could be:
- **Crawl4AI** — AI-optimized web crawler: `pip install crawl4ai` — has an MCP server
- **OpenCrawl** — open-source web crawler
- **Open-WebUI** — already running in your Docker stack at http://localhost:3000
- Something else entirely?

Tell me which one and I'll wire it up in 2 minutes.

---

## AirLLM Assessment for Your Setup

**What it does:** Runs massive models (70B+) by loading them layer-by-layer instead of all at once. Trades speed for memory efficiency.

**For your M4 Mini 16GB:**
- ✅ Could technically run 70B models (Llama 3.3 70B etc.)
- ❌ Speed will be very slow — 1-5 tokens/second vs 30-50 t/s with phi4-mini
- ❌ Not suitable for Forest's real-time security analysis (needs <30s response)
- ✅ Good for one-off deep analysis tasks where you have time to wait

**Better option for your use case:** Stay with phi4-mini (fast, good reasoning) for Forest. If you want a bigger model for occasional deep analysis, use mlx-lm directly:

```bash
pip install mlx-lm
mlx_lm.generate --model mlx-community/Qwen2.5-7B-Instruct-4bit \
  --prompt "Your analysis prompt here" --max-tokens 500
```

This uses your M4's Metal GPU natively and is 10x faster than AirLLM for the same model.

**TL;DR on AirLLM:** Cool experiment, not the right tool for your production workload. MLX is the native M-series path to larger models.

---

## Current MCP Config Location
```
~/Library/Application Support/Claude/claude_desktop_config.json
```
