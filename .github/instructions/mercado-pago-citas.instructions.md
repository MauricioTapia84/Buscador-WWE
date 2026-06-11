# Validación de Abonos Mercado Pago

**Apply to:** `Producto/back-fadebooker/src/modules/citas/**`

## Contexto
En FadeBooker, la lógica de negocio prohíbe la creación o confirmación de citas sin un abono previo (entre 30% y 100%) procesado vía Mercado Pago.

## Instrucciones para el Agente
1. **Validación de Pago**: Al crear o actualizar una cita (`CitaController`, `CitaService`), asegúrate de que el campo relacionado con el pago (ej. `monto_abono`, `id_transaccion_mp`) sea validado.
2. **Estado de Cita**: Una cita no debe marcarse como `confirmada` si el estado del pago en Mercado Pago no es `approved`.
3. **Manejo de Errores**: Si se intenta crear una cita sin los metadatos de Mercado Pago, lanza un error de negocio claro: `Error: Se requiere abono de retención para agendar (30%-100%)`.
4. **Seguridad**: Verifica que los tokens de Mercado Pago se manejen mediante variables de entorno y no estén hardcodeados.

## Referencia Técnica
- Consulte `knowledge/TECHNICAL_KNOWLEDGE.md` para el detalle de la política de retenciones.
- Revise `Producto/back-fadebooker/src/modules/pagos/` para la integración existente.
