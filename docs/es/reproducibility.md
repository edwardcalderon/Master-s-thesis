# Protocolo de reproducibilidad

El flujo público se organiza en un ciclo pequeño y repetible:

```text
fuente → transformación → cuaderno → figura/tabla → capítulo de tesis → versión
```

## Configuración local

```bash
pnpm install
pnpm dev
```

Ejecuta `pnpm build` antes de publicar. Los entornos de los cuadernos deben declarar
la versión de Python y sus dependencias en los metadatos del cuaderno o en un futuro
`environment.yml`. Los conjuntos de datos grandes o restringidos deben mantenerse
fuera de Git; documenta su checksum y nota de adquisición en `data/README.md`.

## Superficies obligatorias en inglés y español

El idioma predeterminado de la aplicación es el inglés; el encabezado del sitio permite
cambiar a español. Mantén sincronizado el contenido de interfaz en inglés y español.
Los documentos internos, cuadernos, registros de tareas y recursos experimentales pueden
estar únicamente en inglés; las traducciones existentes son opcionales.
`pnpm language:check` comprueba la estructura de los locales de la aplicación y la
alineación de revisión del manuscrito.

## Compilación de la tesis en ambos idiomas

El manuscrito principal está en inglés. Su traducción al español es obligatoria en cada
revisión. Desde `thesis/`, `make pdf` comprueba que ambos árboles de fuentes declaren
la misma versión del espacio de trabajo y revisión del manuscrito, y luego compila los
PDF en inglés y español. El flujo de Pages publica ambos en el mismo despliegue; si
falta la fuente o el PDF en español, la publicación está incompleta.

## MVP determinista de mecanismos de mercado

El primer simulador es un ejecutor determinista de mecanismos CPMM, no el modelo de
agentes heterogéneos ni el prototipo preliminar no verificado que describe el
manuscrito. Ejecútalo desde la raíz del repositorio:

```bash
python3 experiments/cex_dex_mvp/run.py
```

Cada ejecución guarda la configuración, series temporales, resúmenes por escenario,
checksums de fuente/configuración y metadatos del entorno en el directorio ignorado
`experiments/cex_dex_mvp/output/`. La configuración incluida es determinista y no usa
semillas aleatorias. Consulta las [notas del ejecutor](../../experiments/cex_dex_mvp/README.md),
la [especificación ODD](../../experiments/cex_dex_mvp/ODD.md) y la [hoja de ruta del MVP](mvp-plan.md).
No sustituyas con estas salidas la tabla preliminar del manuscrito hasta reconciliar
todos los escenarios y definiciones.

## Lista para publicar una versión

- Confirma que `VERSION` y `VERSION_HISTORY.json` coincidan.
- Vuelve a ejecutar los cuadernos usados en la versión actual de la tesis.
- Ejecuta `pnpm language:check`.
- Compila ambos PDF con `make -C thesis pdf` y verifica que estén la edición principal en inglés y la traducción al español.
- Registra la procedencia de los datos y cualquier cambio de supuestos.
- Publica el sitio estático desde el mismo commit que los artefactos de la tesis.

---

[English](../reproducibility.md)
