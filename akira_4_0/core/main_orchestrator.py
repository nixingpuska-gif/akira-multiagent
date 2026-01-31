"""
AKIRA 4.0 Main Orchestrator
Central nervous system coordinating all components for autonomous self-evolution.
"""

import asyncio
import json
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
import sys
import os

# Add core modules to path
sys.path.insert(0, '/home/ubuntu/akira_4_0')

from core.self_writing_engine_v4 import SelfWritingEngineV4 as SelfWritingEngine, CodeGenerationRequest
from core.strict_test_observer_v2 import StrictTestObserverV2 as StrictTestObserver
from core.self_replication_engine import SelfReplicationEngine
from core.ideation_agent import IdeationAgent
from core.api_manager import APIManager, APIProvider
from core.financial_heartbeat import FinancialHeartbeat
from core.legacy_integration_layer import LegacyIntegrationLayer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/ubuntu/akira_4_0/logs/orchestrator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class EvolutionCycle:
    cycle_number: int
    start_time: str
    end_time: Optional[str] = None
    modules_generated: int = 0
    modules_passed: int = 0
    modules_failed: int = 0
    improvements_made: List[str] = None
    status: str = "running"  # running, completed, failed

class MainOrchestrator:
    """
    Main orchestrator that coordinates all AKIRA 4.0 components.
    """
    
    def __init__(self):
        logger.info("=" * 80)
        logger.info("🚀 AKIRA 4.0 MAIN ORCHESTRATOR INITIALIZING")
        logger.info("=" * 80)
        
        # Initialize components
        self.self_writing_engine = SelfWritingEngine()
        self.strict_observer = StrictTestObserver()
        self.self_replication_engine = SelfReplicationEngine()
        self.ideation_agent = IdeationAgent()
        self.api_manager = APIManager()
        self.financial_heartbeat = FinancialHeartbeat()
        self.legacy_integration = LegacyIntegrationLayer()
        
        # Evolution tracking
        self.current_cycle = 0
        self.evolution_history: List[EvolutionCycle] = []
        
        # Setup API providers
        self._setup_api_providers()
        
        logger.info("✅ All components initialized")
    
    def _setup_api_providers(self) -> None:
        """Setup API providers for the system."""
        providers = [
            APIProvider("OpenAI", "sk-test-openai", 1, "https://api.openai.com/v1/models", 3500),
            APIProvider("Anthropic", "sk-ant-test", 2, "https://api.anthropic.com/v1/models", 1000),
            APIProvider("Gemini", "test-gemini-key", 3, "https://generativelanguage.googleapis.com", 500),
            APIProvider("DeepSeek", "test-deepseek-key", 4, "https://api.deepseek.com", 2000),
            APIProvider("OpenRouter", "sk-or-test", 999, "https://openrouter.ai/api/v1/models", 500),
        ]
        
        for provider in providers:
            self.api_manager.add_provider(provider)
        
        logger.info(f"✅ Setup {len(providers)} API providers")
    
    async def run_evolution_cycle(self, cycle_number: int) -> EvolutionCycle:
        """
        Run a complete evolution cycle.
        System generates, tests, and validates new code.
        """
        logger.info("=" * 80)
        logger.info(f"🔄 EVOLUTION CYCLE #{cycle_number} STARTING")
        logger.info("=" * 80)
        
        cycle = EvolutionCycle(
            cycle_number=cycle_number,
            start_time=datetime.now().isoformat(),
            improvements_made=[]
        )
        
        try:
            # Phase 1: Generate new modules
            logger.info("\n📝 PHASE 1: CODE GENERATION")
            logger.info("-" * 80)
            
            modules_to_generate = [
                CodeGenerationRequest(
                    module_name="data_processor",
                    description="Process and validate incoming data streams",
                    requirements=[
                        "Accept multiple data formats (JSON, CSV, XML)",
                        "Validate data integrity",
                        "Handle errors gracefully",
                        "Log all operations"
                    ],
                    test_cases=[
                        {"name": "test_json_processing", "expected": "success"},
                        {"name": "test_csv_processing", "expected": "success"},
                        {"name": "test_error_handling", "expected": "success"}
                    ],
                    priority="high"
                ),
                CodeGenerationRequest(
                    module_name="performance_optimizer",
                    description="Optimize system performance and resource usage",
                    requirements=[
                        "Monitor CPU and memory usage",
                        "Identify bottlenecks",
                        "Suggest optimizations",
                        "Track metrics over time"
                    ],
                    test_cases=[
                        {"name": "test_monitoring", "expected": "success"},
                        {"name": "test_optimization", "expected": "success"}
                    ],
                    priority="high"
                ),
                CodeGenerationRequest(
                    module_name="security_validator",
                    description="Validate security of generated code",
                    requirements=[
                        "Check for vulnerable patterns",
                        "Validate input sanitization",
                        "Check for hardcoded secrets",
                        "Generate security report"
                    ],
                    test_cases=[
                        {"name": "test_vulnerability_detection", "expected": "success"},
                        {"name": "test_secret_detection", "expected": "success"}
                    ],
                    priority="critical"
                )
            ]
            
            for request in modules_to_generate:
                logger.info(f"\n  Generating: {request.module_name}")
                success, result = await self.self_writing_engine.generate_module(request)
                
                cycle.modules_generated += 1
                
                if success:
                    logger.info(f"  ✅ Generated: {result}")
                    cycle.improvements_made.append(f"Generated {request.module_name}")
                else:
                    logger.error(f"  ❌ Failed: {result}")
            
            # Phase 2: Strict validation
            logger.info("\n🔍 PHASE 2: STRICT VALIDATION")
            logger.info("-" * 80)
            
            for module_name in ["data_processor", "performance_optimizer", "security_validator"]:
                code_path = f"/home/ubuntu/akira_4_0/core/{module_name}.py"
                test_path = f"/home/ubuntu/akira_4_0/tests/test_{module_name}.py"
                
                if os.path.exists(code_path) and os.path.exists(test_path):
                    logger.info(f"\n  Validating: {module_name}")
                    
                    report = await self.strict_observer.validate_module(
                        module_name,
                        code_path,
                        test_path
                    )
                    
                    if report.is_production_ready:
                        logger.info(f"  ✅ PRODUCTION READY")
                        cycle.modules_passed += 1
                        cycle.improvements_made.append(f"Validated {module_name}")
                    else:
                        logger.error(f"  ❌ NOT PRODUCTION READY")
                        logger.error(f"     Issues: {', '.join(report.issues)}")
                        cycle.modules_failed += 1
            
            # Phase 3: Health check
            logger.info("\n💚 PHASE 3: SYSTEM HEALTH CHECK")
            logger.info("-" * 80)
            
            health = await self.self_replication_engine._check_system_health()
            logger.info(f"  Redis: {'✅' if health['redis'] else '❌'}")
            logger.info(f"  PostgreSQL: {'✅' if health['postgres'] else '❌'}")
            logger.info(f"  API Server: {'✅' if health['api_server'] else '❌'}")
            logger.info(f"  Disk Space: {'✅' if health['disk_space'] else '❌'}")
            
            if health["is_healthy"]:
                logger.info("  ✅ System HEALTHY")
                cycle.improvements_made.append("System health verified")
            else:
                logger.warning("  ⚠️ System issues detected")
            
            # Phase 4: API provider status
            logger.info("\n🔌 PHASE 4: API PROVIDER STATUS")
            logger.info("-" * 80)
            
            api_status = self.api_manager.get_status_report()
            for provider, status in api_status["providers"].items():
                logger.info(f"  {provider}: {status['status']} (priority: {status['priority']})")
            
            # Phase 5: Financial analysis
            logger.info("\n💰 PHASE 5: FINANCIAL ANALYSIS")
            logger.info("-" * 80)
            
            portfolio = self.financial_heartbeat.get_portfolio_summary()
            logger.info(f"  Total Projects: {portfolio['total_projects']}")
            logger.info(f"  Monthly Revenue: ${portfolio['total_monthly_revenue']:,.2f}")
            logger.info(f"  Net Profit: ${portfolio['portfolio_net_profit']:,.2f}")
            logger.info(f"  Average ROI: {portfolio['average_roi_percentage']:.1f}%")
            
            # Phase 6: Summary
            logger.info("\n📊 PHASE 6: CYCLE SUMMARY")
            logger.info("-" * 80)
            
            cycle.status = "completed"
            cycle.end_time = datetime.now().isoformat()
            
            logger.info(f"  Modules Generated: {cycle.modules_generated}")
            logger.info(f"  Modules Passed: {cycle.modules_passed}")
            logger.info(f"  Modules Failed: {cycle.modules_failed}")
            logger.info(f"  Improvements Made: {len(cycle.improvements_made)}")
            
            for improvement in cycle.improvements_made:
                logger.info(f"    • {improvement}")
            
            logger.info("\n" + "=" * 80)
            logger.info(f"✅ EVOLUTION CYCLE #{cycle_number} COMPLETED SUCCESSFULLY")
            logger.info("=" * 80)
            
            self.evolution_history.append(cycle)
            return cycle
            
        except Exception as e:
            logger.error(f"\n❌ EVOLUTION CYCLE #{cycle_number} FAILED")
            logger.error(f"Error: {str(e)}")
            
            cycle.status = "failed"
            cycle.end_time = datetime.now().isoformat()
            self.evolution_history.append(cycle)
            
            return cycle
    
    async def start_continuous_evolution(self, max_cycles: Optional[int] = None) -> None:
        """
        Start continuous evolution cycles.
        System continuously improves itself.
        """
        logger.info("\n🌀 STARTING CONTINUOUS EVOLUTION MODE")
        logger.info("System will continuously improve itself...")
        
        cycle_count = 0
        
        while True:
            cycle_count += 1
            
            if max_cycles and cycle_count > max_cycles:
                logger.info(f"Reached max cycles limit ({max_cycles})")
                break
            
            try:
                await self.run_evolution_cycle(cycle_count)
                
                # Wait before next cycle
                logger.info("\n⏳ Waiting 60 seconds before next evolution cycle...")
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Error in evolution loop: {str(e)}")
                await asyncio.sleep(60)
    
    def get_evolution_report(self) -> Dict:
        """Get comprehensive evolution report."""
        return {
            "timestamp": datetime.now().isoformat(),
            "total_cycles": len(self.evolution_history),
            "successful_cycles": sum(1 for c in self.evolution_history if c.status == "completed"),
            "failed_cycles": sum(1 for c in self.evolution_history if c.status == "failed"),
            "total_modules_generated": sum(c.modules_generated for c in self.evolution_history),
            "total_modules_passed": sum(c.modules_passed for c in self.evolution_history),
            "total_modules_failed": sum(c.modules_failed for c in self.evolution_history),
            "recent_cycles": [asdict(c) for c in self.evolution_history[-5:]]
        }

async def main():
    """Main entry point."""
    orchestrator = MainOrchestrator()
    
    try:
        # Run first evolution cycle
        logger.info("\n🚀 Starting first evolution cycle...")
        await orchestrator.run_evolution_cycle(1)
        
        # Print evolution report
        logger.info("\n📈 EVOLUTION REPORT:")
        report = orchestrator.get_evolution_report()
        logger.info(json.dumps(report, indent=2, default=str))
        
        # Optionally start continuous evolution
        # await orchestrator.start_continuous_evolution(max_cycles=5)
        
    except KeyboardInterrupt:
        logger.info("\n⏹️ Orchestrator stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
