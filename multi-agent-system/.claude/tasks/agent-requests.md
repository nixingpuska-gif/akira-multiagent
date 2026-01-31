# Agent Requests - Запросы на Создание Новых Агентов

Только Product Manager может запросить создание нового агента.
Только HR Manager (вы) может создавать новых агентов.

## Формат Запроса

```markdown
## Agent Request
- **Type**: Backend Developer / Frontend Developer
- **Module**: [module-name]
- **Reason**: [why is this agent needed]
- **Requested by**: Product Manager
- **Requested at**: [timestamp]
- **Status**: ✅ created / created
```

---

## Текущие Запросы

## Agent Request #1: Backend Developer 1

- **Type**: Backend Developer (GPT)
- **Module**: Database, API, Infrastructure
- **Specialization**: PostgreSQL/Supabase, Prisma, Redis, Docker, Vault, Stripe
- **Reason**: Week 1 implementation requires database setup (PostgreSQL), Redis, Vault secrets management, and Stripe integration. This is the primary backend developer responsible for core infrastructure.
- **Requested by**: Product Manager
- **Requested at**: 2026-01-22T10:00:00Z
- **Status**: ✅ created
- **Tasks Waiting**: task-1.1 (Database Setup), task-1.2 (Redis Setup), task-1.3 (Monorepo Verification)
- **Priority**: 🔴 Critical (blocks Week 1 Day 1)

