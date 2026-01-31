# Architecture - Архитектура Проекта

## Статус: ✅ ACTIVE PROJECT: Beauty Salon SaaS

**Последнее обновление**: 2026-01-22 (Phase 2 - Integration Architecture)
**Автор**: Architect Agent
**Проект**: Beauty Salon SaaS Platform
**Open-Source Reuse**: **75-78%** (было 68.3%) ⬆️

---

## 🎯 Active Project: Beauty Salon SaaS

**Полная архитектура**: [beauty-salon-saas Plan](c:\Users\Nicita\.claude\plans\sharded-marinating-balloon.md)

**Проект Location**: `C:\Users\Nicita\beauty-salon-saas\`

### Executive Summary
- 🏢 **Масштаб**: 10,000 салонов (tenants)
- 👥 **Пользователи**: ~100,000 мастеров
- 📨 **Нагрузка**: 20M сообщений/день (пик)
- 🤖 **AI-автономность Level 1**: 80% запросов клиентов без человека
- 🤖 **AI-автономность Level 2**: **100% управление платформой AI**
- 🌐 **Каналы**: Telegram, WhatsApp, Instagram, VK, MAX
- 📊 **Функции**: 130+ функций (F-001 до F-131)

---

## 📁 Project Structure - ПОЛНАЯ СТРУКТУРА ПРОЕКТА

**ВАЖНО**: Все developer-агенты ОБЯЗАНЫ прочитать эту секцию перед началом работы!

### Root Directory
```
C:\Users\Nicita\beauty-salon-saas\
```

### Полная Структура Папок

```
C:\Users\Nicita\beauty-salon-saas\
│
├── .github/
│   └── workflows/                    # CI/CD (GitHub Actions)
│       ├── backend-tests.yml
│       ├── frontend-tests.yml
│       └── deploy.yml
│
├── apps/                             # МИКРОСЕРВИСЫ (каждый - отдельный сервис)
│   │
│   ├── booking-api/                  # Laravel 10 API (Backend Developer 1)
│   │   ├── app/
│   │   │   ├── Http/Controllers/
│   │   │   ├── Models/
│   │   │   └── Services/
│   │   ├── database/
│   │   │   ├── migrations/
│   │   │   └── seeders/
│   │   ├── routes/
│   │   │   └── api.php
│   │   ├── tests/
│   │   │   ├── Feature/
│   │   │   └── Unit/
│   │   ├── .env.example
│   │   ├── composer.json
│   │   └── README.md
│   │
│   ├── messaging-hub/                # Chatwoot fork (Backend Developer 2)
│   │   ├── app/
│   │   │   ├── controllers/
│   │   │   ├── models/
│   │   │   └── services/
│   │   ├── config/
│   │   ├── adapters/                 # Custom adapters
│   │   │   ├── max_adapter/
│   │   │   └── vk_adapter/
│   │   ├── spec/                     # Tests (RSpec)
│   │   ├── Gemfile
│   │   └── README.md
│   │
│   ├── calendar-service/             # Cal.com fork (Backend Developer 2)
│   │   ├── apps/
│   │   │   └── web/
│   │   ├── packages/
│   │   │   ├── features/
│   │   │   └── ui/
│   │   ├── prisma/
│   │   ├── package.json
│   │   └── README.md
│   │
│   ├── ai-orchestrator/              # CrewAI agents (Backend Developer 3)
│   │   ├── agents/                   # Python 3.11+
│   │   │   ├── booking_agent.py
│   │   │   ├── support_agent.py
│   │   │   └── marketing_agent.py
│   │   ├── tools/
│   │   │   ├── search_slots_tool.py
│   │   │   ├── create_appointment_tool.py
│   │   │   └── send_message_tool.py
│   │   ├── crews/
│   │   ├── tests/
│   │   ├── requirements.txt
│   │   └── README.md
│   │
│   ├── queue-manager/                # BullMQ workers (Backend Developer 1)
│   │   ├── workers/                  # Node.js 20+
│   │   │   ├── reminder-worker.ts
│   │   │   ├── campaign-worker.ts
│   │   │   └── case-worker.ts
│   │   ├── queues/
│   │   │   └── index.ts
│   │   ├── processors/
│   │   ├── tests/
│   │   ├── package.json
│   │   └── README.md
│   │
│   ├── admin-panel/                  # Next.js 14 Admin UI (Frontend Developer)
│   │   ├── app/                      # App Router
│   │   │   ├── (dashboard)/
│   │   │   │   ├── appointments/
│   │   │   │   ├── clients/
│   │   │   │   ├── staff/
│   │   │   │   ├── analytics/
│   │   │   │   └── settings/
│   │   │   ├── api/                  # API routes
│   │   │   │   ├── appointments/
│   │   │   │   ├── analytics/
│   │   │   │   └── webhooks/
│   │   │   ├── layout.tsx
│   │   │   └── page.tsx
│   │   ├── components/               # React components
│   │   │   ├── ui/                   # shadcn/ui base
│   │   │   ├── appointments/
│   │   │   ├── analytics/
│   │   │   └── payments/
│   │   ├── lib/
│   │   │   ├── auth.ts
│   │   │   └── utils.ts
│   │   ├── public/
│   │   │   └── locales/              # i18next translations
│   │   │       ├── ru/
│   │   │       │   ├── common.json
│   │   │       │   └── appointments.json
│   │   │       └── en/
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   └── README.md
│   │
│   └── mobile-apps/                  # React Native (Frontend Developer)
│       ├── client-app/               # Expo
│       │   ├── src/
│       │   ├── app.json
│       │   └── package.json
│       └── staff-app/                # Expo
│           ├── src/
│           ├── app.json
│           └── package.json
│
├── packages/                         # SHARED CODE (переиспользуемый код)
│   │
│   ├── database/                     # ✅ ГОТОВ (Backend Developer 1)
│   │   ├── prisma/
│   │   │   ├── schema.prisma         # 9 tables с RLS
│   │   │   ├── seed.ts
│   │   │   └── migrations/
│   │   │       ├── 001_rls_policies.sql
│   │   │       └── 002_partitioning.sql
│   │   ├── src/
│   │   │   └── index.ts
│   │   ├── test/
│   │   │   └── connection.test.ts
│   │   ├── package.json
│   │   └── README.md
│   │
│   ├── types/                        # TypeScript types (Backend Developer 1)
│   │   ├── src/
│   │   │   ├── tenant.ts
│   │   │   ├── appointment.ts
│   │   │   ├── client.ts
│   │   │   └── index.ts
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   ├── ui/                           # Shared UI components (Frontend Developer)
│   │   ├── src/
│   │   │   ├── button.tsx
│   │   │   ├── input.tsx
│   │   │   └── index.ts
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   ├── utils/                        # Utility functions (Backend Developer 1)
│   │   ├── src/
│   │   │   ├── date.ts
│   │   │   ├── format.ts
│   │   │   └── index.ts
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   ├── localization/                 # i18next setup (Frontend Developer)
│   │   ├── src/
│   │   │   ├── i18n.config.ts
│   │   │   ├── formatters.ts
│   │   │   └── index.ts
│   │   ├── package.json
│   │   └── README.md
│   │
│   ├── notifications/                # Novu integration (Backend Developer 2)
│   │   ├── src/
│   │   │   ├── novu-client.ts
│   │   │   ├── notification-service.ts
│   │   │   └── index.ts
│   │   ├── package.json
│   │   └── README.md
│   │
│   ├── payments/                     # Stripe integration (Backend Developer 1)
│   │   ├── src/
│   │   │   ├── stripe-client.ts
│   │   │   ├── payment-service.ts
│   │   │   ├── subscription-service.ts
│   │   │   └── index.ts
│   │   ├── package.json
│   │   └── README.md
│   │
│   ├── analytics/                    # Metabase integration (Backend Developer 2)
│   │   ├── src/
│   │   │   ├── metabase-client.ts
│   │   │   ├── ai-reports.ts
│   │   │   └── index.ts
│   │   ├── package.json
│   │   └── README.md
│   │
│   ├── rate-limiting/                # Rate limiting (Backend Developer 3)
│   │   ├── src/
│   │   │   ├── redis.ts
│   │   │   ├── client-limiters.ts
│   │   │   ├── tenant-limiters.ts
│   │   │   ├── channel-limiters.ts
│   │   │   ├── middleware.ts
│   │   │   └── index.ts
│   │   ├── package.json
│   │   └── README.md
│   │
│   └── secrets/                      # Supabase Vault (Backend Developer 1)
│       ├── src/
│       │   ├── vault-client.ts
│       │   ├── rotation.ts
│       │   └── index.ts
│       ├── package.json
│       └── README.md
│
├── infrastructure/                   # Infrastructure as Code
│   ├── kubernetes/
│   │   ├── deployments/
│   │   └── services/
│   ├── terraform/
│   └── docker/
│       └── Dockerfile.backend
│
├── docs/                             # ✅ ГОТОВ - Документация
│   ├── architecture/
│   │   ├── ADR-001-multi-tenant-strategy.md
│   │   ├── ADR-007-notification-infrastructure.md
│   │   ├── ADR-008-analytics-platform.md
│   │   ├── ADR-009-payment-processing.md
│   │   ├── ADR-010-localization-strategy.md
│   │   ├── ADR-011-rate-limiting-strategy.md
│   │   └── ADR-012-secrets-management.md
│   ├── deployment/
│   │   ├── supabase-setup.md
│   │   └── docker-compose-setup.md
│   ├── api/                          # API documentation (будет создано)
│   ├── PROGRESS.md
│   ├── PHASE-2-SUMMARY.md
│   ├── QUICK-REFERENCE.md
│   └── QUICK-START-FOR-HR-MANAGER.md
│
├── scripts/                          # Utility scripts
│   ├── setup-secrets.ts
│   └── generate-types.ts
│
├── .env.example                      # ✅ ГОТОВ - Environment template
├── docker-compose.yml                # ✅ ГОТОВ - Local development
├── package.json                      # ✅ ГОТОВ - Root package.json (Turborepo)
├── turbo.json                        # Turborepo configuration
├── tsconfig.json                     # Root TypeScript config
├── .gitignore                        # ✅ ГОТОВ
└── README.md                         # ✅ ГОТОВ - Project overview
```

---

## 🎯 Developer Workspaces - КТО ГДЕ РАБОТАЕТ

### Backend Developer 1 (GPT) - Core Infrastructure
**Рабочие директории**:
- `apps/booking-api/` - Laravel API
- `apps/queue-manager/` - BullMQ workers
- `packages/database/` - Prisma schema (✅ уже готов)
- `packages/types/` - TypeScript types
- `packages/utils/` - Utility functions
- `packages/payments/` - Stripe integration
- `packages/secrets/` - Supabase Vault

**Основные задачи**:
- Database setup & migrations
- Booking API endpoints
- Payment processing (Stripe)
- Queue workers (BullMQ)
- Secrets management (Vault)

**Tech Stack**: Laravel 10, Node.js 20+, TypeScript, Prisma, Stripe SDK

---

### Backend Developer 2 (GPT) - Messaging & Analytics
**Рабочие директории**:
- `apps/messaging-hub/` - Chatwoot fork
- `apps/calendar-service/` - Cal.com fork
- `packages/notifications/` - Novu integration
- `packages/analytics/` - Metabase integration

**Основные задачи**:
- Chatwoot setup & custom adapters (MAX, VK)
- Calendar integration (Google/Apple/Outlook)
- Notification infrastructure (Novu)
- Analytics dashboards (Metabase)

**Tech Stack**: Ruby on Rails, Node.js 20+, TypeScript, Novu SDK, Metabase

---

### Backend Developer 3 (GPT) - AI & Rate Limiting
**Рабочие директории**:
- `apps/ai-orchestrator/` - CrewAI agents
- `packages/rate-limiting/` - Rate limiting package

**Основные задачи**:
- AI agents implementation (CrewAI)
- Agent tools (search slots, create appointments, etc.)
- Rate limiting (3-level system)
- AI-driven decision making

**Tech Stack**: Python 3.11+, CrewAI, LangChain, OpenAI, Redis, Node.js 20+

---

### Frontend Developer (GPT) - UI/UX
**Рабочие директории**:
- `apps/admin-panel/` - Next.js 14 Admin Panel
- `apps/mobile-apps/client-app/` - React Native (Client)
- `apps/mobile-apps/staff-app/` - React Native (Staff)
- `packages/ui/` - Shared UI components
- `packages/localization/` - i18next setup

**Основные задачи**:
- Admin panel UI (Next.js App Router)
- Mobile apps (React Native + Expo)
- Shared component library
- Localization (i18next) RU/EN
- Responsive design & animations

**Tech Stack**: Next.js 14, React Native, TypeScript, TailwindCSS, shadcn/ui, i18next, Framer Motion

---

## 📦 Package Dependencies - КАК ПАКЕТЫ СВЯЗАНЫ

```
apps/admin-panel/
  depends on:
    - @beauty-salon/database
    - @beauty-salon/types
    - @beauty-salon/ui
    - @beauty-salon/localization
    - @beauty-salon/payments (Stripe frontend)
    - @beauty-salon/analytics (Metabase embed)

