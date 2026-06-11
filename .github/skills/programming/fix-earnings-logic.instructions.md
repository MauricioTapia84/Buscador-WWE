# 💰 Skill: fix-earnings-logic (Manejo de Ingresos)

Esta skill define las reglas innegociables para el cálculo de ingresos y la gestión de estados financieros en FadeBooker.

## 🛠️ Reglas de Negocio
- **Ingresos Reales:** Solo se consideran como ingresos las citas en estado `confirmada` (pagada) o `completada`.
- **Exclusión de Pendientes:** Las citas en estado `pendiente` NO deben sumarse a las métricas financieras bajo ninguna circunstancia.
- **SSOT Financiero:** El campo `monto_total` en la tabla `Cita` es la fuente de verdad, pero debe contrastarse con `pago_abono` si se requiere el desglose de lo pagado vs adeudado.

## 💻 Patrones de Código (Backend)
Al realizar sumatorias de ingresos (repositorios), aplicar siempre:
```javascript
.whereIn('estado', ['confirmada', 'completada'])
```

## 📉 Visualización (Frontend)
- Los componentes de métricas deben mostrar el monto sumado de `confirmada` + `completada`.
- Las citas `pendientes` deben visualizarse como "Ingresos Proyectados" o "Por Confirmar", nunca como "Ingresos Realizados".
