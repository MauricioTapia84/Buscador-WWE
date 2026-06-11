# Skill: Check Security Bcrypt

Audita automáticamente el código para asegurar que ninguna contraseña se almacene o valide en texto plano, obligando el uso de hashing con Bcrypt.

## Acciones
1. **Escaneo de Repositorios/Services**: Busca implementaciones de `UsuarioRepository` y `AuthService`.
2. **Detección de Texto Plano**: Alerta si encuentras comparaciones directas de strings (ej. `user.password === input.password`) o guardado directo de strings sin hash.
3. **Corrección Sugerida**:
   - Para guardar: `await bcrypt.hash(password, saltRounds)`
   - Para validar: `await bcrypt.compare(password, user.passwordHash)`

## Constraints
- **Cero Tolerancia**: No permitas el paso de estas vulnerabilidades a producción.
- **Contexto**: Aplica especialmente en `Producto/back-fadebooker/src/modules/usuarios/`.
