# Manuscrito de tesis

La edición en inglés es la principal. Cada revisión del manuscrito debe incluir una traducción al español. Ambas ediciones comparten la revisión del manuscrito y se compilan y publican juntas.

- Fuente en inglés: `main.tex` y `chapters/`
- Traducción obligatoria al español: `es/main.tex` y `es/chapters/`
- PDF en inglés: `main.pdf`
- PDF en español: `es/main.pdf`

La revisión actual del manuscrito es v0.2.0. La versión del espacio de trabajo se registra por separado en el archivo raíz `VERSION` y se sincroniza en ambas entradas LaTeX. La instantánea de la fuente anterior, que solo estaba en español, se conserva en `versions/v0.1.1/`.

## Compilar ambos PDF

Desde este directorio:

```bash
make pdf
```

El objetivo comprueba primero que ambas fuentes declaren los idiomas requeridos, la misma revisión del manuscrito, la misma versión del espacio de trabajo y el mismo orden de capítulos. Después compila ambos PDF. CI publica el par como `master-thesis.pdf` y `master-thesis.es.pdf`.

## Mantenimiento de la traducción

Al cambiar una revisión del manuscrito, actualiza primero la fuente en inglés y traduce el mismo contenido al español antes de publicar. Mantén alineados el orden de las secciones, las ecuaciones, tablas, figuras, citas, valores reportados y limitaciones. Traduce o explica las etiquetas en inglés incrustadas en las figuras. Ejecuta `pnpm language:check` desde la raíz del repositorio y luego compila con `make -C thesis pdf`.

El borrador recibido el 29 de octubre informa simulaciones preliminares en `experiments/cex_dex_preliminary/`, una ruta que no existe en esta copia. Ahora existe un ejecutor mecánico determinista E0/E1/E2 más acotado en `../experiments/cex_dex_mvp/`, pero no reproduce la tabla reportada. Trata esos valores como afirmaciones del manuscrito hasta recuperar la implementación y los artefactos originales o regenerar los contrastes completos. Consulta el [plan del MVP](../docs/es/mvp-plan.md) y el [ejecutor](../experiments/cex_dex_mvp/README.es.md).

---

[English](README.md)
