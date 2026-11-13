# Nota de arquitectura

Este monorepo es deliberadamente pequeño. La aplicación web pública es la capa de presentación; los recursos de investigación siguen siendo portables y útiles sin JavaScript.

```text
apps/web          → sitio público bilingüe, explorador de cuadernos y visor de PDF
packages/content  → contenido versionado en inglés y español para la aplicación web
packages/ui       → tokens visuales compartidos
docs              → contexto de investigación en Markdown
notebooks         → evidencia ejecutable
thesis            → fuente LaTeX en inglés, traducción obligatoria y PDF en ambos idiomas
docs/es           → versiones españolas de la documentación pública de investigación
notebooks/es      → cuadernos traducidos con el mismo código y resultados
data              → límites explícitos para los datos brutos y procesados
```

El repositorio usa espacios de trabajo de pnpm y Turborepo para poder añadir en el futuro una API, un paquete de análisis o una segunda superficie de presentación sin mover el contrato público actual.

---

[English](../architecture.md)
