## [Sin publicar]

### Corregido

- Se eliminó de ambos anexos una nota editorial sobre la sustitución de una fuente bibliográfica.
- Se corrigió la paginación de la pregunta de investigación en el manuscrito v0.5.1: el título y la pregunta completa permanecen juntos y la tabla de antecedentes queda antes de esta sección en ambas ediciones. La pregunta y los hallazgos se conservan.
- Se añadió una comprobación de la maquetación de los PDF a la compilación bilingüe y al flujo de Pages para detectar una pregunta dividida o interrumpida antes de la publicación.

## [0.1.8] - 2026-11-25

### Añadido

- Se añadió el plan de implementación SIM-002 para la reproducción visual 3D de los hallazgos del micromundo, trazas pareadas de eventos, exploración acotada de escenarios y escenarios guardados en el navegador. La función queda pendiente de implementación.
- Se definieron criterios de evidencia, accesibilidad, interfaz bilingüe, reproducibilidad y rendimiento, además del alcance de investigación independiente que requieren los mundos persistentes compartidos y los agentes evolutivos.

### Corregido

- Se concilió el registro de tareas y la transición de simulación con la evidencia confirmatoria de v0.5.0 y se corrigieron notas desactualizadas sobre la versión del manuscrito. Las versiones del manuscrito y del experimento se conservan.

# Registro de cambios

## [0.1.7] - 2026-11-24

### Añadido

- Se añadió la revisión v0.5.0 del manuscrito, reestructurada según la retroalimentación de la dirección: introducción en seis párrafos, planteamiento del problema y estado del arte, justificación, hipótesis, objetivos, metodología, resultados, discusión y conclusiones, trabajos futuros, bibliografía y anexos, en inglés y español.
- Se añadió el protocolo confirmatorio (`confirm.py`, `confirm_config.json`) con semillas de exploración y de confirmación disjuntas, inferencia pareada por semilla y corrección de Holm, y `export_thesis_data.py` para exportar los datos de figuras y tablas a `thesis/figures/data/`.
- Se añadió una auditoría de referencias (`thesis/literature-audit/`) que verifica cada una de las 87 entradas de la bibliografía con Crossref, arXiv o el editor y las ordena por relevancia.
- Se añadió la instantánea de fuentes v0.5.0 del manuscrito en `thesis/versions/`.

### Cambios

- Se reemplazaron los resultados del manuscrito por la ejecución confirmatoria `cex-dex-confirm-5b06486d695e`: H1 y H2 se sostienen en promedio, H2 solo con la menor profundidad, y H3 supera a la persistencia pero no a un autorregresivo escalar. Todos los resultados son sintéticos; no se alcanzó la precisión objetivo de H1.
- Se actualizaron el resumen, las palabras clave y la versión del sitio web según el nuevo manuscrito.
- Se actualizó la documentación de referencias, del experimento y de la tesis.

## [0.1.6] - 2026-11-13

### Cambios

- Se reordenó la página principal para mostrar el resumen del manuscrito antes del laboratorio de simulación, con navegación y numeración de secciones acordes.

## [0.1.5] - 2026-11-13

### Añadido

- Se añadieron al sitio los resúmenes y las palabras clave exactos de los manuscritos en inglés y español.
- Se añadieron verificaciones para mantener sincronizados el título web y los resúmenes con ambas ediciones del manuscrito.

### Cambios

- El artefacto de Pages publica únicamente los PDF finales en inglés y español.
- Se eliminaron las descargas directas de las fuentes LaTeX de la sección del manuscrito.

## [0.1.4] - 2026-11-13

### Añadido

- Se añadió un laboratorio bilingüe de simulación en el navegador para el seguimiento de precios E0/E1 y la comparación de profundidad E2, con controles acotados y datos del escenario copiables.
- Se añadieron SIM-001 para dar seguimiento a la simulación estática y THESIS-004 para auditar la redacción genérica de trabajo futuro.

### Cambios

- Se actualizó la página principal con los títulos oficiales de la tesis en inglés y español, se ubicó el laboratorio inmediatamente después del título y se redujo el texto introductorio.
- Se mejoró la presentación en pantallas estrechas para mostrar los resultados de la simulación antes de sus controles.

## [0.1.3] - 2026-11-12

### Cambios

- Se aclararon los resúmenes bilingües, la pregunta, los objetivos y los límites de la hipótesis del mapa reducido.
- Se corrigieron la descripción del escenario de liquidez adaptativa y la referencia ODD.
- Se registró la revisión sustantiva del manuscrito como v0.4.0 y se conservaron las instantáneas bilingües v0.3.1 y v0.4.0.

## [0.1.2] - 2026-11-12

### Añadido

- Superficies públicas en inglés y español para la aplicación, documentación, cuadernos y tesis, con inglés como idioma principal.
- Revisión local con refscan para ambas ediciones de la tesis y un fixture de evaluación etiquetado.
- Ejecutores reproducibles deterministas y estocásticos emparejados del MVP CEX/DEX, con un diagnóstico H1c reservado.

### Cambios

- Se actualizó el manuscrito bilingüe a v0.3.1 con resultados trazables del MVP, la taxonomía de cuatro roles aprobada por el autor y los límites explícitos del resultado H1c de 3/8.
- Se conservaron las fuentes v0.2.0 y v0.3.0; las cifras preliminares históricas siguen sin verificarse.

## [0.1.1] - 2026-10-15

### Cambios

- Se reorganizó el sitio público de la tesis como una sala de lectura académica con temas claro y oscuro.
- Se añadió un modo de lectura persistente con una columna más estrecha y menos distracciones.
- Se corrigió la detección de paquetes del sistema de versionado para sincronizar los manifiestos explícitos del espacio de trabajo antes de validar una versión.

## [0.1.0] - 2026-10-15

### Añadido

- Espacio de investigación público con pnpm y Turborepo.
- Borrador LaTeX de tesis v0.1.0 y flujo de publicación de PDF en GitHub Pages.
- Explorador de cuadernos, superficie de documentación y base de reproducibilidad.

---

[English](CHANGELOG.md)
