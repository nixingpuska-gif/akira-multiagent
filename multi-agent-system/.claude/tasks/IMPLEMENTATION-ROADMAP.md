# Implementation Roadmap - Beauty Salon SaaS

**Версия**: 1.0
**Дата создания**: 2026-01-22
**Статус**: Ready for Implementation
**Владелец**: Architect → Product Manager

---

## 📋 Обзор Roadmap

Этот документ содержит **детальный пошаговый план реализации** Beauty Salon SaaS платформы.

**⚠️ ВАЖНО**: Это НЕ MVP - полный коммерческий продукт готовый к продаже
**Включает**: Документацию, контракты, бизнес-инфраструктуру, поддержку, мониторинг

**Общая длительность**: 6 недель (Full Commercial Product)
**Фазы**: 6 (Week 1-6)
**Агентов задействовано**: 8 базовых + 2-3 динамических Backend Developer
**Open-Source Reuse**: 77.2%
**Ценообразование**: 15,000₽ (мин) / 25,000₽ (средний) / 50,000₽ (макс)

---

## 🎯 Sprint Overview

| Sprint | Фокус | Длительность | Приоритет | Агенты |
|--------|-------|--------------|-----------|--------|
| **Week 1** | Foundation & High Priority | 5 дней | 🔴 Critical | All |
| **Week 2** | Payment & Analytics | 5 дней | 🟠 High | Backend, Frontend |
| **Week 3** | AI Agent System & CRM | 5 дней | 🔴 Critical | Backend, AI |
| **Week 4** | Omnichannel & Self-Healing | 5 дней | 🔴 Critical | Backend, AI |
| **Week 5** | Business Docs & Polish | 5 дней | 🟠 High | All |
| **Week 6** | Final Testing & Launch | 5 дней | 🔴 Critical | All |

---

## Week 1: Foundation & High Priority Integrations

**Цель**: Настроить базовую инфраструктуру и критически важные интеграции
**Статус**: 🚧 Pending
**Completion Criteria**: Database running, i18next setup, Vault working, Novu sending notifications, Rate limiting active

---

### Day 1: Database & Infrastructure Setup

#### Task 1.1: Supabase/PostgreSQL Setup
**Assignee**: Backend Developer 1 (GPT)
**Duration**: 2 hours
**Priority**: 🔴 Critical
**Dependencies**: None

**Description**:
Настроить PostgreSQL базу данных (Supabase или Docker Compose)

**Steps**:
1. Выбрать опцию:
   - **Option A**: Создать проект на supabase.com (рекомендуется для production)
   - **Option B**: Запустить Docker Compose (для local dev)
2. Обновить `.env` с credentials
3. Запустить `npx prisma generate`
4. Запустить `npx prisma migrate dev`
5. Запустить seed: `npm run db:seed`
6. Проверить connection: `npm run test:connection`

**Acceptance Criteria**:
- ✅ PostgreSQL доступен
- ✅ Все 9 таблиц созданы
- ✅ RLS policies активны
- ✅ Seed data загружен (2 тенанта, 10 клиентов)
- ✅ Connection test проходит

