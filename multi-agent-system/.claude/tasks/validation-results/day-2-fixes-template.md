# Day 2 Fixes — Validator Report (Template)

Дата: <YYYY-MM-DD>
Спринт: Week 1 Day 2
Задачи: Task 2.1 (i18next), Task 2.2 (Vault)
Статус: ⏳ In Review / ✅ Ready for Validation

## 1) Изменения (Summary)

Backend (Vault):
- docker-compose.yml: postgres → supabase/postgres (pgsodium)
- VaultClient: pg‑client fallback (без supabase-js)
- setup-secrets: локальный режим через DATABASE_URL
- README: локальная инструкция

Frontend (i18n):
- next.config.mjs: transpilePackages для @beauty-salon-saas/localization
- next dev без сборки пакета
- next-i18next: использован / удалён (указать)

## 2) Proof of Work

Коммиты:
- <commit hash> — <message>

Файлы:
- docker-compose.yml
- packages/secrets/src/vault-client.ts
- scripts/setup-secrets.ts
- packages/secrets/README.md
- apps/admin-panel/next.config.mjs
- <другие>

Скриншоты/Видео:
- Vault schema (pgAdmin/Supabase SQL)
- Audit log entries
- RU/EN переключение (скрин + видео/гиф)

## 2.1) Ссылки на артефакты (пути/имена файлов)
- Скрин Vault schema: <path>
- Скрин Audit log: <path>
- Видео/гиф RU/EN: <path>

Логи команд:
- npm run setup:secrets — SUCCESS
- npm run dev (admin-panel) — SUCCESS

## 3) Проверки (Checklist Results)

- pgsodium установлен (query ok)
- vault.sql применён без ошибок
- secrets записаны и читаются
- audit log пополняется
- next dev без ошибок
- RU/EN переключение работает

## 4) Итог

Готовность: ✅ Ready for Validation
Блокеры: None

---

# Чек‑лист SQL/команд (Day 2 Fixes)

## 1. Запуск Postgres (новый образ)

cd C:\Users\Nicita\beauty-salon-saas
docker-compose up -d postgres

Ожидаемый результат:
- Контейнер postgres запущен без ошибок
- В `docker ps` видно образ `supabase/postgres`

## 2. Проверка pgsodium

SELECT * FROM pg_extension WHERE extname = 'pgsodium';

Ожидаемый результат:
- 1 строка с extname = pgsodium

## 3. Применение SQL схемы Vault

# Через psql (локально):
psql "postgresql://postgres:postgres@localhost:5433/beauty_salon_saas" -f packages/secrets/sql/vault.sql

Ожидаемый результат:
- SQL выполнен без ошибок
- Таблица `vault.secrets` и функции `vault.create_secret`, `vault.read_secret` созданы

## 4. Установка app.encryption_key
Выбрать один вариант:

Вариант A — в сессии (рекомендуем для setup‑скрипта):

SELECT set_config('app.encryption_key', '<DEV_KEY>', true);
-- или
SELECT vault.set_encryption_key('<DEV_KEY>');

Вариант B — на уровне роли:

ALTER ROLE postgres SET app.encryption_key = '<DEV_KEY>';
-- затем заново подключиться

Вариант C — на уровне базы:

ALTER DATABASE beauty_salon_saas SET app.encryption_key = '<DEV_KEY>';
-- затем заново подключиться

Ожидаемый результат:
- `SHOW app.encryption_key;` возвращает значение (после переподключения, если нужно)

## 5. Запуск миграции секретов

npm run setup:secrets

Ожидаемый результат:
- Логи SUCCESS/OK для всех секретов

## 6. Проверка audit log

SELECT * FROM vault.secret_access_log ORDER BY accessed_at DESC LIMIT 20;

Ожидаемый результат:
- Есть новые записи о доступе к секретам

## 7. Next.js admin-panel (проверка transpilePackages)

cd C:\Users\Nicita\beauty-salon-saas
npm install
npm run dev -- --filter=@beauty-salon-saas/admin-panel

Ожидаемый результат:
- Dev сервер стартует без ошибок компиляции

## 8. Проверка UI

- Открыть страницу admin-panel
- Переключить RU/EN
- Сделать скрин + видео/гиф

Ожидаемый результат:
- Текст меняется между RU и EN
