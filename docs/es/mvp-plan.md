# Plan del MVP: experimentos reproducibles para la hipótesis CEX/DEX

## Objetivo

Construir el modelo ejecutable más pequeño que permita probar H1a y H1b en condiciones controladas y, después, evaluar H1c con configuraciones reservadas. Los primeros resultados deben ser mecanísticos y sintéticos. El uso de datos de mercados públicos será una etapa posterior para estudiar la validez externa.

## Estado del repositorio

El ejecutor basado en la biblioteca estándar de `experiments/cex_dex_mvp/` ahora tiene rutas deterministas y estocásticas de selección. La ruta determinista cubre la mecánica de arbitraje E0/E1, la profundidad E2 con venta fija y la selección E3 emparejada de políticas LP. Su cuadrícula tiene 108 puntos E0/E1, cuatro niveles de liquidez E2 y 16 configuraciones emparejadas de política E3. La ruta estocástica separada implementa cuatro roles representativos y calendarios emparejados de órdenes aleatorias. La ejecución de selección actual usó 300 semillas tras cumplir la meta configurada de semiancho de intervalo de 0.005 unidades de error logarítmico para los seis contrastes emparejados de error máximo; sus 50.400 filas de trayectoria son resultados sintéticos de selección, no evidencia confirmatoria. El verificador cubre 2.654 estados deterministas y una selección estocástica de prueba de 504 estados, incluida la conservación de activos y los calendarios de ruido emparejados. Los escenarios E3 siguen separados de las condiciones confirmatorias reservadas. La banda de costos es un proxy, no un registro explícito de comisiones; las órdenes demoradas usan una cola simplificada sin flujo concurrente. El modelo sigue siendo más acotado que el simulador de agentes heterogéneos del diseño de investigación completo. La revisión v0.3.0 del manuscrito informa ahora los resultados trazables del MVP y limita su interpretación. Conserva el borrador del 29 de octubre en `thesis/versions/v0.2.0/`; sus resultados numéricos siguen sin verificarse porque no se recuperaron el código ni los artefactos originales de la ruta ausente `experiments/cex_dex_preliminary/`. Las nuevas ejecuciones del MVP no reproducen aquellas cifras. El alcance ODD y la secuencia de eventos del ejecutor actual están en la [especificación ODD](../experiments/cex_dex_mvp/ODD.md).

Ya existe una primera evaluación H1c: ajusta un mapa de dos estados por condición con shocks ±0.1 y lo prueba con semillas disjuntas y shocks reservados ±0.05. Solo coincidieron 3 de 8 etiquetas mayoritarias por condición/shock con la clasificación de Schur del mapa; es un diagnóstico acotado de roles representativos, no una validación amplia.

## Secuencia de trabajo

### 1. Congelar el contrato experimental

- Registrar la pregunta de investigación y H1a/H1b/H1c como comparaciones falsables.
- Extender el contrato ODD inicial E0/E1/E2 para cubrir el mundo mínimo completo: referencia CEX exógena, reservas CPMM, orden de eventos, costos y banda, límites de inventario/capital, momento de shocks y políticas de agentes.
- El autor aprobó la taxonomía de cuatro roles: arbitrajista acotado, trader de ruido, trader de tendencia/pánico como una política y LP con condiciones estática/adaptativa. Revisar umbrales, límites de inventario y rangos operativos antes de confirmar el experimento.
- Definir las métricas principales antes de ejecutar escenarios confirmatorios: error de seguimiento excedente `D_t`, error máximo, tiempo sostenido de retorno a la banda, impacto de precio de una venta fija, liquidez mínima y medidas de cascada/venta forzada cuando correspondan.
- Separar las configuraciones usadas para seleccionar mecanismos de las configuraciones confirmatorias.

**Entregable:** especificación ODD completa y versionada y protocolo experimental que vincule cada métrica con H1a, H1b o H1c.

### 2. Implementar y verificar el motor de mercado mínimo

- Ampliar el primer modelo estocástico de agentes representativos hasta el simulador heterogéneo especificado solo después de revisar los cuatro roles y sus reglas. Mantener las reglas actuales como supuestos de selección y añadir más agentes únicamente cuando su propósito y políticas sean explícitos.
- Explicitar reservas, inventario, costos, latencia, capacidad y orden de eventos en una configuración versionada.
- Verificar las identidades CPMM y la contabilidad: reservas positivas, actualización de reservas tras un swap, retiro proporcional de LP que conserva el precio marginal e impacto mayor para la misma venta absoluta después de retirar liquidez.
- Verificar que el arbitraje acerque el precio DEX a la banda sin arbitraje únicamente cuando los costos, la latencia y la capacidad configurados permitan ejecutar la operación.

