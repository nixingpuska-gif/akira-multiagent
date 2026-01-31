# AKIRA 4.0 - Autonomous Kernel for Intelligent Request Automation

**Version:** 4.0.0  
**Status:** ✅ Production Ready  
**Self-Generation:** ✅ Enabled  
**Self-Replication:** ✅ Enabled  

## 🚀 Quick Start

### Docker (Recommended)
```bash
docker-compose up -d
```

### Linux/macOS
```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m akira_4_0.core.main_orchestrator
```

### Windows
```bash
run_akira.bat
```

## 📁 Project Structure

```
akira_4_0/
├── core/                          # Core system modules
│   ├── main_orchestrator.py       # Main system controller
│   ├── self_writing_engine_v4.py  # Code generation engine
│   ├── strict_test_observer_v2.py # Code validation system
│   ├── self_replication_engine.py # Auto-migration system
│   ├── legacy_integration_layer.py # Protocol Omega, Ghost Mode, etc.
│   ├── self_generation_api.py     # Self-generation API
│   ├── api_manager.py             # API provider management
│   ├── ideation_agent.py          # Idea discussion agent
│   ├── key_manager.py             # API key management
│   ├── health_check.py            # System health monitoring
│   └── financial_heartbeat.py     # Profitability tracking
├── telegram_client/               # Telegram integration
│   └── stealth_client.py          # Session-based Telegram client
├── docker/                        # Docker configuration
│   ├── Dockerfile
│   └── docker-compose.yml
├── windows/                       # Windows scripts
│   ├── run_akira.bat
│   └── run_akira.ps1
├── gui/                           # GUI configuration
│   └── config.json
├── telegram/                      # Telegram configuration
│   └── config.json
├── tests/                         # Test suite
│   ├── test_data_processor.py
│   ├── test_performance_optimizer.py
│   └── test_security_validator.py
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## 🔧 Core Components

### 1. Self-Writing Engine v4
Generates production-ready Python code with pytest-compatible tests.

### 2. Strict Test Observer v2
Validates generated code with 7-step validation process:
- Syntax validation
- Import verification
- Code quality analysis
- Unit test execution
- Integration testing
- Performance testing
- Security analysis

### 3. Self-Replication Engine
Automatic failover and migration to new servers when primary fails.

### 4. Legacy Integration Layer
Integrates all AKIRA 3.0 advanced features:
- Protocol Omega (LLM filter bypass)
- Brainfuck obfuscator
- Ghost Mode (IP rotation)
- Stealth communication
- Self-defense system

### 5. Self-Generation API
Generates deployment components through API:
- Docker configurations
- Windows support scripts
- GUI specifications
- Telegram integration
- Deployment manifests

## 🔑 Configuration

Create `.env` file with:

```env
# API Keys
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
GEMINI_API_KEY=your_key
DEEPSEEK_API_KEY=your_key
OPENROUTER_API_KEY=your_key

# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=akira_db
POSTGRES_USER=akira
POSTGRES_PASSWORD=your_password

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# System
AKIRA_MODE=production
LOG_LEVEL=INFO
```

## 📊 System Capabilities

✅ **Self-Writing:** Generates and improves its own code  
✅ **Self-Testing:** Validates all generated code  
✅ **Self-Healing:** Automatically fixes broken code  
✅ **Self-Replicating:** Migrates to new servers on failure  
✅ **Self-Generating:** Creates deployment configurations  
✅ **Self-Improving:** Learns from each execution cycle  

## 🎯 Evolution Cycle

1. **CODE GENERATION** - System generates new modules
2. **STRICT VALIDATION** - Observer validates each module
3. **SYSTEM HEALTH CHECK** - Monitors Redis, PostgreSQL, API
4. **API PROVIDER STATUS** - Checks all provider health
5. **FINANCIAL ANALYSIS** - Analyzes profitability
6. **CYCLE SUMMARY** - Reports improvements

## 📈 Performance

- **Code Generation:** ~2 seconds per module
- **Validation:** ~1 second per module
- **Test Execution:** ~3 seconds per module
- **Total Cycle:** ~8 seconds for 3 modules
- **Pass Rate:** 100% (19/19 tests)

## 🔒 Security Features

- AES-256 encryption for Telegram
- No hardcoded secrets
- Environment variable configuration
- Rate limiting
- Command validation
- Automatic security scanning

## 📱 Interfaces

- **Web GUI:** http://localhost:3000
- **REST API:** http://localhost:8000
- **WebSocket:** ws://localhost:8001
- **Telegram:** Session-based (no bot limitations)

## 🐛 Troubleshooting

See `AKIRA_4_0_INSTALLATION_GUIDE.md` for detailed troubleshooting.

## 📚 Documentation

- `AKIRA_4_0_INSTALLATION_GUIDE.md` - Complete installation guide
- `AKIRA_4_0_Complete_Blueprint.md` - System architecture
- `AKIRA_4_0_Comprehensive_Test_Report.md` - Test results
- `AKIRA_4_0_Self_Generated_Deployment_Report.md` - Self-generation report

## 🤝 Support

- GitHub Issues: Report bugs
- Telegram: @akira_support
- Email: support@akira.ai

## 📄 License

MIT License - See LICENSE file

---

**AKIRA 4.0 - Self-Generating, Self-Deploying, Self-Improving**

🦾💀🚀🔥
