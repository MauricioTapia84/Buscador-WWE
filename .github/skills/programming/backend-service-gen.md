# 🔧 Backend Service Generator Skill

Standardizes the creation of new features in the `@backend-agent`.

## 🎯 Purpose
Enforce Hexagonal Architecture and JSend-like responses in JavaScript.

## 🛠️ Actions
1. **Domain Model**: Define the entity as a JS Class or Plain Object in `src/domain/`.
2. **Application UseCase**: Implement logic in `src/application/usecases/` with Zod validation.
3. **Infrastructure Repository**: Implement `src/infraestructure/database/` using Knex.js.
4. **Interface Controller**: Create endpoints in `src/interfaces/http/controllers/`.
5. **Unit Test**: Generate a `*.test.js` file using Jest.

## ⚠️ Constraints
- Language: **JavaScript (CommonJS)**, NOT TypeScript.
- Naming: **Spanish** for entities (Usuario, Cita).
- Dependency Injection: Pass repository instance to the UseCase constructor.
