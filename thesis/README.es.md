# Manuscrito de tesis

La edición en inglés es la principal. Cada revisión del manuscrito debe incluir una traducción al español. Ambas ediciones comparten la revisión del manuscrito y se compilan y publican juntas.

- Fuente en inglés: `main.tex` y `chapters/`
- Traducción obligatoria al español: `es/main.tex` y `es/chapters/`
- PDF en inglés: `main.pdf`
- PDF en español: `es/main.pdf`

La revisión actual del manuscrito es v0.8.0. Conserva los hallazgos confirmatorios
congelados de v0.5.0, corrige la paginación bilingüe y elimina de ambos anexos la nota
editorial sobre la sustitución de una fuente. Añade una sensibilidad de ingeniería con
semillas nuevas: al retorno puede seguirle otra salida de la banda, y el efecto con poca
profundidad cambia según el tamaño de las órdenes relativo a las reservas y la regla
de pánico. Las conclusiones derivan requisitos de monitoreo y pruebas de estrés, pero
mantienen el carácter sintético de los hallazgos y requieren validación con un par real
antes de cualquier uso operativo. La revisión v0.6.1 añadió un glosario técnico bilingüe después de las tablas de notación. La revisión v0.7.0 incorpora un análisis cuadrático no exhaustivo de Lyapunov para los mapas afines ajustados y aclara que el estado contable registrado no se considera completo de Markov. No demuestra estabilidad del simulador estocástico completo ni cambia los hallazgos experimentales. El manuscrito estructura la tesis según la retroalimentación de la dirección (introducción en seis párrafos; planteamiento del problema y estado del arte; justificación; hipótesis; objetivos; metodología; resultados; discusión y conclusiones; trabajos futuros; bibliografía; anexos) e informa una ejecución confirmatoria (`cex-dex-confirm-5b06486d695e`) con semillas de exploración y de confirmación disjuntas. La versión del espacio de trabajo se registra por separado en el archivo raíz `VERSION` y se sincroniza en ambas entradas LaTeX. Las instantáneas `versions/v0.4.0/` y anteriores conservan las fuentes previas; v0.2.0 conserva el borrador del 29 de octubre y sus cifras preliminares no verificadas.

La revisión v0.8.0 incorpora una comparación reservada de un mapa híbrido sensible a la banda frente al mapa afín, con 300 semillas nuevas. La mejora predictiva del error de precio es pequeña y depende de la condición; no mejora la presión de flujo ni demuestra estabilidad del simulador completo o validez en mercados reales.

Los datos confirmatorios originales de figuras y tablas de `figures/data/` se exportan de la ejecución congelada con `experiments/cex_dex_mvp/export_thesis_data.py`; `figures/data/manifest.json` registra la ejecución de origen y los hashes. Los datos suplementarios de `figures/engineering/` provienen del análisis 0.6.0 e
incluyen el identificador y hashes de la nueva ejecución. La bibliografía (87 entradas) se verificó entrada por entrada; véase `literature-audit/REFERENCE_AUDIT.md`.

## Compilar ambos PDF

Desde este directorio:

```bash
make pdf
```

El objetivo comprueba primero que ambas fuentes declaren los idiomas requeridos, la misma revisión del manuscrito, la misma versión del espacio de trabajo y el mismo orden de capítulos. Después compila ambos PDF. CI publica el par como `master-thesis.pdf` y `master-thesis.es.pdf`.

La compilación ejecuta también `python3 ../scripts/check-thesis-layout.py`. Requiere Poppler (`pdftotext`) y rechaza una pregunta dividida entre páginas o separada de su título. El flujo de Pages aplica la misma comprobación antes de publicar los archivos.

## Mantenimiento de la traducción

Al cambiar una revisión del manuscrito, actualiza primero la fuente en inglés y traduce el mismo contenido al español antes de publicar. Mantén alineados el orden de las secciones, las ecuaciones, tablas, figuras, citas, valores reportados y limitaciones. Traduce o explica las etiquetas en inglés incrustadas en las figuras. Ejecuta `pnpm language:check` desde la raíz del repositorio y luego compila con `make -C thesis pdf`.

El borrador del 29 de octubre informó cifras preliminares de la ruta fuente ausente `experiments/cex_dex_preliminary/`. La revisión v0.3.0 las reemplazó como evidencia activa por resultados trazables del MVP determinista y estocástico; conserva los valores y la figura anteriores en `versions/v0.2.0/`, marcados explícitamente como no verificados. Las nuevas ejecuciones no reproducen la tabla antigua. Consulta el [plan del MVP](../docs/es/mvp-plan.md) y el [ejecutor](../experiments/cex_dex_mvp/README.es.md).

---

[English](README.md)