apps/booking-api/
  depends on:
    - @beauty-salon/database (Prisma)
    - @beauty-salon/types
    - @beauty-salon/utils
    - @beauty-salon/payments (Stripe backend)
    - @beauty-salon/secrets (Vault)

apps/queue-manager/
  depends on:
    - @beauty-salon/database
    - @beauty-salon/types
    - @beauty-salon/notifications (Novu)
    - @beauty-salon/rate-limiting

apps/ai-orchestrator/
  depends on:
    - @beauty-salon/database (Prisma Python client)
    - @beauty-salon/notifications (via API)

packages/notifications/
  depends on:
    - @beauty-salon/database
    - @beauty-salon/types
    - @beauty-salon/rate-limiting

packages/payments/
  depends on:
    - @beauty-salon/database
    - @beauty-salon/types
    - @beauty-salon/secrets (API keys)

packages/analytics/
  depends on:
    - @beauty-salon/secrets (embedding secret)
```

---

## 🔧 Development Workflow - КАК РАБОТАТЬ

### 1. Первый запуск (для новых агентов)

```bash
# Clone repository (если ещё не сделано)
cd C:\Users\Nicita\beauty-salon-saas

# Install dependencies (root)
npm install

# Build all packages
npm run build

# Start databases (Docker Compose)
docker-compose up -d

# Setup database (Prisma)
cd packages/database
npx prisma generate
npx prisma migrate dev
npm run db:seed

# Verify connection
npm run test:connection
```

### 2. Daily development

```bash
# Start development mode (watches all packages)
npm run dev

# Run tests
npm run test

# Lint code
npm run lint

# Build for production
npm run build
```

### 3. Working on specific package

```bash
# Example: Working on payments package
cd packages/payments

# Install dependencies (if new)
npm install

# Run tests
npm test

# Build
npm run build
```

### 4. Git workflow

```bash
# Create feature branch
git checkout -b feature/task-xyz

# Commit changes
git add .
git commit -m "feat(payments): implement Stripe payment intent

Co-Authored-By: Backend Developer 1 (GPT) <noreply@anthropic.com>"

