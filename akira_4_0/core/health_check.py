"""
AKIRA 4.0 Health Check System
Comprehensive monitoring of all system components with real-time metrics.
"""

import asyncio
import json
import time
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import logging
import psutil
import redis
import aiohttp

logger = logging.getLogger(__name__)

class ComponentStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    OFFLINE = "offline"

@dataclass
class HealthMetric:
    component: str
    status: ComponentStatus
    response_time: float
    timestamp: str
    error_message: Optional[str] = None
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    disk_usage: Optional[float] = None

class HealthCheckSystem:
    """
    Comprehensive health monitoring for all AKIRA components.
    """
    
    def __init__(self, redis_host: str = "localhost", redis_port: int = 6379):
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        self.check_interval = 300  # 5 minutes
        self.metrics_history: Dict[str, List[HealthMetric]] = {}
        self.alert_thresholds = {
            "response_time": 5.0,  # seconds
            "cpu_usage": 80.0,  # percent
            "memory_usage": 85.0,  # percent
            "disk_usage": 90.0  # percent
        }
        
        # Component endpoints
        self.components = {
            "api_manager": "http://localhost:8000/health",
            "postgres": "postgresql://akira_user:password@localhost:5432/akira_db",
            "redis": "redis://localhost:6379",
            "telegram": "local",  # No external check
            "gui": "http://localhost:3000/health"
        }
    
    async def run_health_checks(self) -> Dict[str, HealthMetric]:
        """
        Run health checks on all components.
        Returns a dictionary of component health metrics.
        """
        logger.info("Starting comprehensive health check...")
        
        results = {}
        
        # Check each component
        for component_name, endpoint in self.components.items():
            try:
                metric = await self._check_component(component_name, endpoint)
                results[component_name] = metric
                
                # Store in history
                if component_name not in self.metrics_history:
                    self.metrics_history[component_name] = []
                self.metrics_history[component_name].append(metric)
                
                # Keep only last 100 metrics per component
                if len(self.metrics_history[component_name]) > 100:
                    self.metrics_history[component_name].pop(0)
                
                # Store in Redis
                self.redis_client.hset(
                    f"health_metrics:{component_name}",
                    "latest",
                    json.dumps(asdict(metric), default=str)
                )
                
            except Exception as e:
                logger.error(f"Error checking {component_name}: {str(e)}")
                results[component_name] = HealthMetric(
                    component=component_name,
                    status=ComponentStatus.OFFLINE,
                    response_time=0,
                    timestamp=datetime.now().isoformat(),
                    error_message=str(e)
                )
        
        # Check system resources
        system_metrics = await self._check_system_resources()
        results["system"] = system_metrics
        
        # Evaluate overall health
        overall_status = self._evaluate_overall_health(results)
        results["overall"] = overall_status
        
        # Check for alerts
        await self._check_and_trigger_alerts(results)
        
        logger.info(f"Health check completed. Overall status: {overall_status.status.value}")
        
        return results
    
    async def _check_component(self, component_name: str, endpoint: str) -> HealthMetric:
        """
        Check the health of a specific component.
        """
        start_time = time.time()
        
        try:
            if component_name == "postgres":
                status = await self._check_postgres(endpoint)
            elif component_name == "redis":
                status = await self._check_redis(endpoint)
            elif component_name == "telegram":
                status = ComponentStatus.HEALTHY  # Assume healthy if not explicitly checked
            else:
                status = await self._check_http_endpoint(endpoint)
            
            response_time = time.time() - start_time
            
            # Determine status based on response time
            if response_time > self.alert_thresholds["response_time"]:
                status = ComponentStatus.DEGRADED
            
            return HealthMetric(
                component=component_name,
                status=status,
                response_time=response_time,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            return HealthMetric(
                component=component_name,
                status=ComponentStatus.OFFLINE,
                response_time=response_time,
                timestamp=datetime.now().isoformat(),
                error_message=str(e)
            )
    
    async def _check_http_endpoint(self, endpoint: str) -> ComponentStatus:
        """Check HTTP endpoint."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        return ComponentStatus.HEALTHY
                    elif response.status < 500:
                        return ComponentStatus.DEGRADED
                    else:
                        return ComponentStatus.CRITICAL
        except asyncio.TimeoutError:
            return ComponentStatus.DEGRADED
        except Exception:
            return ComponentStatus.OFFLINE
    
    async def _check_postgres(self, connection_string: str) -> ComponentStatus:
        """Check PostgreSQL connection."""
        try:
            import psycopg2
            conn = psycopg2.connect(connection_string)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            conn.close()
            return ComponentStatus.HEALTHY
        except Exception:
            return ComponentStatus.OFFLINE
    
    async def _check_redis(self, connection_string: str) -> ComponentStatus:
        """Check Redis connection."""
        try:
            client = redis.from_url(connection_string)
            client.ping()
            return ComponentStatus.HEALTHY
        except Exception:
            return ComponentStatus.OFFLINE
    
    async def _check_system_resources(self) -> HealthMetric:
        """Check system CPU, memory, and disk usage."""
        try:
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Determine status based on thresholds
            if (cpu_usage > self.alert_thresholds["cpu_usage"] or
                memory.percent > self.alert_thresholds["memory_usage"] or
                disk.percent > self.alert_thresholds["disk_usage"]):
                status = ComponentStatus.DEGRADED
            else:
                status = ComponentStatus.HEALTHY
            
            return HealthMetric(
                component="system",
                status=status,
                response_time=0,
                timestamp=datetime.now().isoformat(),
                cpu_usage=cpu_usage,
                memory_usage=memory.percent,
                disk_usage=disk.percent
            )
            
        except Exception as e:
            logger.error(f"Error checking system resources: {str(e)}")
            return HealthMetric(
                component="system",
                status=ComponentStatus.UNKNOWN,
                response_time=0,
                timestamp=datetime.now().isoformat(),
                error_message=str(e)
            )
    
    def _evaluate_overall_health(self, results: Dict[str, HealthMetric]) -> HealthMetric:
        """Evaluate overall system health based on component metrics."""
        critical_count = sum(1 for m in results.values() if m.status == ComponentStatus.CRITICAL)
        offline_count = sum(1 for m in results.values() if m.status == ComponentStatus.OFFLINE)
        degraded_count = sum(1 for m in results.values() if m.status == ComponentStatus.DEGRADED)
        
        if critical_count > 0 or offline_count > 2:
            overall_status = ComponentStatus.CRITICAL
        elif degraded_count > 2:
            overall_status = ComponentStatus.DEGRADED
        else:
            overall_status = ComponentStatus.HEALTHY
        
        return HealthMetric(
            component="overall",
            status=overall_status,
            response_time=0,
            timestamp=datetime.now().isoformat()
        )
    
    async def _check_and_trigger_alerts(self, results: Dict[str, HealthMetric]) -> None:
        """Check for alert conditions and trigger notifications."""
        alerts = []
        
        for component_name, metric in results.items():
            if metric.status == ComponentStatus.CRITICAL:
                alerts.append(f"🚨 CRITICAL: {component_name} is offline!")
            elif metric.status == ComponentStatus.DEGRADED:
                alerts.append(f"⚠️ DEGRADED: {component_name} is degraded (response time: {metric.response_time:.2f}s)")
            
            # Check resource thresholds
            if metric.cpu_usage and metric.cpu_usage > self.alert_thresholds["cpu_usage"]:
                alerts.append(f"⚠️ HIGH CPU: {metric.cpu_usage:.1f}%")
            if metric.memory_usage and metric.memory_usage > self.alert_thresholds["memory_usage"]:
                alerts.append(f"⚠️ HIGH MEMORY: {metric.memory_usage:.1f}%")
            if metric.disk_usage and metric.disk_usage > self.alert_thresholds["disk_usage"]:
                alerts.append(f"⚠️ HIGH DISK: {metric.disk_usage:.1f}%")
        
        if alerts:
            logger.warning(f"Health alerts: {', '.join(alerts)}")
            # Store alerts in Redis for Telegram client to pick up
            for alert in alerts:
                self.redis_client.rpush("health_alerts", json.dumps({
                    "timestamp": datetime.now().isoformat(),
                    "alert": alert
                }))
    
    def get_health_report(self) -> Dict:
        """Generate a comprehensive health report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "components": {},
            "history": {}
        }
        
        # Add latest metrics
        for component_name, metrics in self.metrics_history.items():
            if metrics:
                latest = metrics[-1]
                report["components"][component_name] = asdict(latest)
                
                # Add trend (last 10 metrics)
                recent_metrics = metrics[-10:]
                report["history"][component_name] = [asdict(m) for m in recent_metrics]
        
        return report
    
    async def start_continuous_monitoring(self) -> None:
        """Start continuous health monitoring loop."""
        logger.info("Starting continuous health monitoring...")
        
        while True:
            try:
                await self.run_health_checks()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in health check loop: {str(e)}")
                await asyncio.sleep(60)

# Example usage
if __name__ == "__main__":
    async def main():
        health_system = HealthCheckSystem()
        
        # Run a single health check
        results = await health_system.run_health_checks()
        
        print("Health Check Results:")
        for component, metric in results.items():
            print(f"  {component}: {metric.status.value} ({metric.response_time:.2f}s)")
        
        # Get full report
        report = health_system.get_health_report()
        print("\nHealth Report:")
        print(json.dumps(report, indent=2, default=str))
    
    asyncio.run(main())