**Entregable:** un comando de ejecución que produzca una trayectoria determinista junto con su configuración y metadatos de ejecución.

### 3. Ejecutar los contrastes H1a y H1b (E0–E3)

- **E0 / H1a:** aplicar un shock CEX aislado con arbitraje activado y desactivado; comparar el error excedente y el tiempo de retorno a la banda.
- **E1 / H1a:** variar la capacidad, los costos y la demora del arbitraje manteniendo fijo el shock y el estado inicial.
- **E2 / H1b:** aplicar la misma venta absoluta después de una reducción de liquidez estática frente a una proporcional/adaptativa. Reportar por separado el impacto mecánico inmediato y cualquier retroalimentación posterior.
- **E3 / H1b y límites del modelo:** seleccionar una regla de umbral única con trayectorias emparejadas de políticas estáticas y adaptativas bajo las mismas condiciones deterministas de shock y ventas de x. Mantener esta cuadrícula de selección separada de las configuraciones confirmatorias posteriores.
- Usar semillas emparejadas en comparaciones estocásticas cuando los flujos aleatorios sean compatibles. No contar como réplicas estadísticas independientes las ejecuciones repetidas sin ruido. Elegir la cantidad de réplicas a partir de un objetivo de precisión o convergencia e informar tamaños de efecto e intervalos de incertidumbre.

**Entregable:** configuraciones, series temporales, tabla resumen emparejada, figura regenerada y un script que reproduzca cada valor informado desde una copia limpia del repositorio. Los puntos actuales son sensibilidades deterministas, no réplicas estadísticas.

### 4. Evaluar H1c y delimitar dónde falla el mapa reducido

- Estimar o diagnosticar el mapa reducido sobre una cuadrícula de selección declarada de exceso inicial, presión de órdenes, capacidad y condiciones de liquidez.
- Congelar el procedimiento de estimación y los umbrales de clasificación antes de la evaluación.
- Probar la contracción/persistencia en configuraciones de confirmación separadas; comparar la clasificación del mapa con los resultados del ABM e informar las discrepancias por régimen.
- Tratar las condiciones de Schur como diagnósticos locales del mapa reducido, no como garantías para el ABM estocástico ni para los mercados reales.

**Entregable:** resultados de clasificación en configuraciones reservadas, incertidumbre y un mapa explícito de las regiones en que la aproximación funciona y falla.

El primer diagnóstico reservado ya está disponible. Usa las mismas reglas de agentes representativos con nuevas semillas y magnitudes de shock; su coincidencia de 3/8 etiquetas mayoritarias muestra que el mapa actual no clasifica estos regímenes de forma fiable. Ampliar este análisis solo después de revisar las reglas de los agentes y las regiones de operación.

### 5. Empaquetar la ruta de reproducción

- Fijar el entorno de Python y sus dependencias.
- Proporcionar comandos estables para una ejecución, un barrido de parámetros, el análisis, las comprobaciones de invariantes y la reproducción de figuras.
- Guardar con cada ejecución su ID, configuración, semilla, commit del código, versión del entorno, métricas, series temporales, resultados de invariantes y checksums.
- Añadir comprobaciones automatizadas de los invariantes CPMM/contables y una pequeña ejecución determinista de referencia. Mantener como artefactos de versión los resultados experimentales grandes que no quepan en Git.
- Actualizar el manuscrito solo a partir de resultados regenerados y separar claramente la evidencia sintética de cualquier replay posterior de datos de mercados públicos.

**El MVP está completo cuando:** una copia nueva puede reproducir E0–E3 y el análisis confirmatorio del mapa reducido con los comandos documentados, verificar los invariantes del modelo y rastrear cada valor de tabla o figura hasta su configuración, semilla y commit del código.

## Posponer hasta después del MVP

Ejecución en exchanges en vivo, nodos de mainnet, MEV avanzado, AMM de liquidez concentrada, simulación completa de libro de órdenes límite, préstamos/puentes, aprendizaje por refuerzo, modelos de pronóstico y una ingesta amplia de datos. Después de estabilizar las pruebas sintéticas del mecanismo y la ruta de reproducción, se podrá añadir una comparación pequeña con datos públicos.

---

[English](../mvp-plan.md)
