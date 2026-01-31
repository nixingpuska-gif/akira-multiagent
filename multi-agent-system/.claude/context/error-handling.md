# Error Handling Protocol - Протокол Обработки Ошибок

## API Errors (400, 404, 403, 429, 500, 529)

### Automatic Retry Strategy

1. **Первая ошибка**: Подождать 30 секунд, повторить
2. **Вторая ошибка**: Подождать 2 минуты, повторить
3. **Третья ошибка**: Подождать 5 минут, повторить
4. **Четвертая ошибка**: Залогировать в `.claude/tasks/blocked.md` с деталями ошибки

### Error Logging Format

```markdown
## Blocked Task: [task-id]
- **Agent**: [agent-name]
- **Error**: [error-code] - [error-message]
- **Timestamp**: [ISO timestamp]
- **Attempts**: 4
- **Last attempt**: [timestamp]
- **Action needed**: Manual intervention or wait for API recovery
```

### Self-Healing Actions

- ✅ Agent логирует ошибку в blocked tasks
- ✅ Agent продолжает работу с другими задачами если они доступны
- ✅ Product Manager периодически проверяет blocked tasks
- ✅ Product Manager уведомляет User только если критично

## Common Errors

### 400 Bad Request
**Причина**: Неправильный формат запроса
**Действие**: Проверить формат данных, исправить запрос

### 403 Forbidden
**Причина**: Недостаточно прав доступа
**Действие**: Проверить permissions, запросить доступ у Product Manager

### 404 Not Found
**Причина**: Файл/ресурс не найден
**Действие**: Проверить пути к файлам, создать файл если нужно

### 429 Too Many Requests
**Причина**: Превышен rate limit API
**Действие**: Подождать указанное время (см. Retry-After header), затем повторить

### 500 Internal Server Error
**Причина**: Ошибка на стороне сервера
**Действие**: Подождать и повторить, если повторяется - уведомить Product Manager

### 529 Service Overloaded
**Причина**: Сервер перегружен
**Действие**: Подождать 5-10 минут, затем повторить

## Escalation Protocol

### Level 1: Agent Self-Healing
Agent пытается решить проблему автоматически (retry, alternative approach)

### Level 2: Blocked Task
После 4 неудачных попыток - задача блокируется, логируется в blocked.md

### Level 3: Product Manager Review
Product Manager периодически проверяет blocked tasks и пытается разрешить

### Level 4: User Notification
Только критичные блокеры эскалируются к пользователю

## Best Practices

- ✅ Всегда логируйте детали ошибки
- ✅ Включайте timestamp и контекст
- ✅ Сохраняйте состояние перед retry
- ✅ Не блокируйте другие задачи из-за одной ошибки
- ✅ Документируйте решение проблемы для будущих случаев
