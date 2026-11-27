# Manuscrito v0.8.4

Instantánea inmutable de la fuente bilingüe y la evidencia. Esta revisión conserva las preguntas de investigación aprobadas en v0.8.3 e incorpora una repetición exploratoria H2 de 9,000 trayectorias con semillas existentes.

El análisis distingue las salidas únicas asociadas al pánico en E1 estático poco profundo de las salidas recurrentes en E3, añade una ablación comparable sin pánico y evalúa un control de capacidad fija según las reservas iniciales a profundidad baja. El control reduce sustancialmente el contraste del área posrecuperación de E3, pero no identifica una proporción causal universal: cubre una profundidad y condiciona el resultado a la recuperación. Sigue pendiente el diseño factorial completo.

La instantánea conserva ambas fuentes, el control de preguntas, figuras y datos, el protocolo de repetición, entradas comprimidas, dependencias del ejecutor, salida bruta de 9,000 trayectorias y sumas de verificación. Todos los resultados siguen condicionados al simulador especificado sin comisiones; no constituyen validación de mercado. El mapa reducido de dos estados no supera al AR(1) escalar; la repetición sensible a la banda no es un pronóstico en tiempo real.

## Reproducir la repetición

Desde este directorio, ejecuta:

    python3 experiments/cex_dex_mvp/analyze_h2_revision.py \
      --output-root /tmp/v0.8.4-h2-replay \
      --export-dir /tmp/v0.8.4-h2-export \
      --web-export /tmp/v0.8.4-h2-export/web_findings.json

Se reutilizan las semillas 2000--2299. La entrada predeterminada es el archivo comprimido de métricas de ingeniería en experiments/cex_dex_mvp/fixtures/. El protocolo congelado está en experiments/cex_dex_mvp/H2_REVISION_PROTOCOL_0.7.0.md; la ejecución archivada y su manifiesto están bajo experiments/cex_dex_mvp/archived-run/. Usa una ruta --output-root nueva o vacía en cada ejecución. El identificador de ejecución y las sumas de verificación CSV deben coincidir con el manifiesto archivado.

Las instantáneas v0.8.3 y anteriores permanecen sin cambios.

[English](README.md)
