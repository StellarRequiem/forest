# Security Policy

## Scope

Forest CUS is a **defensive, blue-team monitoring tool**. It:

- Collects local system telemetry (network connections, system logs, running processes)
- Analyzes that data with locally-hosted LLMs via [Ollama](https://ollama.ai)
- Runs entirely on your own machine — no data leaves your device
- Has no network-facing services by default

This policy covers the Forest CUS source code in this repository.

---

## Intended use

Forest CUS is built for:

- Blue-team security monitoring of a single host
- Security awareness training (phishing detection, URL analysis, password hygiene)
- Studying local LLM agent orchestration with LangGraph

It is **not** designed for:
- Scanning or monitoring systems you do not own
- Red-team or offensive operations
- Production deployment without your own security review

---

## Reporting a vulnerability

If you find a security issue in this code (e.g. a prompt injection path that allows the LLM to generate and execute commands, or a hash collision in the audit chain), please:

1. **Do not open a public GitHub issue** for vulnerabilities that could be exploited before a fix is available
2. Email the maintainer directly at the address in the GitHub profile, with the subject line `[Forest CUS] Security Report`
3. Include: what you found, how to reproduce it, and what the potential impact is

You'll receive a response within 7 days. Once a fix is merged you'll be credited in the release notes unless you prefer to remain anonymous.

---

## Known design constraints

| Constraint | Notes |
|---|---|
| `training_chain.json` integrity | SHA-256 per-line hash detects modification but does not prevent it. The file is append-only by convention, not by enforcement. |
| LLM constitution check | `qwen2.5:3b` at temp 0.0 is not a cryptographic guarantee — it is a defense-in-depth layer. Adversarial prompts crafted specifically against this model may bypass it. |
| Local-only isolation | The swarm cycle runs shell commands (`netstat`, `log show`) as the current user. It does not request elevated privileges. |
| No authentication on dashboard | The Streamlit dashboard (`:8501`) binds to localhost by default. Exposing it on a network interface requires your own auth layer. |

---

## Dependency security

Dependencies are pinned to minimum versions in `requirements.txt`. Run a vulnerability scan before deploying:

```bash
pip install pip-audit
pip-audit -r requirements.txt
```
