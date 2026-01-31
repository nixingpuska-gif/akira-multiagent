# Day 3-4 Tasks - Для Backend Developer 2 и Backend Developer 3

## Day 3 Tasks (Backend Developer 2 - Novu Integration)

---
task_id: task-3.1
title: "Novu Infrastructure Setup"
status: inbox
assigned_to: null
from: product-manager
to: backend-developer-2
language: ru
created_at: 2026-01-22T11:40:00Z
priority: high
module: notifications
dependencies: task-1.1, task-1.2
---

# Task 3.1: Novu Infrastructure Setup

**Assignee**: Backend Developer 2 (GPT)
**Priority**: 🟠 High (needed for Day 3)
**Sprint**: Week 1, Day 3
**Duration**: 4 hours
**Dependencies**: Task 1.1 (PostgreSQL), Task 1.2 (Redis)

## Description
Развернуть Novu notification infrastructure

## Steps
1. Добавить Novu services в docker-compose.yml:
   - novu-api
   - novu-worker
   - novu-web (UI)
2. Start services: `docker-compose up -d novu-api novu-worker novu-web`
3. Open Novu Web UI: http://localhost:3002
4. Create API key в Novu UI
5. Store API key в Vault: `await vault.setSecret('novu_api_key', key)`
6. Verify Novu API responding

## Acceptance Criteria
- ✅ Novu services running
- ✅ Novu Web UI accessible
- ✅ API key created и stored в Vault
- ✅ Health check passes

## Reference
- **ADR**: C:\Users\Nicita\beauty-salon-saas\docs\architecture\ADR-007-notification-infrastructure.md
- **Roadmap**: C:\Users\Nicita\multi-agent-system\.claude\tasks\IMPLEMENTATION-ROADMAP.md (Day 3, Task 3.1)

## Code Location
- `docker-compose.yml` (update)

## Proof of Work (Required)
- Screenshot: Novu Web UI running
- Screenshot: API key в Vault
- Terminal output: `docker-compose ps` showing novu services
- Git commit: "feat: setup Novu infrastructure"

---

---
task_id: task-3.2
title: "Novu SDK Integration"
status: inbox
assigned_to: null
from: product-manager
to: backend-developer-2
language: ru
created_at: 2026-01-22T11:40:00Z
priority: high
module: notifications
dependencies: task-3.1
---

# Task 3.2: Novu SDK Integration

**Assignee**: Backend Developer 2 (GPT)
**Priority**: 🟠 High
**Sprint**: Week 1, Day 3
**Duration**: 4 hours
**Dependencies**: Task 3.1 (Novu running)

## Description
Интегрировать Novu SDK в backend

## Steps
1. Install: `npm install @novu/node`
2. Create `packages/notifications/src/novu-client.ts`
3. Create `packages/notifications/src/notification-service.ts`
4. Implement workflows:
   - `REMINDER_24H`
   - `REMINDER_1H`
   - `CONFIRM_RESCHEDULE`
5. Create notification templates в Novu Web UI (RU/EN)
6. Test sending notification

## Acceptance Criteria
- ✅ Novu SDK integrated
- ✅ NotificationService created
- ✅ 3+ workflow templates created
- ✅ Test notification sent successfully
- ✅ Templates support RU/EN

## Reference
- **ADR**: C:\Users\Nicita\beauty-salon-saas\docs\architecture\ADR-007-notification-infrastructure.md
- **Roadmap**: C:\Users\Nicita\multi-agent-system\.claude\tasks\IMPLEMENTATION-ROADMAP.md (Day 3, Task 3.2)

## Code Location
- `packages/notifications/`

## Proof of Work (Required)
- Screenshot: Workflow templates в Novu UI
- Terminal output: Test notification sent
- Git commit: "feat: integrate Novu SDK"

---

## Day 4 Tasks (Backend Developer 3 - Rate Limiting)

---
task_id: task-4.1
title: "Rate Limiter Package Setup"
status: inbox
assigned_to: null
from: product-manager
to: backend-developer-3
language: ru
created_at: 2026-01-22T11:40:00Z
priority: high
module: rate-limiting
dependencies: task-1.2
---

# Task 4.1: Rate Limiter Package Setup

**Assignee**: Backend Developer 3 (GPT)
**Priority**: 🟠 High (needed for Day 4)
**Sprint**: Week 1, Day 4
**Duration**: 3 hours
**Dependencies**: Task 1.2 (Redis)

## Description
Создать rate limiting package с 3-уровневой системой

## Steps
1. Install: `npm install rate-limiter-flexible`
2. Create `packages/rate-limiting/src/redis.ts`
3. Create `packages/rate-limiting/src/client-limiters.ts` (Level 1)
4. Create `packages/rate-limiting/src/tenant-limiters.ts` (Level 2)
5. Create `packages/rate-limiting/src/channel-limiters.ts` (Level 3)
6. Create `packages/rate-limiting/src/middleware.ts`
7. Write unit tests

## Acceptance Criteria
- ✅ rate-limiter-flexible integrated
- ✅ 3 levels implemented (client, tenant, channel)
- ✅ Middleware created
- ✅ Unit tests pass
- ✅ Redis connection working

## Reference
- **ADR**: C:\Users\Nicita\beauty-salon-saas\docs\architecture\ADR-011-rate-limiting-strategy.md
- **Roadmap**: C:\Users\Nicita\multi-agent-system\.claude\tasks\IMPLEMENTATION-ROADMAP.md (Day 4, Task 4.1)

## Code Location
- `packages/rate-limiting/`

## Proof of Work (Required)
- Terminal output: Unit tests passing
- Screenshot: 3 limiter files created
- Git commit: "feat: setup rate limiting package"

---

---
task_id: task-4.2
title: "Rate Limiting Integration"
status: inbox
assigned_to: null
from: product-manager
to: backend-developer-3
language: ru
created_at: 2026-01-22T11:40:00Z
priority: high
module: rate-limiting
dependencies: task-4.1
---

# Task 4.2: Rate Limiting Integration

**Assignee**: Backend Developer 3 (GPT)
**Priority**: 🟠 High
**Sprint**: Week 1, Day 4
**Duration**: 2 hours
**Dependencies**: Task 4.1 (Rate limiter package)

## Description
Интегрировать rate limiting в API routes и notification service

## Steps
1. Add rate limit middleware в API routes
2. Update NotificationService для использования limiters
3. Test client limit (10 bookings/hour)
4. Test tenant limit (3000 TX msgs/day)
5. Test channel limit (30 msg/s Telegram)

## Acceptance Criteria
- ✅ API routes protected
- ✅ NotificationService uses limiters
- ✅ Client limit enforced
- ✅ Tenant limit enforced
- ✅ Channel limit enforced
- ✅ 429 errors returned correctly

## Reference
- **ADR**: C:\Users\Nicita\beauty-salon-saas\docs\architecture\ADR-011-rate-limiting-strategy.md
- **Roadmap**: C:\Users\Nicita\multi-agent-system\.claude\tasks\IMPLEMENTATION-ROADMAP.md (Day 4, Task 4.2)

## Code Location
- `apps/admin-panel/app/api/`
- `packages/notifications/`

## Proof of Work (Required)
- Screenshot: 429 error when limit exceeded
- Terminal output: Rate limit tests passing
- Git commit: "feat: integrate rate limiting"

---
