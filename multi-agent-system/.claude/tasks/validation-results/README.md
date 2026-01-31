# Validation Results

Эта директория содержит результаты валидации от Validator Agent.

## Формат Файлов

**Одобрение (Approval)**:
```
phase-2-approved.md
```

**Отклонение (Rejection)**:
```
phase-2-rejected.md
```

## Структура Отчета

**Для Approved**:
- Summary: "Phase 2 architecture APPROVED"
- Documents Validated: (список всех проверенных документов)
- Key Strengths: (что хорошо)
- Minor Suggestions: (необязательные улучшения)
- Decision: "Implementation may continue"
- Validator: [agent-name]
- Timestamp: [ISO 8601]

**Для Rejected**:
- Summary: "Phase 2 architecture REJECTED"
- Critical Issues: (список критических проблем)
- How to Fix: (инструкции по исправлению)
- Decision: "Stop implementation immediately"
- Recommendation: "Architect must fix issues before continuing"
- Validator: [agent-name]
- Timestamp: [ISO 8601]

## Workflow

1. Validator Agent создает отчет в этой директории
2. Product Manager читает отчет
3. Если APPROVED → продолжить имплементацию
4. Если REJECTED → остановить, координировать с Architect
