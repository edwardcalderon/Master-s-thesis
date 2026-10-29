# Preprint CEX/DEX - borrador para revision de direccion

Fuente LaTeX y figura del manuscrito **Seguimiento de precios y fragilidad de liquidez en mercados cripto hibridos CEX/DEX**.

## Compilacion

Requiere XeLaTeX y una distribucion con las fuentes DejaVu:

```bash
cd thesis/preprint
xelatex manuscrito_cex_dex_revision_direccion_2026-10-29.tex
xelatex manuscrito_cex_dex_revision_direccion_2026-10-29.tex
```

El codigo y los resultados sinteticos que sustentan la figura estan en `../../experiments/cex_dex_preliminary/`.

## Alcance de evidencia

Los resultados E0-E3 son simulaciones sinteticas con 100 semillas por variante. Verifican mecanismos del prototipo; no validan mercados reales ni constituyen calibracion empirica.
