# Code Style Guide - Руководство по Стилю Кода

## Статус: Placeholder

**Примечание**: Конкретный язык программирования и фреймворки будут определены Architect Agent. Этот файл будет обновлен после принятия архитектурных решений.

---

## General Rules

### Базовые Принципы

- **Читаемость превыше всего**: Код пишется один раз, читается много раз
- **Консистентность**: Следуйте одному стилю во всем проекте
- **Простота**: Избегайте over-engineering
- **DRY (Don't Repeat Yourself)**: Избегайте дублирования кода
- **SOLID Principles**: Следуйте принципам объектно-ориентированного программирования

### Formatting

- **Indentation**: 2 spaces (не tabs)
- **Line length**: максимум 100 символов
- **Encoding**: UTF-8
- **Line endings**: LF (Unix-style)

### Comments

- **Язык комментариев**: English для кода
- **When to comment**:
  - ✅ Сложная бизнес-логика
  - ✅ Non-obvious solutions
  - ✅ TODO, FIXME, NOTE markers
  - ❌ Не комментируйте очевидное
  - ❌ Не оставляйте закомментированный код

---

## Naming Conventions (Placeholder)

**Будет определено после выбора языка программирования**

### Example (TypeScript/JavaScript)

- **Files**: `kebab-case.ts` (user-service.ts)
- **Classes**: `PascalCase` (UserService)
- **Functions**: `camelCase` (getUserById)
- **Constants**: `UPPER_SNAKE_CASE` (MAX_RETRY_COUNT)
- **Private members**: `_leadingUnderscore` (_privateMethod)
- **Interfaces**: `I` prefix or descriptive name (IUser or UserInterface)

### Example (Python)

- **Files**: `snake_case.py` (user_service.py)
- **Classes**: `PascalCase` (UserService)
- **Functions**: `snake_case` (get_user_by_id)
- **Constants**: `UPPER_SNAKE_CASE` (MAX_RETRY_COUNT)
- **Private members**: `_leading_underscore` (_private_method)

---

## File Structure (Placeholder)

**TypeScript/JavaScript Example**:

```typescript
// 1. Imports (grouped: external, internal, types)
import express from 'express';
import { UserService } from './services/user-service';
import type { User } from './types';

// 2. Constants
const MAX_USERS = 1000;
const DEFAULT_TIMEOUT = 5000;

// 3. Types/Interfaces
interface Config {
  port: number;
  host: string;
}

// 4. Main code
class UserController {
  constructor(private userService: UserService) {}

  async getUser(id: string): Promise<User> {
    // implementation
  }
}

// 5. Exports
export { UserController };
export type { Config };
```

---

## Testing Standards

### Framework

- **TBD** (определит Architect - Jest/PyTest/etc)

### Requirements

- **Minimum coverage**: 90%
- **Test file naming**: `*.test.ts` или `*_test.py` (рядом с source файлом)
- **Test structure**: Arrange-Act-Assert

### Test Example

```typescript
describe('UserService', () => {
  describe('getUserById', () => {
    it('should return user when user exists', async () => {
      // Arrange
      const userId = '123';
      const expectedUser = { id: '123', name: 'Test User' };

      // Act
      const result = await userService.getUserById(userId);

      // Assert
      expect(result).toEqual(expectedUser);
    });

    it('should throw error when user does not exist', async () => {
      // Arrange
      const userId = 'non-existent';

      // Act & Assert
      await expect(userService.getUserById(userId)).rejects.toThrow();
    });
  });
});
```

---

## Error Handling

### Best Practices

- **Always use try-catch** для async операций
- **Custom error classes** для domain errors
- **Log all errors** с контекстом
- **Never swallow errors silently**

### Example

```typescript
class UserNotFoundError extends Error {
  constructor(userId: string) {
    super(`User with id ${userId} not found`);
    this.name = 'UserNotFoundError';
  }
}

async function getUser(id: string): Promise<User> {
  try {
    const user = await database.findUser(id);
    if (!user) {
      throw new UserNotFoundError(id);
    }
    return user;
  } catch (error) {
    logger.error('Failed to get user', { userId: id, error });
    throw error;
  }
}
```

---

## Git Commit Messages

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Build/tools changes

### Example

```
feat(auth): add JWT authentication

Implemented JWT-based authentication with refresh tokens.
- Added login endpoint
- Added token refresh endpoint
- Added middleware for protected routes

Related to: task-001
```

---

## Code Review Checklist

### Style Compliance

- [ ] Naming conventions followed
- [ ] Indentation consistent (2 spaces)
- [ ] No lines > 100 characters
- [ ] Imports properly grouped

### Code Quality

- [ ] No code duplication
- [ ] Functions are single-purpose
- [ ] Complexity is reasonable (cyclomatic < 10)
- [ ] No magic numbers (use named constants)

### Testing

- [ ] Test coverage > 90%
- [ ] Edge cases tested
- [ ] Error cases tested
- [ ] Tests are readable and maintainable

### Documentation

- [ ] Public APIs documented
- [ ] Complex logic has explanatory comments
- [ ] README updated if needed

### Architecture Compliance

- [ ] Follows architectural decisions (ADRs)
- [ ] No architectural violations
- [ ] Module boundaries respected
- [ ] Dependencies are correct

---

**Примечание**: Этот файл будет обновлен Architect Agent после определения технологического стека.