**Reference**:
- [Docker Compose Setup Guide](file://c:/Users/Nicita/beauty-salon-saas/docs/deployment/docker-compose-setup.md)
- [Supabase Setup Guide](file://c:/Users/Nicita/beauty-salon-saas/docs/deployment/supabase-setup.md)
- Database package: `packages/database/`

---

#### Task 1.2: Redis Setup
**Assignee**: Backend Developer 1 (GPT)
**Duration**: 30 minutes
**Priority**: 🔴 Critical
**Dependencies**: None (параллельно с 1.1)

**Description**:
Настроить Redis для кеширования и очередей

**Steps**:
1. Запустить Redis через Docker Compose: `docker-compose up -d redis`
2. Проверить доступность: `redis-cli ping` (должен вернуть PONG)
3. Открыть Redis Commander: http://localhost:8081
4. Создать тестовое подключение в коде

**Acceptance Criteria**:
- ✅ Redis running
- ✅ Redis Commander доступен
- ✅ Connection test проходит

---

#### Task 1.3: Monorepo Setup Verification
**Assignee**: Backend Developer 1 (GPT)
**Duration**: 30 minutes
**Priority**: 🟠 High
**Dependencies**: None (параллельно)

**Description**:
Проверить, что monorepo корректно настроен

**Steps**:
1. `npm install` в root
2. `npm run build` (должен собрать все packages)
3. Проверить, что `@beauty-salon/database` импортируется

**Acceptance Criteria**:
- ✅ All packages installed
- ✅ Build проходит без ошибок
- ✅ TypeScript типы работают

---

### Day 2: Quick Wins - i18next & Secrets

#### Task 2.1: i18next Setup (Localization)
**Assignee**: Frontend Developer (GPT)
**Duration**: 2 hours
**Priority**: 🔴 Critical
**Dependencies**: Task 1.3 (monorepo ready)

**Description**:
Настроить i18next для мультиязычности (RU/EN)

**Steps**:
1. Install: `npm install i18next react-i18next next-i18next`
2. Создать `packages/localization/src/i18n.config.ts`
3. Создать translation files:
   - `public/locales/ru/common.json`
   - `public/locales/en/common.json`
   - `public/locales/ru/appointments.json`
   - `public/locales/en/appointments.json`
4. Wrap Next.js app в I18nextProvider
5. Migrate 10-20 hardcoded strings в translations
6. Добавить language switcher

**Acceptance Criteria**:
- ✅ i18next configured
- ✅ Translation files created (RU/EN)
- ✅ Language switching works
- ✅ No hardcoded strings в примерах
- ✅ TypeScript types для translations

**Reference**:
- [ADR-010: Localization Strategy](file://c:/Users/Nicita/beauty-salon-saas/docs/architecture/ADR-010-localization-strategy.md)

**Code Location**:
- `packages/localization/`
- `apps/admin-panel/app/`

---

#### Task 2.2: Supabase Vault Setup (Secrets Management)
**Assignee**: Backend Developer 1 (GPT)
**Duration**: 4 hours
**Priority**: 🔴 Critical
**Dependencies**: Task 1.1 (PostgreSQL ready)

**Description**:
Настроить Supabase Vault для безопасного хранения secrets

**Steps**:
1. Enable pgsodium extension в Supabase SQL Editor:
   ```sql
   CREATE EXTENSION IF NOT EXISTS pgsodium;
   ```
2. Create vault schema (run SQL из ADR-012)
3. Create `packages/secrets/src/vault-client.ts`
4. Create setup script: `scripts/setup-secrets.ts`
5. Migrate secrets из `.env` в Vault:
   - `stripe_secret_key`
   - `novu_api_key`
   - `jwt_secret`
   - `metabase_embedding_secret`
6. Обновить код для чтения из Vault вместо env vars
7. Remove secrets из `.env` (оставить только `.env.example`)

**Acceptance Criteria**:
- ✅ pgsodium extension enabled
- ✅ Vault schema created
- ✅ VaultClient working
- ✅ Platform secrets migrated (5+ secrets)
- ✅ Code reads from Vault
- ✅ Audit log working
- ✅ Zero secrets в `.env` files

**Reference**:
- [ADR-012: Secrets Management](file://c:/Users/Nicita/beauty-salon-saas/docs/architecture/ADR-012-secrets-management.md)

**Code Location**:
- `packages/secrets/`
- `scripts/setup-secrets.ts`

---

### Day 3: Novu Integration (Notifications)

#### Task 3.1: Novu Infrastructure Setup
**Assignee**: Backend Developer 2 (GPT)
**Duration**: 4 hours
**Priority**: 🔴 Critical
**Dependencies**: Task 1.1 (PostgreSQL), Task 1.2 (Redis)

**Description**:
Развернуть Novu notification infrastructure

**Steps**:
1. Добавить Novu services в docker-compose.yml:
   - novu-api
   - novu-worker
   - novu-web (UI)
2. Start services: `docker-compose up -d novu-api novu-worker novu-web`
3. Open Novu Web UI: http://localhost:3002
4. Create API key в Novu UI
5. Store API key в Vault: `await vault.setSecret('novu_api_key', key)`
6. Verify Novu API responding

**Acceptance Criteria**:
- ✅ Novu services running
- ✅ Novu Web UI accessible
- ✅ API key created и stored в Vault
- ✅ Health check passes

**Reference**:
- [ADR-007: Notification Infrastructure](file://c:/Users/Nicita/beauty-salon-saas/docs/architecture/ADR-007-notification-infrastructure.md)

**Code Location**:
- `docker-compose.yml` (update)

---

#### Task 3.2: Novu SDK Integration
**Assignee**: Backend Developer 2 (GPT)
**Duration**: 4 hours
**Priority**: 🔴 Critical
**Dependencies**: Task 3.1 (Novu running)

**Description**:
Интегрировать Novu SDK в backend

**Steps**:
1. Install: `npm install @novu/node`
2. Create `packages/notifications/src/novu-client.ts`
3. Create `packages/notifications/src/notification-service.ts`
4. Implement workflows:
   - `REMINDER_24H`
   - `REMINDER_1H`
   - `CONFIRM_RESCHEDULE`
5. Create notification templates в Novu Web UI (RU/EN)
6. Test sending notification

**Acceptance Criteria**:
- ✅ Novu SDK integrated
- ✅ NotificationService created
- ✅ 3+ workflow templates created
- ✅ Test notification sent successfully
- ✅ Templates support RU/EN

**Reference**:
- [ADR-007: Notification Infrastructure](file://c:/Users/Nicita/beauty-salon-saas/docs/architecture/ADR-007-notification-infrastructure.md)

**Code Location**:
- `packages/notifications/`

---

### Day 4: Rate Limiting Implementation

#### Task 4.1: Rate Limiter Package Setup
**Assignee**: Backend Developer 3 (GPT)
**Duration**: 3 hours
**Priority**: 🟠 High
**Dependencies**: Task 1.2 (Redis)

**Description**:
Создать rate limiting package с 3-уровневой системой

**Steps**:
1. Install: `npm install rate-limiter-flexible`
2. Create `packages/rate-limiting/src/redis.ts`
3. Create `packages/rate-limiting/src/client-limiters.ts` (Level 1)
4. Create `packages/rate-limiting/src/tenant-limiters.ts` (Level 2)
5. Create `packages/rate-limiting/src/channel-limiters.ts` (Level 3)
6. Create `packages/rate-limiting/src/middleware.ts`
7. Write unit tests

**Acceptance Criteria**:
- ✅ rate-limiter-flexible integrated
- ✅ 3 levels implemented (client, tenant, channel)
- ✅ Middleware created
- ✅ Unit tests pass
- ✅ Redis connection working

**Reference**:
- [ADR-011: Rate Limiting Strategy](file://c:/Users/Nicita/beauty-salon-saas/docs/architecture/ADR-011-rate-limiting-strategy.md)

**Code Location**:
- `packages/rate-limiting/`

---

#### Task 4.2: Rate Limiting Integration
**Assignee**: Backend Developer 3 (GPT)
**Duration**: 2 hours
**Priority**: 🟠 High
**Dependencies**: Task 4.1 (Rate limiter package)

**Description**:
Интегрировать rate limiting в API routes и notification service

**Steps**:
1. Add rate limit middleware в API routes
2. Update NotificationService для использования limiters
3. Test client limit (10 bookings/hour)
4. Test tenant limit (3000 TX msgs/day)
5. Test channel limit (30 msg/s Telegram)

**Acceptance Criteria**:
- ✅ API routes protected
- ✅ NotificationService uses limiters
- ✅ Client limit enforced
- ✅ Tenant limit enforced
- ✅ Channel limit enforced
- ✅ 429 errors returned correctly

**Code Location**:
- `apps/admin-panel/app/api/`
- `packages/notifications/`

---

### Day 5: Week 1 Testing & Validation

#### Task 5.1: Integration Testing
**Assignee**: Tester (Claude)
**Duration**: 4 hours
**Priority**: 🔴 Critical
**Dependencies**: All Week 1 tasks

**Description**:
Comprehensive testing всех Week 1 интеграций

**Test Scenarios**:
1. **Database**:
   - Connection stable
   - RLS policies work (tenant isolation)
   - Seed data correct

2. **i18next**:
   - Language switching works
   - Translations loaded
   - No missing keys

3. **Vault**:
   - Secrets stored encrypted
   - VaultClient works
   - Audit log populated

4. **Novu**:
   - Notifications send successfully
   - Templates render (RU/EN)
   - Delivery tracking works

5. **Rate Limiting**:
   - Client limit enforced
   - Tenant limit enforced
   - Channel limit enforced

**Acceptance Criteria**:
- ✅ All tests pass
- ✅ No critical bugs
- ✅ Performance acceptable (p95 < 200ms)

**Reference**:
- Testing strategies в каждом ADR

---

#### Task 5.2: Week 1 Validation & Sign-off
**Assignee**: Validator (Claude)
**Duration**: 2 hours
**Priority**: 🔴 Critical
**Dependencies**: Task 5.1 (Testing complete)

**Description**:
Final validation Week 1 deliverables

**Validation Checklist**:
- ✅ Database running stably
- ✅ i18next works (RU/EN switching)
- ✅ Vault stores secrets securely
- ✅ Novu sends notifications
- ✅ Rate limiting active (3 levels)
- ✅ All tests pass
- ✅ Documentation updated
- ✅ Code quality acceptable

**Deliverables**:
- Week 1 completion report
- Known issues log
- Week 2 readiness confirmation

---

## Week 2: Payment & Analytics

**Цель**: Реализовать payment processing и analytics dashboards
**Статус**: 📅 Scheduled
**Completion Criteria**: Stripe payments working, Metabase dashboards embedded

---

### Day 6-7: Stripe Integration

#### Task 6.1: Stripe Account Setup
**Assignee**: Backend Developer 1 (GPT)
**Duration**: 1 hour
**Priority**: 🟠 High
**Dependencies**: Week 1 complete

**Description**:
Настроить Stripe account и API keys

**Steps**:
1. Create Stripe account (stripe.com)
2. Get test API keys (pk_test_..., sk_test_...)
3. Store secret key в Vault: `stripe_secret_key`
4. Store webhook secret в Vault: `stripe_webhook_secret`
5. Configure webhook endpoint URL

**Acceptance Criteria**:
- ✅ Stripe account created
- ✅ Test keys obtained
- ✅ Keys stored в Vault
- ✅ Webhook endpoint configured

**Reference**:
- [ADR-009: Payment Processing](file://c:/Users/Nicita/beauty-salon-saas/docs/architecture/ADR-009-payment-processing.md)

---

#### Task 6.2: Stripe Backend Integration
**Assignee**: Backend Developer 1 (GPT)
**Duration**: 6 hours
**Priority**: 🟠 High
**Dependencies**: Task 6.1

**Description**:
Implement payment processing backend

**Steps**:
1. Install: `npm install stripe`
2. Create `packages/payments/src/stripe-client.ts`
3. Create `packages/payments/src/payment-service.ts`:
   - `createPaymentIntent()`
   - `handlePaymentSucceeded()`
   - `handlePaymentFailed()`
   - `refundPayment()`
4. Create webhook handler: `app/api/webhooks/stripe/route.ts`
5. Update Prisma schema (add payment fields)
6. Write tests

**Acceptance Criteria**:
- ✅ Stripe SDK integrated
- ✅ PaymentService working
- ✅ Webhook handler created
- ✅ Database schema updated
- ✅ Tests pass

**Code Location**:
- `packages/payments/`
- `apps/admin-panel/app/api/webhooks/stripe/`

---

#### Task 6.3: Stripe Frontend Integration
**Assignee**: Frontend Developer (GPT)
**Duration**: 4 hours
**Priority**: 🟠 High
**Dependencies**: Task 6.2

**Description**:
Implement Stripe Elements для payment form

**Steps**:
1. Install: `npm install @stripe/stripe-js @stripe/react-stripe-js`
2. Create `components/payments/payment-form.tsx`
3. Create payment page: `app/appointments/[id]/payment/page.tsx`
4. Create success page: `app/appointments/payment-success/page.tsx`
5. Test payment flow end-to-end

**Acceptance Criteria**:
- ✅ Payment form renders
- ✅ Stripe Elements работают
- ✅ Test payment succeeds
- ✅ Webhook updates database
- ✅ Success page shows

**Code Location**:
- `apps/admin-panel/components/payments/`
- `apps/admin-panel/app/appointments/`

---

### Day 8-9: Metabase Integration

#### Task 7.1: Metabase Deployment
**Assignee**: Backend Developer 2 (GPT)
**Duration**: 2 hours
**Priority**: 🟡 Medium
**Dependencies**: Week 1 complete

**Description**:
Deploy Metabase via Docker Compose

**Steps**:
1. Add Metabase service в docker-compose.yml
2. Start Metabase: `docker-compose up -d metabase`
3. Open Metabase UI: http://localhost:3004
4. Complete setup wizard
5. Connect to PostgreSQL database
6. Create metabase_user в PostgreSQL (read-only)
7. Store embedding secret в Vault

**Acceptance Criteria**:
- ✅ Metabase running
- ✅ PostgreSQL connected
- ✅ Metabase user created
- ✅ Embedding secret stored

**Reference**:
- [ADR-008: Analytics Platform](file://c:/Users/Nicita/beauty-salon-saas/docs/architecture/ADR-008-analytics-platform.md)

---

#### Task 7.2: Metabase Dashboards Creation
**Assignee**: Backend Developer 2 (GPT)
**Duration**: 6 hours
**Priority**: 🟡 Medium
**Dependencies**: Task 7.1

**Description**:
Создать 4 core dashboards в Metabase

**Steps**:
1. Create Dashboard 1: Overview
   - Total appointments
   - Completion rate
   - Revenue metrics
2. Create Dashboard 2: Money Dashboard
   - Daily revenue trend
   - Lost revenue (no-shows, cancellations)
   - Revenue forecast
3. Create Dashboard 3: Clients Dashboard
   - Client retention
   - Inactive clients (win-back candidates)
   - VIP clients
4. Create Dashboard 4: Staff Performance
   - Staff load distribution
   - Revenue per staff
   - Completion rate per staff

**Acceptance Criteria**:
- ✅ 4 dashboards created
- ✅ All queries use tenant_id (RLS)
- ✅ Visualizations configured
- ✅ Date filters working

**Code Location**:
- Metabase Web UI (configuration)

---

#### Task 7.3: Metabase Embedding
**Assignee**: Frontend Developer (GPT)
**Duration**: 4 hours
**Priority**: 🟡 Medium
**Dependencies**: Task 7.2

**Description**:
Embed Metabase dashboards в Next.js admin panel

**Steps**:
1. Create `packages/analytics/src/metabase-client.ts`
2. Implement `generateEmbedUrl()` with JWT signing
3. Create API route: `app/api/analytics/dashboard/route.ts`
4. Create component: `components/analytics/dashboard-embed.tsx`
5. Create analytics page: `app/analytics/page.tsx`
6. Test embedding for 4 dashboards

**Acceptance Criteria**:
- ✅ JWT signing works
- ✅ Embed URLs generated
- ✅ Dashboards render в iframe
- ✅ Tenant isolation works
- ✅ All 4 dashboards accessible

**Code Location**:
- `packages/analytics/`
- `apps/admin-panel/app/analytics/`

---

### Day 10: Week 2 Testing & Validation

#### Task 8.1: Payment Testing
**Assignee**: Tester (Claude)
**Duration**: 2 hours
**Priority**: 🟠 High

**Test Scenarios**:
1. Create payment intent
2. Complete payment (test card: 4242 4242 4242 4242)
3. Verify webhook received
4. Verify database updated
5. Test failed payment (card: 4000 0000 0000 0002)
6. Test refund

**Acceptance Criteria**:
- ✅ All payment scenarios pass
- ✅ Webhook processing < 5s
- ✅ No data loss

---

#### Task 8.2: Analytics Testing
**Assignee**: Tester (Claude)
**Duration**: 2 hours
**Priority**: 🟠 High

**Test Scenarios**:
1. Load each dashboard
2. Verify tenant isolation (switch tenants, data changes)
3. Check query performance (<5s)
4. Test date filters
5. Verify calculations correct

**Acceptance Criteria**:
- ✅ All dashboards load
- ✅ Tenant isolation works
- ✅ Performance acceptable
- ✅ Data accurate

---

#### Task 8.3: Week 2 Validation
**Assignee**: Validator (Claude)
**Duration**: 2 hours

**Validation Checklist**:
- ✅ Stripe payments working
- ✅ Webhooks processing
- ✅ Metabase dashboards embedded
- ✅ Tenant isolation verified
- ✅ All tests pass

---

## Week 3: AI Agent Creation System & CRM Integration

**Цель**: Реализовать систему создания AI-агентов для владельцев салонов + CRM интеграцию
**Статус**: 📅 Scheduled
**Completion Criteria**: Salon owners can create AI agents, CRM import/export works, CrewAI integrated

**⚠️ КРИТИЧЕСКАЯ ФИЧА**: Это AI-first платформа - владельцы салонов создают AI-агентов для автоматизации

---

### Day 11-12: AI Agent Creation System (для владельцев салонов)

#### Task 9.1: AI Agent Creation UI
**Assignee**: Frontend Developer (GPT)
**Duration**: 6 hours
**Priority**: 🔴 Critical

**Description**:
Создать UI для владельцев салонов для создания и настройки AI-агентов

**Steps**:
1. Create page: `app/agents/create/page.tsx`
2. Create form для agent configuration:
   - Agent name
   - Agent personality (friendly, professional, casual)
   - Services knowledge (auto-import from tenant services)
   - Business hours
   - Language preferences (RU/EN)
   - Response templates
3. Create agent management dashboard: `app/agents/page.tsx`
4. Create agent preview/testing interface
5. Add agent status indicator (active/inactive)

**Acceptance Criteria**:
- ✅ Create agent form works
- ✅ Agent configuration saved
- ✅ Agent list displayed
- ✅ Agent preview works
- ✅ Agent can be activated/deactivated

**Code Location**:
- `apps/admin-panel/app/agents/`
- `apps/admin-panel/components/agents/`

---

#### Task 9.2: AI Agent Configuration Backend
**Assignee**: Backend Developer 3 (GPT)
**Duration**: 6 hours
**Priority**: 🔴 Critical

**Description**:
Создать backend API для управления AI-агентами

**Steps**:
1. Add `ai_agents` table to Prisma schema:
   ```prisma
   model AIAgent {
     id           String   @id @default(uuid())
     tenant_id    String
     name         String
     personality  String
     config       Json     // agent configuration
     is_active    Boolean  @default(false)
     created_at   DateTime @default(now())
     updated_at   DateTime @updatedAt
   }
   ```
2. Create API routes:
   - `POST /api/agents` - create agent
   - `GET /api/agents` - list agents
   - `PUT /api/agents/:id` - update agent
   - `DELETE /api/agents/:id` - delete agent
   - `POST /api/agents/:id/activate` - activate agent
3. Implement agent configuration validation
4. Create agent template library (3-5 pre-built personalities)

**Acceptance Criteria**:
- ✅ Database schema updated
- ✅ CRUD API working
- ✅ Agent templates available
- ✅ Validation works
- ✅ RLS policies applied

**Code Location**:
- `packages/database/prisma/schema.prisma`
- `apps/admin-panel/app/api/agents/`

---

#### Task 9.3: CrewAI Integration
**Assignee**: Backend Developer 3 (GPT)
**Duration**: 4 hours
**Priority**: 🟡 Medium

**Description**:
Setup CrewAI framework для AI agents

**Steps**:
1. Install: `pip install crewai langchain openai`
2. Create `apps/ai-orchestrator/` (Python project)
3. Create `agents/booking_agent.py`
4. Create `agents/support_agent.py`
5. Create `agents/marketing_agent.py`
6. Configure OpenAI API key (store в Vault)
7. Test simple agent response

**Acceptance Criteria**:
- ✅ CrewAI installed
- ✅ 3 agents created
- ✅ OpenAI API key configured
- ✅ Test query responds

**Reference**:
- Architecture.md Section 5 (AI Agents)

---

#### Task 9.4: AI Agents Tools Implementation
**Assignee**: Backend Developer 3 (GPT)
**Duration**: 6 hours
**Priority**: 🔴 Critical

**Description**:
Implement tools для AI agents (для booking, CRM, messages)

**Steps**:
1. Create `tools/search_slots_tool.py`
2. Create `tools/create_appointment_tool.py`
3. Create `tools/send_message_tool.py`
4. Create `tools/create_case_tool.py`
5. Create `tools/query_services_tool.py`
6. Integrate tools с agents
7. Test agent using tools end-to-end

**Acceptance Criteria**:
- ✅ 5+ tools implemented
- ✅ Tools work correctly
- ✅ Agents use tools autonomously
- ✅ End-to-end booking flow works
- ✅ Error handling implemented

**Code Location**:
- `apps/ai-orchestrator/tools/`

---

#### Task 9.5: AI Provider Multi-Fallback System ⚠️ NEW
**Assignee**: Backend Developer 3 (GPT)
**Duration**: 6 hours
**Priority**: 🔴 Critical

**⚠️ КРИТИЧЕСКИ ВАЖНО**:
- **Primary AI Provider**: DeepSeek (самая дешевая нейросеть)
- **NOT OpenAI as primary** - OpenAI только как fallback
- Резервные ключи для каждого провайдера

**Description**:
Создать систему автоматического переключения между AI провайдерами (DeepSeek → OpenAI → Claude → Gemini)

**Steps**:
1. Create `packages/ai-providers/` package
2. Install providers:
   ```bash
   pip install openai anthropic google-generativeai
   # DeepSeek uses OpenAI-compatible API
   ```
3. Create provider adapters:
   - `src/providers/deepseek-adapter.ts` - Primary (OpenAI-compatible API)
   - `src/providers/openai-adapter.ts` - Fallback #1
   - `src/providers/claude-adapter.ts` - Fallback #2
   - `src/providers/gemini-adapter.ts` - Fallback #3
4. Create provider manager:
   ```python
   # apps/ai-orchestrator/providers/manager.py
   class AIProviderManager:
       def __init__(self):
           self.providers = [
               DeepSeekProvider(priority=1, cost_per_1k_tokens=0.001),
               OpenAIProvider(priority=2, cost_per_1k_tokens=0.002),
               ClaudeProvider(priority=3, cost_per_1k_tokens=0.008),
               GeminiProvider(priority=4, cost_per_1k_tokens=0.0005),
           ]
           self.current_provider = self.providers[0]  # DeepSeek

       async def send_message(self, messages, retry=True):
           try:
               response = await self.current_provider.chat(messages)
               return response
           except Exception as e:
               if retry and len(self.providers) > 1:
                   # Fallback to next provider
                   self.current_provider = self.providers[1]
                   return await self.send_message(messages, retry=False)
               raise e
   ```
5. Store API keys в Vault:
   - `deepseek_api_key` (primary)
   - `openai_api_key` (fallback 1)
   - `anthropic_api_key` (fallback 2)
   - `google_api_key` (fallback 3)
6. Add health check для каждого провайдера (каждые 5 min)
7. Log provider usage statistics (provider, cost, response time, success rate)

**Acceptance Criteria**:
- ✅ DeepSeek configured as primary
- ✅ 3 fallback providers configured
- ✅ Automatic failover working (DeepSeek fails → switches to OpenAI)
- ✅ All API keys stored в Vault
- ✅ Health checks running
- ✅ Usage statistics logged
- ✅ Cost tracking per provider

**Fallback Logic**:
1. Try DeepSeek (cheapest)
2. If DeepSeek fails → OpenAI
3. If OpenAI fails → Claude
4. If Claude fails → Gemini
5. If all fail → escalate to owner via Telegram

**Cost Comparison** (per 1M tokens):
- DeepSeek: ~$1 (PRIMARY)
- Gemini: ~$0.5
- OpenAI GPT-4o-mini: ~$2
- Claude Haiku: ~$8

**Code Location**:
- `packages/ai-providers/`
- `apps/ai-orchestrator/providers/`

---

#### Task 9.6: Conversation State Management ⚠️ NEW
**Assignee**: Backend Developer 3 (GPT)
**Duration**: 4 hours
**Priority**: 🔴 Critical

**Description**:
Реализовать систему сохранения контекста разговоров между сообщениями

**Steps**:
1. Add `conversation_history` table to Prisma schema:
   ```prisma
   model ConversationHistory {
     id            String   @id @default(uuid())
     tenant_id     String
     client_phone  String
     agent_id      String   // AI agent ID
     messages      Json     // Array of {role, content, timestamp}
     last_message_at DateTime @default(now())
     created_at    DateTime @default(now())

     @@index([tenant_id, client_phone])
     @@index([last_message_at])
   }
   ```
2. Implement Redis caching для active conversations:
   ```typescript
   // Cache key: `conversation:{tenant_id}:{client_phone}`
   // TTL: 24 hours
   interface CachedConversation {
     messages: Array<{role: 'user' | 'assistant', content: string, timestamp: string}>
     agentId: string
     lastMessageAt: string
   }
   ```
3. Create conversation manager:
   ```python
   # apps/ai-orchestrator/conversation/manager.py
   class ConversationManager:
       async def get_context(self, tenant_id, client_phone):
           # Try Redis first (fast)
           cached = await redis.get(f"conversation:{tenant_id}:{client_phone}")
           if cached:
               return json.loads(cached)

           # Fallback to PostgreSQL
           history = await db.conversation_history.findFirst({
               where: {tenant_id, client_phone},
               orderBy: {last_message_at: 'desc'}
           })

           if history:
               # Restore to Redis
               await redis.setex(
                   f"conversation:{tenant_id}:{client_phone}",
                   86400,  # 24h TTL
                   json.dumps(history.messages)
               )
               return history.messages

           return []  # New conversation

       async def add_message(self, tenant_id, client_phone, role, content):
           messages = await self.get_context(tenant_id, client_phone)
           messages.append({
               'role': role,
               'content': content,
               'timestamp': datetime.utcnow().isoformat()
           })

           # Keep only last 20 messages (context window limit)
           if len(messages) > 20:
               messages = messages[-20:]

           # Update Redis
           await redis.setex(
               f"conversation:{tenant_id}:{client_phone}",
               86400,
               json.dumps(messages)
           )

           # Update PostgreSQL (async background job)
           await db.conversation_history.upsert({
               where: {tenant_id, client_phone},
               update: {
                   messages: messages,
                   last_message_at: datetime.utcnow()
               },
               create: {
                   tenant_id,
                   client_phone,
                   messages: messages
               }
           })
   ```
4. Implement conversation cleanup (delete conversations older than 30 days)
5. Add RLS policies для conversation_history table

**Acceptance Criteria**:
- ✅ Conversation history stored (Redis + PostgreSQL)
- ✅ Context preserved between messages
- ✅ Last 20 messages retained
- ✅ Redis caching working (fast retrieval)
- ✅ PostgreSQL fallback working
- ✅ Old conversations cleaned up (30 days)
- ✅ RLS policies applied

**Code Location**:
- `packages/database/prisma/schema.prisma`
- `apps/ai-orchestrator/conversation/`

---

#### Task 9.7: Multi-Agent Selection Logic ⚠️ NEW
**Assignee**: Backend Developer 3 (GPT)
**Duration**: 3 hours
**Priority**: 🟠 High

**Description**:
Реализовать логику выбора правильного AI агента для клиента

**Steps**:
1. Create agent selector:
   ```python
   # apps/ai-orchestrator/agent-selector.py
   class AgentSelector:
       async def select_agent(self, tenant_id, client_phone, message):
           # Get all active agents for tenant
           agents = await db.ai_agents.findMany({
               where: {tenant_id, is_active: true}
           })

           if len(agents) == 0:
               raise NoActiveAgentError("No active AI agents")

           if len(agents) == 1:
               return agents[0]  # Only one agent

           # Multiple agents - intelligent selection

           # Strategy 1: Check conversation history (sticky agent)
           history = await conversation_manager.get_context(tenant_id, client_phone)
           if history and 'agent_id' in history:
               agent = next((a for a in agents if a.id == history['agent_id']), None)
               if agent:
                   return agent  # Continue with same agent

           # Strategy 2: Intent classification (simple keyword matching)
           message_lower = message.lower()
           if any(word in message_lower for word in ['запись', 'записаться', 'booking', 'appointment']):
               # Booking intent → prefer booking specialist
               booking_agent = next((a for a in agents if 'booking' in a.name.lower()), None)
               if booking_agent:
                   return booking_agent

           if any(word in message_lower for word in ['скидка', 'акция', 'promo', 'discount']):
               # Marketing intent → prefer marketing specialist
               marketing_agent = next((a for a in agents if 'marketing' in a.name.lower()), None)
               if marketing_agent:
                   return marketing_agent

           # Strategy 3: Load balancing (least recently used)
           agent_usage = await redis.get(f"agent_usage:{tenant_id}")
           if agent_usage:
               usage_counts = json.loads(agent_usage)
               least_used = min(agents, key=lambda a: usage_counts.get(a.id, 0))
               return least_used

           # Default: first agent
           return agents[0]
   ```
2. Track agent usage statistics (для load balancing)
3. Add agent performance metrics (response time, success rate)
4. Implement agent failover (if agent fails, try another)

**Acceptance Criteria**:
- ✅ Agent selection working
- ✅ Sticky sessions (same client → same agent)
- ✅ Intent-based routing working
- ✅ Load balancing between agents
- ✅ Agent failover implemented
- ✅ Performance metrics tracked

**Code Location**:
- `apps/ai-orchestrator/agent-selector.py`

---

#### Task 9.8: AI Cost Management & Rate Limiting ⚠️ NEW
**Assignee**: Backend Developer 3 (GPT)
**Duration**: 4 hours
**Priority**: 🔴 Critical

**Description**:
Реализовать систему контроля затрат на AI API и rate limiting

**Steps**:
1. Create cost tracker:
   ```typescript
   // packages/ai-cost-tracker/src/index.ts
   interface CostEntry {
     tenantId: string
     provider: 'deepseek' | 'openai' | 'claude' | 'gemini'
     model: string
     inputTokens: number
     outputTokens: number
     cost: number  // in USD
     timestamp: Date
   }

   class CostTracker {
     async logUsage(entry: CostEntry) {
       // Save to database
       await prisma.aiUsageLog.create({data: entry})

       // Update tenant daily budget
       const today = new Date().toISOString().split('T')[0]
       const spent = await redis.incrbyfloat(
         `ai_cost:${entry.tenantId}:${today}`,
         entry.cost
       )

       // Check budget limit
       const budget = await this.getTenantBudget(entry.tenantId)
       if (spent > budget) {
         throw new BudgetExceededError(`Daily budget exceeded: ${spent}/${budget}`)
       }
     }
   }
   ```
2. Add `ai_usage_log` table:
   ```prisma
   model AIUsageLog {
     id            String   @id @default(uuid())
     tenant_id     String
     provider      String
     model         String
     input_tokens  Int
     output_tokens Int
     cost_usd      Decimal  @db.Decimal(10, 6)
     created_at    DateTime @default(now())

     @@index([tenant_id, created_at])
   }
   ```
3. Implement tenant AI budgets:
   - Tier 1 (15k₽): 50 AI requests/day, $5/day budget
   - Tier 2 (25k₽): 200 AI requests/day, $20/day budget
   - Tier 3 (50k₽): Unlimited requests, $100/day budget
4. Add AI rate limiting (rate-limiter-flexible):
   ```typescript
   // Level 1: Per tenant (daily)
   const tenantAILimiter = new RateLimiterRedis({
     storeClient: redis,
     keyPrefix: 'rl:ai:tenant',
     points: 200,  // 200 requests
     duration: 86400,  // per day
   })

   // Level 2: Per client (hourly - prevent spam)
   const clientAILimiter = new RateLimiterRedis({
     keyPrefix: 'rl:ai:client',
     points: 10,  // 10 messages
     duration: 3600,  // per hour
   })
   ```
5. Create FAQ cache (Redis) для frequently asked questions:
   ```typescript
   // Если вопрос в кэше → ответить без AI API (cost = $0)
   const cachedAnswer = await redis.get(`faq:${tenant_id}:${questionHash}`)
   if (cachedAnswer) {
     return cachedAnswer  // No AI API call needed!
   }
   ```
6. Add cost analytics dashboard в Admin Panel

**Acceptance Criteria**:
- ✅ Cost tracking working (per tenant, per provider)
- ✅ Daily budgets enforced
- ✅ Rate limiting active (tenant + client levels)
- ✅ FAQ caching implemented
- ✅ Budget exceeded notifications sent
- ✅ Cost analytics dashboard working

**Cost Optimization Strategies**:
- ✅ Use DeepSeek (cheapest) as primary
- ✅ Cache FAQ responses (reduce API calls by 30-50%)
- ✅ Limit conversation history to 20 messages (reduce token usage)
- ✅ Rate limit clients (prevent spam/abuse)

**Code Location**:
- `packages/ai-cost-tracker/`
- `apps/admin-panel/app/analytics/ai-costs/`

---

#### Task 9.9: AI Response Quality Monitoring ⚠️ NEW
**Assignee**: Backend Developer 2 (GPT)
**Duration**: 3 hours
**Priority**: 🟡 Medium

**Description**:
Мониторинг качества ответов AI и feedback loop для улучшения

**Steps**:
1. Add `ai_response_log` table:
   ```prisma
   model AIResponseLog {
     id              String   @id @default(uuid())
     tenant_id       String
     agent_id        String
     client_phone    String
     user_message    String
     ai_response     String
     provider        String
     response_time_ms Int
     success         Boolean  @default(true)
     escalated       Boolean  @default(false)
     created_at      DateTime @default(now())

     @@index([tenant_id, created_at])
     @@index([success])
   }
   ```
2. Track AI performance metrics:
   - Response time (target: <3s)
   - Success rate (AI answered correctly vs escalated to human)
   - Escalation rate (% of conversations escalated)
3. Implement feedback collection:
   - After booking: "Оцените работу ассистента (1-5)"
   - Store ratings в database
4. Create alert system (if success rate < 80% → notify owner)
5. Create AI performance dashboard (Admin Panel)

**Acceptance Criteria**:
- ✅ All AI responses logged
- ✅ Performance metrics calculated
- ✅ Feedback collection working
- ✅ Alerts configured (<80% success → notify)
- ✅ Performance dashboard accessible

**Code Location**:
- `packages/database/prisma/schema.prisma`
- `apps/admin-panel/app/analytics/ai-performance/`

---

### Day 13-14: CRM Integration (Import/Export)

#### Task 10.1: CRM Data Model & Migration Schema
**Assignee**: Backend Developer 1 (GPT)
**Duration**: 4 hours
**Priority**: 🔴 Critical

**Description**:
Создать универсальную схему для импорта/экспорта CRM данных

**Steps**:
1. Create `packages/crm-integration/` package
2. Define universal CRM schema (JSON):
   ```typescript
   interface CRMExport {
     clients: Array<{
       external_id: string
       name: string
       phone: string
       email?: string
       notes?: string
       tags?: string[]
       created_at: string
     }>
     appointments: Array<{
       external_id: string
       client_id: string
       service_name: string
       start_time: string
       duration_minutes: number
       price: number
       status: string
       notes?: string
     }>
   }
   ```
3. Create mappers для popular CRMs:
   - Generic CSV format
   - YCLIENTS format
   - Dikidi format
4. Create validation logic

**Acceptance Criteria**:
- ✅ Universal schema defined
- ✅ TypeScript types created
- ✅ 3+ format mappers ready
- ✅ Validation works

**Code Location**:
- `packages/crm-integration/`

---

#### Task 10.2: CRM Import Implementation
**Assignee**: Backend Developer 1 (GPT)
**Duration**: 6 hours
**Priority**: 🔴 Critical

**Description**:
Implement CRM data import from external systems

**Steps**:
1. Create API route: `POST /api/crm/import`
2. Implement file upload (CSV/JSON)
3. Implement parser для каждого формата
4. Create data mapping & validation
5. Implement batch insert (с RLS bypass для service role)
6. Create import progress tracking
7. Create import report (успешно/ошибки)

**Acceptance Criteria**:
- ✅ File upload works (CSV, JSON)
- ✅ Parsers work for 3+ formats
- ✅ Data validated before import
- ✅ Batch import working (100+ records)
- ✅ Progress tracking works
- ✅ Import report generated
- ✅ Duplicate detection works

**Code Location**:
- `apps/admin-panel/app/api/crm/import/`
- `packages/crm-integration/src/importers/`

---

#### Task 10.3: CRM Export Implementation
**Assignee**: Backend Developer 2 (GPT)
**Duration**: 4 hours
**Priority**: 🟠 High

**Description**:
Implement CRM data export to external systems

**Steps**:
1. Create API route: `GET /api/crm/export`
2. Implement query filters (date range, client segment, etc.)
3. Implement exporters:
   - CSV format
   - JSON format
   - Excel format (xlsx)
4. Add tenant_id filtering (RLS)
5. Create download endpoint

**Acceptance Criteria**:
- ✅ Export API working
- ✅ 3 formats supported (CSV, JSON, XLSX)
- ✅ Filtering works
- ✅ Tenant isolation enforced
- ✅ Large exports handled (1000+ records)

**Code Location**:
- `apps/admin-panel/app/api/crm/export/`
- `packages/crm-integration/src/exporters/`

---

#### Task 10.4: CRM Import/Export UI
**Assignee**: Frontend Developer (GPT)
**Duration**: 4 hours
**Priority**: 🟠 High

**Description**:
Create UI для CRM import/export

**Steps**:
1. Create page: `app/settings/crm-integration/page.tsx`
2. Create import wizard:
   - Step 1: Select CRM type
   - Step 2: Upload file
   - Step 3: Preview & validate
   - Step 4: Confirm & import
   - Step 5: View results
3. Create export form:
   - Select format (CSV/JSON/XLSX)
   - Date range filters
   - Client segment filters
   - Download button
4. Add import history table

**Acceptance Criteria**:
- ✅ Import wizard works
- ✅ File upload UI working
- ✅ Preview shows sample data
- ✅ Export form works
- ✅ Import history displayed

**Code Location**:
- `apps/admin-panel/app/settings/crm-integration/`
- `apps/admin-panel/components/crm/`

---

### Day 15: Week 3 Testing & Validation

#### Task 11.1: AI Agent System Testing
**Assignee**: Tester (Claude)
**Duration**: 3 hours
**Priority**: 🔴 Critical

**Test Scenarios**:
1. **Agent Creation**: Create new agent via UI → saved to DB
2. **Agent Configuration**: Update agent settings → changes applied
3. **Agent Activation**: Activate agent → AI starts responding
4. **AI Response Test**: Send test message → AI responds correctly
5. **Tool Execution**: AI books appointment → booking created in DB
6. **Service Knowledge**: AI answers service questions → accurate info
7. **Escalation**: Complex issue → AI creates case

**Acceptance Criteria**:
- ✅ Agent CRUD works
- ✅ AI responds autonomously
- ✅ Tools execute successfully
- ✅ Booking flow complete
- ✅ Escalation works
- ✅ Response time < 3s

---

#### Task 11.2: CRM Integration Testing
**Assignee**: Tester (Claude)
**Duration**: 2 hours
**Priority**: 🔴 Critical

**Test Scenarios**:
1. **Import CSV**: Upload CSV file → data imported
2. **Import YCLIENTS**: Upload YCLIENTS format → parsed correctly
3. **Import Validation**: Upload invalid data → errors shown
4. **Duplicate Detection**: Re-import same clients → duplicates detected
5. **Export CSV**: Export data → CSV generated
6. **Export Excel**: Export data → XLSX generated
7. **Tenant Isolation**: Export with tenant filter → correct data only

**Acceptance Criteria**:
- ✅ All import formats work
- ✅ Validation catches errors
- ✅ Duplicates detected
- ✅ All export formats work
- ✅ Tenant isolation enforced
- ✅ Large datasets handled (1000+ records)

---

#### Task 11.3: Week 3 Validation
**Assignee**: Validator (Claude)
**Duration**: 2 hours
**Priority**: 🔴 Critical

**Validation Checklist**:
- ✅ AI Agent Creation UI works
- ✅ AI agents respond autonomously
- ✅ CRM import/export functional
- ✅ CrewAI integrated
- ✅ All tests pass
- ✅ Documentation updated
- ✅ Code quality acceptable

---

## Week 4: Omnichannel Messaging & Self-Healing System

**Цель**: Интегрировать Telegram/WhatsApp + создать систему самовосстановления
**Статус**: 📅 Scheduled
**Completion Criteria**: Omnichannel works, System Monitor running 24/7, Auto-fix active, Telegram escalation works

**⚠️ КРИТИЧЕСКАЯ ФИЧА**: Self-Healing System - embedded product feature, runs 24/7 in client installations

---

### Day 16-17: Omnichannel Messaging (Chatwoot)

#### Task 12.1: Chatwoot Setup
**Assignee**: Backend Developer 1 (GPT)
**Duration**: 3 hours
**Priority**: 🔴 Critical

**Description**:
Deploy Chatwoot messaging hub для omnichannel communication

**Steps**:
1. Clone Chatwoot: `git clone https://github.com/chatwoot/chatwoot.git apps/messaging-hub`
2. Setup via Docker Compose
3. Complete initial setup wizard
4. Create API key
5. Store API key в Vault: `await vault.setSecret('chatwoot_api_key', key)`
6. Verify Chatwoot API responding

**Acceptance Criteria**:
- ✅ Chatwoot running on port 3000
- ✅ Web UI accessible
- ✅ API key created и stored в Vault
- ✅ Health check passes

**Code Location**:
- `apps/messaging-hub/` (Chatwoot clone)
- `docker-compose.yml` (update)

---

#### Task 12.2: Telegram Bot Integration
**Assignee**: Backend Developer 1 (GPT)
**Duration**: 4 hours
**Priority**: 🔴 Critical

**Description**:
Integrate Telegram bot via Chatwoot + connect to AI agents

**Steps**:
1. Create Telegram bot via BotFather
2. Add Telegram inbox в Chatwoot
3. Configure webhook (point to Chatwoot)
4. Connect Chatwoot to AI Orchestrator
5. Test message flow:
   - Client sends Telegram message
   - Chatwoot receives
   - AI Agent processes
   - AI response sent to client
6. Add rate limiting (30 msg/s Telegram limit)

**Acceptance Criteria**:
- ✅ Telegram bot created
- ✅ Messages received в Chatwoot
- ✅ AI Agent responds autonomously
- ✅ Messages sent from AI to Telegram
- ✅ Rate limiting active
- ✅ End-to-end flow < 5s

**Code Location**:
- `packages/messaging/src/telegram-handler.ts`

---

#### Task 12.3: WhatsApp Business API Integration
**Assignee**: Backend Developer 2 (GPT)
**Duration**: 4 hours
**Priority**: 🔴 Critical

**Description**:
Integrate WhatsApp Business API via Chatwoot

**Steps**:
1. Setup WhatsApp Business account (Meta Business Suite)
2. Get API credentials (Cloud API or 360Dialog)
3. Add WhatsApp inbox в Chatwoot
4. Configure webhook
5. Connect to AI Orchestrator (same as Telegram)
6. Test message flow
7. Add rate limiting (20 msg/s WhatsApp limit)

**Acceptance Criteria**:
- ✅ WhatsApp Business connected
- ✅ Messages received в Chatwoot
- ✅ AI Agent responds autonomously
- ✅ Messages sent from AI to WhatsApp
- ✅ Rate limiting respected
- ✅ Media messages supported (images)

**Code Location**:
- `packages/messaging/src/whatsapp-handler.ts`

---

### Day 18-19: Self-Healing System (Embedded Product Feature)

**⚠️ ВАЖНО**: Это НЕ dev tool - это фича продукта, которая работает 24/7 в установках клиентов

#### Task 13.1: System Monitor Backend Service
**Assignee**: Backend Developer 2 (GPT)
**Duration**: 6 hours
**Priority**: 🔴 Critical

**Description**:
Создать backend service для мониторинга системы 24/7 (embedded product feature)

**Steps**:
1. Create `packages/system-monitor/` package
2. Create monitoring service:
   - `src/health-checker.ts` - Check AI agents, API, database
   - `src/log-scanner.ts` - Scan logs for errors
   - `src/metrics-collector.ts` - Collect system metrics
3. Add database table `system_health_log`:
   ```prisma
   model SystemHealthLog {
     id          String   @id @default(uuid())
     tenant_id   String
     check_type  String   // "ai_agent", "api", "database", "error_log"
     status      String   // "healthy", "warning", "error"
     details     Json
     checked_at  DateTime @default(now())
   }
   ```
4. Implement health check schedule (every 5 minutes)
5. Define auto-fixable vs escalation scenarios
6. Add RLS policies

**Acceptance Criteria**:
- ✅ Health checks run every 5 min
- ✅ AI agent health monitored
- ✅ API availability monitored
- ✅ Log scanning working
- ✅ Metrics collected
- ✅ Database logging working

**Code Location**:
- `packages/system-monitor/`

---

#### Task 13.2: Auto-Fix System Implementation
**Assignee**: Backend Developer 2 (GPT)
**Duration**: 6 hours
**Priority**: 🔴 Critical

**Description**:
Создать систему автоматического исправления безопасных ошибок

**Steps**:
1. Create `packages/auto-fix/` package
2. Implement auto-fix strategies:
   - `src/fixes/restart-ai-agent.ts` - Restart stuck AI agent
   - `src/fixes/clear-cache.ts` - Clear corrupted cache
   - `src/fixes/retry-api-call.ts` - Retry failed API calls
   - `src/fixes/reset-rate-limiter.ts` - Reset stuck rate limiter
3. Add fix attempt tracking (max 3 attempts)
4. Implement rollback mechanism if fix fails
5. Log all fix attempts to database
6. **CRITICAL**: NEVER modify database directly (too risky)

**Acceptance Criteria**:
- ✅ 4+ auto-fix strategies implemented
- ✅ Max 3 attempts enforced
- ✅ Rollback mechanism works
- ✅ All fixes logged
- ✅ Database modifications blocked
- ✅ Failed fixes trigger escalation

**Code Location**:
- `packages/auto-fix/`

---

#### Task 13.3: Telegram Escalation Bot
**Assignee**: Backend Developer 3 (GPT)
**Duration**: 4 hours
**Priority**: 🔴 Critical

**Description**:
Создать Telegram bot для эскалации критических ошибок владельцу салона

**Steps**:
1. Create separate Telegram bot (BotFather) для системных уведомлений
2. Create `packages/escalation-bot/` package
3. Implement escalation service:
   - `src/telegram-notifier.ts` - Send alerts to owner
   - `src/escalation-rules.ts` - Define when to escalate
4. Escalation triggers:
   - Auto-fix failed after 3 attempts
   - Recurring same error (5+ times in 1 hour)
   - Critical system down (database, AI orchestrator)
5. Message format:
   ```
   🚨 CRITICAL ALERT
   Tenant: Beauty Studio Sample
   Issue: AI Agent не отвечает
   Attempts: 3/3 failed
   Time: 2026-01-23 14:30
   Action: Requires manual intervention
   ```
6. Store escalations in database

**Acceptance Criteria**:
- ✅ Telegram bot created
- ✅ Escalation rules working
- ✅ Owner receives alerts
- ✅ Message format clear
- ✅ Escalations logged
- ✅ No spam (rate limited to 1 msg/10 min max)

**Code Location**:
- `packages/escalation-bot/`

---

#### Task 13.4: Admin Health Dashboard
**Assignee**: Frontend Developer (GPT)
**Duration**: 4 hours
**Priority**: 🟠 High

**Description**:
Создать Admin Dashboard для просмотра здоровья системы

**Steps**:
1. Create page: `app/system-health/page.tsx`
2. Display metrics:
   - System status (healthy/warning/error)
   - AI agent status
   - API uptime
   - Recent errors (last 24h)
   - Auto-fix attempts
   - Escalations sent
3. Add real-time updates (polling every 30s)
4. Add error details modal
5. Add "Manual Fix" button для critical issues

**Acceptance Criteria**:
- ✅ Dashboard displays metrics
- ✅ Real-time updates работают
- ✅ Error details accessible
- ✅ Status indicators clear
- ✅ Owner can view escalation history

**Code Location**:
- `apps/admin-panel/app/system-health/`
- `apps/admin-panel/components/system-health/`

---

### Day 20: Week 4 Testing & Validation

#### Task 14.1: Omnichannel Testing
**Assignee**: Tester (Claude)
**Duration**: 2 hours
**Priority**: 🔴 Critical

**Test Scenarios**:
1. Send message via Telegram → AI responds
2. Send message via WhatsApp → AI responds
3. Book appointment via Telegram → booking created
4. AI escalates issue → case created
5. Test rate limiting (both channels)

**Acceptance Criteria**:
- ✅ Both channels work
- ✅ AI responds autonomously
- ✅ Booking flow complete
- ✅ Escalation works
- ✅ Rate limiting active

---

#### Task 14.2: Self-Healing System Testing
**Assignee**: Tester (Claude)
**Duration**: 3 hours
**Priority**: 🔴 Critical

**Test Scenarios**:
1. **Health Check**: Verify checks run every 5 min
2. **Auto-Fix**: Simulate stuck AI agent → verify restart
3. **Escalation**: Fail fix 3 times → verify Telegram alert
4. **Dashboard**: View health dashboard → metrics displayed
5. **Database Protection**: Attempt database modification → blocked

**Acceptance Criteria**:
- ✅ Health checks running
- ✅ Auto-fix working
- ✅ Escalation received
- ✅ Dashboard accurate
- ✅ Database modifications blocked

---

#### Task 14.3: Week 4 Validation
**Assignee**: Validator (Claude)
**Duration**: 2 hours
**Priority**: 🔴 Critical

**Validation Checklist**:
- ✅ Omnichannel messaging works (Telegram + WhatsApp)
- ✅ AI agents respond via all channels
- ✅ System Monitor running 24/7
- ✅ Auto-fix system functional
- ✅ Telegram escalation works
- ✅ Admin Health Dashboard working
- ✅ All tests pass
- ✅ Documentation updated

---

## Week 5: Business Documentation & Polish

**Цель**: Создать бизнес-документацию для коммерческого продукта
**Статус**: 📅 Scheduled
**Completion Criteria**: Business docs complete, client docs ready, pricing configured

**⚠️ ВАЖНО**: Это НЕ MVP - полный коммерческий продукт, готовый к продаже

---

### Day 21-22: Business Documentation

#### Task 15.1: Product Documentation
**Assignee**: Technical Writer / Product Manager (Claude)
**Duration**: 6 hours
**Priority**: 🟠 High

**Description**:
Создать полную продуктовую документацию

**Deliverables**:
1. **Product Overview** (`docs/product/overview.md`)
   - What is Beauty Salon SaaS
   - Key features list
   - Target audience
   - Competitive advantages
2. **Feature Documentation** (`docs/product/features/`)
   - AI Agent System
   - Omnichannel Messaging
   - CRM & Analytics
   - Self-Healing System
   - Payment Processing
3. **Pricing Documentation** (`docs/product/pricing.md`)
   - 15,000₽ (Минимальный): 1 salon, 100 clients, basic features
   - 25,000₽ (Средний): 3 salons, 500 clients, all features
   - 50,000₽ (Максимальный): unlimited, white-label, priority support

**Acceptance Criteria**:
- ✅ All docs written (RU)
- ✅ Clear feature descriptions
- ✅ Pricing tiers documented
- ✅ Target audience defined

**Code Location**:
- `docs/product/`

---

#### Task 15.2: Client Onboarding Documentation
**Assignee**: Technical Writer / Product Manager (Claude)
**Duration**: 4 hours
**Priority**: 🟠 High

**Description**:
Создать документацию для клиентов (владельцев салонов)

**Deliverables**:
1. **Getting Started Guide** (`docs/client/getting-started.md`)
   - Registration process
   - Initial setup (services, staff)
   - Creating first AI agent
   - Connecting Telegram/WhatsApp
2. **User Manual** (`docs/client/user-manual.md`)
   - Managing appointments
   - CRM usage
   - Analytics dashboards
   - Payment processing
3. **FAQ** (`docs/client/faq.md`)
   - Common questions
   - Troubleshooting
   - Best practices

**Acceptance Criteria**:
- ✅ Getting started guide complete
- ✅ User manual comprehensive
- ✅ FAQ covers 20+ questions
- ✅ All in RU language

**Code Location**:
- `docs/client/`

---

#### Task 15.3: Admin Guide
**Assignee**: Technical Writer (Claude)
**Duration**: 4 hours
**Priority**: 🟠 High

**Description**:
Создать руководство администратора

**Deliverables**:
1. **Deployment Guide** (`docs/admin/deployment.md`)
   - Installation steps
   - Docker Compose setup
   - Environment variables
   - Database setup
2. **Configuration Guide** (`docs/admin/configuration.md`)
   - Secrets management (Vault)
   - API keys setup
   - Novu configuration
   - Stripe configuration
3. **Maintenance Guide** (`docs/admin/maintenance.md`)
   - Backup procedures
   - Monitoring setup
   - Updates & migrations
   - Troubleshooting

**Acceptance Criteria**:
- ✅ Deployment guide step-by-step
- ✅ Configuration documented
- ✅ Maintenance procedures clear
- ✅ Troubleshooting section comprehensive

**Code Location**:
- `docs/admin/`

---

### Day 23: Additional Features & Polish

#### Task 16.1: Cal.com Calendar Integration
**Assignee**: Backend Developer 2 (GPT)
**Duration**: 4 hours
**Priority**: 🟡 Medium

**Description**:
Integrate Cal.com для calendar sync

**Steps**:
1. Setup Cal.com fork
2. Configure Google Calendar OAuth
3. Implement conflict checker
4. Test bi-directional sync

**Acceptance Criteria**:
- ✅ Google Calendar connected
- ✅ Conflicts detected
- ✅ Bi-directional sync working
- ✅ Salon staff can view external calendar events

---

#### Task 16.2: Voucher/Promo Codes System
**Assignee**: Backend Developer 3 (GPT)
**Duration**: 4 hours
**Priority**: 🟡 Medium

**Description**:
Implement promo code generation and validation

**Steps**:
1. Install voucher-code-generator-ts
2. Add promo_codes table to schema
3. Create API routes (generate, validate, apply)
4. Add UI for creating codes
5. Implement discount logic

**Acceptance Criteria**:
- ✅ Codes generated
- ✅ Validation works
- ✅ Discount applied correctly
- ✅ UI intuitive

---

#### Task 16.3: Loyalty & Referral System
**Assignee**: Backend Developer 1 (GPT)
**Duration**: 4 hours
**Priority**: 🟡 Medium

**Description**:
Implement basic loyalty and referral tracking

**Steps**:
1. Use existing `bonus_balance` field in clients table
2. Implement referral link generation
3. Create loyalty rules (10% bonus on 5th visit)
4. Add referral tracking (bonus for both parties)
5. Create redemption UI

**Acceptance Criteria**:
- ✅ Referral links работают
- ✅ Bonus points accrued automatically
- ✅ Redemption works
- ✅ Loyalty rules configurable

---

### Day 24-25: Week 5 Testing & Bug Fixes

#### Task 17.1: End-to-End Integration Testing
**Assignee**: Tester (Claude)
**Duration**: 6 hours
**Priority**: 🔴 Critical

**Test Scenarios** (Complete user flows):
1. **Tenant Onboarding**:
   - Register new salon
   - Setup services & staff
   - Create AI agent
   - Connect Telegram bot
2. **Client Booking Flow**:
   - Client sends Telegram message
   - AI responds with available slots
   - Client books appointment
   - Booking created in CRM
   - Calendar updated
3. **Payment Flow**:
   - Appointment completion
   - Payment processed via Stripe
   - Receipt sent
4. **Self-Healing**:
   - Simulate AI agent failure
   - Verify auto-fix attempt
   - Verify escalation if fix fails
5. **Analytics**:
   - View Metabase dashboards
   - Verify data accuracy

**Acceptance Criteria**:
- ✅ All flows complete without errors
- ✅ Data consistency verified
- ✅ Performance acceptable (p95 < 3s)
- ✅ No critical bugs found

---

#### Task 17.2: Bug Fixes & Polish
**Assignee**: All Developers
**Duration**: 6 hours
**Priority**: 🟠 High

**Description**:
Fix all bugs found during testing

**Acceptance Criteria**:
- ✅ All critical bugs fixed
- ✅ All high priority bugs fixed
- ✅ Medium/low bugs documented

---

#### Task 17.3: Week 5 Validation
**Assignee**: Validator (Claude)
**Duration**: 2 hours
**Priority**: 🔴 Critical

**Validation Checklist**:
- ✅ Business documentation complete
- ✅ Client docs comprehensive
- ✅ Additional features working (Calendar, Vouchers, Loyalty)
- ✅ All bugs fixed
- ✅ End-to-end tests pass
- ✅ Product ready for final testing

---

## Week 6: Final Testing & Commercial Launch

**Цель**: Final testing, production deployment, commercial launch
**Статус**: 📅 Scheduled
**Completion Criteria**: Production deployed, demo ready, launch complete

---

### Day 26-27: Production Deployment

#### Task 18.1: Production Environment Setup
**Assignee**: Backend Developer 1 (GPT)
**Duration**: 4 hours
**Priority**: 🔴 Critical

**Steps**:
1. Setup production server (AWS/DigitalOcean/Hetzner)
2. Configure domain & SSL certificates
3. Setup production PostgreSQL (Supabase)
4. Setup production Redis
5. Configure environment variables (production)
6. Setup CI/CD pipeline (GitHub Actions)

**Acceptance Criteria**:
- ✅ Production server ready
- ✅ SSL configured
- ✅ Database migrated
- ✅ CI/CD working
- ✅ Health checks passing

---

#### Task 18.2: Production Data Migration
**Assignee**: Backend Developer 1 (GPT)
**Duration**: 2 hours
**Priority**: 🔴 Critical

**Steps**:
1. Run production migrations
2. Seed initial data (if needed)
3. Verify RLS policies active
4. Test database connections
5. Backup production database

**Acceptance Criteria**:
- ✅ Migrations applied
- ✅ RLS working
- ✅ Connections stable
- ✅ Backup created

---

#### Task 18.3: Smoke Testing (Production)
**Assignee**: Tester (Claude)
**Duration**: 3 hours
**Priority**: 🔴 Critical

**Test Scenarios**:
1. Registration flow
2. Create AI agent
3. Send test Telegram message
4. Book appointment
5. Process test payment
6. View analytics dashboard
7. System health monitoring

**Acceptance Criteria**:
- ✅ All critical flows work
- ✅ Performance acceptable
- ✅ No errors in logs

---

### Day 28: Demo Preparation & Documentation Finalization

#### Task 19.1: Demo Preparation
**Assignee**: Product Manager (Claude)
**Duration**: 3 hours
**Priority**: 🟠 High

**Deliverables**:
1. Demo script (step-by-step walkthrough)
2. Sample data (realistic salon scenario)
3. Demo video (5-10 minutes)
4. Presentation slides

**Acceptance Criteria**:
- ✅ Demo script complete
- ✅ Sample data prepared
- ✅ Video recorded (optional)
- ✅ Slides ready

---

#### Task 19.2: API Documentation Finalization
**Assignee**: Backend Developer 2 (GPT)
**Duration**: 3 hours
**Priority**: 🟠 High

**Deliverables**:
1. OpenAPI/Swagger documentation
2. API endpoint list with examples
3. Authentication guide
4. Rate limiting documentation

**Acceptance Criteria**:
- ✅ Swagger UI accessible
- ✅ All endpoints documented
- ✅ Examples provided
- ✅ Auth guide clear

---

#### Task 19.3: README & Changelog
**Assignee**: Technical Writer (Claude)
**Duration**: 2 hours
**Priority**: 🟠 High

**Deliverables**:
1. Update root README.md:
   - Project description
   - Installation steps
   - Quick start guide
   - Links to docs
2. Create CHANGELOG.md:
   - Version 1.0.0 features
   - Known issues
   - Future roadmap

**Acceptance Criteria**:
- ✅ README comprehensive
- ✅ CHANGELOG complete
- ✅ Links valid

---

### Day 29-30: Final Testing & Launch

#### Task 20.1: Final User Acceptance Testing
**Assignee**: Tester (Claude) + Product Manager
**Duration**: 4 hours
**Priority**: 🔴 Critical

**Test Scenarios**:
Complete product walkthrough as real user:
1. Register as salon owner
2. Complete onboarding
3. Create AI agent with custom personality
4. Connect Telegram & WhatsApp
5. Import CRM data
6. Configure services & staff
7. Test client booking via Telegram
8. Process payment
9. View analytics
10. Test self-healing (simulate error)

**Acceptance Criteria**:
- ✅ All features work flawlessly
- ✅ User experience smooth
- ✅ No critical issues
- ✅ Performance excellent

---

#### Task 20.2: Launch Checklist & Go-Live
**Assignee**: Product Manager (Claude)
**Duration**: 2 hours
**Priority**: 🔴 Critical

**Launch Checklist**:
- ✅ Production environment stable
- ✅ All documentation complete
- ✅ Pricing tiers configured
- ✅ Payment processing working (Stripe)
- ✅ Monitoring & alerts active
- ✅ Backup procedures tested
- ✅ Support channels ready
- ✅ Demo ready
- ✅ Marketing materials ready (handled separately)
- ✅ Legal docs ready (handled by юрист-бот)

**Go-Live Steps**:
1. Final smoke test
2. Announce launch to stakeholders
3. Enable user registration
4. Monitor first 24h closely

**Acceptance Criteria**:
- ✅ Launch successful
- ✅ System stable
- ✅ First users onboarded

---

#### Task 20.3: Post-Launch Monitoring
**Assignee**: All Agents
**Duration**: Ongoing (first 48h critical)
**Priority**: 🔴 Critical

**Monitoring Tasks**:
1. Watch error logs (Real-time)
2. Monitor system health dashboard
3. Track first user registrations
4. Respond to escalations immediately
5. Collect user feedback

**Acceptance Criteria**:
- ✅ System stable first 48h
- ✅ No critical issues
- ✅ Users successfully onboarding
- ✅ Performance metrics good

---

## 📊 Updated Progress Tracking

Product Manager должен обновлять следующие файлы:

### Task Files
- `.claude/tasks/inbox.md` - новые задачи
- `.claude/tasks/in-progress.md` - текущие задачи
- `.claude/tasks/review.md` - на проверке
- `.claude/tasks/completed.md` - выполненные
- `.claude/tasks/blocked.md` - заблокированные

### Progress Reports
- `.claude/tasks/progress-report.md` - еженедельный отчёт

### Agent States
- `.claude/agents/backend-developer-1.md`
- `.claude/agents/backend-developer-2.md`
- `.claude/agents/frontend-developer.md`
- etc.

---

## 🎯 Updated Success Metrics

### Week 1
- ✅ Database running
- ✅ 4 integrations working (i18next, Vault, Novu, Rate Limiter)
- ✅ Zero critical bugs

### Week 2
- ✅ Payments processing
- ✅ Analytics dashboards live
- ✅ Performance < 5s (dashboards)

### Week 3
- ✅ AI Agent Creation System working
- ✅ CRM import/export functional
- ✅ CrewAI integrated

### Week 4
- ✅ Omnichannel messaging working (Telegram + WhatsApp)
- ✅ Self-Healing System operational (Monitor + Auto-Fix + Escalation)
- ✅ Admin Health Dashboard live

### Week 5
- ✅ Business documentation complete
- ✅ Client onboarding docs ready
- ✅ Additional features working (Calendar, Vouchers, Loyalty)

### Week 6
- ✅ Production deployed
- ✅ All tests passing
- ✅ Commercial launch successful
- ✅ Documentation complete

---

## 🚨 Updated Risk Management

### High Risk Items
1. **AI Agent reliability** - Mitigation: Self-healing system, escalation to owner
2. **Omnichannel integration complexity** - Mitigation: Chatwoot as unified hub
3. **Payment processing security** - Mitigation: Stripe compliance, Vault secrets
4. **Self-healing over-correction** - Mitigation: Max 3 attempts, database modifications blocked
5. **Production deployment issues** - Mitigation: Staging environment testing first

### Blocked Tasks Protocol
1. Developer пытается решить (30 min)
2. Escalate к Product Manager
3. PM reassigns или creates blocker ticket
4. Critical blockers → escalate к HR Manager (вам)

---

## 📞 Communication

### Daily Standups (async)
Каждый агент обновляет:
- Что сделано вчера
- Что планируется сегодня
- Блокеры

### Weekly Reviews
- Product Manager → Executive Summary
- Metrics dashboard update
- Next week planning

---

## 🎯 Commercial Product Scope Summary

**Что НЕ включено** (handled separately):
- ❌ Юридические документы (отдельный юрист-бот)
- ❌ Маркетинговые материалы (отдельная marketing система)
- ❌ Видео-туториалы (only text instructions to save time)

**Что ВКЛЮЧЕНО**:
- ✅ Полная техническая документация
- ✅ Клиентская документация (Getting Started, User Manual, FAQ)
- ✅ Администраторская документация (Deployment, Configuration, Maintenance)
- ✅ API документация (Swagger)
- ✅ Бизнес-документация (Product Overview, Features, Pricing)
- ✅ Демо-презентация
- ✅ Система поддержки (Admin Health Dashboard, Telegram alerts)
- ✅ Ценообразование (15k/25k/50k RUB)

---

**Roadmap Version**: 2.0
**Last Updated**: 2026-01-23
**Owner**: Product Manager (Claude)
**Timeline**: 6 weeks (Full Commercial Product)

**Status**: ✅ Updated and ready for execution
3. Launch announcement

**Acceptance Criteria**:
- ✅ MVP accessible
- ✅ Demo ready
- ✅ Stakeholders notified

---

## 📊 Progress Tracking

Product Manager должен обновлять следующие файлы:

### Task Files
- `.claude/tasks/inbox.md` - новые задачи
- `.claude/tasks/in-progress.md` - текущие задачи
- `.claude/tasks/review.md` - на проверке
- `.claude/tasks/completed.md` - выполненные
- `.claude/tasks/blocked.md` - заблокированные

### Progress Reports
- `.claude/tasks/progress-report.md` - еженедельный отчёт

### Agent States
- `.claude/agents/backend-developer-1.md`
- `.claude/agents/backend-developer-2.md`
- `.claude/agents/frontend-developer.md`
- etc.

---

## 🎯 Success Metrics

### Week 1
- ✅ Database running
- ✅ 4 integrations working (i18next, Vault, Novu, Rate Limiter)
- ✅ Zero critical bugs

### Week 2
- ✅ Payments processing
- ✅ Analytics dashboards live
- ✅ Performance < 5s (dashboards)

### Week 3
- ✅ AI agents responding
- ✅ 2+ channels integrated
- ✅ 80%+ autonomous responses

### Week 4
- ✅ MVP deployed
- ✅ All core features working
- ✅ Documentation complete

---

## 🚨 Risk Management

### High Risk Items
1. **Novu stability** - Mitigation: Fallback to BullMQ direct
2. **AI hallucinations** - Mitigation: Strict guardrails, escalation
3. **Rate limit tuning** - Mitigation: Monitor и adjust

### Blocked Tasks Protocol
1. Developer пытается решить (30 min)
2. Escalate к Product Manager
3. PM reassigns или creates blocker ticket
4. Critical blockers → escalate к HR Manager (вам)

---

## 📞 Communication

### Daily Standups (async)
Каждый агент обновляет:
- Что сделано вчера
- Что планируется сегодня
- Блокеры

### Weekly Reviews
- Product Manager → Executive Summary
- Metrics dashboard update
- Next week planning

---

**Roadmap Version**: 1.0
**Last Updated**: 2026-01-22
**Owner**: Architect → Product Manager

**Status**: ✅ Ready for execution
