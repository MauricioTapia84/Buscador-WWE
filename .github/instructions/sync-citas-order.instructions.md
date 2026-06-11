# 📅 Instrucciones: sync-citas-order (Ordenamiento de Citas)

Guía para mantener un orden consistente en todas las vistas de citas del sistema.

## 🏛️ Convenciones de Ordenamiento

### 1. Agenda (Próximas Citas y Hoy)
- **Orden:** Ascendente (`ASC`).
- **Propósito:** Mostrar lo más cercano en el tiempo primero para facilitar la gestión del día.
- **Uso en:** `Panel Dueño (Agenda del Día)`, `Agenda Barbero`.

### 2. Historial (Citas Pasadas)
- **Orden:** Descendente (`DESC`).
- **Propósito:** Mostrar las experiencias más recientes al principio del listado.
- **Uso en:** `Mis Citas (Cliente)`, `Reporte de Ventas`.

## 💻 Ejemplo de implementación en Knex
```javascript
// Agenda del día
query.orderBy('fecha_hora_inicio', 'asc');

// Historial
query.orderBy('fecha_hora_inicio', 'desc');
```
