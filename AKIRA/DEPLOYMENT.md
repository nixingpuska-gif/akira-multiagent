# AKIRA Deployment Guide

## Distributed Deployment

### Architecture Overview

```
Master Node (Main Server)
    |
    +-- Worker Node 1 (Laptop)
    +-- Worker Node 2 (Laptop)
    +-- Worker Node 3 (Server)
    +-- ... (up to 50 nodes)
```

## Node Setup

### Master Node Setup

1. Install AKIRA on main server:
```bash
git clone <repo> /opt/akira
cd /opt/akira
docker-compose up -d
```

2. Configure as master:
```python
# config/master.yaml
node:
  id: "master-001"
  role: "master"
  ip: "192.168.1.100"
  port: 8000
```

### Worker Node Setup

1. Install on each laptop/server:
```bash
git clone <repo> /home/user/akira
cd /home/user/akira
```

2. Configure as worker:
```python
# config/worker.yaml
node:
  id: "worker-001"
  role: "worker"
  master_ip: "192.168.1.100"
  master_port: 8000
  capabilities: ["compute", "storage", "network"]
```

3. Start worker:
```bash
python app/worker.py
```

## Network Configuration

### Required Ports

- 8000: Main API/Web UI
- 8001: Swarm coordination
- 8002: Node heartbeat

### Firewall Rules

```bash
# Allow swarm communication
ufw allow 8000:8002/tcp
```

## Monitoring

### Check Swarm Status

```bash
curl http://192.168.1.100:8000/swarm/status
```

### View Node Health

```bash
python -c "
from core.distributed.swarm_controller import SwarmController
controller = SwarmController.load_from_config()
print(controller.get_swarm_status())
"
```

## Scaling

### Adding New Nodes

1. Prepare new machine
2. Install AKIRA
3. Configure as worker
4. Node auto-registers with master

### Removing Nodes

```python
controller.unregister_node("worker-005")
```

## Backup Strategy

- Automatic backups in `.backups/` directory
- Self-patching creates backups before modifications
- Distributed state replication across nodes

