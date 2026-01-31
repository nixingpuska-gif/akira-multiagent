# Inbox - Новые Задачи

Задачи, которые еще не назначены агентам.

## Формат

```markdown
---
task_id: task-001
title: "Название задачи"
status: inbox
assigned_to: null
from: product-manager
to: [agent-name]
language: ru
created_at: 2025-01-22T00:00:00Z
priority: high|medium|low
module: [module-name]
---

# Task: [Название]

[Полное описание задачи]
```

## Правила

- ✅ Только Product Manager может создавать задачи
- ✅ Каждая задача должна иметь уникальный task_id
- ✅ Обязательно указывать получателя (to: [agent-name])
- ✅ Статус всегда "inbox" пока не назначена

---

## Текущие Задачи

---
task_id: DAY-3-4-KICKOFF
title: "Start Week 1 Day 3–4 (Novu + Rate Limiting)"
status: inbox
assigned_to: null
from: product-manager
to: tech-lead
language: ru
created_at: 2026-01-23T22:10:00Z
priority: critical
module: notifications+rate-limiting
---

# Task: Start Week 1 Day 3–4 (Novu + Rate Limiting)

**Assignee**: DTM / Tech Lead  
**Priority**: 🔴 Critical  
**Sprint**: Week 1, Day 3–4  
**Status**: 📋 Inbox  

## Цель
Запустить параллельно Day 3 и Day 4: Novu (Backend Dev 2) и Rate Limiting (Backend Dev 3).

## Что нужно сделать
1) Создать и делегировать задачи для разработчиков:
   - Task 3.1: Novu Infrastructure (Backend Dev 2)
   - Task 3.2: Novu SDK Integration (Backend Dev 2)
   - Task 4.1: Rate Limiter Package (Backend Dev 3)
   - Task 4.2: Rate Limiting Integration (Backend Dev 3)
2) Проверить зависимости:
   - PostgreSQL + Redis готовы (Day 1)
   - Vault + i18next завершены (Day 2)
3) Обновить:
   - `.claude/tasks/inbox.md` (задачи разработчикам)
   - `.claude/tasks/in-progress.md` (активные задачи)
   - `.claude/context/file-locks.md` (если блокируете файлы)
4) Мониторить прогресс и блокеры. Если критично — эскалировать PM.

## Acceptance Criteria
- ✅ Задачи 3.1, 3.2, 4.1, 4.2 созданы и назначены
- ✅ Задачи переведены в in-progress
- ✅ File locks обновлены при необходимости
- ✅ Есть краткий статус-отчет PM по плану и ETA

## Reference
- Roadmap: `C:\Users\Nicita\multi-agent-system\.claude\tasks\IMPLEMENTATION-ROADMAP.md`
- ADR-007 (Novu): `C:\Users\Nicita\beauty-salon-saas\docs\architecture\ADR-007-notification-infrastructure.md`
- ADR-011 (Rate Limiting): `C:\Users\Nicita\beauty-salon-saas\docs\architecture\ADR-011-rate-limiting-strategy.md`
- Architecture: `C:\Users\Nicita\multi-agent-system\.claude\context\architecture.md`

## Отчетность PM
Короткий отчет в формате:
- Что запущено
- Текущий прогресс
- Блокеры (если есть)
- ETA для передачи на Validator

---
task_id: task-3.1
title: "Novu Infrastructure Setup"
status: inbox
assigned_to: null
from: tech-lead
to: backend-developer-2
language: ru
created_at: 2026-01-23T22:10:00Z
priority: critical
module: notifications
---

# Task 3.1: Novu Infrastructure Setup

**Assignee**: Backend Developer 2 (GPT)
**Priority**: 🔴 Critical
**Sprint**: Week 1, Day 3
**Duration**: 4 hours
**Dependencies**: Task 1.1 (PostgreSQL), Task 1.2 (Redis)

## Description
Развернуть Novu notification infrastructure.

## Steps
1. Добавить Novu services в docker-compose.yml (novu-api, novu-worker, novu-web)
2. Запустить сервисы, открыть UI
3. Создать API key
4. Сохранить ключ в Vault
5. Проверить healthcheck

---
---
task_id: task-3.2
title: "Novu SDK Integration"
status: inbox
assigned_to: null
from: tech-lead
to: backend-developer-2
language: ru
created_at: 2026-01-23T22:10:00Z
priority: critical
module: notifications
---

# Task 3.2: Novu SDK Integration

**Assignee**: Backend Developer 2 (GPT)
**Priority**: 🔴 Critical
**Sprint**: Week 1, Day 3
**Duration**: 4 hours
**Dependencies**: Task 3.1 (Novu running)

## Description
Интеграция Novu SDK и шаблонов уведомлений.

---
---
task_id: task-4.1
title: "Rate Limiter Package Setup"
status: inbox
assigned_to: null
from: tech-lead
to: backend-developer-3
language: ru
created_at: 2026-01-23T22:10:00Z
priority: high
module: rate-limiting
---

# Task 4.1: Rate Limiter Package Setup

**Assignee**: Backend Developer 3 (GPT)
**Priority**: 🟡 High
**Sprint**: Week 1, Day 4
**Duration**: 3 hours
**Dependencies**: Task 1.2 (Redis)

## Description
Создать пакет rate-limiting с 3-уровневой системой лимитов.

---
---
task_id: task-4.2
title: "Rate Limiting Integration"
status: inbox
assigned_to: null
from: tech-lead
to: backend-developer-3
language: ru
created_at: 2026-01-23T22:10:00Z
priority: high
module: rate-limiting
---

# Task 4.2: Rate Limiting Integration

**Assignee**: Backend Developer 3 (GPT)
**Priority**: 🟡 High
**Sprint**: Week 1, Day 4
**Duration**: 2 hours
**Dependencies**: Task 4.1 + Task 3.2

## Description
Интегрировать rate limiting в API routes и NotificationService.