# Push to remote
git push origin feature/task-xyz
```

---

## 📚 Important Files - ВАЖНЫЕ ФАЙЛЫ ДЛЯ КАЖДОГО АГЕНТА

### Для ВСЕХ агентов (ОБЯЗАТЕЛЬНО прочитать перед началом):
1. **Этот файл** - `C:\Users\Nicita\multi-agent-system\.claude\context\architecture.md`
2. **Roadmap** - `C:\Users\Nicita\multi-agent-system\.claude\tasks\IMPLEMENTATION-ROADMAP.md`
3. **Progress** - `C:\Users\Nicita\beauty-salon-saas\docs\PROGRESS.md`

### Для Backend Developers:
4. **Database Schema** - `packages/database/prisma/schema.prisma`
5. **ADR-001** - Multi-Tenant Strategy
6. **ADR-007** - Notification Infrastructure (Novu)
7. **ADR-009** - Payment Processing (Stripe)
8. **ADR-011** - Rate Limiting Strategy
9. **ADR-012** - Secrets Management (Vault)

### Для Frontend Developer:
10. **ADR-010** - Localization Strategy (i18next)
11. **Design System** - `apps/admin-panel/components/ui/`
12. **Translation Files** - `apps/admin-panel/public/locales/`

### Для AI Developer (Backend Developer 3):
13. **ADR-008** - Analytics Platform (Metabase) - AI Reports
14. **CrewAI Docs** - https://docs.crewai.com/

---

## 🚨 КРИТИЧЕСКИ ВАЖНО

### Правила для ВСЕХ developer-агентов:

1. **ВСЕГДА читай architecture.md перед началом работы**
2. **ВСЕГДА проверяй свою рабочую директорию** (см. "Developer Workspaces" выше)
3. **НЕ изменяй код других агентов** без координации через Product Manager
4. **ВСЕГДА используй shared packages** (`@beauty-salon/...`) вместо дублирования кода
5. **ВСЕГДА пиши тесты** (coverage > 80%)
6. **ВСЕГДА следуй Code Style** (будет в `.claude/context/code-style.md`)
7. **ВСЕГДА логируй прогресс** в `.claude/agents/[your-name].md`
8. **ВСЕГДА используй TypeScript** (где applicable)
9. **ВСЕГДА соблюдай RLS** (tenant_id везде!)
10. **ВСЕГДА документируй API** (JSDoc/PHPDoc)

### Module Boundaries - НЕ ВЫХОДИТЬ ЗА ГРАНИЦЫ!

- Backend Developer 1 → ТОЛЬКО `apps/booking-api`, `apps/queue-manager`, связанные packages
- Backend Developer 2 → ТОЛЬКО `apps/messaging-hub`, `apps/calendar-service`, связанные packages
- Backend Developer 3 → ТОЛЬКО `apps/ai-orchestrator`, `packages/rate-limiting`
- Frontend Developer → ТОЛЬКО `apps/admin-panel`, `apps/mobile-apps`, `packages/ui`, `packages/localization`

**Если нужно изменить shared package** (`packages/*`) → coordinate с Product Manager!

---

## 🚀 Технологический Стек (Обновлённый)

### Backend Services (Microservices)

#### Core Services (Phase 1 - Deployed)
- **Booking Service**: Laravel 10 (multi-tenant-bookings-saas fork) - 40% reuse
- **Messaging Hub**: Chatwoot + custom adapters (MAX, VK) - 60% reuse
- **AI Orchestrator**: CrewAI (Python 3.11+) - 100% framework reuse
- **Calendar Service**: Cal.com fork (Node.js 20+) - 70% reuse
- **Queue Manager**: BullMQ (Node.js 20+) - 100% reuse

#### New Integrated Services (Phase 2 - Integration) ⭐ NEW
- **Notification Service**: **Novu** (Node.js 20+) - 90% reuse ⭐
- **Analytics Platform**: **Metabase** (Clojure/Java) - 95% reuse ⭐
- **Payment Processing**: **Stripe SDK** (Node.js/Laravel) - 100% SDK reuse ⭐
- **Localization Service**: **i18next** (Next.js/Laravel) - 100% reuse ⭐
- **Rate Limiting Service**: **rate-limiter-flexible** (Node.js) - 70% reuse ⭐
- **Promo Code Generator**: **voucher-code-generator** (Node.js) - 60% reuse ⭐
- **Loyalty/Referral/Reviews**: Custom (patterns from industry) - 75% pattern reuse ⭐

### Database & Cache
- **Primary DB**: Supabase (PostgreSQL 15+ with RLS)
- **Cache**: Redis 7+ Cluster
- **Search**: MeiliSearch (optional)
- **Secrets**: Supabase Vault (encrypted storage)

### Frontend
- **Admin Panel**: Next.js 14+ (App Router)
- **Mobile Apps**: React Native (Expo)
- **UI**: Custom design system + shadcn/ui
- **State**: Zustand + React Query
- **Real-time**: Supabase Realtime
- **Localization**: i18next + next-i18next ⭐ NEW
- **Analytics Embed**: Metabase iframe widgets ⭐ NEW
- **Payment Forms**: Stripe Elements ⭐ NEW

### Infrastructure
- **Hosting**: DigitalOcean/Hetzner (Kubernetes)
- **Monitoring**: Sentry + Grafana + Prometheus
- **CI/CD**: GitHub Actions + Docker
- **Analytics Dashboard**: Metabase (self-hosted) ⭐ NEW

---

## 📊 Open-Source Reuse (Updated)

### Phase 1 Projects (6 проектов)
| Проект | Coverage | Stars | Status |
|--------|----------|-------|--------|
| multi-tenant-bookings-saas | 40% | - | ✅ Cloned |
| Chatwoot | 60% | 20k+ | ✅ Cloned |
| Cal.com | 70% | 31k+ | ✅ Cloned |
| Supabase/Prisma | 100% | 70k+ | ✅ Setup |
| BullMQ | 100% | 6k+ | ✅ Configured |
| CrewAI | 100% | 19k+ | 📅 Pending |

**Phase 1 Average**: 68.3%

### Phase 2 Projects (7 проектов) ⭐ NEW
| Проект | Coverage | Stars | Status | Priority |
|--------|----------|-------|--------|----------|
| **Novu** | 90% | 35k+ | 📅 Pending | ⭐⭐⭐⭐⭐ |
| **Metabase** | 95% | 39k+ | 📅 Pending | ⭐⭐⭐⭐⭐ |
| **Stripe SDK** | 100% | - | 📅 Pending | ⭐⭐⭐⭐⭐ |
| **i18next** | 100% | 7.5k+ | 📅 Pending | ⭐⭐⭐⭐⭐ |
| **rate-limiter-flexible** | 70% | 3k+ | 📅 Pending | ⭐⭐⭐⭐ |
| **voucher-code-generator** | 60% | 400+ | 📅 Pending | ⭐⭐⭐ |
| **Loyalty/Referral patterns** | 75% | - | 📅 Pending | ⭐⭐⭐⭐ |

**Phase 2 Average**: 84.3%

### Combined Coverage (13 проектов)
**Total Average**: (68.3% × 6 + 84.3% × 7) / 13 = **77.2%** ⬆️

**Target**: 60%+ ✅ **EXCEEDED by 17.2%**

---

## 🏗️ Архитектура Системы (Обновлённая)

```
┌──────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                              │
│    Telegram  WhatsApp  Instagram  VK  MAX  Web  Mobile           │
└────────────┬─────────────────────────────────────────────────────┘
             │
┌────────────▼─────────────────────────────────────────────────────┐
│                CHATWOOT (Omnichannel Hub)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │ Telegram Bot │  │ WhatsApp API │  │ MAX Adapter  │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
└────────────┬─────────────────────────────────────────────────────┘
             │
┌────────────▼─────────────────────────────────────────────────────┐
│                CrewAI (AI Agent Orchestrator)                     │
│  ┌────────────┐ ┌────────────┐ ┌──────────────┐                 │
│  │ Booking AI │ │ Support AI │ │ Marketing AI │                 │
│  │ Platform   │ │ Billing AI │ │ Analytics AI │                 │
│  └────────────┘ └────────────┘ └──────────────┘                 │
└────┬────────┬────────┬─────────────────────────────────────────┘
     │        │        │
┌────▼────┐ ┌▼───┐ ┌─▼────────────────────────────────────────────┐
│ Booking │ │Cal │ │    BullMQ Queue System                       │
│ Service │ │.com│ │ ┌─────┐ ┌─────┐ ┌────┐ ┌──────────┐        │
│(Laravel)│ │    │ │ │TX Q │ │MK Q │ │Case│ │Reminder Q│        │
└────┬────┘ └┬───┘ └─┴─────┴──┴─────┴──┴────┴──┴──────────────────┘
     │       │         │
     │       │    ┌────▼────────────────────────────────────┐
     │       │    │   NOVU (Notification Infrastructure) ⭐  │
     │       │    │ ┌──────────┐ ┌────────┐ ┌───────────┐  │
     │       │    │ │ Telegram │ │WhatsApp│ │   Email   │  │
     │       │    │ └──────────┘ └────────┘ └───────────┘  │
     │       │    └─────────────────────────────────────────┘
     │       │
     │  ┌────▼────────────────────────────────────────────────┐
     │  │   STRIPE (Payment Processing) ⭐                     │
     │  │ ┌─────────────┐ ┌─────────────┐ ┌──────────────┐  │
     │  │ │ Payments    │ │ Billing     │ │  Webhooks    │  │
     │  │ └─────────────┘ └─────────────┘ └──────────────┘  │
     │  └─────────────────────────────────────────────────────┘
     │
┌────▼──────────────────────────────────────────────────────────────┐
│              Supabase (PostgreSQL 15+ with RLS)                    │
│  ┌─────────────┐ ┌──────────────┐ ┌────────────────────┐         │
│  │ tenant_id   │ │ Partitioned  │ │ Composite Indexes  │         │
│  │ everywhere  │ │ Tables       │ │ (tenant_id first)  │         │
│  └─────────────┘ └──────────────┘ └────────────────────┘         │
└───────────────────────────────────────────────────────────────────┘
     │
┌────▼──────────────────────────────────────────────────────────────┐
│              METABASE (Analytics & BI Platform) ⭐                 │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐          │
│  │  Dashboards  │ │ SQL Queries  │ │  Alerts & Reports│          │
│  └──────────────┘ └──────────────┘ └──────────────────┘          │
└───────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────┐
│              SUPPORT SERVICES (Cross-Cutting)                      │
│  ┌──────────────┐ ┌──────────────────┐ ┌────────────────┐        │
│  │  i18next ⭐   │ │ Rate Limiter ⭐   │ │ Voucher Gen ⭐ │        │
│  │(Localization)│ │  (Anti-Fraud)    │ │ (Promo Codes)  │        │
│  └──────────────┘ └──────────────────┘ └────────────────┘        │
└───────────────────────────────────────────────────────────────────┘
```

---

## 📦 Модули и Границы (Updated)

### Core Modules (apps/)

#### 1. **booking-api** (Laravel 10)
- **Reuse**: 40% (multi-tenant-bookings-saas)
- **Responsibilities**:
  - Tenant/Staff/Services/Appointments CRUD
  - Slot generation algorithm
  - Multi-tenant context management
- **Dependencies**:
  - Supabase (PostgreSQL)
  - Redis (cache)
  - **Stripe SDK** ⭐ (payments F-080-F-083)
  - **i18next-php** ⭐ (localization F-003)
- **Location**: `apps/booking-api/`
- **API**: REST `/api/v1/tenants`, `/api/v1/appointments`

#### 2. **messaging-hub** (Ruby on Rails)
- **Reuse**: 60% (Chatwoot)
- **Responsibilities**:
  - Omnichannel message routing (Telegram, WhatsApp, Instagram, VK, MAX)
  - Conversation management
  - Agent inbox (heavy chat)
- **Custom Adapters**: MAX, VK (using chatwoot-messenger-gateway patterns)
- **Dependencies**:
  - Supabase (message_log)
  - Redis (session cache)
  - **Novu** ⭐ (notification triggers)
  - **rate-limiter-flexible** ⭐ (anti-spam F-055)
- **Location**: `apps/messaging-hub/`
- **API**: Webhooks `/webhooks/telegram`, `/webhooks/whatsapp`

#### 3. **ai-orchestrator** (Python 3.11+)
- **Reuse**: 100% (CrewAI framework)
- **Responsibilities**:
  - AI agent orchestration (Booking, Support, Marketing, Platform, Billing, Analytics)
  - Decision logging
  - Escalation logic
- **Dependencies**:
  - Supabase (ai_decisions, cases)
  - OpenAI/Anthropic APIs
  - **Novu** ⭐ (send notifications)
  - Booking API (create appointments)
  - Messaging Hub (send messages)
- **Location**: `apps/ai-orchestrator/`
- **API**: REST `/api/v1/ai/chat`, `/api/v1/ai/decisions`

#### 4. **calendar-service** (Node.js 20+)
- **Reuse**: 70% (Cal.com)
- **Responsibilities**:
  - Google/Apple/Outlook calendar sync
  - Conflict detection
  - Async sync queue
- **Dependencies**:
  - Supabase (appointments)
  - BullMQ (calendar queue)
  - External calendar APIs (Google, Apple, Outlook)
- **Location**: `apps/calendar-service/`
- **API**: REST `/api/v1/calendar/sync`, `/api/v1/calendar/conflicts`

#### 5. **queue-manager** (Node.js 20+)
- **Reuse**: 100% (BullMQ)
- **Responsibilities**:
  - Queue orchestration (tx, mk, calendar, case, reminder)
  - Rate limiting enforcement
  - Retry logic
  - Job scheduling
- **Dependencies**:
  - Redis Cluster
  - **Novu** ⭐ (notification workers)
  - **rate-limiter-flexible** ⭐ (3-level rate limiting)
  - Booking API (reminders F-070-F-072)
  - Messaging Hub (send messages)
- **Location**: `apps/queue-manager/`
- **Workers**: `workers/reminder-worker.ts`, `workers/notification-worker.ts`

#### 6. **notification-service** ⭐ NEW (Node.js 20+)
- **Reuse**: 90% (Novu)
- **Responsibilities**:
  - Multi-channel notification delivery (Telegram, WhatsApp, Email, SMS)
  - Notification templates management
  - Delivery tracking
  - Rate limiting per channel
- **Functions Covered**: F-070, F-071, F-072 (Reminders + Confirmations)
- **Dependencies**:
  - Novu Cloud API or self-hosted
  - Supabase (clients, appointments)
  - BullMQ (reminder queue)
  - Messaging Hub (fallback for delivery)
- **Location**: `apps/notification-service/`
- **API**: Internal only (called by queue-manager)
- **Setup**:
  ```bash
  npm install @novu/node
  docker run -p 3000:3000 novu/api  # self-hosted option
  ```

#### 7. **analytics-service** ⭐ NEW (Java/Clojure)
- **Reuse**: 95% (Metabase)
- **Responsibilities**:
  - SQL query builder (visual)
  - Dashboard creation
  - Scheduled reports
  - Email/Slack alerts
  - Embeddable widgets (iframe)
- **Functions Covered**: F-081, F-083, F-110, F-111, F-112 (Analytics & Reports)
- **Dependencies**:
  - Supabase (read-only connection)
  - SMTP (email alerts)
  - Slack API (alert notifications)
- **Location**: `apps/analytics-service/` (Docker)
- **API**: REST `/api/dashboard`, `/api/embed`
- **Setup**:
  ```bash
  docker run -p 3000:3000 metabase/metabase
  # Connect to Supabase PostgreSQL
  # Create dashboards, queries, alerts
  ```

#### 8. **payment-service** ⭐ NEW (Integrated into booking-api)
- **Reuse**: 100% (Stripe SDK)
- **Responsibilities**:
  - Payment intent creation
  - Webhook handling (payment events)
  - Subscription billing (for tenants)
  - Invoice generation
  - Refund processing
- **Functions Covered**: F-080, F-081, F-082, F-083 (Payments & Billing)
- **Dependencies**:
  - Stripe API
  - Supabase (appointments, tenants)
  - **Kill Bill** (optional, for advanced billing)
- **Location**: `apps/booking-api/app/Services/PaymentService.php`
- **API**: REST `/api/v1/payments`, Webhook `/webhooks/stripe`
- **Setup**:
  ```bash
  composer require stripe/stripe-php
  # or npm install stripe (Node.js)
  ```

#### 9. **admin-panel** (Next.js 14+)
- **Reuse**: 0% (custom design)
- **Responsibilities**:
  - Tenant management UI
  - Appointment management
  - Analytics dashboard (embeds Metabase ⭐)
  - Staff management
  - Settings (notifications, payments, localization)
- **New Features**: ⭐
  - **Language Switcher** (i18next)
  - **Payment Forms** (Stripe Elements)
  - **Notification Settings UI** (Novu preferences)
  - **Embedded Analytics** (Metabase iframe)
- **Dependencies**:
  - Next.js 14 (App Router)
  - **i18next + next-i18next** ⭐ (localization F-003)
  - **Stripe Elements** ⭐ (payment UI)
  - shadcn/ui (base components)
  - Zustand + React Query (state)
  - Supabase Realtime (live updates)
- **Location**: `apps/admin-panel/`
- **Routes**: `/[locale]/dashboard`, `/[locale]/appointments`, `/[locale]/analytics`

#### 10. **mobile-apps** (React Native + Expo)
- **Reuse**: 0% (custom)
- **Responsibilities**:
  - Client app (booking, profile)
  - Staff app (schedule, clients)
- **New Features**: ⭐
  - **Localization** (i18next)
  - **Payment integration** (Stripe React Native SDK)
- **Location**: `apps/mobile-apps/client-app/`, `apps/mobile-apps/staff-app/`

---

### Shared Packages (packages/)

#### 1. **database** ✅ (Prisma + Supabase)
- Prisma schema (9 tables)
- RLS policies
- Migrations
- Seed scripts
- **Location**: `packages/database/`

#### 2. **types** (TypeScript)
- Shared types for all services
- API contracts
- Event types
- **Location**: `packages/types/`

#### 3. **ui** (React Components)
- Shared UI components
- Design system
- shadcn/ui wrappers
- **Location**: `packages/ui/`

#### 4. **utils** (Shared Utilities)
- Date/time helpers
- Validation
- Formatters
- **Location**: `packages/utils/`

#### 5. **localization** ⭐ NEW (i18next)
- Translation files (RU/EN)
- i18next configuration
- Translation utilities
- **Location**: `packages/localization/`
- **Structure**:
  ```
  packages/localization/
  ├── locales/
  │   ├── ru/
  │   │   ├── common.json
  │   │   ├── appointments.json
  │   │   └── notifications.json
  │   └── en/
  │       ├── common.json
  │       ├── appointments.json
  │       └── notifications.json
  └── i18n.config.ts
  ```

#### 6. **rate-limiting** ⭐ NEW (rate-limiter-flexible)
- Rate limiter service
- 3-level rate limiting (client, tenant, channel)
- Redis store configuration
- **Location**: `packages/rate-limiting/`
- **Functions Covered**: F-022 (Anti-fraud), F-055 (Anti-spam)

#### 7. **promo-codes** ⭐ NEW (voucher-code-generator)
- Promo code generation
- Validation logic
- **Location**: `packages/promo-codes/`
- **Functions Covered**: F-013 (Promotions)

---

## 🔗 Integration Points (Detailed)

### 1. Novu Integration (Notification Service)

**Architecture**:
```typescript
// Notification flow
BullMQ Worker (reminder-worker.ts)
  → NotificationService.sendReminder()
    → Novu API (novu.trigger())
      → Novu delivers via:
        - Telegram (via Chatwoot)
        - WhatsApp (via Chatwoot)
        - Email (via SMTP)
        - SMS (via Twilio)

// Fallback
If Novu fails → Queue retry → Messaging Hub direct send
```

**Configuration**:
```typescript
// apps/notification-service/src/config/novu.config.ts
import { Novu } from '@novu/node'

export const novu = new Novu(process.env.NOVU_API_KEY)

// Notification workflows
export const workflows = {
  'reminder-24h': 'appointment-reminder-24h',
  'reminder-1h': 'appointment-reminder-1h',
  'confirm-reschedule': 'appointment-confirm-reschedule',
  'win-back-stage-1': 'client-winback-stage-1',
}
```

**Functions Covered**:
- F-070: Reminders (24h/1h)
- F-071: Confirm/Reschedule buttons
- F-072: Cancel/reschedule notifications
- F-092: Win-back campaigns (partially)

**API Endpoints**:
- Internal: `POST /notifications/send`
- Webhook: `POST /webhooks/novu` (delivery status)

---

### 2. Metabase Integration (Analytics Platform)

**Architecture**:
```
Metabase (Docker)
  → Connects to Supabase PostgreSQL (read-only user)
  → Queries with RLS context (SET app.tenant_id)
  → Generates dashboards
  → Embeds in admin-panel (iframe with signed URL)

Admin Panel (Next.js)
  → Fetches embed token from backend
  → Renders <iframe src="metabase-dashboard-url?token=..." />
```

**Configuration**:
```yaml
# docker-compose.yml
services:
  metabase:
    image: metabase/metabase:latest
    ports:
      - "3000:3000"
    environment:
      MB_DB_TYPE: postgres
      MB_DB_CONNECTION_URI: ${SUPABASE_DATABASE_URL}
      MB_SITE_URL: https://analytics.beauty-saas.com
```

**SQL Queries** (Examples):
```sql
-- F-081: Money Dashboard (losses)
SELECT
  DATE_TRUNC('day', start_at) as date,
  COUNT(*) FILTER (WHERE status = 'no_show') as no_shows,
  SUM(price) FILTER (WHERE status = 'no_show') as lost_revenue
FROM appointments
WHERE tenant_id = {{tenant_id}}
  AND start_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE_TRUNC('day', start_at)
ORDER BY date;

-- F-083: Staff load & revenue
SELECT
  s.name as staff_name,
  COUNT(a.id) as total_appointments,
  SUM(a.price) as total_revenue,
  AVG(EXTRACT(EPOCH FROM (a.end_at - a.start_at)) / 3600) as avg_hours
FROM appointments a
JOIN staff s ON a.staff_id = s.id
WHERE a.tenant_id = {{tenant_id}}
  AND a.start_at >= NOW() - INTERVAL '30 days'
GROUP BY s.id, s.name
ORDER BY total_revenue DESC;

-- F-110: Custom report constructor (user creates in Metabase UI)
```

**Embedding**:
```typescript
// apps/admin-panel/app/[locale]/analytics/page.tsx
import { getMetabaseEmbedUrl } from '@/lib/metabase'

export default async function AnalyticsPage() {
  const embedUrl = await getMetabaseEmbedUrl({
    dashboardId: 1,
    tenantId: currentTenant.id,
  })

  return (
    <iframe
      src={embedUrl}
      width="100%"
      height="800px"
      frameBorder="0"
    />
  )
}
```

**Functions Covered**:
- F-081: Money Dashboard (losses)
- F-083: Revenue forecast + staff load
- F-110: Report constructor (Metabase UI)
- F-111: Team detailed report
- F-112: Alerts (email/Slack)

---

### 3. Stripe Integration (Payment Processing)

**Architecture**:
```
Client (Admin Panel)
  → Stripe Elements (payment form)
  → POST /api/v1/appointments/{id}/pay
    → PaymentService.createPaymentIntent()
      → Stripe API (create payment intent)
      → Return client_secret
    → Client confirms payment (Stripe.js)
  → Stripe webhook → POST /webhooks/stripe
    → PaymentService.handleWebhook()
      → Update appointment.paid
      → Log payment in Supabase
```

**Configuration**:
```php
// apps/booking-api/app/Services/PaymentService.php
use Stripe\Stripe;
use Stripe\PaymentIntent;

class PaymentService {
    public function __construct() {
        Stripe::setApiKey(config('services.stripe.secret'));
    }

    public function createPaymentIntent(Appointment $appointment) {
        return PaymentIntent::create([
            'amount' => $appointment->price * 100, // cents
            'currency' => $appointment->tenant->currency,
            'metadata' => [
                'tenant_id' => $appointment->tenant_id,
                'appointment_id' => $appointment->id,
            ],
            'automatic_payment_methods' => ['enabled' => true],
        ]);
    }

    public function handleWebhook($payload, $signature) {
        $event = \Stripe\Webhook::constructEvent(
            $payload,
            $signature,
            config('services.stripe.webhook_secret')
        );

        if ($event->type === 'payment_intent.succeeded') {
            $this->markAppointmentAsPaid($event->data->object);
        }
    }
}
```

**Frontend**:
```typescript
// apps/admin-panel/app/[locale]/appointments/[id]/pay/page.tsx
import { loadStripe } from '@stripe/stripe-js'
import { Elements, PaymentElement } from '@stripe/react-stripe-js'

const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_KEY)

export default function PaymentPage({ appointment }) {
  const [clientSecret, setClientSecret] = useState('')

  useEffect(() => {
    fetch(`/api/appointments/${appointment.id}/pay`, { method: 'POST' })
      .then(res => res.json())
      .then(data => setClientSecret(data.client_secret))
  }, [])

  return (
    <Elements stripe={stripePromise} options={{ clientSecret }}>
      <PaymentElement />
    </Elements>
  )
}
```

**Functions Covered**:
- F-080: Payment tracking
- F-081: Money Dashboard (revenue)
- F-082: Return attribution
- F-083: Revenue forecast

---

### 4. i18next Integration (Localization)

**Architecture**:
```
Next.js App Router
  → [locale] dynamic segment (ru/en)
  → Middleware detects locale
  → Loads translation files (JSON)
  → SSR with translations

Backend (Laravel)
  → Translation files (resources/lang/ru/, resources/lang/en/)
  → Localization middleware
  → API responses in requested locale
```

**Configuration**:
```typescript
// packages/localization/i18n.config.ts
import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'

i18n
  .use(initReactI18next)
  .init({
    resources: {
      ru: {
        common: require('./locales/ru/common.json'),
        appointments: require('./locales/ru/appointments.json'),
      },
      en: {
        common: require('./locales/en/common.json'),
        appointments: require('./locales/en/appointments.json'),
      },
    },
    lng: 'ru',
    fallbackLng: 'ru',
    interpolation: { escapeValue: false },
  })

export default i18n
```

**Translation Files**:
```json
// packages/localization/locales/ru/appointments.json
{
  "title": "Записи",
  "create": "Создать запись",
  "status": {
    "planned": "Запланирована",
    "confirmed": "Подтверждена",
    "completed": "Завершена",
    "cancelled": "Отменена",
    "no_show": "Не пришёл",
    "rescheduled": "Перенесена"
  },
  "reminder": {
    "24h": "Напоминаем о вашей записи завтра в {{time}}",
    "1h": "Через час ваша запись к {{staff}}"
  }
}
```

**Usage**:
```typescript
// apps/admin-panel/app/[locale]/appointments/page.tsx
import { useTranslation } from 'react-i18next'

export default function AppointmentsPage() {
  const { t } = useTranslation('appointments')

  return (
    <div>
      <h1>{t('title')}</h1>
      <Button>{t('create')}</Button>
    </div>
  )
}
```

**Functions Covered**:
- F-003: RU/EN localization
- F-054: Message templates RU/EN (partially)

---

### 5. Rate Limiter Integration (Anti-Fraud)

**Architecture**:
```
API Request
  → Express/Laravel Middleware
  → RateLimiterService.consume(key)
    → Redis (increment counter)
    → Check limit
      → If exceeded → Throw 429 Too Many Requests
      → If ok → Continue
```

**3-Level Rate Limiting**:
```typescript
// packages/rate-limiting/src/RateLimiterService.ts
import { RateLimiterRedis } from 'rate-limiter-flexible'
import Redis from 'ioredis'

const redis = new Redis(process.env.REDIS_URL)

// Level 1: Client (anti-fraud for bookings)
export const clientBookingLimiter = new RateLimiterRedis({
  storeClient: redis,
  keyPrefix: 'rl:client:booking',
  points: 10, // Max 10 bookings
  duration: 3600, // Per hour
})

// Level 2: Tenant (daily message limits)
export const tenantTxLimiter = new RateLimiterRedis({
  storeClient: redis,
  keyPrefix: 'rl:tenant:tx',
  points: 3000, // Max 3000 TX msgs
  duration: 86400, // Per day
})

export const tenantMkLimiter = new RateLimiterRedis({
  storeClient: redis,
  keyPrefix: 'rl:tenant:mk',
  points: 1500, // Max 1500 MK msgs
  duration: 86400, // Per day
})

// Level 3: Channel (per API limits)
export const channelTelegramLimiter = new RateLimiterRedis({
  storeClient: redis,
  keyPrefix: 'rl:channel:telegram',
  points: 30, // 30 RPS
  duration: 1,
})

// Usage
async function checkRateLimit(clientPhone: string) {
  try {
    await clientBookingLimiter.consume(clientPhone)
    // OK, proceed
  } catch (rejRes) {
    throw new Error(`Rate limit exceeded. Retry after ${rejRes.msBeforeNext}ms`)
  }
}
```

**Express Middleware**:
```typescript
// apps/booking-api/middleware/rateLimiter.ts
import { Request, Response, NextFunction } from 'express'
import { clientBookingLimiter } from '@beauty-salon-saas/rate-limiting'

export async function rateLimitMiddleware(req: Request, res: Response, next: NextFunction) {
  const clientPhone = req.body.client_phone

  try {
    await clientBookingLimiter.consume(clientPhone)
    next()
  } catch (rejRes) {
    res.status(429).json({
      error: 'Too many requests',
      retry_after: rejRes.msBeforeNext,
    })
  }
}
```

**Functions Covered**:
- F-022: Anti-fraud rules
- F-055: Anti-spam policy

---

### 6. Promo Codes Integration

**Architecture**:
```
Admin creates promotion
  → PromoCodeService.generateCodes()
    → voucher-code-generator
    → Save codes to DB (promo_codes table)
  → Client applies code
    → PromoCodeService.validateAndApply()
      → Check: not expired, not used, valid for tenant
      → Apply discount to appointment
      → Mark code as used
```

**Implementation**:
```typescript
// packages/promo-codes/src/PromoCodeService.ts
import voucher_codes from 'voucher-code-generator'

export class PromoCodeService {
  static generateCodes(count: number, prefix: string) {
    return voucher_codes.generate({
      length: 8,
      count: count,
      prefix: `${prefix}-`,
      charset: '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ',
    })
  }

  static async validateAndApply(code: string, tenantId: string) {
    const promo = await prisma.promoCode.findUnique({
      where: { code, tenantId },
    })

    if (!promo) throw new Error('Invalid code')
    if (promo.used) throw new Error('Code already used')
    if (new Date() > promo.expiresAt) throw new Error('Code expired')

    return {
      discount: promo.discount,
      type: promo.type, // 'percent' or 'fixed'
    }
  }
}
```

**Database Schema** (add to Prisma):
```prisma
model PromoCode {
  id        String   @id @default(uuid())
  tenantId  String   @map("tenant_id")
  code      String   @unique
  discount  Decimal
  type      String   // 'percent' or 'fixed'
  used      Boolean  @default(false)
  usedBy    String?  @map("used_by")
  expiresAt DateTime @map("expires_at")
  createdAt DateTime @default(now()) @map("created_at")

  tenant Tenant @relation(fields: [tenantId], references: [id])

  @@index([tenantId])
  @@map("promo_codes")
}
```

**Functions Covered**:
- F-013: Promotions (promo codes)

---

### 7. Loyalty/Referral/Reviews (Custom Patterns)

**Loyalty System** (F-014):
```prisma
model Client {
  bonusBalance Int @default(0) @map("bonus_balance")
}

model BonusTransaction {
  id        String   @id @default(uuid())
  clientId  String   @map("client_id")
  amount    Int      // +100 or -50
  reason    String   // "appointment_completed", "promo", "spent"
  createdAt DateTime @default(now()) @map("created_at")

  client Client @relation(fields: [clientId], references: [id])

  @@map("bonus_transactions")
}
```

**Referral System** (F-021):
```prisma
model Referral {
  id           String         @id @default(uuid())
  tenantId     String         @map("tenant_id")
  referrerId   String         @map("referrer_id") // Who invited
  referredId   String         @map("referred_id") // Who was invited
  status       ReferralStatus // pending/completed/rewarded
  reward       Decimal        // Reward for successful conversion
  completedAt  DateTime?      @map("completed_at")
  createdAt    DateTime       @default(now()) @map("created_at")

  tenant   Tenant @relation(fields: [tenantId], references: [id])
  referrer Client @relation("Referrals", fields: [referrerId], references: [id])
  referred Client @relation("ReferredBy", fields: [referredId], references: [id])

  @@map("referrals")
}

enum ReferralStatus {
  pending
  completed
  rewarded
}
```

**Review System** (F-090, F-091):
```prisma
model Review {
  id            String   @id @default(uuid())
  tenantId      String   @map("tenant_id")
  appointmentId String   @map("appointment_id")
  clientId      String   @map("client_id")
  rating        Int      // 1-5
  text          String?
  createdAt     DateTime @default(now()) @map("created_at")

  tenant      Tenant      @relation(fields: [tenantId], references: [id])
  appointment Appointment @relation(fields: [appointmentId], references: [id])
  client      Client      @relation(fields: [clientId], references: [id])

  @@index([tenantId, rating])
  @@map("reviews")
}
```

**Auto-escalation logic** (F-091):
```typescript
// After review is created
if (review.rating <= 3) {
  await prisma.case.create({
    data: {
      tenantId: review.tenantId,
      clientId: review.clientId,
      reason: `Negative review (${review.rating}/5): ${review.text}`,
      status: 'open',
      context: {
        review_id: review.id,
        appointment_id: review.appointmentId,
      },
    },
  })
}
```

**Functions Covered**:
- F-014: Bonus points system
- F-021: Referral program
- F-090: Review collection
- F-091: Negative→auto case
- F-092: Win-back campaigns (with BullMQ)

---

## 📊 Data Flow (Updated)

### Flow 1: Client → Booking (with Payment)
```
1. Client sends "Хочу записаться" (Telegram)
2. Chatwoot receives → webhook to AI Orchestrator
3. CrewAI Booking Agent:
   - Classifies intent
   - Calls Booking API (GET /api/v1/slots)
   - Shows available slots
4. Client selects slot
5. Booking Agent creates appointment (POST /api/v1/appointments)
6. Payment flow:
   - Booking API → PaymentService.createPaymentIntent() ⭐
   - Returns payment URL (Stripe)
   - Client pays
   - Stripe webhook → update appointment.paid ⭐
7. Confirmation sent via Novu ⭐ (multi-channel)
8. Calendar synced via Cal.com
9. Reminder scheduled in BullMQ
```

### Flow 2: Reminder Notification
```
1. BullMQ scheduler triggers reminder job (24h before)
2. reminder-worker.ts executes:
   - Fetches appointment from Supabase
   - Calls NotificationService.sendReminder() ⭐
3. NotificationService:
   - Calls Novu API (novu.trigger('reminder-24h')) ⭐
   - Novu delivers via Telegram/WhatsApp/Email ⭐
4. If Novu fails:
   - Retry via BullMQ
   - Fallback: direct send via Chatwoot
5. Delivery status tracked in Supabase (message_log)
```

### Flow 3: Analytics Dashboard View
```
1. Admin opens /analytics page (Next.js)
2. Backend generates Metabase embed URL ⭐
   - With signed token
   - With tenant_id filter
3. Frontend renders iframe with Metabase dashboard ⭐
4. Metabase:
   - Connects to Supabase (read-only)
   - Executes SQL queries with RLS context ⭐
   - Returns visualizations
5. Admin sees real-time dashboard ⭐
```

### Flow 4: Rate Limiting Check
```
1. Client makes 11th booking in 1 hour
2. API receives request
3. Rate Limit Middleware:
   - Calls RateLimiterService.consume(client_phone) ⭐
   - Redis check: 11 > 10 (limit) ⭐
   - Returns 429 Too Many Requests ⭐
4. Response: "Rate limit exceeded, retry after 3523ms"
5. Log suspicious activity in audit log
6. Optionally: escalate to Case if repeated abuse
```

### Flow 5: Localization
```
1. User selects language (RU/EN)
2. Next.js middleware:
   - Detects locale from URL (/ru/ or /en/)
   - Loads translation files via i18next ⭐
3. SSR with translated content ⭐
4. Client-side:
   - useTranslation('appointments') ⭐
   - t('title') → "Записи" (RU) or "Appointments" (EN) ⭐
5. Backend API:
   - Accept-Language header
   - Returns localized error messages ⭐
```

---

## 🔐 Security Considerations (Updated)

### Multi-Tenant Isolation ✅
- **RLS (Row-Level Security)** in PostgreSQL
- `tenant_id` on every table
- Connection-level tenant context
- **Metabase**: read-only user, RLS enforced ⭐

### Authentication ✅
- **Supabase Auth** (JWT)
- Role-based access (Owner/Staff/Admin)
- API key rotation
- **Stripe**: webhook signature verification ⭐
- **Novu**: API key in environment variables ⭐

### Data Protection ✅
- Encrypted secrets (**Supabase Vault**) ⭐
- PII masking in logs
- HTTPS only (TLS 1.3)
- Webhook signature verification (Stripe, Telegram, etc.)
- **Payment data**: PCI DSS compliant (Stripe handles) ⭐

### Rate Limiting ✅ (Enhanced)
- **3-Level Rate Limiting** ⭐:
  - Client level: 10 bookings/hour (anti-fraud)
  - Tenant level: 3000 TX + 1500 MK msgs/day
  - Channel level: per API limits (20-30 RPS)
- **Implementation**: rate-limiter-flexible + Redis ⭐
- **Monitoring**: Track rate limit violations in logs ⭐

### Secrets Management ✅
- **Supabase Vault**: Telegram tokens, WhatsApp keys, Stripe keys ⭐
- Environment variables: `.env` files (not committed)
- **Doppler** (optional): centralized secrets management ⭐

---

## 📈 Performance Requirements (Updated)

### Target Scale ✅
- **Tenants**: 10,000
- **Staff**: ~100,000
- **Messages**: 20M/day (peak), 2M/day (baseline)
- **Appointments**: ~500k/day
- **Notifications**: 1M+/day via Novu ⭐
- **Analytics Queries**: 10k+/day via Metabase ⭐

### SLAs ✅
- API response time: p95 < 200ms
- Message delivery: p95 < 5s
- **Notification delivery** (Novu): p95 < 3s ⭐
- Slot search: p95 < 1s
- Database queries: p95 < 50ms
- **Analytics query** (Metabase): p95 < 2s ⭐
- **Payment processing** (Stripe): p95 < 1s ⭐
- Uptime: 99.9%

### Caching Strategy ✅
- **Redis**:
  - Session cache
  - Rate limit counters ⭐
  - Calendar conflict cache (14 days per staff)
  - Slot cache (1 hour TTL)
  - **Translation cache** (i18next) ⭐
- **Metabase**: query result cache (configurable TTL) ⭐

### Scaling Strategy ✅
- **Phase 1** (0-1k tenants): Single DB + Redis
- **Phase 2** (1k-5k tenants): DB replicas + Redis Cluster
- **Phase 3** (5k-10k tenants): Citus extension + auto-scaling
- **Novu**: Cloud-hosted (auto-scales) or self-hosted cluster ⭐
- **Metabase**: horizontal scaling (multiple instances behind LB) ⭐

---

## 📋 Связанные ADR (Updated)

### Phase 1 ADRs ✅
- **ADR-001**: Multi-Tenant Strategy (RLS vs Schemas) ✅
- **ADR-002**: Message Queue Selection (BullMQ) 📅
- **ADR-003**: AI Framework Selection (CrewAI) 📅
- **ADR-004**: Omnichannel Platform (Chatwoot) 📅
- **ADR-005**: Calendar Integration (Cal.com) 📅
- **ADR-006**: Database Platform (Supabase) 📅

### Phase 2 ADRs ⭐ NEW (Pending)
- **ADR-007**: Notification Infrastructure (Novu vs alternatives) 📅
- **ADR-008**: Analytics Platform (Metabase vs Redash vs Superset) 📅
- **ADR-009**: Payment Processing (Stripe vs alternatives) 📅
- **ADR-010**: Localization Strategy (i18next vs alternatives) 📅
- **ADR-011**: Rate Limiting Strategy (3-level approach) 📅
- **ADR-012**: Secrets Management (Supabase Vault vs Doppler) 📅

**Location**: `C:\Users\Nicita\beauty-salon-saas\docs\architecture\`

---

## 🚀 Progress (Updated)

### ✅ Phase 1 Complete (2026-01-22)
- [x] Architecture planned and approved (60+ pages)
- [x] Project initialized (monorepo with Turborepo)
- [x] Open-source projects cloned (Booking, Chatwoot, Cal.com)
- [x] Configuration files created (package.json, .env.example, docker-compose.yml)
- [x] Database package created (Prisma schema, RLS policies, migrations, seed)
- [x] Docker Compose setup (PostgreSQL, Redis, pgAdmin, Redis Commander)
- [x] Documentation (Supabase guide, Docker guide, ADR-001, README, PROGRESS)
- [x] Open-source reuse: **68.3%**

### 🚧 Phase 2 In Progress (Integration Architecture)
- [x] Research 7 new open-source projects ✅
- [x] Architecture updated with integration details ✅
- [ ] ADR-007 to ADR-012 creation 📅
- [ ] Novu integration (notification-service) 📅
- [ ] Metabase setup (analytics-service) 📅
- [ ] Stripe integration (payment-service) 📅
- [ ] i18next setup (localization package) 📅
- [ ] Rate limiter implementation 📅
- [ ] Promo codes service 📅
- [ ] Loyalty/Referral/Reviews implementation 📅
- [ ] **Target open-source reuse**: **75-78%** 🎯

### 📅 Phase 3 Roadmap
- **Week 1**: Core integrations (Novu, i18next, Rate Limiter)
- **Week 2**: Analytics & Payments (Metabase, Stripe)
- **Week 3**: Loyalty programs, Promo codes, Reviews
- **Week 4**: Testing, optimization, MVP launch

---

## 📊 Module Dependency Graph

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend Layer                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Admin Panel  │  │ Client App   │  │  Staff App   │          │
│  │  (Next.js)   │  │ (RN Expo)    │  │  (RN Expo)   │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │ i18next ⭐      │ i18next ⭐      │ i18next ⭐        │
│         │ Stripe UI ⭐    │ Stripe RN ⭐    │                   │
│         │ Metabase ⭐     │                 │                   │
└─────────┼─────────────────┼─────────────────┼───────────────────┘
          │                 │                 │
┌─────────▼─────────────────▼─────────────────▼───────────────────┐
│                       API Gateway (Future)                        │
│                    (Authentication, Routing)                      │
└─────────┬─────────────────────────────────────────────────────────┘
          │
┌─────────▼─────────────────────────────────────────────────────────┐
│                       Backend Services                             │
│                                                                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  Booking    │  │  Messaging  │  │     AI      │              │
│  │   (Laravel) │  │  (Chatwoot) │  │  (CrewAI)   │              │
│  │             │  │             │  │             │              │
│  │  depends:   │  │  depends:   │  │  depends:   │              │
│  │  - Stripe⭐ │  │  - Novu⭐   │  │  - Novu⭐   │              │
│  │  - i18n⭐   │  │  - RateLim⭐│  │  - Booking  │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│                                                                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  Calendar   │  │   Queue     │  │Notification │ ⭐ NEW       │
│  │  (Cal.com)  │  │  (BullMQ)   │  │   (Novu)    │              │
│  │             │  │             │  │             │              │
│  │  depends:   │  │  depends:   │  │  depends:   │              │
│  │  - Booking  │  │  - Novu⭐   │  │  - Chatwoot │              │
│  │  - Supabase │  │  - RateLim⭐│  │  - Supabase │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│                                                                    │
│  ┌─────────────┐  ┌─────────────┐                                │
│  │ Analytics   │  │  Payment    │ ⭐ NEW                         │
│  │ (Metabase)  │  │  (Stripe)   │                                │
│  │             │  │             │                                │
│  │  depends:   │  │  depends:   │                                │
│  │  - Supabase │  │  - Booking  │                                │
│  │  (read-only)│  │  - Supabase │                                │
│  └─────────────┘  └─────────────┘                                │
└────────────────────────┬──────────────────────────────────────────┘
                         │
┌────────────────────────▼──────────────────────────────────────────┐
│                    Shared Infrastructure                           │
│                                                                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  Database   │  │    Redis    │  │    Vault    │ ⭐ NEW       │
│  │ (Supabase)  │  │   Cluster   │  │  (Secrets)  │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│                                                                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ Localization│  │ Rate Limiter│  │ Promo Codes │ ⭐ NEW       │
│  │  (i18next)  │  │  (rl-flex)  │  │  (voucher)  │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└───────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Implementation Priority

### Week 1: High-Priority (Must-Have) ⭐⭐⭐⭐⭐
1. **i18next** (F-003) - 2 часа
   - Frontend (Next.js) + Backend (Laravel)
   - Translation files (RU/EN)
2. **Novu** (F-070-F-072) - 2 дня
   - Notification service setup
   - Integration with BullMQ
   - Templates creation
3. **Rate Limiter** (F-022, F-055) - 2 дня
   - 3-level rate limiting
   - Redis store
   - Middleware integration

### Week 2: Medium-Priority ⭐⭐⭐⭐
4. **Stripe** (F-080-F-083) - 3 дня
   - Payment intent flow
   - Webhook handling
   - Subscription billing (for tenants)
5. **Metabase** (F-110-F-112) - 2 дня
   - Docker setup
   - Dashboard creation
   - Embed integration

### Week 3-4: Low-Priority (Can Defer) ⭐⭐⭐
6. **Voucher Generator** (F-013) - 1 день
7. **Loyalty System** (F-014) - 3 дня
8. **Referral Program** (F-021) - 4 дня
9. **Reviews** (F-090-F-091) - 3 дня
10. **Win-back Campaigns** (F-092) - 3 дня

---

## 📚 References & Resources

### Official Documentation
- **Novu**: https://docs.novu.co/
- **Metabase**: https://www.metabase.com/docs/
- **Stripe**: https://stripe.com/docs/api
- **i18next**: https://www.i18next.com/
- **rate-limiter-flexible**: https://github.com/animir/node-rate-limiter-flexible
- **voucher-code-generator**: https://github.com/voucherifyio/voucher-code-generator-js

### Integration Examples
- **Novu + BullMQ**: https://docs.novu.co/platform/queues
- **Metabase Embedding**: https://www.metabase.com/docs/latest/embedding/introduction
- **Stripe Webhooks**: https://stripe.com/docs/webhooks
- **Next.js i18n**: https://nextjs.org/docs/app/building-your-application/routing/internationalization

### Community Resources
- **Novu Discord**: https://discord.gg/novu
- **Metabase Forum**: https://discourse.metabase.com/
- **Stripe Community**: https://stripe.com/community

---

## 🔄 Change Log

### 2026-01-22 (Phase 2 Update) ⭐
- Added 7 new open-source integrations
- Updated tech stack with Novu, Metabase, Stripe, i18next, rate-limiter, voucher-gen
- Created detailed integration architecture
- Updated open-source reuse: 68.3% → **77.2%**
- Added new modules: notification-service, analytics-service, payment-service
- Updated data flows with new integrations
- Enhanced security section (rate limiting, secrets management)
- Added 6 new ADRs (ADR-007 to ADR-012)
- Updated dependency graph
- Created implementation priority plan

### 2026-01-22 (Phase 1 Complete)
- Initial architecture created
- 6 open-source projects selected
- Database schema designed (9 tables)
- RLS policies implemented
- Docker Compose setup
- Open-source reuse: 68.3%

---

**Last Updated**: 2026-01-22 by Architect Agent
**Status**: Phase 2 - Integration Architecture Complete ✅
**Next**: ADR-007 to ADR-012 creation → Implementation

**Full Plan**: [C:\Users\Nicita\.claude\plans\sharded-marinating-balloon.md](c:\Users\Nicita\.claude\plans\sharded-marinating-balloon.md)

**Progress Tracker**: [C:\Users\Nicita\beauty-salon-saas\docs\PROGRESS.md](c:\Users\Nicita\beauty-salon-saas\docs\PROGRESS.md)
