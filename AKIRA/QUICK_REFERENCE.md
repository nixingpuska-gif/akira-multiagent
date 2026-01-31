# AKIRA Quick Reference

## Essential Commands

### Testing
```bash
# Test all advanced modules
python tests/test_advanced_modules.py

# Test self-modification pipeline
python tests/test_self_mod_pipeline.py
```

### Running
```bash
# Docker
docker-compose up -d

# Local
python app/main.py
```

### System Check
```bash
# Quick diagnostics
python -c "
import asyncio
from core.tools.system_diagnostics import SystemDiagnosticsTool
tool = SystemDiagnosticsTool()
result = asyncio.run(tool.execute({'check_network': True, 'check_tools': True}, None))
print(result.output)
"
```

## Key Files

- `core/agents/self_improver.py` - Self-improvement agent
- `core/agents/voice_agent.py` - Voice processing
- `core/distributed/swarm_controller.py` - Multi-node coordination
- `core/self_mod/self_patching.py` - Autonomous self-repair
- `core/tools/stealth_protocol.py` - Ghost mode
- `core/tools/system_diagnostics.py` - System health
- `core/tools/osint_tools.py` - Intelligence gathering

## Configuration

### Environment Variables
```bash
TELEGRAM_BOT_TOKEN=your_token
OPENAI_API_KEY=your_key
```

### Config Files
- `config/master.yaml` - Master node config
- `config/worker.yaml` - Worker node config

## Troubleshooting

### Tests Failing
```bash
# Check Python version (3.11+ recommended)
python --version

# Reinstall dependencies
pip install -r requirements.txt
```

### Swarm Not Connecting
```bash
# Check network connectivity
ping master_ip

# Verify ports open
netstat -an | grep 8000
```

### Self-Patching Issues
```bash
# Check backup directory
ls .backups/

# View patch history
python -c "
from core.self_mod.self_patching import SelfPatchingEngine
engine = SelfPatchingEngine('.')
print(engine.get_patch_status())
"
```

## Next Steps

1. Run tests to verify installation
2. Configure master node
3. Deploy to worker nodes
4. Monitor swarm status
5. Enable autonomous operations