**Agent Configuration**:
- Platform: GPT (1M context for code generation)
- Working Directory: `C:\Users\Nicita\beauty-salon-saas\`
- State File: `.claude/agents/backend-developer-1.md`
- Responsibilities:
  - Database setup and management
  - API development
  - Infrastructure (Docker, Docker Compose)
  - Secrets management (Vault)
  - Payment processing (Stripe)

---

## Agent Request #2: Backend Developer 2

- **Type**: Backend Developer (GPT)
- **Module**: Notifications, Analytics, Messaging
- **Specialization**: Novu, Metabase, Chatwoot, Cal.com
- **Reason**: Week 1 Day 3+ requires Novu notification infrastructure. Week 2 requires Metabase analytics. Week 3 requires Chatwoot messaging hub.
- **Requested by**: Product Manager
- **Requested at**: 2026-01-22T10:00:00Z
- **Status**: ✅ created
- **Tasks Waiting**: task-3.1 (Novu Infrastructure), task-3.2 (Novu SDK Integration)
- **Priority**: 🟠 High (needed for Week 1 Day 3)

**Agent Configuration**:
- Platform: GPT (1M context)
- Working Directory: `C:\Users\Nicita\beauty-salon-saas\`
- State File: `.claude/agents/backend-developer-2.md`
- Responsibilities:
  - Notification infrastructure (Novu)
  - Analytics platform (Metabase)
  - Messaging channels (Chatwoot, Telegram, WhatsApp)
  - Calendar integration (Cal.com)

---

## Agent Request #3: Backend Developer 3

- **Type**: Backend Developer (GPT)
- **Module**: Rate Limiting, AI Agents
- **Specialization**: rate-limiter-flexible, CrewAI, LangChain, OpenAI
- **Reason**: Week 1 Day 4 requires rate limiting implementation. Week 3 requires AI agents (CrewAI) for autonomous booking and support.
- **Requested by**: Product Manager
- **Requested at**: 2026-01-22T10:00:00Z
- **Status**: ✅ created
- **Tasks Waiting**: task-4.1 (Rate Limiter Package), task-4.2 (Rate Limiting Integration)
- **Priority**: 🟠 High (needed for Week 1 Day 4)

**Agent Configuration**:
- Platform: GPT (1M context)
- Working Directory: `C:\Users\Nicita\beauty-salon-saas\`
- State File: `.claude/agents/backend-developer-3.md`
- Responsibilities:
  - Rate limiting (3-level system)
  - AI agents development (CrewAI)
  - AI tools implementation
  - Voucher codes generation

---

## Agent Request #4: Frontend Developer

- **Type**: Frontend Developer (GPT)
- **Module**: Admin Panel, Mobile App
- **Specialization**: Next.js, React, TypeScript, React Native, i18next, Stripe Elements
- **Reason**: Week 1 Day 2 requires i18next localization setup. Week 2+ requires payment forms (Stripe Elements), analytics embeds (Metabase), and admin panel UI.
- **Requested by**: Product Manager
- **Requested at**: 2026-01-22T10:00:00Z
- **Status**: ✅ created
- **Tasks Waiting**: task-2.1 (i18next Setup)
- **Priority**: 🟠 High (needed for Week 1 Day 2)

**Agent Configuration**:
- Platform: GPT (1M context)
- Working Directory: `C:\Users\Nicita\beauty-salon-saas\`
- State File: `.claude/agents/frontend-developer.md`
- Responsibilities:
  - Admin panel (Next.js)
  - Mobile app (React Native)
  - Localization (i18next)
  - Payment UI (Stripe Elements)
  - Analytics embeds (Metabase iframes)

---

## Agent Request #5: Validator

- **Type**: Validator (QA/Tester)
- **Module**: Quality Assurance, Architecture Validation, Testing
- **Specialization**: Code review, Architecture validation, Test verification, Documentation review
- **Reason**: ⚠️ **CRITICAL PROTOCOL VIOLATION** - Phase 2 architecture (7 ADRs, architecture.md, IMPLEMENTATION-ROADMAP.md) has NOT been validated before starting implementation. Backend Developer 1 is already working on Day 1 tasks without Validator approval. Per Product Manager protocol: "только Validator может утверждать работу!" We must validate Phase 2 deliverables before continuing any implementation.
- **Requested by**: Product Manager
- **Requested at**: 2026-01-22T10:30:00Z
- **Status**: ✅ completed - Phase 2 APPROVED (11:30)
- **Tasks Waiting**:
  - Validate Phase 2 architecture (7 ADRs)
  - Validate IMPLEMENTATION-ROADMAP.md
  - Validate architecture.md
  - Approve/reject Day 1 task continuation
- **Priority**: 🔴 Critical (blocks ALL implementation - must validate before continuing)

**Agent Configuration**:
- Platform: Claude (preferred for architecture review)
- Working Directory: `C:\Users\Nicita\beauty-salon-saas\`
- State File: `.claude/agents/validator.md`
- Responsibilities:
  - Validate all architecture decisions
  - Review and approve ADRs
  - Test verification (unit, integration, e2e)
  - Code quality checks
  - Documentation completeness review
  - Final approval for task completion

**Immediate Action Required**:
1. Create Validator agent
2. Submit Phase 2 deliverables for validation
3. Pause Backend Developer 1 if validation fails
4. Only continue Day 1 tasks after Validator approval

---

## Agent Request #6: Tech Lead (CTO / Руководитель отдела разработки)

- **Type**: Tech Lead / CTO (Technical Manager)
- **Module**: All Development (Backend, Frontend, Infrastructure, Testing)
- **Specialization**: Team coordination, Technical architecture, Code review, Sprint planning, Developer management
- **Reason**: ⚠️ **CRITICAL OPTIMIZATION** - Product Manager перегружен микроменеджментом 5 агентов (Backend Dev 1-3, Frontend Dev, Tester). PM обрабатывает слишком много технической информации и становится неэффективным. Необходим Tech Lead для управления командой разработки, координации задач, code review, и технических решений. PM будет делегировать технические задачи Tech Lead'у, который затем распределяет работу между разработчиками.
- **Requested by**: Product Manager
- **Requested at**: 2026-01-23T16:30:00Z
- **Status**: ✅ created (READY TO LAUNCH!)
- **Priority**: 🔴 Critical (оптимизация Product Manager workflow)

**Иерархия управления**:
```
Product Manager (Claude)
    ↓
Tech Lead (GPT) ← НОВЫЙ АГЕНТ
    ↓
    ├── Backend Developer 1 (GPT)
    ├── Backend Developer 2 (GPT)
    ├── Backend Developer 3 (GPT)
    ├── Frontend Developer (GPT)
    └── Tester Agent (Claude)
