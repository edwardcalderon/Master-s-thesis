# Manuscrito de tesis

La edición en inglés es la principal. Cada revisión del manuscrito debe incluir una traducción al español. Ambas ediciones comparten la revisión del manuscrito y se compilan y publican juntas.

- Fuente en inglés: `main.tex` y `chapters/`
- Traducción obligatoria al español: `es/main.tex` y `es/chapters/`
- PDF en inglés: `main.pdf`
- PDF en español: `es/main.pdf`

La revisión actual del manuscrito es v0.8.5. La pregunta de investigación principal aprobada no cambia. H1 ahora interpreta la diferencia entre el plazo de la piscina aislada y la recuperación sostenida simulada. La repetición H2 y la comprobación de razones de capacidad de 1\,800 trayectorias distinguen las salidas únicas poco profundas de E1 asociadas al pánico de las salidas recurrentes de E3, y muestran que el control de capacidad fija iguala las razones configuradas en vez de descomponer capacidad y profundidad. La comparación H2 principal usa el área de exceso posrecuperación, que excluye el choque impuesto y los dos ticks de confirmación del retorno; su denominador condicional se informa de forma uniforme. Los resúmenes condensados describen los hallazgos analíticos, de simulación, sensibilidad y mapas reducidos. La comprobación del PDF informa el espacio ocupado y verifica que cada resumen y sus palabras clave permanezcan juntos en una página.

Todos los resultados siguen condicionados al modelo sintético. La repetición H2 reutiliza semillas existentes y no constituye una muestra Monte Carlo independiente; 7\,200 trayectorias con límite ligado a reservas reproducen exactamente las métricas archivadas. El control poco profundo con capacidad fija reduce sustancialmente el contraste posrecuperación de E3, pero el condicionamiento por recuperación, una sola profundidad y el diseño posterior al análisis inicial impiden una descomposición causal general. La coincidencia con el pánico es descriptiva y los episodios al final del tick no identifican causalidad intratick. No se realizó validación con datos de mercado. El trabajo futuro extiende el control de capacidad a un diseño factorial y reproduce eventos sincronizados con costos y demoras realistas.

El piloto v0.8.1 de tres intercambios DEX públicos ya no se presenta como evidencia de la tesis y su cita de datos se retiró de la bibliografía activa. La fuente BibTeX contiene 87 registros; la bibliografía compilada contiene 56 elementos citados (55 trabajos académicos y un registro del repositorio).

Los resultados Monte Carlo archivados conservan el identificador histórico `cex-dex-confirm-5b06486d695e`; la repetición exploratoria H2 es `cex-dex-h2-review-81af3e984e2c` y la comprobación de razones es `cex-dex-capacity-ratio-e269f980fd26`. Se reproducen con `python3 experiments/cex_dex_mvp/analyze_h2_revision.py` y `python3 experiments/cex_dex_mvp/analyze_capacity_ratio_check.py`; sus manifiestos registran las sumas de verificación de entradas y productos, y los scripts exportan las tablas del manuscrito y el resumen interactivo web. La versión del espacio de trabajo sigue separada en el archivo raíz `VERSION`. Las instantáneas previas permanecen sin cambios; v0.8.5 registra esta revisión bilingüe y conserva intacta la pregunta aprobada.

## Control de cambios de las preguntas

La pregunta principal y las subpreguntas de evaluación H2/H3 están bloqueadas en ambas
ediciones. Cada compilación del manuscrito ejecuta la verificación y un flujo de pull
request revisa los cambios en esas secciones. Una modificación sin registro aprobado hace
fallar la comprobación.

Para cambiar una pregunta se requiere aprobación explícita del autor de la tesis o de la
dirección. Añade un nuevo registro aprobado a thesis/question-control.json con la persona
que aprueba, la fecha, la motivación y la procedencia (por ejemplo, un documento de
retroalimentación aprobado, un acta o un issue); luego actualiza el texto marcado en inglés
y español y la redacción aprobada del registro. No sobrescribas los registros anteriores.
Ejecuta la verificación con:

```bash
pnpm thesis:questions:check
```

La verificación compara el texto marcado con el último registro aprobado y comprueba en los
pull requests que los registros anteriores permanezcan intactos. Valida la procedencia
registrada, pero no autentica a la persona indicada como aprobadora. Para exigir el
consentimiento, los cambios deben tramitarse mediante pull requests con aprobación requerida
por las reglas de protección de la rama del repositorio.

## Compilar ambos PDF

Desde este directorio:

```bash
make pdf
```

El objetivo comprueba primero que ambas fuentes declaren los idiomas requeridos, la misma revisión del manuscrito, la misma versión del espacio de trabajo y el mismo orden de capítulos. Después compila ambos PDF. CI publica el par como `master-thesis.pdf` y `master-thesis.es.pdf`.

La compilación ejecuta también `python3 ../scripts/check-thesis-layout.py`. Requiere Poppler (`pdftotext`) y rechaza una pregunta dividida entre páginas o separada de su título. También comprueba que cada resumen y sus palabras clave permanezcan juntos en una página e informa el espacio vertical que ocupan.

## Copias anónimas para evaluación doble ciego

Genera solo el PDF anónimo actual en inglés o español:

```bash
pnpm thesis:pdf:en-blind
pnpm thesis:pdf:es-blind
```

Para generar ambas copias anónimas sin compilar primero las ediciones con nombre:

```bash
make -C thesis pdf-blind
```

Para compilar las dos ediciones con nombre e incluir a demanda las dos copias anónimas:

```bash
make -C thesis pdf BLIND=1
# equivalente:
pnpm thesis:pdf:blind
```

Los archivos resultantes son thesis/build/manuscript-en-double-blind.pdf y
thesis/build/manuscrito-es-doble-ciego.pdf. El proceso oculta nombres, directores,
programa, institución y ubicación de las portadas; limpia los metadatos de autoría del PDF;
anonimiza la autocita del repositorio y los identificadores de ejecución, hashes y rutas
locales que podrían revelar el repositorio. Después busca esos marcadores en el texto
extraído de cada PDF y comprueba que la pregunta de investigación completa quede en una
página con su encabezado. Las fuentes de cada idioma conservan la misma pregunta de
investigación.

## Mantenimiento de la traducción

Al cambiar una revisión del manuscrito, actualiza primero la fuente en inglés y traduce el mismo contenido al español antes de publicar. Mantén alineados el orden de las secciones, las ecuaciones, tablas, figuras, citas, valores reportados y limitaciones. Traduce o explica las etiquetas en inglés incrustadas en las figuras. Ejecuta `pnpm language:check` desde la raíz del repositorio y luego compila con `make -C thesis pdf`.

El borrador del 29 de octubre informó cifras preliminares de la ruta fuente ausente `experiments/cex_dex_preliminary/`. La revisión v0.3.0 las reemplazó como evidencia activa por resultados trazables del MVP determinista y estocástico; conserva los valores y la figura anteriores en `versions/v0.2.0/`, marcados explícitamente como no verificados. Las nuevas ejecuciones no reproducen la tabla antigua. Consulta el [plan del MVP](../docs/es/mvp-plan.md) y el [ejecutor](../experiments/cex_dex_mvp/README.es.md).

---

[English](README.md)
