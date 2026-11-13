# Política de idiomas

## Idioma predeterminado del proyecto

El inglés (`en`) es el idioma principal del trabajo interno, los archivos fuente, las
notas de investigación, los cuadernos y la documentación. Los recursos internos pueden
estar únicamente en inglés. Pueden conservarse traducciones complementarias existentes
cuando sean útiles, pero son opcionales y no constituyen un requisito de publicación.

## Superficies bilingües obligatorias

Solo dos superficies del proyecto deben estar disponibles en inglés y español:

1. **La interfaz de la aplicación web y su contenido dirigido a usuarios.** El inglés
   es el idioma predeterminado; se puede seleccionar español en la interfaz. Ambos
   archivos de idioma deben contener las mismas claves y estructura de contenido.
2. **Los PDF finales de la tesis.** Cada revisión final en inglés tiene una traducción
   completa al español. Ambos PDF comparten la misma revisión del manuscrito, se compilan
   juntos y se publican juntos. Los archivos TeX son insumos de compilación y no se
   copian a Pages.

| Función | Artefacto público en Pages |
| --- | --- |
| Inglés principal | `thesis/master-thesis.pdf` |
| Traducción obligatoria al español | `thesis/master-thesis.es.pdf` |

La revisión del manuscrito es distinta de la versión del espacio de trabajo. La
comprobación de idioma exige los locales de la aplicación y la coincidencia del idioma,
revisión, versión del espacio de trabajo y orden de capítulos de la tesis. No exige
traducir documentos internos, cuadernos, registros de tareas, configuraciones ni
recursos experimentales.

## Actualización y publicación

1. Actualiza las cadenas y el contenido de la interfaz en inglés; en el mismo cambio,
   actualiza el contenido de interfaz correspondiente en español.
2. Edita el manuscrito en inglés y aumenta su revisión.
3. Traduce al español todo el cambio de la tesis, conservando ecuaciones, tablas,
   significado de figuras, citas, resultados, limitaciones y orden de secciones.
   Traduce o explica las etiquetas en inglés incrustadas en las figuras cuando sea
   necesario.
4. Ejecuta `pnpm language:check` y luego `make -C thesis pdf`.
5. Publica ambos PDF de la tesis en el mismo despliegue de Pages. CI compila las dos
   entradas y copia los artefactos como `master-thesis.pdf` y `master-thesis.es.pdf`.

`language-policy.json` define los locales obligatorios de la aplicación y las rutas del
manuscrito. `scripts/check-language-pair.mjs` comprueba estas superficies; las
traducciones adicionales de documentos son opcionales.

---

[English](../language-policy.md)
