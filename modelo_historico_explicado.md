# Modelo histórico de perfil campeón

## Qué hace el modelo

El modelo **no predice el futuro** ni intenta adivinar si un luchador ganará un título mañana.

Lo que hace es esto:

1. Toma el historial visible de un luchador.
2. Mira 4 variables:
   - `total_matches`
   - `total_wins`
   - `total_losses`
   - `win_rate`
3. Compara ese perfil con los patrones históricos del dataset.
4. Entrega un **score de afinidad histórica con campeones**.

En palabras simples:

- Si el score es alto, el luchador se parece mucho al grupo de luchadores que en el dataset sí aparecen como campeones.
- Si el score es intermedio, el perfil queda en una zona mixta.
- Si el score es bajo, el perfil se parece más al grupo sin campeonatos visibles.

## Cómo fue entrenado

El modelo usado es una **Regresión Logística**.

Aprende a separar dos grupos:

- Luchadores con campeonato visible en los datos.
- Luchadores sin campeonato visible en los datos.

La variable objetivo es básicamente:

- `es_campeon = 1` si el luchador tiene al menos un título registrado.
- `es_campeon = 0` si no lo tiene.

## Qué significa un 100%

No significa:

- 100% de probabilidad de volver a ganar un título.
- 100% de certeza sobre el futuro.
- que el luchador sea “perfecto”.

Sí significa:

- que, usando solo esas 4 variables, el perfil quedó **muy del lado del grupo campeón**.
- que el modelo casi no tiene dudas al clasificarlo como similar a campeones históricos.

Ejemplo simple:

Si un luchador tiene muchísimos combates, muchísimas victorias y un win rate muy alto frente al resto del dataset, el modelo lo empuja muy fuerte hacia el lado “campeón”.

Por eso un caso como **John Cena** puede terminar en `100%`.

## Qué significa un 50%

Un `50%` significa que el luchador quedó **cerca de la frontera** entre ambos grupos.

Eso suele pasar cuando:

- algunas métricas se parecen a las de campeones,
- pero otras se parecen más a las de no campeones.

En simple:

- el modelo ve señales mezcladas,
- por eso no se inclina con fuerza hacia ningún lado.

## Qué significa un score bajo

Un score bajo significa que, con esas 4 variables, el perfil se parece más al grupo histórico sin campeonatos visibles.

No significa obligatoriamente que el luchador sea malo.

Puede significar también que:

- tiene poco historial en la base,
- le faltan combates registrados,
- o el dataset no lo representa bien.

## Por qué no basta con mirar el promedio

En la app se muestran promedios de campeones y no campeones para ayudar a interpretar.

Pero el modelo **no decide solo comparando contra el promedio**.

Hace algo más completo:

- aprende una frontera matemática usando **todos los casos históricos** del dataset,
- no solo una media general.

Por eso un luchador puede quedar en `100%` aunque sea un caso atípico muy por encima del promedio.

## Para qué le sirve esto a un fanático de WWE

Le sirve para:

- comparar leyendas, mid-carders y rookies con una misma lógica histórica,
- entender qué tan “perfil campeón” se ve un luchador dentro de la base,
- explorar datos de forma entretenida y argumentable,
- abrir conversación: “¿Este luchador se parece o no al patrón típico de campeón?”

## Qué limitaciones tiene

Este modelo tiene límites importantes:

- no usa contexto actual de WWE,
- no mira storyline,
- no considera popularidad real,
- no considera lesiones, retiros o fallecimiento,
- no distingue si el luchador sigue activo hoy,
- depende totalmente de la calidad del dataset.

Por eso debe presentarse como:

- **clasificación histórica comparativa**

y no como:

- **predicción real del próximo campeón**.

## Respuesta corta para el profesor

### “¿Qué hace el modelo?”

Clasifica qué tan parecido es el historial agregado de un luchador al patrón histórico de campeones del dataset.

### “¿Cómo lo hace?”

Usa Regresión Logística con 4 variables:

- combates,
- victorias,
- derrotas,
- win rate.

Con eso separa perfiles campeones y no campeones históricos.

### “¿Por qué da 100%?”

Porque el luchador cae muy claramente del lado del grupo campeón con esas 4 variables. No es una predicción del futuro; es una afinidad histórica extrema.

### “¿Por qué otro puede dar 50%?”

Porque queda cerca de la frontera de decisión del modelo. Tiene señales mezcladas y el modelo no se inclina con fuerza.

### “¿Qué valor aporta?”

Convierte datos históricos dispersos en una lectura comparativa simple, útil para análisis, narrativa y exploración del roster.
