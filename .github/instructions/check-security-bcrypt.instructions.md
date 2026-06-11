# Seguridad: Hashing de Contraseñas con Bcrypt

**Apply to:** `**/*.{js,ts}`

## Contexto
El proyecto FadeBooker tiene una política de tolerancia cero para contraseñas en texto plano. Todas las contraseñas deben ser hasheadas con Bcrypt antes de ser persistidas en Azure SQL.

## Reglas para el Agente
1. **Detección de Texto Plano**: Si ves código que guarda `password` directamente en la base de datos sin pasar por un proceso de hash, detente y solicita la implementación de Bcrypt.
2. **Uso Obligatorio de Bcrypt**: 
   - Para registros: Usa `bcrypt.hash(password, 10)`.
   - Para login: Usa `bcrypt.compare(password, user.password_hash)`.
3. **Validación de Capas**: Asegúrate de que el hashing ocurra en la capa de aplicación o infraestructura, pero el dominio debe reconocer explícitamente la necesidad de protección.
4. **Tests**: Al generar tests para autenticación, incluye siempre un caso que verifique que la contraseña guardada NO es igual a la contraseña enviada en texto plano.

## Ejemplo Correcto
\`\`\`javascript
const hashedPassword = await bcrypt.hash(rawPassword, 10);
await usuarioRepository.create({ ...data, password: hashedPassword });
\`\`\`
