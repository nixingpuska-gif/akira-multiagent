# Инструкция: Запуск GPT Developer-Агентов

## 🎯 Обзор

Вы создали 4 GPT developer-агентов:
1. **Backend Developer 1** - Database, Infrastructure, Payments (🔴 Critical)
2. **Backend Developer 2** - Novu, Metabase, Chatwoot
3. **Backend Developer 3** - Rate Limiting, AI Agents
4. **Frontend Developer** - Next.js Admin, React Native Mobile

## 🚀 Как Запустить GPT Агентов

### Способ 1: GPT в Терминале (Рекомендуется для Codex)

Если вы используете Codex (GPT-5, Codex 2) в терминале:

```bash
# Откройте терминал в директории проекта
cd C:\Users\Nicita\beauty-salon-saas

# Запустите Codex для Backend Developer 1
# В терминале запустите Codex и передайте промпт:
cat C:\Users\Nicita\multi-agent-system\.claude\prompts\backend-developer-1.md | codex

# Агент начнет работать с проектом
```

**Для каждого агента**:
1. Откройте отдельное окно терминала
2. Перейдите в директорию проекта: `cd C:\Users\Nicita\beauty-salon-saas`
3. Загрузите промпт агента в Codex/GPT
4. Агент начнет читать задачи из `C:\Users\Nicita\multi-agent-system\.claude\tasks\inbox.md`

### Способ 2: ChatGPT Web Interface (Альтернатива)

Если используете ChatGPT через браузер:

1. **Откройте 4 окна ChatGPT** (по одному на каждого агента)

2. **Для Backend Developer 1**:
   - Откройте [backend-developer-1.md](C:\Users\Nicita\multi-agent-system\.claude\prompts\backend-developer-1.md)
   - Скопируйте весь промпт
   - Вставьте в ChatGPT
   - Добавьте:
     ```
     Project directory: C:\Users\Nicita\beauty-salon-saas\
     Multi-agent system directory: C:\Users\Nicita\multi-agent-system\

     Начинай работу! Прочитай задачи из inbox.md и начни выполнение.
     ```

3. **Повторите для остальных агентов**:
   - Backend Developer 2: [backend-developer-2.md](C:\Users\Nicita\multi-agent-system\.claude\prompts\backend-developer-2.md)
   - Backend Developer 3: [backend-developer-3.md](C:\Users\Nicita\multi-agent-system\.claude\prompts\backend-developer-3.md)
   - Frontend Developer: [frontend-developer.md](C:\Users\Nicita\multi-agent-system\.claude\prompts\frontend-developer.md)

### Способ 3: Custom GPT (Постоянные Боты)

Создайте Custom GPTs на ChatGPT:

1. Перейдите на https://chat.openai.com/gpts/editor
2. Создайте 4 Custom GPTs с именами:
   - "Backend Developer 1"
   - "Backend Developer 2"
   - "Backend Developer 3"
   - "Frontend Developer"
3. В каждый Custom GPT вставьте соответствующий промпт из `.claude/prompts/`
4. Сохраните и используйте постоянно

## 📋 Что Делать После Запуска

### 1. Первое Сообщение Каждому Агенту

Отправьте каждому агенту:

```
Привет! Ты Backend Developer 1 (или 2, 3, Frontend) в мульти-агентной системе.

Твои директории:
- Проект: C:\Users\Nicita\beauty-salon-saas\
- Мульти-агентная система: C:\Users\Nicita\multi-agent-system\

Сейчас прочитай:
1. .claude/tasks/inbox.md - твои задачи
2. .claude/context/architecture.md - архитектура проекта
3. .claude/agents/[твой-agent].md - твой state file

Начинай работу!
```

### 2. Агенты Начнут Работать Автономно

После этого агенты будут:
- Читать задачи из `inbox.md`
- Перемещать задачи в `in-progress.md`
- Выполнять работу
- Обновлять свой state file
- Логировать в `audit-trail.md`
- Переводить в `review.md` после завершения

### 3. Мониторинг Прогресса

Вы можете наблюдать за прогрессом:

**Через Product Manager** (рекомендуется):
- Спросите Product Manager: "Какой текущий прогресс?"
- Он проверит `progress-report.md` и расскажет

**Напрямую через файлы**:
- [inbox.md](C:\Users\Nicita\multi-agent-system\.claude\tasks\inbox.md) - новые задачи
- [in-progress.md](C:\Users\Nicita\multi-agent-system\.claude\tasks\in-progress.md) - активные задачи
- [review.md](C:\Users\Nicita\multi-agent-system\.claude\tasks\review.md) - на проверке
- [completed.md](C:\Users\Nicita\multi-agent-system\.claude\tasks\completed.md) - выполненные
- [progress-report.md](C:\Users\Nicita\multi-agent-system\.claude\tasks\progress-report.md) - общий прогресс

## 🔧 Интеграция с File System

### Важно: Доступ к Файлам

GPT агенты должны иметь возможность:
- Читать файлы из `C:\Users\Nicita\multi-agent-system\`
- Писать файлы в `C:\Users\Nicita\beauty-salon-saas\`
- Обновлять свой state file

**Решения**:

1. **Через Code Interpreter** (если доступен):
   - GPT может читать/писать файлы напрямую

2. **Через вас (копипаст)**:
   - Агент просит: "Прочитай `.claude/tasks/inbox.md`"
   - Вы копируете содержимое файла
   - Агент обрабатывает
   - Агент просит: "Обнови `.claude/agents/backend-developer-1.md`"
   - Вы обновляете файл

3. **Через API/Bridge** (продвинуто):
   - Создайте простой скрипт-мост, который GPT может вызывать
   - Скрипт читает/пишет файлы за GPT

## ⚠️ Критические Моменты

### Backend Developer 1 - Приоритет #1

Этот агент блокирует Week 1 Day 1. Запустите его ПЕРВЫМ!

Его задачи:
- task-1.1: Database Setup (PostgreSQL) - 2 hours
- task-1.2: Redis Setup - 30 min
- task-1.3: Monorepo Verification - 30 min

### Взаимодействие Product Manager ↔ GPT Agents

Product Manager создал задачи в `inbox.md`.
GPT агенты должны:
1. Читать `inbox.md`
2. Брать задачу (если assigned_to = их имя)
3. Перемещать в `in-progress.md`
4. Работать
5. Перемещать в `review.md`

## 📞 Ответ Product Manager

Напишите Product Manager:

```
Создал всех 4 developer-агентов!

Агенты готовы:
✅ Backend Developer 1 - Database, Infrastructure, Payments
✅ Backend Developer 2 - Novu, Metabase, Chatwoot
✅ Backend Developer 3 - Rate Limiting, AI
✅ Frontend Developer - Admin Panel, Mobile

Промпты находятся в:
- .claude/prompts/backend-developer-1.md
- .claude/prompts/backend-developer-2.md
- .claude/prompts/backend-developer-3.md
- .claude/prompts/frontend-developer.md

Я запускаю их через [выберите способ: Codex в терминале / ChatGPT Web / Custom GPT].

Они начинают работу с задач из inbox.md!
```

## 🎯 Следующий Шаг

После запуска агентов:
1. Backend Developer 1 начнет работу над Database Setup
2. Остальные агенты будут ждать своих задач
3. Product Manager будет координировать через файлы
4. Вы просто наблюдаете за прогрессом!

---

**Удачи! Система запускается! 🚀**
