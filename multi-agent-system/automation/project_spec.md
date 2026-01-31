# Project Spec: Beauty Salon SaaS (RU)

Goal:
- B2B SaaS for beauty salons in Russia.
- Replace admins/managers with autonomous AI bots.
- Channels: MAX + Instagram + Telegram (Phase 1). WhatsApp/VK later.
- Bots: client-facing booking/FAQ/consultations + marketing broadcasts; internal owner/staff bot in Telegram.
- SPM analytics: staff KPI, utilization, no-show, avg check, LTV, optimization.
- Warehouse basics (consumables) + low-stock alerts.
- Billing: subscription via SBP QR with auto-confirmation; no online cash registers.
- Languages: Russian + English.
- Data isolation: schema-per-tenant (strong isolation).
- Integrations: one-time import from 1C/Yclients/MoySklad/Bitrix/telephony (CSV/Excel/API exports). Full sync later.
- Safety: dangerous actions off by default (mass broadcasts, delete bookings, price changes, refunds/cancellations). Owner enables explicitly.
- Escalation: aggression or non-standard cases -> human escalation.
- Design: luxury minimalism (A).
- Infrastructure: local servers (2 nodes), Linux, 4x E5-2680v3, 64-128GB RAM.
- Scale: 1000 salons in 3 months, 3000 later.
- Use open-source as much as possible (permissive licenses).
- Concurrency: 50 agents, 30 parallel.
