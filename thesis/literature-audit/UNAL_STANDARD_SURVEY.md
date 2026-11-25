# UNAL "minimum standard" survey: theses directed by Prof. Ospina Arango and/or Prof. Branch Bedoya

Date of survey: 2026-11-23. Method: the UNAL repository (DSpace 7) was queried through its public REST API
(`bffrepositorio.unal.edu.co/server/api`, the backend named in `repositorio.unal.edu.co/assets/config.json`) for
the advisor fields "Ospina Arango, Juan David" (12 records) and "Branch Bedoya, John Willian" (76 records).
Sixteen PDFs were downloaded to `/tmp/unal_theses` and read with `pdftotext -layout` (nothing was executed).
Every handle below was resolved against the API (metadata) and returned HTTP 301 on `repositorio.unal.edu.co/handle/unal/N`.
Page counts are PDF pages (`pdfinfo`) and match the repository `dc.format.extent` where one is given.

Limits, stated plainly:
- The repository search page itself (Angular UI) is not scrapable; the REST API was used instead. The API result sets are
  complete for the exact advisor strings above, but a thesis where the advisor's name is spelled differently would be missed.
- "Profesor John" is NOT confirmed by the advisor's message. Evidence only: the repository shows Ospina Arango and
  **John Willian Branch Bedoya** as co-directors of two Ingenieria de Sistemas master's theses (handles 84387 and 81179).
  No other "John" co-directs with Ospina in the repository. Ask the advisor to confirm before relying on this.
- Measured formatting (fonts) was read from PDF font tables; margins were not measured, the official template was used instead.
- The Facultad de Minas "Arial 12, interlineado 1, margenes 3,5" rule came from a web-search summary of an admissions page
  (`minas.medellin.unal.edu.co/formacion/admisiones?id=1464`), which returned 404 when fetched. Treat it as UNVERIFIED and,
  per the summary itself, as applying to admission proposals, not final theses.

## 1. Reviewed theses

