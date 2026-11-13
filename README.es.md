# Laboratorio de Tesis de Maestría

Un espacio de investigación abierto y reproducible para una tesis de maestría. El inglés es el idioma principal del proyecto, el sitio y la documentación. La aplicación web, la documentación, los cuadernos, el changelog y el historial de versiones tienen ediciones en inglés y español. Cada versión de la tesis debe incluir una traducción obligatoria al español del manuscrito en PDF.

La experiencia pública toma como referencia algunos elementos útiles de [GeoAuPredict](https://github.com/edwardcalderon/GeoAuPredict): una presentación clara de la investigación, un explorador de cuadernos, una superficie de documentación y una publicación orientada a artefactos mediante GitHub Pages. El código específico para predicción de oro y los servicios pesados se dejan fuera hasta que la tesis los necesite.

## 📋 Últimos cambios (v0.1.4)

### Añadido

- Se añadió un laboratorio bilingüe de simulación en el navegador para el seguimiento de precios E0/E1 y la comparación de profundidad E2, con controles acotados y datos del escenario copiables.
- Se añadieron SIM-001 para dar seguimiento a la simulación estática y THESIS-004 para auditar la redacción genérica de trabajo futuro.

### Cambios

- Se actualizó la página principal con los títulos oficiales de la tesis en inglés y español, se ubicó el laboratorio inmediatamente después del título y se redujo el texto introductorio.
- Se mejoró la presentación en pantallas estrechas para mostrar los resultados de la simulación antes de sus controles.

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
├── thesis/               # Manuscrito LaTeX en inglés e instrucciones de compilación
│   └── es/                # Fuente de la traducción obligatoria al español
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

La fuente primaria en inglés está en [`thesis/main.tex`](thesis/main.tex), y la traducción obligatoria al español está en [`thesis/es/`](thesis/es/). Compila ambos PDF localmente con:

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
**Versión actual:** [`v0.1.4`](https://github.com/edwardcalderon/Master-s-thesis/releases/tag/v0.1.4)
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
