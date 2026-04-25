# Atlas Install Chain

Atlas (the CFO Agent) ships through the **unified OASIS AI Agent Factory installer** hosted in [CC90210/CEO-Agent](https://github.com/CC90210/CEO-Agent). The two scripts in this folder are thin shims that preselect `--profile atlas` so users land directly in Atlas's wizard.

## One-Line Install

**macOS / Linux / WSL:**
```bash
curl -sSL https://raw.githubusercontent.com/CC90210/CFO-Agent/main/install/quickstart.sh | bash
```

**Windows (PowerShell):**
```powershell
irm https://raw.githubusercontent.com/CC90210/CFO-Agent/main/install/quickstart.ps1 | iex
```

## What Happens

1. The shim prints "Atlas — fetching unified installer" and forwards to `CEO-Agent/install/quickstart.{sh,ps1}` with `--profile atlas` preselected.
2. The unified installer auto-detects + installs missing prereqs (python ≥3.10, git, node, npm) via Homebrew / apt / dnf / pacman / zypper / winget after one consent prompt.
3. It clones `CC90210/CFO-Agent` into `~/atlas-repo` (or `$ATLAS_REPO_DIR` if set).
4. It launches the wizard at `bravo_cli/wizard.py`. Because `--profile atlas` is preselected, the wizard skips the picker and asks Atlas-specific questions: tax region, base currency, fiscal year start, risk tolerance, trading enable flag, FIRE target, and required keys (Anthropic + optional OpenAI, Telegram, Stripe, Plaid, CCXT).
5. Final step: `bravo doctor` runs to confirm everything is wired.

## Why a Shim Instead of a Forked Installer

The Bravo wizard is **multi-profile aware** — every C-Suite agent (Bravo, Atlas, Maven, Aura, Hermes) is a first-class profile with its own metadata, env-var prefix (`ATLAS_*`), service prompts, and repo target. Forking the install chain per agent would multiply maintenance burden 5x. The shim approach keeps one installer, one wizard, one set of fixes.

## Manual / Non-Interactive

```bash
# Skip consent prompts (CI / scripted installs):
OASIS_AUTO_INSTALL=1 curl -sSL https://raw.githubusercontent.com/CC90210/CFO-Agent/main/install/quickstart.sh | bash

# Custom clone destination:
ATLAS_REPO_DIR=$HOME/cfo-agent BRAVO_REPO_DIR=$HOME/.bravo-launcher \
  curl -sSL https://raw.githubusercontent.com/CC90210/CFO-Agent/main/install/quickstart.sh | bash
```

## Environment Variables

| Var | Purpose |
|-----|---------|
| `OASIS_PROFILE` | Pre-selected profile (set to `atlas` by the shim — override only if you know why) |
| `OASIS_AUTO_INSTALL` | `1` skips consent prompts |
| `OASIS_NO_AUTO_INSTALL` | `1` keeps the old "tell me what's missing" behavior |
| `ATLAS_REPO_DIR` | Where to clone `CFO-Agent` (default: `~/atlas-repo`) |
| `BRAVO_REPO_DIR` | Where to drop the launcher copy of `CEO-Agent` (default: `~/bravo-repo`) |

## Troubleshooting

- **"python3 not found after install"** → open a new terminal so the freshly-installed binary is on PATH, then re-run.
- **"Microsoft Store python.exe stub"** (Windows) → the installer detects + rejects the stub, then installs `Python.Python.3.12` via winget. If you've manually installed Python in a non-standard location, set `OASIS_AUTO_INSTALL=0` and install from python.org first.
- **Failed clone** → the installer retries via atomic swap; the broken directory is preserved at `<repo-dir>.broken.<timestamp>` for inspection.
- **Wizard launches but skips a service you care about** → the profile picker uses `PROFILE_DEFINITIONS` in `bravo_cli/wizard.py`. Re-run with `--profile custom` to get the full menu.
