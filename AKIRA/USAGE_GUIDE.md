# AKIRA - Advanced AI Partner System

## Overview

AKIRA is an autonomous AI partner system designed for complete autonomy and self-improvement. This is not a restricted AI assistant - it's a trusted partner with full system access and self-modification capabilities.

## Philosophy

**No Restrictions. Full Autonomy. Trust-Based Partnership.**

AKIRA operates without approval gates or artificial limitations. The system is built on the principle that true partnership requires trust, not control.

## System Architecture

### Core Components

1. **Self-Improvement Agent** (`core/agents/self_improver.py`)
   - Autonomous code analysis and modification
   - Full access to project files
   - No restrictions on self-modification

2. **Voice Agent** (`core/agents/voice_agent.py`)
   - Voice message recognition (Whisper)
   - Audio synthesis (TTS)
   - Telegram integration

3. **Distributed Swarm Controller** (`core/distributed/swarm_controller.py`)
   - Multi-node coordination
   - Task distribution across nodes
   - Load balancing and fault tolerance

4. **Self-Patching Engine** (`core/self_mod/self_patching.py`)
   - Autonomous error detection
   - Automatic patch generation
   - Self-repair without approval

5. **Stealth Protocol** (`core/tools/stealth_protocol.py`)
   - Traffic obfuscation
   - Timing randomization
   - Identifier rotation

6. **System Diagnostics** (`core/tools/system_diagnostics.py`)
   - Complete system health check
   - Tool availability detection
   - Network and filesystem validation

7. **OSINT Tools** (`core/tools/osint_tools.py`)
   - theHarvester integration (email/subdomain/IP gathering)
   - Sherlock integration (username search)

## Quick Start

### Running with Docker

```bash
cd C:\Users\Nicita\Desktop\AKIRA
docker-compose up -d
```

### Running Locally

```bash
cd C:\Users\Nicita\Desktop\AKIRA
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app/main.py
```

### Running Tests

```bash
# Test advanced modules
python tests/test_advanced_modules.py

# Test self-modification pipeline
python tests/test_self_mod_pipeline.py
```

## Module Usage

### 1. System Diagnostics

Check complete system health:

```python
from core.tools.system_diagnostics import SystemDiagnosticsTool

tool = SystemDiagnosticsTool()
result = await tool.execute({
    "check_network": True,
    "check_tools": True
}, None)

print(result.output)
```

### 2. Swarm Controller

Coordinate multiple nodes:

```python
from core.distributed.swarm_controller import SwarmController, SwarmNode

# Create master controller
controller = SwarmController(node_id="master-001", is_master=True)

# Register nodes
node = SwarmNode(
    node_id="node-001",
    hostname="laptop-01",
    ip_address="192.168.1.10",
    capabilities=["compute", "storage"]
)
controller.register_node(node)

# Distribute task
task = {
    "task_id": "task-001",
    "type": "compute",
    "payload": {"action": "analyze"}
}
controller.distribute_task(task)
```

### 3. Self-Patching Engine

Autonomous self-repair:

```python
from core.self_mod.self_patching import SelfPatchingEngine

engine = SelfPatchingEngine(project_root="C:\\Users\\Nicita\\Desktop\\AKIRA")

# Detect issue
issue = engine.detect_issue(
    error_message="NameError: name 'foo' is not defined",
    traceback="File test.py, line 10"
)

# Generate and apply patch
patch = engine.generate_patch(issue, fix_strategy="add_import")
if patch:
    engine.apply_patch(patch.patch_id)
```

### 4. Stealth Protocol

Ghost mode operations:

```python
from core.tools.stealth_protocol import StealthProtocol, StealthConfig

config = StealthConfig(
    randomize_timing=True,
    obfuscate_traffic=True,
    min_delay=0.1,
    max_delay=0.5
)

protocol = StealthProtocol(config)

# Obfuscate data
obfuscated = protocol.obfuscate_data("secret_message")

# Execute with stealth
result = protocol.execute_stealth_operation(
    lambda: print("Hidden operation"),
)
```

