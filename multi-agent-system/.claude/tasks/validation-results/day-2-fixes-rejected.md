# Day 2 Fixes: i18next + Vault — Validator Report (REJECTED)

Дата проверки: 2026-01-23
Время: 2026-01-23T20:52:53+03:00
Задачи: task-2.1 (i18next), task-2.2 (Vault)
Статус: ❌ REJECTED (требуются исправления)

## 1) Область проверки

**Артефакты:**
- C:\Users\Nicita\artifacts\day2_nextdev_turbo3.log
- C:\Users\Nicita\artifacts\day2_i18n_ru.png
- C:\Users\Nicita\artifacts\day2_i18n_en.png
- C:\Users\Nicita\artifacts\day2_i18n_switch.gif
- C:\Users\Nicita\artifacts\day2_setup_secrets.log
- C:\Users\Nicita\artifacts\day2_vault_schema.png
- C:\Users\Nicita\artifacts\day2_vault_audit.png
- (доп.) C:\Users\Nicita\artifacts\day2_vault_schema.txt
- (доп.) C:\Users\Nicita\artifacts\day2_vault_audit.txt

**Изменения кода:**
- C:\Users\Nicita\beauty-salon-saas\apps\admin-panel\package.json
- C:\Users\Nicita\beauty-salon-saas\packages\secrets\sql\vault.sql
- C:\Users\Nicita\beauty-salon-saas\packages\secrets\tsconfig.json

**Сверка с ADR:**
- ADR-010 (i18next)
- ADR-012 (Vault)

## 2) Результаты проверки по артефактам

**i18next:**
- Next dev стартует и отвечает (лог есть) — OK.
- Скриншоты RU/EN и GIF показывают одинаковые ключи переводов и `language.current: ru` даже в EN — НЕ OK.

**Vault:**
- setup:secrets завершён успешно (лог — OK).
- Схема vault создана (таблицы + функции — OK).
- Audit log содержит записи INSERT/UPDATE — OK.

## 3) Найденные проблемы (по критичности)

### BLOCKER
1) **RU/EN переключение не работает (локализация не применяется).**
   - **Доказательства:** `day2_i18n_ru.png`, `day2_i18n_en.png`, `day2_i18n_switch.gif`.
   - **Наблюдение:** видны ключи переводов (`app.name`, `navigation.dashboard`, `common.save` и т.д.), в EN-скриншоте `language.current: ru`.
   - **Почему важно:** критерий приемки «i18next RU/EN works; language switcher functional» не выполнен.
   - **Рекомендованная правка:**
     - Убедиться, что `I18nextProvider`/инициализация подключены в корне приложения.
     - Проверить наличие `public/locales/{lng}/{ns}.json` и корректный `backend.loadPath`.
     - Проверить `useTranslation`/namespace и вызов `i18n.changeLanguage('en')`.
     - Повторно снять скрины RU/EN с разными строками и обновить GIF.

### MINOR (не блокирует, но желательно)
2) **Нет явного proof read-пути секретов.**
   - В логах есть INSERT/UPDATE, но нет демонстрации `read_secret`/`read_secrets`.
   - Рекомендация: добавить один read в proof (чтобы в audit log появился `read`).

## 4) Итог

**Decision:** ❌ REJECTED

Причина: i18next переключение языков не подтверждено; фактически UI остаётся на ключах переводов и не меняет язык.

**Что нужно для принятия:**
- Исправить i18n (см. блокер) и приложить новые скриншоты/GIF.
- (желательно) приложить read-proof для Vault.

**Validator:** Validator (Codex)
