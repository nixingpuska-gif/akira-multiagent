# AKIRA 4.0 - Полная инструкция по установке и использованию

**Версия:** 4.0.0  
**Дата:** Январь 2026  
**Статус:** ✅ Production Ready  
**Язык:** Русский / English

---

## Содержание

1. [Системные требования](#системные-требования)
2. [Установка на Linux](#установка-на-linux)
3. [Установка на Windows](#установка-на-windows)
4. [Установка на macOS](#установка-на-macos)
5. [Docker установка (рекомендуется)](#docker-установка-рекомендуется)
6. [Первый запуск](#первый-запуск)
7. [Конфигурация](#конфигурация)
8. [Использование](#использование)
9. [Troubleshooting](#troubleshooting)

---

## Системные требования

### Минимальные требования

| Компонент | Требование |
|-----------|-----------|
| ОС | Linux, Windows 10+, macOS 10.15+ |
| Python | 3.11 или выше |
| RAM | 4 GB минимум, 8 GB рекомендуется |
| Disk Space | 5 GB свободного места |
| Интернет | Требуется для API запросов |

### Рекомендуемые требования

| Компонент | Рекомендация |
|-----------|-------------|
| ОС | Ubuntu 22.04 LTS или Windows 11 |
| Python | 3.11+ |
| RAM | 16 GB |
| Disk Space | 20 GB |
| Docker | 20.10+ (если используется Docker) |
| PostgreSQL | 15+ (если не используется Docker) |
| Redis | 7.0+ (если не используется Docker) |

### Необходимые API ключи

Перед установкой подготовьте API ключи:

- **OpenAI API Key** (основной провайдер)
- **Anthropic API Key** (резервный провайдер)
- **Google Gemini API Key** (резервный провайдер)
- **DeepSeek API Key** (резервный провайдер)
- **OpenRouter API Key** (последний резерв)

Получить ключи можно на официальных сайтах провайдеров.

---

## Установка на Linux

### Шаг 1: Клонирование репозитория

```bash
# Создаем директорию для проекта
mkdir -p ~/projects
cd ~/projects

# Клонируем репозиторий AKIRA
git clone https://github.com/yourusername/akira-4.0.git
cd akira-4.0
```

### Шаг 2: Установка зависимостей системы

```bash
# Обновляем пакеты
sudo apt-get update
sudo apt-get upgrade -y

# Устанавливаем Python и необходимые пакеты
sudo apt-get install -y python3.11 python3.11-venv python3.11-dev

# Устанавливаем PostgreSQL
sudo apt-get install -y postgresql postgresql-contrib

# Устанавливаем Redis
sudo apt-get install -y redis-server

# Устанавливаем git (если не установлен)
sudo apt-get install -y git
```

### Шаг 3: Создание виртуального окружения

```bash
# Создаем виртуальное окружение
python3.11 -m venv venv

# Активируем виртуальное окружение
source venv/bin/activate

# Обновляем pip
pip install --upgrade pip setuptools wheel
```

### Шаг 4: Установка зависимостей Python

```bash
# Устанавливаем все зависимости
pip install -r requirements.txt

# Дополнительные пакеты
pip install python-dotenv psycopg2-binary redis pyrogram telethon
```

### Шаг 5: Конфигурация переменных окружения

```bash
# Копируем пример конфигурации
cp .env.example .env

# Редактируем конфиг
nano .env
```

Добавьте следующие переменные в `.env`:

```env
# API Keys
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GEMINI_API_KEY=your_gemini_key_here
DEEPSEEK_API_KEY=your_deepseek_key_here
OPENROUTER_API_KEY=your_openrouter_key_here

# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=akira_db
POSTGRES_USER=akira
POSTGRES_PASSWORD=your_secure_password

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Telegram (опционально)
TELEGRAM_PHONE=+1234567890
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash

# System
AKIRA_MODE=production
LOG_LEVEL=INFO
```

### Шаг 6: Инициализация базы данных

```bash
# Запускаем PostgreSQL
sudo systemctl start postgresql

# Создаем пользователя и базу данных
sudo -u postgres psql << EOF
CREATE USER akira WITH PASSWORD 'your_secure_password';
CREATE DATABASE akira_db OWNER akira;
GRANT ALL PRIVILEGES ON DATABASE akira_db TO akira;
EOF

# Запускаем миграции
python akira_4_0/core/main_orchestrator.py --migrate
```

### Шаг 7: Запуск AKIRA

```bash
# Убеждаемся, что Redis запущен
sudo systemctl start redis-server

# Запускаем AKIRA
python -m akira_4_0.core.main_orchestrator
```

---

## Установка на Windows

### Шаг 1: Установка Python

1. Скачайте Python 3.11+ с [python.org](https://www.python.org/downloads/)
2. Запустите установщик
3. **Важно:** Отметьте "Add Python to PATH"
4. Нажмите "Install Now"

### Шаг 2: Проверка установки

Откройте Command Prompt (cmd) или PowerShell и выполните:

```bash
python --version
pip --version
```

### Шаг 3: Клонирование репозитория

```bash
# Создаем директорию
mkdir C:\Users\YourUsername\projects
cd C:\Users\YourUsername\projects

# Клонируем репозиторий
git clone https://github.com/yourusername/akira-4.0.git
cd akira-4.0
```

### Шаг 4: Установка зависимостей Windows

**Вариант 1: Использование Docker (рекомендуется)**

Установите [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop) и переходите к разделу [Docker установка](#docker-установка-рекомендуется).

**Вариант 2: Локальная установка**

```bash
# Создаем виртуальное окружение
python -m venv venv

# Активируем виртуальное окружение
venv\Scripts\activate.bat

# Обновляем pip
python -m pip install --upgrade pip

# Устанавливаем зависимости
pip install -r requirements.txt
```

### Шаг 5: Установка PostgreSQL и Redis (Windows)

**PostgreSQL:**
1. Скачайте с [postgresql.org](https://www.postgresql.org/download/windows/)
2. Запустите установщик
3. Запомните пароль для пользователя postgres
4. Завершите установку

**Redis (опционально для Windows):**
- Используйте WSL2 (Windows Subsystem for Linux 2) или Docker
- Или установите [Redis for Windows](https://github.com/microsoftarchive/redis/releases)

### Шаг 6: Конфигурация

```bash
# Копируем пример конфигурации
copy .env.example .env

# Редактируем конфиг (используйте Notepad или VS Code)
notepad .env
```

Добавьте те же переменные, что и для Linux (см. выше).

### Шаг 7: Запуск AKIRA на Windows

**Используя Batch скрипт (рекомендуется):**

```bash
run_akira.bat
```

**Используя PowerShell:**

```powershell
.\run_akira.ps1
```

**Вручную:**

```bash
# Активируем виртуальное окружение
venv\Scripts\activate.bat

# Запускаем AKIRA
python -m akira_4_0.core.main_orchestrator
```

---

## Установка на macOS

### Шаг 1: Установка Homebrew

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Шаг 2: Установка зависимостей

```bash
# Обновляем Homebrew
brew update

# Устанавливаем Python
brew install python@3.11

# Устанавливаем PostgreSQL
brew install postgresql

# Устанавливаем Redis
brew install redis

# Устанавливаем git
brew install git
```

### Шаг 3: Запуск сервисов

```bash
# Запускаем PostgreSQL
brew services start postgresql

# Запускаем Redis
brew services start redis
```

### Шаг 4: Клонирование и установка

```bash
# Создаем директорию
mkdir -p ~/projects
cd ~/projects

# Клонируем репозиторий
git clone https://github.com/yourusername/akira-4.0.git
cd akira-4.0

# Создаем виртуальное окружение
python3.11 -m venv venv

# Активируем виртуальное окружение
source venv/bin/activate

# Устанавливаем зависимости
pip install -r requirements.txt
```

### Шаг 5: Конфигурация

```bash
# Копируем пример конфигурации
cp .env.example .env

# Редактируем конфиг
nano .env
```

Добавьте необходимые API ключи и параметры базы данных.

### Шаг 6: Запуск AKIRA

```bash
# Убеждаемся, что сервисы запущены
brew services list

# Запускаем AKIRA
python -m akira_4_0.core.main_orchestrator
```

---

## Docker установка (рекомендуется)

### Шаг 1: Установка Docker

**Linux:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

**Windows/macOS:**
Скачайте [Docker Desktop](https://www.docker.com/products/docker-desktop)

### Шаг 2: Клонирование репозитория

```bash
git clone https://github.com/yourusername/akira-4.0.git
cd akira-4.0
```

### Шаг 3: Конфигурация переменных окружения

```bash
# Копируем пример конфигурации
cp .env.example .env

# Редактируем конфиг
nano .env
```

### Шаг 4: Запуск Docker Compose

```bash
# Запускаем все сервисы
docker-compose up -d

# Проверяем статус
docker-compose ps

# Просматриваем логи
docker-compose logs -f akira-core
```

### Шаг 5: Проверка статуса

```bash
# Проверяем, что все сервисы запущены
docker-compose ps

# Должны быть запущены:
# - akira-redis
# - akira-postgres
# - akira-core
```

### Остановка Docker контейнеров

```bash
# Останавливаем все сервисы
docker-compose down

# Останавливаем и удаляем данные
docker-compose down -v
```

---

## Первый запуск

### Шаг 1: Проверка подключения

После запуска AKIRA проверьте логи:

```bash
# Linux/macOS
tail -f logs/akira.log

# Windows PowerShell
Get-Content logs/akira.log -Tail 20 -Wait
```

Вы должны увидеть сообщения вроде:

```
[INFO] AKIRA 4.0 Starting...
[INFO] Redis connection: OK
[INFO] PostgreSQL connection: OK
[INFO] API Providers initialized: 5
[INFO] System ready for requests
```

### Шаг 2: Проверка API

```bash
# Проверяем, что API работает
curl http://localhost:8000/health

# Должен вернуть:
# {"status": "ok", "version": "4.0.0"}
```

### Шаг 3: Первый запрос

Откройте браузер и перейдите на:

```
http://localhost:3000
```

Вы должны увидеть AKIRA Control Center Dashboard.

---

## Конфигурация

### Основные параметры конфигурации

| Параметр | Описание | По умолчанию |
|----------|---------|-------------|
| AKIRA_MODE | production или development | production |
| LOG_LEVEL | DEBUG, INFO, WARNING, ERROR | INFO |
| API_TIMEOUT | Timeout для API запросов (сек) | 30 |
| MAX_RETRIES | Максимальное количество повторов | 3 |
| BATCH_SIZE | Размер батча для обработки | 100 |

### API провайдеры

Настройте приоритет провайдеров в `.env`:

```env
# Priority 1 (основной)
OPENAI_API_KEY=your_key

# Priority 2-4 (резервные)
ANTHROPIC_API_KEY=your_key
GEMINI_API_KEY=your_key
DEEPSEEK_API_KEY=your_key

# Priority 999 (последний резерв)
OPENROUTER_API_KEY=your_key
```

### Telegram конфигурация

Для использования Telegram интеграции:

```env
TELEGRAM_ENABLED=true
TELEGRAM_PHONE=+1234567890
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
```

Получить API ID и Hash можно на [my.telegram.org](https://my.telegram.org)

---

## Использование

### Запуск через GUI

1. Откройте браузер: `http://localhost:3000`
2. Перейдите на Dashboard
3. Нажмите "New Request"
4. Опишите вашу задачу
5. Система начнет выполнение

### Запуск через Telegram

1. Отправьте сообщение боту AKIRA в Telegram
2. Используйте команды:
   - `/status` - статус системы
   - `/execute <command>` - выполнить команду
   - `/logs` - последние логи
   - `/restart` - перезагрузить систему

### Запуск через API

```bash
# Создаем новый запрос
curl -X POST http://localhost:8000/api/requests \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Create a Python script",
    "description": "Write a script that processes CSV files",
    "priority": "high"
  }'

# Получаем статус запроса
curl http://localhost:8000/api/requests/{request_id}

# Получаем результаты
curl http://localhost:8000/api/requests/{request_id}/results
```

### Мониторинг системы

```bash
# Просмотр логов в реальном времени
docker-compose logs -f akira-core

# Статус контейнеров
docker-compose ps

# Использование ресурсов
docker stats

# Проверка здоровья системы
curl http://localhost:8000/health
```

---

## Troubleshooting

### Проблема: "Connection refused" при подключении к PostgreSQL

**Решение:**

```bash
# Linux
sudo systemctl start postgresql

# macOS
brew services start postgresql

# Windows
# Запустите PostgreSQL из Services (services.msc)
```

### Проблема: "Redis connection failed"

**Решение:**

```bash
# Linux
sudo systemctl start redis-server

# macOS
brew services start redis

# Windows (Docker)
docker-compose up -d akira-redis
```

### Проблема: "Invalid API key"

**Решение:**

1. Проверьте, что API ключи правильно добавлены в `.env`
2. Убедитесь, что ключи не содержат пробелов
3. Проверьте, что ключи активны на сайтах провайдеров
4. Перезагрузите AKIRA: `docker-compose restart akira-core`

### Проблема: "Port 8000 already in use"

**Решение:**

```bash
# Linux/macOS - найти процесс на порту 8000
lsof -i :8000

# Завершить процесс
kill -9 <PID>

# Windows PowerShell
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process
```

### Проблема: "Insufficient disk space"

**Решение:**

```bash
# Очистить Docker кэш
docker system prune -a

# Удалить старые логи
docker-compose exec akira-core rm -rf logs/*

# Проверить место на диске
df -h
```

### Проблема: "Memory limit exceeded"

**Решение:**

Увеличьте лимит памяти в `docker-compose.yml`:

```yaml
services:
  akira-core:
    mem_limit: 8g
    memswap_limit: 8g
```

### Проблема: "Telegram authentication failed"

**Решение:**

1. Убедитесь, что номер телефона правильный
2. Проверьте API ID и Hash
3. Удалите файл сессии: `rm -f telegram_session.session`
4. Переавторизуйтесь

---

## Обновление AKIRA

### Обновление из репозитория

```bash
# Получаем последние изменения
git pull origin main

# Переустанавливаем зависимости
pip install -r requirements.txt --upgrade

# Перезагружаем систему
docker-compose restart akira-core
```

### Обновление Docker образа

```bash
# Пересобираем образ
docker-compose build --no-cache

# Перезагружаем контейнеры
docker-compose up -d
```

---

## Резервное копирование

### Резервная копия базы данных

```bash
# Экспортируем PostgreSQL
docker-compose exec akira-postgres pg_dump -U akira akira_db > backup.sql

# Восстанавливаем из резервной копии
docker-compose exec -T akira-postgres psql -U akira akira_db < backup.sql
```

### Резервная копия конфигурации

```bash
# Архивируем конфигурацию
tar -czf akira_backup.tar.gz .env logs/

# Восстанавливаем конфигурацию
tar -xzf akira_backup.tar.gz
```

---

## Поддержка и помощь

### Получение помощи

- **Документация:** [docs.akira.ai](https://docs.akira.ai)
- **GitHub Issues:** [github.com/akira/issues](https://github.com/akira/issues)
- **Telegram чат:** [t.me/akira_support](https://t.me/akira_support)
- **Email:** support@akira.ai

### Отправка отчета об ошибке

При отправке отчета об ошибке включите:

1. Версию AKIRA: `python -m akira_4_0 --version`
2. Версию Python: `python --version`
3. ОС и версию: `uname -a` (Linux/macOS) или `systeminfo` (Windows)
4. Полный текст ошибки из логов
5. Шаги для воспроизведения проблемы

---

## Лицензия

AKIRA 4.0 распространяется под лицензией MIT. Подробнее см. [LICENSE](LICENSE)

---

## Благодарности

Спасибо всем, кто помогал в разработке AKIRA 4.0!

---

**Версия документации:** 1.0  
**Последнее обновление:** Январь 2026  
**Статус:** ✅ Production Ready

🦾💀🚀🔥 **AKIRA 4.0 - Self-Generating, Self-Deploying, Self-Improving**
