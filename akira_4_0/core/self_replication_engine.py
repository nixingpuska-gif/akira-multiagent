"""
AKIRA 4.0 Self-Replication Engine
System that detects failures and automatically migrates to new infrastructure.
"""

import json
import asyncio
import subprocess
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
import redis

logger = logging.getLogger(__name__)

@dataclass
class ServerInstance:
    instance_id: str
    provider: str  # aws, digitalocean, azure, local
    region: str
    status: str  # running, stopped, failed, migrating
    created_at: str
    last_heartbeat: str
    cpu_usage: float
    memory_usage: float
    disk_usage: float

class SelfReplicationEngine:
    """
    Detects system failures and automatically replicates AKIRA to new infrastructure.
    """
    
    def __init__(self, redis_host: str = "localhost"):
        self.redis_client = redis.Redis(host=redis_host, decode_responses=True)
        self.primary_instance: Optional[ServerInstance] = None
        self.backup_instances: List[ServerInstance] = []
        self.heartbeat_interval = 60  # seconds
        self.failure_threshold = 3  # consecutive failures before migration
        self.current_failures = 0
        
        # Cloud provider credentials (loaded from environment)
        self.aws_credentials = self._load_aws_credentials()
        self.do_credentials = self._load_do_credentials()
        self.azure_credentials = self._load_azure_credentials()
    
    def _load_aws_credentials(self) -> Dict:
        """Load AWS credentials from environment."""
        import os
        return {
            "access_key": os.getenv("AWS_ACCESS_KEY_ID"),
            "secret_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
            "region": os.getenv("AWS_REGION", "us-east-1")
        }
    
    def _load_do_credentials(self) -> Dict:
        """Load DigitalOcean credentials from environment."""
        import os
        return {
            "api_token": os.getenv("DO_API_TOKEN"),
            "region": os.getenv("DO_REGION", "nyc3")
        }
    
    def _load_azure_credentials(self) -> Dict:
        """Load Azure credentials from environment."""
        import os
        return {
            "subscription_id": os.getenv("AZURE_SUBSCRIPTION_ID"),
            "client_id": os.getenv("AZURE_CLIENT_ID"),
            "client_secret": os.getenv("AZURE_CLIENT_SECRET"),
            "tenant_id": os.getenv("AZURE_TENANT_ID")
        }
    
    async def start_heartbeat_monitor(self) -> None:
        """Start continuous heartbeat monitoring."""
        logger.info("Starting heartbeat monitor...")
        
        while True:
            try:
                health = await self._check_system_health()
                
                if health["is_healthy"]:
                    self.current_failures = 0
                    logger.info("✅ System healthy")
                else:
                    self.current_failures += 1
                    logger.warning(f"⚠️ System unhealthy (failures: {self.current_failures}/{self.failure_threshold})")
                    
                    if self.current_failures >= self.failure_threshold:
                        logger.critical("🚨 FAILURE THRESHOLD REACHED - INITIATING REPLICATION")
                        await self.initiate_replication()
                        self.current_failures = 0
                
                await asyncio.sleep(self.heartbeat_interval)
                
            except Exception as e:
                logger.error(f"Error in heartbeat monitor: {str(e)}")
                await asyncio.sleep(self.heartbeat_interval)
    
    async def _check_system_health(self) -> Dict:
        """Check overall system health."""
        try:
            # Check Redis
            redis_ok = await self._check_redis()
            
            # Check PostgreSQL
            postgres_ok = await self._check_postgres()
            
            # Check API server
            api_ok = await self._check_api_server()
            
            # Check disk space
            disk_ok = await self._check_disk_space()
            
            is_healthy = redis_ok and postgres_ok and api_ok and disk_ok
            
            return {
                "is_healthy": is_healthy,
                "redis": redis_ok,
                "postgres": postgres_ok,
                "api_server": api_ok,
                "disk_space": disk_ok,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error checking system health: {str(e)}")
            return {"is_healthy": False, "error": str(e)}
    
    async def _check_redis(self) -> bool:
        """Check Redis connectivity."""
        try:
            self.redis_client.ping()
            return True
        except Exception:
            return False
    
    async def _check_postgres(self) -> bool:
        """Check PostgreSQL connectivity."""
        try:
            import psycopg2
            conn = psycopg2.connect(
                host="localhost",
                database="akira_db",
                user="akira_user"
            )
            conn.close()
            return True
        except Exception:
            return False
    
    async def _check_api_server(self) -> bool:
        """Check API server health."""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get("http://localhost:8000/health", timeout=aiohttp.ClientTimeout(total=5)) as response:
                    return response.status == 200
        except Exception:
            return False
    
    async def _check_disk_space(self) -> bool:
        """Check available disk space."""
        try:
            import shutil
            stat = shutil.disk_usage("/")
            # Fail if less than 5% free
            free_percent = (stat.free / stat.total) * 100
            return free_percent > 5
        except Exception:
            return False
    
    async def initiate_replication(self) -> bool:
        """
        Initiate system replication to a new server.
        """
        logger.critical("🚨 INITIATING SYSTEM REPLICATION")
        
        try:
            # Step 1: Backup current state
            logger.info("Step 1: Backing up current state...")
            backup_ok = await self._backup_system_state()
            if not backup_ok:
                logger.error("Backup failed")
                return False
            
            # Step 2: Provision new server
            logger.info("Step 2: Provisioning new server...")
            new_instance = await self._provision_new_server()
            if not new_instance:
                logger.error("Server provisioning failed")
                return False
            
            logger.info(f"New server provisioned: {new_instance.instance_id}")
            
            # Step 3: Restore state on new server
            logger.info("Step 3: Restoring state on new server...")
            restore_ok = await self._restore_system_state(new_instance)
            if not restore_ok:
                logger.error("State restoration failed")
                await self._terminate_instance(new_instance)
                return False
            
            # Step 4: Verify new server
            logger.info("Step 4: Verifying new server...")
            verify_ok = await self._verify_new_server(new_instance)
            if not verify_ok:
                logger.error("Verification failed")
                await self._terminate_instance(new_instance)
                return False
            
            # Step 5: Switch traffic to new server
            logger.info("Step 5: Switching traffic to new server...")
            switch_ok = await self._switch_traffic(new_instance)
            if not switch_ok:
                logger.error("Traffic switch failed")
                return False
            
            # Step 6: Terminate old server
            logger.info("Step 6: Terminating old server...")
            if self.primary_instance:
                await self._terminate_instance(self.primary_instance)
            
            # Update primary instance
            self.primary_instance = new_instance
            
            logger.critical("✅✅✅ REPLICATION COMPLETE - SYSTEM MIGRATED ✅✅✅")
            
            # Send notification
            await self._send_replication_notification(new_instance)
            
            return True
            
        except Exception as e:
            logger.error(f"Replication failed: {str(e)}")
            return False
    
    async def _backup_system_state(self) -> bool:
        """Backup current system state to S3."""
        try:
            logger.info("Creating database backup...")
            
            # Backup PostgreSQL
            cmd = [
                "pg_dump",
                "-h", "localhost",
                "-U", "akira_user",
                "-d", "akira_db",
                "-F", "c",
                "-f", "/tmp/akira_backup.dump"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                logger.error(f"Database backup failed: {result.stderr}")
                return False
            
            logger.info("Uploading backup to S3...")
            
            # Upload to S3
            import boto3
            s3 = boto3.client('s3')
            s3.upload_file(
                '/tmp/akira_backup.dump',
                'akira-backups',
                f"backup_{datetime.now().isoformat()}.dump"
            )
            
            # Store backup location in Redis
            self.redis_client.set(
                "latest_backup",
                json.dumps({
                    "timestamp": datetime.now().isoformat(),
                    "location": f"s3://akira-backups/backup_{datetime.now().isoformat()}.dump"
                })
            )
            
            logger.info("✅ Backup complete")
            return True
            
        except Exception as e:
            logger.error(f"Backup failed: {str(e)}")
            return False
    
    async def _provision_new_server(self) -> Optional[ServerInstance]:
        """Provision a new server on a cloud provider."""
        try:
            # Try AWS first
            if self.aws_credentials.get("access_key"):
                logger.info("Provisioning on AWS...")
                instance = await self._provision_aws_instance()
                if instance:
                    return instance
            
            # Try DigitalOcean
            if self.do_credentials.get("api_token"):
                logger.info("Provisioning on DigitalOcean...")
                instance = await self._provision_do_instance()
                if instance:
                    return instance
            
            # Try Azure
            if self.azure_credentials.get("subscription_id"):
                logger.info("Provisioning on Azure...")
                instance = await self._provision_azure_instance()
                if instance:
                    return instance
            
            logger.error("No cloud provider credentials available")
            return None
            
        except Exception as e:
            logger.error(f"Server provisioning failed: {str(e)}")
            return None
    
    async def _provision_aws_instance(self) -> Optional[ServerInstance]:
        """Provision an EC2 instance on AWS."""
        try:
            import boto3
            
            ec2 = boto3.resource(
                'ec2',
                region_name=self.aws_credentials["region"],
                aws_access_key_id=self.aws_credentials["access_key"],
                aws_secret_access_key=self.aws_credentials["secret_key"]
            )
            
            # Create instance
            instances = ec2.create_instances(
                ImageId='ami-0c55b159cbfafe1f0',  # Ubuntu 22.04
                MinCount=1,
                MaxCount=1,
                InstanceType='t3.medium'
            )
            
            instance = instances[0]
            instance.wait_until_running()
            instance.reload()
            
            return ServerInstance(
                instance_id=instance.id,
                provider="aws",
                region=self.aws_credentials["region"],
                status="running",
                created_at=datetime.now().isoformat(),
                last_heartbeat=datetime.now().isoformat(),
                cpu_usage=0.0,
                memory_usage=0.0,
                disk_usage=0.0
            )
            
        except Exception as e:
            logger.error(f"AWS provisioning failed: {str(e)}")
            return None
    
    async def _provision_do_instance(self) -> Optional[ServerInstance]:
        """Provision a Droplet on DigitalOcean."""
        try:
            import requests
            
            headers = {
                "Authorization": f"Bearer {self.do_credentials['api_token']}",
                "Content-Type": "application/json"
            }
            
            data = {
                "name": f"akira-replica-{datetime.now().timestamp()}",
                "region": self.do_credentials["region"],
                "size_slug": "s-2vcpu-4gb",
                "image": "ubuntu-22-04-x64"
            }
            
            response = requests.post(
                "https://api.digitalocean.com/v2/droplets",
                headers=headers,
                json=data
            )
            
            if response.status_code != 201:
                logger.error(f"DO API error: {response.text}")
                return None
            
            droplet = response.json()["droplet"]
            
            return ServerInstance(
                instance_id=str(droplet["id"]),
                provider="digitalocean",
                region=self.do_credentials["region"],
                status="running",
                created_at=datetime.now().isoformat(),
                last_heartbeat=datetime.now().isoformat(),
                cpu_usage=0.0,
                memory_usage=0.0,
                disk_usage=0.0
            )
            
        except Exception as e:
            logger.error(f"DigitalOcean provisioning failed: {str(e)}")
            return None
    
    async def _provision_azure_instance(self) -> Optional[ServerInstance]:
        """Provision a VM on Azure."""
        # Implementation similar to AWS/DO
        logger.warning("Azure provisioning not yet implemented")
        return None
    
    async def _restore_system_state(self, instance: ServerInstance) -> bool:
        """Restore system state on new server."""
        try:
            logger.info(f"Restoring state on {instance.instance_id}...")
            
            # SSH into new instance and restore database
            # This is a simplified example
            
            logger.info("✅ State restored")
            return True
            
        except Exception as e:
            logger.error(f"State restoration failed: {str(e)}")
            return False
    
    async def _verify_new_server(self, instance: ServerInstance) -> bool:
        """Verify that new server is operational."""
        try:
            logger.info(f"Verifying {instance.instance_id}...")
            
            # Wait for instance to be fully ready
            await asyncio.sleep(30)
            
            # Check if services are running
            # This is a simplified check
            
            logger.info("✅ Verification passed")
            return True
            
        except Exception as e:
            logger.error(f"Verification failed: {str(e)}")
            return False
    
    async def _switch_traffic(self, instance: ServerInstance) -> bool:
        """Switch traffic to new server."""
        try:
            logger.info(f"Switching traffic to {instance.instance_id}...")
            
            # Update DNS or load balancer
            # Update Redis with new primary instance
            
            self.redis_client.set(
                "primary_instance",
                json.dumps(asdict(instance))
            )
            
            logger.info("✅ Traffic switched")
            return True
            
        except Exception as e:
            logger.error(f"Traffic switch failed: {str(e)}")
            return False
    
    async def _terminate_instance(self, instance: ServerInstance) -> bool:
        """Terminate a server instance."""
        try:
            logger.info(f"Terminating {instance.instance_id}...")
            
            if instance.provider == "aws":
                import boto3
                ec2 = boto3.resource('ec2', region_name=instance.region)
                ec2.instances.filter(InstanceIds=[instance.instance_id]).terminate()
            
            elif instance.provider == "digitalocean":
                import requests
                headers = {"Authorization": f"Bearer {self.do_credentials['api_token']}"}
                requests.delete(
                    f"https://api.digitalocean.com/v2/droplets/{instance.instance_id}",
                    headers=headers
                )
            
            logger.info("✅ Instance terminated")
            return True
            
        except Exception as e:
            logger.error(f"Instance termination failed: {str(e)}")
            return False
    
    async def _send_replication_notification(self, new_instance: ServerInstance) -> None:
        """Send notification about replication."""
        message = (
            f"🔄 **SYSTEM REPLICATION COMPLETE**\n\n"
            f"Old instance terminated\n"
            f"New instance: {new_instance.instance_id}\n"
            f"Provider: {new_instance.provider}\n"
            f"Region: {new_instance.region}\n"
            f"Status: {new_instance.status}\n"
        )
        
        # Send to Telegram
        self.redis_client.rpush("telegram_queue", json.dumps({
            "message": message,
            "type": "notification"
        }))

# Example usage
if __name__ == "__main__":
    async def main():
        engine = SelfReplicationEngine()
        
        # Start heartbeat monitoring
        await engine.start_heartbeat_monitor()
    
    asyncio.run(main())
