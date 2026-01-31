# In Progress - РђРєС‚РёРІРЅС‹Рµ Р—Р°РґР°С‡Рё

Р—Р°РґР°С‡Рё, РЅР°Рґ РєРѕС‚РѕСЂС‹РјРё Р°РіРµРЅС‚С‹ СЃРµР№С‡Р°СЃ СЂР°Р±РѕС‚Р°СЋС‚.

## РџСЂР°РІРёР»Р°

- вљ пёЏ РљР°Р¶РґР°СЏ Р·Р°РґР°С‡Р° assigned to EXACTLY ONE agent
- вљ пёЏ No two agents can work on same files simultaneously
- вљ пёЏ Check this file before starting ANY work
- вљ пёЏ Update file locks when starting/finishing work

---

## РђРєС‚РёРІРЅС‹Рµ Р—Р°РґР°С‡Рё

---
task_id: task-3.1
title: "Novu Infrastructure Setup"
status: in_progress
assigned_to: backend-developer-2
from: tech-lead
started_at: 2026-01-23T22:10:00
priority: critical
module: notifications
dependencies: task-1.1, task-1.2
file_locks:
  - docker-compose.yml
---

# Task 3.1: Novu Infrastructure Setup

**Assignee**: Backend Developer 2 (GPT)  
**Priority**: 🔴 Critical  
**Sprint**: Week 1, Day 3  
**Status**: in_progress  

**Notes**:
- Add Novu services to docker-compose (novu-api, novu-worker, novu-web).
- Start services, open Novu UI, create API key.
- Store API key in Vault.
- Verify Novu API health.

---
task_id: task-3.2
title: "Novu SDK Integration"
status: in_progress
assigned_to: backend-developer-2
from: tech-lead
started_at: 2026-01-23T22:10:00
priority: critical
module: notifications
dependencies: task-3.1
file_locks:
  - packages/notifications/
---

# Task 3.2: Novu SDK Integration

**Assignee**: Backend Developer 2 (GPT)  
**Priority**: 🔴 Critical  
**Sprint**: Week 1, Day 3  
**Status**: in_progress (waiting for Task 3.1)  

**Notes**:
- Integrate @novu/node SDK in packages/notifications.
- Implement workflows: REMINDER_24H, REMINDER_1H, CONFIRM_RESCHEDULE.
- Create templates RU/EN in Novu UI.
- Test sending notification.

---
task_id: task-4.1
title: "Rate Limiter Package Setup"
status: in_progress
assigned_to: backend-developer-3
from: tech-lead
started_at: 2026-01-23T22:10:00
priority: high
module: rate-limiting
dependencies: task-1.2
file_locks:
  - packages/rate-limiting/
---

# Task 4.1: Rate Limiter Package Setup

**Assignee**: Backend Developer 3 (GPT)  
**Priority**: 🟡 High  
**Sprint**: Week 1, Day 4  
**Status**: in_progress  

**Notes**:
- Add rate-limiter-flexible package.
- Implement 3-level limiters + middleware.
- Add unit tests.

---
task_id: task-4.2
title: "Rate Limiting Integration"
status: in_progress
assigned_to: backend-developer-3
from: tech-lead
started_at: 2026-01-23T22:10:00
priority: high
module: rate-limiting
dependencies: task-4.1, task-3.2
file_locks:
  - apps/admin-panel/app/api/
---

# Task 4.2: Rate Limiting Integration

**Assignee**: Backend Developer 3 (GPT)  
**Priority**: 🟡 High  
**Sprint**: Week 1, Day 4  
**Status**: pending Task 4.1 + Task 3.2 (do not touch packages/notifications until Dev2 finishes)  

**Notes**:
- Apply middleware to API routes.
- Integrate limiters into NotificationService (after Task 3.2).
- Verify 429 behavior for client/tenant/channel.
