# Basic-chan (ベーシック・ちゃん)

<p align="center">
  <img src="assets/basic_chan_logo.png" alt="Basic-chan Silhouette Mascot" width="240" />
</p>

```text
            /\_/\
           (     )
          /       \
         /  |   |  \
        (   |___|   )
         \         /
          \_______/
           /     \
          |   |   |
          |   |   |
          |   |   |
         (___|___)
    "Zero daemons, unified sisters, and agent-native execution!"
```

> **Daemonless, agent-native foundational framework for the `-chan` ecosystem.**  
> Standardizes dynamic sister discovery, SQLite WAL memory, immutability shields, scope guards, rich CLIs, and Model Context Protocol (MCP) servers across **Morphē-chan**, **Karyon-chans**, **Sensei-chan**, and **Kunoichi-chan**.

---

## 🌸 Core Subsystems

1. **Dynamic Sister Discovery (Zero Static Lists)**: 4-tier discovery via Python entrypoints (`basic_chan.sisters`), workspace filesystem directory crawling, daemonless SQLite WAL IPC registry, and programmatic registration.
2. **Daemonless Architecture & Memory Vault**: Ephemeral, on-demand execution backed by SQLite WAL mode (`PRAGMA journal_mode=WAL`) and advisory filelocks.
3. **Safety & Guardrails**:
   - `ScopeGuard`: Directory confinement & authorized target network allowlists.
   - `CoreShield`: SHA-256 integrity barrier guarding kernel files against unauthorized mutation.
   - `BehaviorOverrideRegistry`: Safe runtime hooks with guaranteed zero-crash fallback to default logic.
   - `DryRunGuard`: Mutation simulation mode without modifying disk or network state.
4. **Agent Intelligence & Recovery**:
   - `ChanError`: Structured diagnostic error payload with actionable `remedy_hint` for AI agents.
   - `ConfusionTracker`: Autonomy-first failure cycle tracking before escalating to higher tiers.
   - `WorkflowDAG`: Kahn’s algorithm linear-time Directed Acyclic Graph engine for dependency management.
   - `AIGateway`: Multi-model client (Gemini, OpenAI, Claude, Ollama, Mock) with automatic fallback chaining.
5. **Diff-Aware Git Intelligence**: Line-level PR diff parsing (`--diff`), baseline debt suppression (`--baseline`), inline comment pragma parser (`# chan-ignore`), and SARIF 2.1.0 export.
6. **Multi-Format Reporting & Historical Snapshots**: Markdown, standalone offline dark-glassmorphism HTML with embedded Chart.js, and versioned run snapshotting (`.chan_snapshots/`).
7. **Ecosystem Script Standards**: Standardized `install.sh`, `setup.sh`, `start.sh`, and `basic-chan scaffold <name>`.

---

## 🚀 Quick Start

### 1. Installation
```bash
./install.sh
```

### 2. Bootstrap & Self-Verification
```bash
./setup.sh
```

### 3. Interactive Console
```bash
./start.sh
```

### 4. CLI Commands
```bash
# Display health, storage, and discovered sister status
basic-chan status

# Dynamically list all sister chans discovered in environment
basic-chan sisters

# Catalog registered tools & schemas
basic-chan tools
basic-chan tools --compact

# Launch native stdio MCP server for AI coding agents
basic-chan mcp

# Scaffold a new compliant -chan application
basic-chan scaffold Shinobi-chan --slug shinobi-chan
```

---

## 🤝 Building a `-chan` App with `BaseChan`

```python
from basic_chan import BaseChan, ChanIdentity, chan_tool

IDENTITY = ChanIdentity(
    name="Shinobi-chan",
    slug="shinobi-chan",
    japanese_name="忍ちゃん",
    tagline="Precision stealth execution.",
)

class ShinobiChan(BaseChan):
    def initialize(self) -> None:
        pass

    @chan_tool(name="stealth_scan", description="Scan a target silently.")
    def stealth_scan(self, target: str) -> dict:
        self.scope.assert_target_allowed(target)
        return {"status": "ok", "target": target}
```
