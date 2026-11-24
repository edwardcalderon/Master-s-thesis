# Laboratorio de Tesis de Maestría

Un espacio de investigación abierto y reproducible para una tesis de maestría. El inglés es el idioma principal del proyecto, el sitio y la documentación. La aplicación web, la documentación, los cuadernos, el changelog y el historial de versiones tienen ediciones en inglés y español. Cada versión de la tesis debe incluir una traducción obligatoria al español del manuscrito en PDF.

La experiencia pública toma como referencia algunos elementos útiles de [GeoAuPredict](https://github.com/edwardcalderon/GeoAuPredict): una presentación clara de la investigación, un explorador de cuadernos, una superficie de documentación y una publicación orientada a artefactos mediante GitHub Pages. El código específico para predicción de oro y los servicios pesados se dejan fuera hasta que la tesis los necesite.

## 📋 Últimos cambios (v0.1.7)

### Añadido

- Se añadió la revisión v0.5.0 del manuscrito, reestructurada según la retroalimentación de la dirección: introducción en seis párrafos, planteamiento del problema y estado del arte, justificación, hipótesis, objetivos, metodología, resultados, discusión y conclusiones, trabajos futuros, bibliografía y anexos, en inglés y español.
- Se añadió el protocolo confirmatorio (`confirm.py`, `confirm_config.json`) con semillas de exploración y de confirmación disjuntas, inferencia pareada por semilla y corrección de Holm, y `export_thesis_data.py` para exportar los datos de figuras y tablas a `thesis/figures/data/`.
- Se añadió una auditoría de referencias (`thesis/literature-audit/`) que verifica cada una de las 87 entradas de la bibliografía con Crossref, arXiv o el editor y las ordena por relevancia.
- Se añadió la instantánea de fuentes v0.5.0 del manuscrito en `thesis/versions/`.

### Cambios

- Se reemplazaron los resultados del manuscrito por la ejecución confirmatoria `cex-dex-confirm-5b06486d695e`: H1 y H2 se sostienen en promedio, H2 solo con la menor profundidad, y H3 supera a la persistencia pero no a un autorregresivo escalar. Todos los resultados son sintéticos; no se alcanzó la precisión objetivo de H1.
- Se actualizaron el resumen, las palabras clave y la versión del sitio web según el nuevo manuscrito.
- Se actualizó la documentación de referencias, del experimento y de la tesis.

Consulta el [historial completo](./CHANGELOG.es.md) y las [versiones de GitHub](https://github.com/edwardcalderon/Master-s-thesis/releases). [English version](./README.md).

## Estructura del monorepo

```text
.
├── apps/web/             # Página pública en Vite + React y visor de artefactos
├── packages/content/     # Metadatos tipados de tesis, cuadernos y documentación
├── packages/ui/          # Tokens visuales compartidos para futuras aplicaciones
├── docs/                 # Notas públicas de investigación y reproducibilidad
│   └── es/                # Versiones en español de la documentación pública
├── notebooks/            # Cuadernos Jupyter y versiones en español en notebooks/es/
├── thesis/               # Espacio de trabajo del manuscrito; Pages publica solo ambos PDF
│   └── es/                # Edición obligatoria en español
├── data/                 # Límites entre datos brutos y procesados; los datos grandes no van en Git
├── .github/workflows/    # Compilación y publicación en GitHub Pages
├── VERSION               # Versión pública única
├── VERSION_HISTORY.json  # Registro de versiones en inglés
└── VERSION_HISTORY.es.json # Registro de versiones en español
```

## Desarrollo local

```bash
pnpm install
pnpm dev
```

La aplicación web se ejecuta en `http://localhost:5173`. Las comprobaciones de producción son:

```bash
pnpm version:check
pnpm language:check
pnpm lint
pnpm typecheck
pnpm build
pnpm docs:build
```

## PDF de la tesis

El sitio público ofrece únicamente el PDF final en inglés y el PDF obligatorio en español. El equipo puede compilar ambos manuscritos localmente con:

```bash
cd thesis
make pdf
```

`make pdf` genera ambos archivos: `thesis/main.pdf` (inglés) y `thesis/es/main.pdf` (español). El flujo de Pages publica los dos junto con sus fuentes; una compilación que solo genere inglés está incompleta. Los PDF binarios se excluyen de Git de forma predeterminada para mantener canónicas las fuentes de ambos idiomas.

## Política de idiomas

- El inglés (`en`) es el idioma principal del resumen del proyecto, el sitio, la documentación y la fuente canónica de la tesis.
- La aplicación web, la documentación, los cuadernos, el changelog y el historial de versiones cuentan con ediciones en español; la aplicación inicia en inglés y recuerda el idioma elegido.
- La tesis se redacta primero en inglés y cada revisión debe incluir una traducción al español (`es`).
- Los PDF en inglés y español comparten la misma revisión del manuscrito y se compilan y publican juntos. El sitio permite elegir inglés o español.
- Ejecuta `pnpm language:check` para comprobar la estructura de las traducciones de la aplicación, los pares de documentos y cuadernos, el historial de versiones y la paridad de las revisiones del manuscrito. CI ejecuta esta comprobación y compila ambos PDF.

Consulta la [política de idiomas](docs/es/language-policy.md) para conocer las reglas de fuentes y publicación.

## Seguimiento de versiones

[`@edcalderon/versioning`](https://www.npmjs.com/package/@edcalderon/versioning) gestiona los incrementos SemVer del espacio de trabajo y el changelog en inglés. El sincronizador del repositorio proyecta la versión en `VERSION`, ambos historiales, los dos archivos de idioma de la aplicación, las dos macros LaTeX de versión y los bloques de versión de ambos README. `pnpm readme:update` copia las entradas completas en inglés y español del changelog a los resúmenes correspondientes del README. Una macro distinta identifica la revisión del manuscrito y mantiene vinculadas las dos ediciones.

<!-- versioning:release:start -->
**Versión actual:** [`v0.1.7`](https://github.com/edwardcalderon/Master-s-thesis/releases/tag/v0.1.7)
**Registro:** [Versiones de GitHub](https://github.com/edwardcalderon/Master-s-thesis/releases) · sincronizado con `@edcalderon/versioning`
<!-- versioning:release:end -->

El pie de página del sitio muestra la misma versión y enlaza directamente con su etiqueta de GitHub. La configuración está en [`versioning.config.json`](versioning.config.json).

```bash
pnpm version:validate  # valida @edcalderon/versioning y los artefactos de la tesis
pnpm readme:update     # sincroniza los resúmenes de ambos README con sus changelogs
pnpm secrets:check     # analiza los cambios preparados con la extensión de secretos
pnpm release:patch     # prepara la siguiente versión patch, sincroniza y valida
```

`pnpm release:patch` no crea un commit ni una etiqueta. Actualiza la versión, sincroniza los metadatos del paquete y la tesis, refresca los resúmenes de ambos README y ejecuta `release:verify`. Antes de usarlo, completa las entradas en inglés y español del changelog para la nueva versión. Revisa los cambios y luego crea el commit y la etiqueta `vX.Y.Z`. Husky revisa los archivos preparados en busca de secretos y valida la integridad de las versiones antes de cada commit.

## GitHub Pages

Los cambios enviados a `main` ejecutan [`.github/workflows/pages.yml`](.github/workflows/pages.yml). El flujo compila la aplicación web, copia la documentación pública y los cuadernos al artefacto estático y publica el resultado en GitHub Pages.

---

[English](README.md)
