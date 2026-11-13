# Manuscrito de tesis

La edición en inglés es la principal. Cada revisión del manuscrito debe incluir una traducción al español. Ambas ediciones comparten la revisión del manuscrito y se compilan y publican juntas.

- Fuente en inglés: `main.tex` y `chapters/`
- Traducción obligatoria al español: `es/main.tex` y `es/chapters/`
- PDF en inglés: `main.pdf`
- PDF en español: `es/main.pdf`

La revisión actual del manuscrito es v0.3.2. La versión del espacio de trabajo se registra por separado en el archivo raíz `VERSION` y se sincroniza en ambas entradas LaTeX. La instantánea bilingüe v0.3.0 conserva la fuente previa a la actualización de la taxonomía de roles aprobada por el autor. La instantánea v0.2.0 conserva el borrador del 29 de octubre con sus cifras preliminares no verificadas; también se retiene v0.1.1.

## Compilar ambos PDF

Desde este directorio:

```bash
make pdf
```

El objetivo comprueba primero que ambas fuentes declaren los idiomas requeridos, la misma revisión del manuscrito, la misma versión del espacio de trabajo y el mismo orden de capítulos. Después compila ambos PDF. CI publica el par como `master-thesis.pdf` y `master-thesis.es.pdf`.

## Mantenimiento de la traducción

Al cambiar una revisión del manuscrito, actualiza primero la fuente en inglés y traduce el mismo contenido al español antes de publicar. Mantén alineados el orden de las secciones, las ecuaciones, tablas, figuras, citas, valores reportados y limitaciones. Traduce o explica las etiquetas en inglés incrustadas en las figuras. Ejecuta `pnpm language:check` desde la raíz del repositorio y luego compila con `make -C thesis pdf`.

El borrador del 29 de octubre informó cifras preliminares de la ruta fuente ausente `experiments/cex_dex_preliminary/`. La revisión v0.3.0 las reemplazó como evidencia activa por resultados trazables del MVP determinista y estocástico; conserva los valores y la figura anteriores en `versions/v0.2.0/`, marcados explícitamente como no verificados. Las nuevas ejecuciones no reproducen la tabla antigua. Consulta el [plan del MVP](../docs/es/mvp-plan.md) y el [ejecutor](../experiments/cex_dex_mvp/README.es.md).

---

[English](README.md)