```

**Agent Configuration**:
- Platform: GPT (1M context, нужен для технического контекста)
- Working Directory: `C:\Users\Nicita\beauty-salon-saas\`
- State File: `.claude/agents/tech-lead.md`
- Communication: Product Manager → Tech Lead → Developers (NO direct PM → Developer communication)

**Responsibilities**:
1. **Team Management** (5 агентов):
   - Управление Backend Dev 1-3, Frontend Dev, Tester Agent
   - Распределение задач между разработчиками
   - Координация работы команды
   - Разрешение технических блокеров

2. **Sprint Coordination**:
   - Получает задачи от Product Manager (недельные спринты)
   - Разбивает на подзадачи для каждого разработчика
   - Координирует тестирование (Tester Agent)
   - Отслеживает прогресс команды
   - Отчитывается Product Manager'у о статусе

3. **Code Review & Quality**:
   - Review кода от всех разработчиков
   - Проверка соответствия архитектуре (ADRs)
   - Координация с Tester Agent для тестирования
   - Координация с Validator Agent для финальной проверки
   - Обеспечение code quality standards

4. **Technical Decision Making**:
   - Технические решения на уровне реализации
   - Выбор библиотек и инструментов
   - Оптимизация производительности
   - Архитектурные вопросы (в рамках утверждённых ADRs)

5. **Communication Hub**:
   - Product Manager делегирует Week 1-6 tasks Tech Lead'у
   - Tech Lead распределяет работу между разработчиками
   - Tech Lead координирует тестирование с Tester Agent
   - Tech Lead собирает proof of work от всех агентов
   - Tech Lead отчитывается PM о completion статусе

**Workflow Example**:
```
1. PM: "Tech Lead, начинаем Week 1 Day 2 (i18next + Vault)"
2. Tech Lead: Читает roadmap, создаёт задачи для Frontend Dev + Backend Dev 1
3. Tech Lead: Делегирует задачи разработчикам
4. Разработчики: Выполняют работу, отчитываются Tech Lead'у
5. Tech Lead: Review кода, координирует с Tester Agent для тестирования
6. Tester Agent: Выполняет тесты, отчитывается Tech Lead'у
7. Tech Lead: Собирает proof of work (код + тесты)
8. Tech Lead: "PM, Day 2 complete. Proof: [список файлов, commits, test results]"
9. PM: Отправляет на Validator проверку
```

**Why This Improves Efficiency**:
- ✅ PM фокусируется на стратегии, roadmap, delegation (НЕ на технических деталях)
- ✅ Tech Lead управляет 5 агентами (специализация на техническом менеджменте)
- ✅ Уменьшается context overload для PM (не нужно читать весь код каждого разработчика)
- ✅ Быстрее принятие технических решений (Tech Lead решает без эскалации к PM)
- ✅ Лучшая координация между разработчиками (один point of contact)
- ✅ Координация тестирования встроена в workflow

**Initial Tasks After Creation**:
1. Прочитать IMPLEMENTATION-ROADMAP.md (6-week plan)
2. Прочитать состояние всех агентов:
   - backend-developer-1.md, backend-developer-2.md, backend-developer-3.md
   - frontend-developer.md
   - tester.md
3. Понять текущий статус: Day 1 COMPLETE (awaiting Validator final review)
4. Подготовиться к Week 1 Day 2 tasks (i18next + Vault)
5. После Validator approval Day 1 → начать Day 2 coordination

**Success Criteria**:
- ✅ PM больше не микроменеджит разработчиков
- ✅ PM делегирует только high-level tasks Tech Lead'у
- ✅ Tech Lead координирует команду разработки (5 агентов)
- ✅ Время на decision making уменьшается на 50%+
- ✅ Тестирование интегрировано в dev workflow

**Reporting Format to PM**:
```markdown
## Day X Status Report

**Assigned Tasks**: [список задач от PM]
**Developers**:
- Backend Dev 1: [статус, файлы]
- Backend Dev 2: [статус, файлы]
- Backend Dev 3: [статус, файлы]
- Frontend Dev: [статус, файлы]
**Testing**: [результаты от Tester Agent]
**Status**: ✅ Complete / ⏳ In Progress / ❌ Blocked
**Blockers**: [если есть]
**Ready for Validation**: Yes/No
```

---