Program abbreviations: MII-Sist = Maestria en Ingenieria - Ingenieria de Sistemas (the student's program family);
MI-Anal = Maestria en Ingenieria - Analitica; all are Facultad de Minas, Sede Medellin, Depto. de Ciencias de la Computacion y de la Decision unless noted.
"Dir." = director(s) as recorded in repository metadata; first-listed is not necessarily the formal director.

| # | Handle | Title (short) | Author | Year | Program | Dir. | Pages | Citation style |
|---|--------|---------------|--------|------|---------|------|-------|----------------|
| 1 | https://repositorio.unal.edu.co/handle/unal/90091 | Comparacion de modelos estocasticos y de aprendizaje de maquina para el pronostico de la mortalidad edad-especifica por tuberculosis en Colombia | Simon Cuartas Rendon | 2026 | MI-Anal (profundizacion) | Ospina Arango | 79 | numeric [n] |
| 2 | https://repositorio.unal.edu.co/handle/unal/90990 | Modelo de prediccion basado en aprendizaje de maquina para estimar el valor de las exportaciones del sector de desarrollo de sistemas informaticos en Antioquia | Juan Manuel Castrillon Mora | 2026 | MI-Anal | Ospina Arango | 71 | author-year |
| 3 | https://repositorio.unal.edu.co/handle/unal/84387 | Dimensionamiento laboral para un canal de venta de seguros basado en un modelo de prediccion de la demanda empleando tecnicas de aprendizaje de maquinas | Ligia Fernanda Zabala Gamez | 2023 | MII-Sist | Branch Bedoya + Ospina Arango | 41 | author-year |
| 4 | https://repositorio.unal.edu.co/handle/unal/81179 | Metodo de segmentacion de imagenes de la prostata tomadas mediante resonancia magnetica mediante tecnicas de inteligencia artificial | Juan Esteban Duque Miranda | 2021 | MII-Sist | Branch Bedoya (dir.) + Ospina Arango (codir.) | 42 | author-year |
| 5 | https://repositorio.unal.edu.co/handle/unal/81608 | Identificacion de factores a mejorar para aumentar la recomendacion, analisis de NPS para clientes neutros a partir de PLN | Leydi Agudelo Restrepo | 2022 | MI-Anal | Ospina Arango | 70 | numeric [n] |
| 6 | https://repositorio.unal.edu.co/handle/unal/81613 | Entendiendo comportamientos ciudadanos viales a partir de datos abiertos e inteligencia artificial | Juan Camilo Del Rio Cuervo | 2022 | MI-Anal | Ospina Arango | 49 | author-year |
| 7 | https://repositorio.unal.edu.co/handle/unal/80870 | Modelamiento espacial de la oferta y la demanda en el territorio colombiano a partir de analitica de datos financieros | Juan Jose Ospina Carvajal | 2021 | MI-Anal | Ospina Arango | 63 | numeric [n] |
| 8 | https://repositorio.unal.edu.co/handle/unal/89017 | Analisis de imagenes en platos de comida tipicos de Antioquia: vision por computadora para el conteo de carbohidratos (diabetes) | Andres Felipe Jaramillo Tamayo | 2025 | MI-Anal (profundizacion) | Ospina Arango + 2 codirectores | 86 | author-year |
| 9 | https://repositorio.unal.edu.co/handle/unal/78495 | Modelos de emprendimiento a partir de datos abiertos en el Valle de Aburra | Daniel Villada Cano | 2020 | Maestria en Ing. Administrativa | Bedoya Botero + Ospina Arango | 75 | author-year |
| 10 | https://repositorio.unal.edu.co/handle/unal/75561 | Prediccion y seleccion de variables con bosques aleatorios en presencia de variables correlacionadas | Nestor Ivan Cardona Alzate | 2019 | Estadistica (simulation study) | Ospina Arango + Correa Morales | 53 | author-year, LaTeX |
| 11 | https://repositorio.unal.edu.co/handle/unal/89313 | Measuring reported and observed financial well-being in emerging economies (PhD, Ing. - Industria y Organizaciones) | Juan Felipe Hernandez Zuluaga | 2025 | Doctorado | Medina Hurtado + Ospina Arango | 129 | author-year (APA) |
| 12 | https://repositorio.unal.edu.co/handle/unal/81631 | Metodo para la segmentacion de clientes incorporando la prediccion del valor monetario del cliente | Davinson Mosquera Gonzalez | 2022 | MI-Anal | Branch Bedoya | 94 | author-year |
| 13 | https://repositorio.unal.edu.co/handle/unal/81466 | Metodologia para la gestion de la calidad de los datos (data driven, datos maestros) | Yubar Daniel Marin Benjumea | 2022 | MII-Sist | Branch Bedoya + Iral Palomino | 69 | author-year |
| 14 | https://repositorio.unal.edu.co/handle/unal/78323 | Analitica de datos en la gestion de recuperacion de la cartera financiera | Jonathan Steven Herrera Roman | 2020 | MII-Sist | Branch Bedoya | 58 | author-year |
| 15 | https://repositorio.unal.edu.co/handle/unal/87853 | Clasificacion de transacciones ACH ... con tecnicas de inteligencia artificial | Laura Maria Caro Zapata | 2025 | MI-Anal | Branch Bedoya | 40 | author-year |
| 16 | https://repositorio.unal.edu.co/handle/unal/82053 | Prediccion de riesgos en salud, para personas con obesidad empleando aprendizaje de maquinas | Wilmer Jesus Agamez Julio | 2022 | MI-Anal | Branch Bedoya | 51 | author-year |

Closest to our manuscript (computational/simulation/finance + master's in Sistemas): #3, #4 (the two verified Ospina+Branch co-directed Sistemas theses),
#1 and #2 (the two most recent Ospina-directed, model-comparison designs), #11 (finance, PhD-level, hypotheses H1-H3 explicit).
Note: #10 is a simulation-study thesis (Estadistica, 2019) and a good precedent for a "Estudios de simulacion" chapter, but it is a different program/era and uses the older LaTeX template.
Not found in the repository: any Ospina/Branch thesis on agent-based modelling or discrete-event simulation proper.

Observation about the "standard": the 2 co-directed Sistemas theses are SHORT (41 and 42 total pages). Total pages of the 16 range 40-129; median about 65.
The advisor's 35-page minimum is therefore consistent with the shortest accepted theses; the safer target is 60-80 pages total (see 2.2).

## 2. Synthesized minimum-standard checklist

### 2.1 What these theses actually do vs. what the advisor asked for (important differences)

The advisor's 11-chapter outline is MORE demanding than any reviewed thesis. Specifically:
- No reviewed thesis has a stand-alone "Hipotesis" chapter. Only #2 has a section "Pregunta de Investigacion e Hipotesis" (1.4), #11 has Research question / Hypothesis / Objectives in the introduction plus H1-H3 inside the empirical chapter, #9 has "2.3 Hipotesis o problema a resolver", and #12 states its "hipotesis principal" only in contributions and conclusions.
- Most reviewed Ospina theses (#1, #5, #7) use the order Planteamiento/Justificacion -> Objetivos -> Marco teorico/Estado del arte -> Metodologia -> Resultados -> Conclusiones; i.e., Objetivos BEFORE the state of the art, and the state of the art is placed after objectives. The advisor's order (Planteamiento + estado del arte -> Justificacion -> Hipotesis -> Objetivos -> Metodologia) is different and should simply be followed.
- The UNAL official template recommends 3-6 chapters including conclusions and says chapter titles are "agreed between student and director" (template text). So an 11-chapter outline is allowed if the director asks for it; follow the advisor.
- Only #1 and #2 have "trabajos futuros/recomendaciones" as a sub-section of Conclusiones (11.2 and 6.2 respectively); a separate chapter 9 "Trabajos futuros" is fine but is not the observed pattern.
- Bilingual front matter (title, resumen, palabras clave, abstract, keywords) is mandatory per UNAL Resolucion 023 de 2015 art. 2 (quoted in the official template).

### 2.2 Page budget (derived from #1, #2, #3, #12, #8; proposal for a ~60-70 page manuscript)

Observed body lengths (body = Introduccion through Conclusiones, excluding bibliography/annexes):
#1 about 60 pp (Planteamiento 5, Justificacion 1, Objetivos 1, Marco teorico 12, Metodologia 6, EDA/datos 10, Modelos 20, Discusion 3, Conclusiones 2);
#2 about 56 pp (Introduccion 4, Cap.1 descripcion+objetivos+hipotesis+marco 8, Metodologia 6, EDA 6, Modelos 21, Proyecciones 7, Conclusiones 4, anexos 4);
#3 about 37 pp (Introduccion 11 incl. problem/objectives, Marco teorico 1, Revision sistematica 4, Metodo 8, Resultados 6, Conclusiones 1, Trabajo futuro 1);
#12 about 76 pp (Introduccion 6, Marco teorico 3, Revision sistematica 15, caracterizacion 17, metodo 28 over 3 chapters, conclusiones 4).

Proposed budget for our 11-chapter structure (pages, 11-12 pt Arial 1.5 spacing is the template default; adjust to reach the target):

| Cap. | Section | Min pages | Notes |
|------|---------|-----------|-------|
| 1 | Introduccion | 3-4 | Template: introduccion of min 2, max 4 pages |
| 2 | Planteamiento del problema y estado del arte | 10-14 | Observed: #1 problem 5 + antecedentes 5; #2 marco+antecedentes 5-6; #3 literature review 4 |
| 3 | Justificacion | 1-2 | #1: 1 page; #2: 1.5 pages |
| 4 | Hipotesis | 1 | Model: #2 (one hypothesis + research question), #11 (H1-H3 with direction) |
| 5 | Objetivos | 1 | 1 general + 3-4 specific (observed #1: 3, #2: 3, #3: 4, #11: 4, #12: 4) |
| 6 | Metodologia | 6-10 | #1: 6, #2: 6; include data, models, validation, metrics, reproducibility |
| 7 | Resultados | 12-20 | Largest chapter in all reviewed theses (#1 about 30 incl. EDA) |
| 8 | Discusion y conclusiones | 4-6 | #1: 3+2, #2: 4 |
| 9 | Trabajos futuros | 1-2 | #1 uses 1 page |
| 10 | Bibliografia | 3-5 | #1: 3+ pp, #3: 4 pp |
| 11 | Anexos | as needed | #2 has A (code repo link) and B (data dictionary) |
| | Front matter | roman numerals | see 2.5 |

Sum of body chapters 1-9: about 40-60 pages; with front matter and bibliography the PDF reaches 55-75 pages, in line with #1, #2, #5, #6. Stay well under the template's suggestion of at most 120 pages.

### 2.3 What each chapter must contain (patterns observed)

1. Introduccion. The template says it must present importance, origin (theoretical and practical antecedents), objectives, scope, limitations, methodology, significance and application, and should not duplicate the abstract. Observed patterns: #2's Introduccion (4 pp) = context + importance, gap/institutional limitation, general objective + specific objectives in one sentence, scope and data limitation, methodology sequence, results preview, and significance. #3/#12 open with "1.1 Motivacion, 1.2 Trabajos previos, 1.3 Problema de investigacion, 1.4 Objetivos, 1.5 Contribuciones" and close the introduction with the document structure ("una estructura del documento dividida en 7 capitulos ..."). The six-paragraph outline the advisor requires (problem; why it matters; what has been done and achieved; our proposal; expected achievement; organization) is compatible with all of these; #12 and #6 ("1.3 Estructura del documento") are the only ones with an explicit organization subsection, so add it.
2. Planteamiento del problema y estado del arte. #1: starts with "Generalidades" (importance), then domain background, relevance, and the explicit research question "¿que tipo de modelo ... permite realizar un pronostico mas preciso y robusto ...?". #12: problem paragraph stating the gap ("generalmente, estos estudios se quedan hasta la prediccion ... pero no se expresa el paso para incorporarlo ...") then one main research question. #3/#12 add a systematic literature review chapter (search equations, inclusion criteria, bibliometrics, tables of relevant papers); this is the strongest state-of-the-art pattern found and it is what supports a "gap" claim.
3. Justificacion. Short (1-2 pp). #1: two paragraphs: gap in national literature + methodological and applied contribution. #2: cites authors to support need (policy, planning).
4. Hipotesis. Pattern from #2: "Hipotesis: La aplicacion de modelos basados en aprendizaje de maquina permitira predecir con mayor precision ... en comparacion con metodos tradicionales." One directional, testable statement, placed with the research question. #11 numbers sub-hypotheses H1-H3 with a direction of effect (positive association). Our hypothesis must name the comparison and a measurable criterion.
5. Objetivos. All reviewed theses give ONE general objective + 3-4 specific objectives, bullet or Roman-numeral list, all starting with an infinitive verb. General-objective verbs observed: Identificar, Desarrollar, Proponer, Implementar, Analizar. Specific-objective verbs: Revisar y sistematizar, Ajustar, Contrastar, Caracterizar, Seleccionar, Disenar, Validar, Definir, Evaluar, Construir, Examinar, Comparar, Traducir. Each specific objective is a step that yields a deliverable and each can be tied to a chapter. #12 is the best exemplar: objectives (1) Caracterizar los datos, (2) Seleccionar metodos de prediccion, (3) Disenar un metodo, (4) Validar resultados correspond one-to-one to chapters 4, 5, 6, 7.
6. Metodologia. Observed structure (#1 Cap. 5): literature review -> data understanding -> modelling (selection, evaluation, validation period, explainability). #2 Cap. 2: data sources and collection, variable construction and preprocessing, algorithm selection with theoretical grounding, validation strategy (temporal split), evaluation metrics. #12 repeats a mini-structure "Introduccion / Metodologia / Resultados / Conclusiones" inside each methodological chapter and ends each chapter with its own conclusions, which makes traceability explicit. #8 uses numbered "Etapas 1-9" mapped to pipeline steps.
7. Resultados. Descriptive/EDA first, then models, with a comparison table of identical metrics for all models (#1 Tables 8-x/9-x, 10-1 to 10-3; #2 4.5 "Sintesis global"). #1 and #2 also report bias/error-direction tables and computing time. Figures follow the "Figura N-M: caption. Elaboracion propia / Tomado de [n]" convention.
8. Discusion y conclusiones. #1 Ch.10 "Discusion: contraste de modelos" (fit, time, explainability) followed by Ch.11 "Conclusiones" with 11.1 Sintesis de resultados and 11.2 Recomendaciones y trabajos futuros. #2 6.1 states it answered the general objective and then explicitly qualifies against the hypothesis: it reports that ML did not guarantee better prediction than the statistical baseline (SARIMAX RMSE 223.26 vs LSTM 240.78 vs SARIMA 259.10) i.e., the hypothesis was only partly supported and the thesis says so. This is the "only conclude what results show" model. #12 8.1 uses one bullet per objective/chapter and a final bullet that validates the hypothesis with a number ("12 % ... mas ingresos"). #8 (#89017) headers each conclusion bullet by objective topic ("Con relacion al objetivo especifico de implementar una metodologia de preprocesamiento ..."). #3 uses 5 short bullets then "Trabajo futuro" in its own chapter (the only reviewed thesis with a stand-alone future-work chapter).
9. Trabajos futuros. 1-2 pp, concrete extensions tied to limitations (#1: extra covariates, zero-inflated models, hierarchical models, response transformations; #3: add exogenous variables for one series).
10. Bibliografia. Complete, consistent style (see 2.6).
11. Anexos. Lettered ("A. Anexo: ..."). #2: code repository link and data dictionary; #5 #6: model description (e.g., "Anexo 1. YOLOv5").

### 2.4 Objective -> hypothesis -> methodology -> results -> conclusion traceability pattern to adopt

Synthesis (best practice drawn from #2, #11, #12 and the template's rule "Las conclusiones deben ser la respuesta a los objetivos o propositos planteados"):
- One research question; one (or H1..Hk) directional hypothesis in cap. 4 stated in measurable terms.
- One general objective that tests/answers the hypothesis; 3-4 specific objectives numbered OE1..OE4 (verbs in infinitive, one deliverable each).
- Methodology (cap. 6) opens with a table: OE -> method/step -> data -> metric/acceptance criterion -> where reported (chapter/section).
- Results (cap. 7) sections carry the same OE numbers in their titles or lead sentences.
- Discussion/conclusions (cap. 8): one sub-heading or bullet per OE (as #12 does), followed by an explicit verdict on the hypothesis (supported / partly supported / not supported) with the number that justifies it (as #2 and #12 do), and a limitations paragraph. No conclusion without a result table/figure reference.
- Trabajos futuros (cap. 9) only from stated limitations.
- A one-page traceability matrix (RQ, H, OG, OE1-4 -> metodologia -> resultado -> conclusion) is NOT present in any reviewed thesis; it would exceed the standard and is cheap to add in chapter 8 or an annex.

### 2.5 Front matter (official template, handle unal/55405, plus what the theses show)

Order in the best-formatted theses (#1, #4, #2): portada (no number, counted) -> segunda portada with "Tesis presentada como requisito para optar por el titulo de: Magister en Ingenieria - ... ; Director(a): ..." (and Linea/Grupo de investigacion in #4, #8) -> dedicatoria or epigraph (optional) -> Declaracion de autoria (#1 only; optional; template notes that signatures must NOT be included in the repository PDF, Ley 1581 de 2012) -> Agradecimientos (optional; #1, #4, #8) -> Resumen (+ palabras clave) -> Abstract (+ keywords) -> Contenido -> Lista de figuras -> Lista de tablas -> Lista de simbolos y abreviaturas (optional; #1 with entries in order of appearance) -> Introduccion (page 1 in Arabic numerals).
- Preliminary pages in Roman numerals, body in Arabic starting at Introduccion = 1 (template). Cover and title page count but are not numbered.
- Title, resumen and palabras clave in Spanish AND title, abstract and keywords in English, inside the same PDF (Res. 023/2015, as quoted in the template).
- Abstract length: template says maximum 250 words, recommended to be "analitico" (objectives, design, main results, conclusions). #1's abstract is about 230 words (single paragraph, quantified result statements, no citations).
- No signatures/handwritten data (template note).
- Do not use the Ancizar typeface (template note: restricts copying from the repository).

### 2.6 Palabras clave (advisor: "Separa las palabras clave")

Convention found everywhere (all 16 theses and the template):
- A labelled line at the end of the abstract: "Palabras clave:" (Spanish) and "Keywords:" (English).
- Keywords separated by COMMAS (not semicolons, not one run-on phrase), each a short term; first word capitalized, rest lower case, e.g. #1 "Palabras clave: Pronostico, series de tiempo, aprendizaje de maquina, aprendizaje profundo, mortalidad, tuberculosis"; #4 ends the list with a period; #1 does not. Choose one and be consistent.
- Count: template says minimum 3, maximum 7 ("preferiblemente use lenguaje tecnico-cientifico"). Observed: 3 (#3), 5 (#4), 6 (#1, #2), 7 (#8).
- Terms are taken from the text, in the same order in both languages; the repository stores each keyword as a separate metadata value (dc.subject.proposal), which is probably what "separa" means: do not write a single sentence-like string such as "simulation, optimization and machine learning for finance"; list 3-7 individual terms.
- Recommended for us: 5-7 comma-separated terms in Spanish and the same terms in English.

### 2.7 Formatting conventions

From the official template (UNAL SINAB, "Plantilla para la presentacion de Tesis UNAL", https://repositorio.unal.edu.co/handle/unal/55405, file "Plantilla sugerida para presentacion de tesis maestria y doctorado", Word):
- Letter paper, margins 2.54 cm (top, bottom, outer) and 3.6 cm inner; double-sided printing assumed; page number top right on odd pages, top left on even pages, Arial 11.
- Body text Arial 11 (the template text calls Garamond, Calibri, Cambria or Times New Roman acceptable alternatives); interlineado 1.5; impersonal and generic voice; foreign terms in italics.
- Headings Arial: chapter title 20 pt bold (lower case, first line, 100 pt space before, 24 pt after), level 2 = 16, level 3 = 14; numbering only to the third level; below that use square bullets; each chapter starts on a new odd page; no "13A/14 bis" numbering.
- Figures: caption above, "Figura capitulo-numero: titulo" with source at the end of the figure (not as a footnote); tables: caption above, same numbering, repeat header and "(Continuacion)" if split; equations numbered by chapter, e.g. (2.1).
- Citation style: the template does NOT impose one (mentions NTC 1486 and APA aspects and invites any standard "con rigurosidad"). Observed: author-year (APA-like) in 12 of 16 (including all Minas Sistemas theses #3, #4, #13, #14), numeric IEEE-like in 3 (#1, #5, #7). Either is acceptable; use one consistently and cite everything including software and data.
- Length: template suggests not exceeding 120 pages unless the faculty sets a limit; 3-6 chapters recommended (see 2.1).
Observed in the theses themselves: letter size in all 11 PDFs inspected; fonts Arial in 9 (the template default, mostly Word), Times New Roman in 1 (#8), Palatino (LaTeX) in 1 (#1). So fonts are not strictly enforced; Arial 11 or 12 with the template layout is safe.

Other UNAL norms found (not fetched in full, from web search only; verify before citing): Acuerdo 035 de 2003 del Consejo Academico (reglamento de propiedad intelectual; articles 24, 26, 27 on deposit of theses), Circular 023 de 2019 de Secretaria General (obligatory deposit in the Repositorio Institucional for master's/doctoral theses), Acuerdo 033 de 2008 del CSU (posgrado trabajos finales/tesis/examen de calificacion). No Facultad de Minas thesis formatting guide was found beyond the university template.

### 2.8 Minimum-standard checklist for our manuscript (short form)

- [ ] 11 chapters in the advisor's order; at least 35 pages of body (target 55-70 pages total incl. front matter and bibliography).
- [ ] Introduccion 3-4 pp, six paragraphs as required, ending with the organization of the document.
- [ ] Planteamiento + estado del arte 10-14 pp, ideally with an explicit literature-search protocol (as in #3/#12) and a sentence stating the gap.
- [ ] One research question and a directional, measurable hypothesis (cap. 4) using the "Hipotesis:" form of #2; sub-hypotheses H1-Hk if several effects are tested (as in #11).
- [ ] General objective + 3-4 specific objectives with infinitive verbs; each answers/tests the hypothesis and maps to one methodology step and one results section.
- [ ] Methodology table OE -> method -> data -> metric -> section; reproducibility statement (code link in an annex as in #2).
- [ ] Results compare all methods with the same metrics; report bias/uncertainty and computing time where relevant (as in #1).
- [ ] Conclusions: one item per specific objective, verdict on the hypothesis (supported / partly / not), limitations; nothing concluded beyond a reported result (as #2 does when its hypothesis is only partly confirmed).
- [ ] Trabajos futuros derived from limitations only; Bibliografia in one consistent style; annexes lettered.
- [ ] Front matter: portada, segunda portada with director(s), dedicatoria/agradecimientos (optional), resumen (max 250 words) + palabras clave (3-7, comma-separated), abstract + keywords, Contenido, Lista de figuras, Lista de tablas, abreviaturas; Roman numerals before the Introduccion; no signatures; no Ancizar font.
- [ ] Layout per template: letter, margins 2.54 / 3.6 inner, 1.5 spacing, Arial 11, chapter headings on new pages, figure/table numbering chapter-number, captions above.

## 3. Citation opportunities (verified metadata)

Verification method: Crossref API (`api.crossref.org/works/{DOI}`) and UNAL repository API; nothing below was invented. Only cite what is topically relevant to the manuscript.

Advisor's own work (Ospina Arango):
1. Hernandez, J. A., & Ospina, J. D. (2010). A multi dynamics algorithm for global optimization. *Mathematical and Computer Modelling*, 52(7-8), 1271-1278. https://doi.org/10.1016/j.mcm.2010.03.024 (Crossref lists the authors as "J.A. Hernandez" and "J.D. Ospina"; the web search summary suggested a third author, Villada, which Crossref does NOT list for this paper). Relevant if the manuscript uses global/metaheuristic optimization.
2. Hernandez, J. A., Ospina, J. D., & Villada, D. (2011). Logit model based performance analysis of an optimization algorithm. *AIP Conference Proceedings* (Numerical Analysis and Applied Mathematics ICNAAM 2011), pp. 1400-1407 as given by Crossref. https://doi.org/10.1063/1.3637883 (Crossref also lists the proceedings editors T. E. Simos, G. Psihoyios, Ch. Tsitouras, Z. Anastassi). Relevant for performance analysis of stochastic optimizers via simulation; volume number not returned, add it before citing.
3. Ardia, D., Ospina Arango, J. D., & Giraldo Gomez, N. D. (2011). Jump-diffusion calibration using differential evolution. *Wilmott*, 2011(55), 76-79. https://doi.org/10.1002/wilm.10034 (Crossref author field is garbled, "Juan David / Ospina Arango"; author order taken from the DOI record title block and Google Scholar). Relevant for finance models calibrated with evolutionary algorithms.
4. Hernandez Zuluaga, J. F., Ospina Arango, J. D., Medina Hurtado, S., & Patino Hurtado, G. A. (2025). Using objective measures to predict subjective financial well-being with machine learning methods. *Journal of Financial Counseling and Planning*, 37(2), 281-297. https://doi.org/10.1891/jfcp-2024-0044 (Crossref: published 2025-11-12). Relevant to finance + ML comparison with interpretability.
5. Ospina Arango, J. D. (2009). *Estimacion de un modelo de difusion con saltos con distribucion de error generalizada asimetrica usando algoritmos evolutivos* (master's thesis, Universidad Nacional de Colombia, Escuela de Estadistica; director N. D. Giraldo). https://repositorio.unal.edu.co/handle/unal/2424 (repository metadata). Relevant for jump-diffusion models and evolutionary estimation.

Theses usable as methodological precedents (cite only if our text actually follows their protocol; handles in section 1):
- Cuartas Rendon, S. (2026). Comparacion de modelos estocasticos y de aprendizaje de maquina ... (unal/90091): protocol for comparing model families with out-of-sample validation, bias tables, computing time and explainability.
- Castrillon Mora, J. M. (2026). (unal/90990): hypothesis stated and then qualified by results; intervention analysis for structural breaks.
- Zabala Gamez, L. F. (2023). (unal/84387) and Duque Miranda, J. E. (2021). (unal/81179): the two verified Ospina + Branch co-directed Sistemas theses; evidence of the advisors' minimum length (41-42 pp).
- Hernandez Zuluaga, J. F. (2025). (unal/89313), doctoral thesis co-directed by Ospina Arango: example of explicit research question, hypothesis, objectives and H1-H3 in a finance setting.
- Mosquera Gonzalez, D. (2022). (unal/81631), directed by Branch Bedoya: best one-to-one objective-chapter mapping.

Branch Bedoya's own work found in Crossref (low relevance; listed only for completeness): Branch B., J. W. (2014). The Facultad de Minas 1970-2012. *DYNA*, 81(184), 9. https://doi.org/10.15446/dyna.v81n184.43082 (editorial; not a methodological source). Other "John Branch" records in Crossref belong to different people (marketing, history) and must not be attributed to him.

## 4. Gaps / things to confirm with the advisor

1. That "profesor John" is John Willian Branch Bedoya (only inferred from co-direction records).
2. Whether the Facultad de Minas applies a specific margin/font rule to final theses (none found; the 3.5 cm / Arial 12 rule is unverified and probably for admission proposals).
3. Whether the advisor wants the six-paragraph introduction as six literal paragraphs or as six content moves (no reviewed thesis follows that exact outline; closest are #2 and #12).
4. Whether chapter 3 "Justificacion" should precede the hypothesis as requested even though the reviewed theses place Justificacion before Objetivos and the state of the art after the objectives (order is a minor difference; the advisor's order governs).
