# Reference audit, 2026-11-23

Scope: verify every reference of the thesis (originals [1]-[20]) against an independent source, then propose better or
additional references per topic. Nothing outside `thesis/literature-audit/` was edited (`thesis/references.bib` and the
`.tex` files are untouched). All web content was treated as data. Registry calls used (all read-only):

- Crossref: `https://api.crossref.org/works/<doi>?mailto=...` (title, authors, container, vol/issue/pages, dates).
- arXiv: `https://export.arxiv.org/api/query?id_list=<id>` (retries needed; abs-page `citation_*` meta tags as fallback).
- OpenLibrary: `https://openlibrary.org/isbn/<isbn>.json` and `/search.json` (books without DOI). OpenAlex for cross-checks.
- Publisher pages: jasss.org, revistas.unal.edu.co (OJS meta tags), redalyc PDF, stlouisfed.org, uniswap PDFs (downloaded, first page read).

Status key: VERIFIED = every field matches the source; VERIFIED-WITH-CORRECTIONS = exists, but the thesis/original
metadata needed a fix; UNVERIFIED DETAIL = the work exists but one stated field could not be machine-confirmed.
No original reference was NOT FOUND or WRONG; the weakest is [20] on relevance, not on existence.

## 1. The 20 original references

| # | Key (references_verified.bib) | Status | Source used | Discrepancy / correction applied |
|---|---|---|---|---|
| 1 | holland1995hidden | VERIFIED (book, no DOI) | OpenLibrary ISBN 0201407930 (title, 1995, Addison-Wesley, by "John H. Holland") | Added ISBN. Conceptual framing only; cannot support any claim about markets. |
| 2 | tesfatsion2003agent | VERIFIED | Crossref 10.1016/S0020-0255(02)00280-3 | Information Sciences 149(4):262-268, Feb 2003. |
| 3 | palmer1994artificial | VERIFIED | Crossref 10.1016/0167-2789(94)90287-9 | Physica D 75(1-3):264-274. Crossref prints "Brian Arthur, W."; normalised to "Arthur, W. Brian". |
| 4 | brock1998heterogeneous | VERIFIED | Crossref 10.1016/S0165-1889(98)00011-6 | JEDC 22(8-9):1235-1274. |
| 5 | lux1999scaling | VERIFIED | Crossref 10.1038/17290 | Nature 397(6719):498-500. |
| 6 | cont2001empirical | VERIFIED | Crossref 10.1080/713665670 | Quant. Finance 1(2):223-236. |
| 7 | cocco2017artificial | VERIFIED-WITH-CORRECTIONS | Crossref 10.1007/s11403-015-0168-2 | Online 2015-10-16, print vol. 12(2) July 2017, pp. 345-365. Year must be chosen consistently (2017 used here). |
| 8 | schar2021defi | VERIFIED-WITH-CORRECTIONS; pages UNVERIFIED DETAIL | Crossref 10.20955/r.103.153-74; OpenAlex; stlouisfed.org landing page | Surname is Sch&auml;r (umlaut), not "Schaer". Journal is *Federal Reserve Bank of St. Louis Review* 103(2), 2021. Pages 153-174 are inferred from the DOI suffix and the older bibitem; neither Crossref nor OpenAlex returns pages. |
| 9 | xu2023sok | VERIFIED-WITH-CORRECTIONS | Crossref 10.1145/3570639 | ACM Comput. Surv. 55(11), pp. 1-50 (article 238 not returned by Crossref); online 2023-02-09, print 2023-11-30. |
| 10 | adams2020uniswap | VERIFIED (whitepaper, not peer reviewed) | PDF downloaded: `blog.uniswap.org/whitepaper.pdf` (200) and `uniswap.org/whitepaper.pdf` (301 to `app.uniswap.org/whitepaper.pdf`); `cmp` shows identical files; first page lists 3 authors, March 2020 | Full first names added. Keep `@misc`. |
| 11 | angeris2020cfmm | VERIFIED-WITH-CORRECTIONS | Crossref 10.1145/3419614.3423251 | Full first names; booktitle is AFT '20 (2nd ACM Conf. on Advances in Financial Technologies), pp. 80-91. Crossref splits the title ("Improved Price Oracles" + subtitle "Constant Function Market Makers"); the thesis title is the combined form, which is correct. |
| 12 | angeris2020uniswap | VERIFIED-WITH-CORRECTIONS; vol/issue UNVERIFIED DETAIL | Crossref 10.21428/58320208.c9738e64; arXiv 1911.03380 (first posted 2019-11-08); PubPub page 403 to bots | Crossref issues it 2020-11-25 (not 2021). Cryptoeconomic Systems vol/issue could not be machine-confirmed, so none is given. |
| 13 | campbell2025optimal | VERIFIED (preprint) | arXiv 2508.08152 (2025-08-11); Crossref SSRN DOI 10.2139/ssrn.5387290 | No journal version found. Cite as preprint; do not present as peer reviewed. |
| 14 | palit2022shuffled | VERIFIED | Crossref 10.3389/fbloc.2022.745101; OpenAlex; Frontiers meta tags | Frontiers in Blockchain 5, art. 745101. Single author (a suspicion of co-authors was checked and rejected). Relevant: zero-intelligence agent replay on Uniswap. |
| 15 | dean2022arbitrage | VERIFIED (SSRN preprint), author-name conflict | Crossref 10.2139/ssrn.4247283 (Dean, McCabe, Psurek, Bhatt); OpenAlex lists first author "Sarah Sylvester"; SSRN page 403 | No peer-reviewed version found. Crossref (authoritative) used; confirm on the SSRN page before citing. Demote: unreviewed. |
| 16 | bergault2025exit | VERIFIED (preprint) | arXiv 2509.06510 (v2 2025-10-20); Crossref SSRN DOI 10.2139/ssrn.5456614 | No journal reference found. Directly relevant to LP exit, but cite as preprint. |
| 17 | roubal2010linearization | VERIFIED-WITH-CORRECTIONS | Crossref 10.1109/TE.2009.2026427 | Added pages 413-418 (IEEE Trans. Educ. 53(3), Aug 2010). Full first names added. |
| 18 | fagiolo2007critical | VERIFIED | Crossref 10.1007/s10614-007-9104-4 | Comput. Econ. 30(3):195-226. Full title includes "Methodologies, Procedures, and Open Problems". |
| 19 | grimm2020odd | VERIFIED-WITH-CORRECTIONS | Crossref 10.18564/jasss.4259 | The thesis bib had "Grimm, V. and others". Replaced by the full 19-author list. JASSS 23(2), art. 7. |
| 20 | medina2009multimodelos | VERIFIED (exists); WEAK RELEVANCE; recommend DROP | UNAL OJS page (`revistas.unal.edu.co/index.php/dyna/article/view/13666`, citation_* meta tags); redalyc PDF `49612068014.pdf`; not in Crossref (no DOI) | Metadata matches: DYNA 76(160):237-246, 2009. The paper is a fault-diagnosis method (multi-model LTI + decoupled Kalman filters); the thesis `.tex` itself says it does not use the fault-diagnosis component. Using it only to "document normal/shock/recovery scenarios" is a stretch. Replace by Takagi and Sugeno 1985 (`takagi1985fuzzy`) if a source for local linear models at operating points is needed, or cite Roubal et al. alone. |
| - | calderon2026repository | VERIFIED | `https://github.com/edwardcalderon/Master-s-thesis` returns 200; matches `git remote origin` | Software citation; add a commit hash or release tag so it is citable. |

Metadata slips found in the thesis `references.bib` (6 entries): `grimm2020odd` author list ("and others"), `roubal2010linearization`
missing pages, `angeris2020cfmm` initials only and booktitle missing "2nd ... (AFT '20)" and pages, `adams2020uniswap` initials only.

## 2. Corrections in one line each

1. Sch&auml;r (umlaut); pages 153-174 inferred, not confirmed.
2. Angeris et al. "An Analysis of Uniswap Markets": registry year 2020, not 2021; volume/issue unconfirmed.
3. Roubal et al.: add pages 413-418.
4. Grimm et al. 2020: write out all 19 authors.
5. Palit 2022: single author (confirmed).
6. Dean et al.: OpenAlex author-name conflict ("Sarah Sylvester"); Crossref says Dean; SSRN not machine-readable.
7. Cocco et al.: online 2015, print 2017.
8. Fagiolo et al.: complete subtitle.
9. Medina et al. 2009: exists, weak relevance, drop.
10. Uniswap v2 whitepaper: the `blog.` and `app.` PDFs are byte-identical; either URL is valid.
11. [13] Campbell et al., [16] Bergault et al., [15] Dean et al. are preprints/working papers only.

## 3. Additional / alternative references (candidates), ranked

Tier meaning (also stored as `audit_tier` in the .bib): **core** = one of the 20 originals kept; **recommended** = best additional
source for its topic; **reserve** = real and verified, but only cite if the specific claim is made; **drop** = do not cite.
Evidence for every row = the DOI/arXiv id shown, checked by `verify_references.py` (section 6). "Supports" states the claim the
source can honestly carry.

### (a) CPMM / AMM theory, arbitrage, LVR, fees

| Rank | Key | Tier | Why relevant / what it can honestly support |
|---|---|---|---|
| 1 | milionis2022lvr (arXiv 2208.06046) | recommended | Loss-versus-rebalancing: LP loss to arbitrage under a CPMM with an external price. Supports: arbitrage-driven LP loss, decomposition of LP returns. Preprint only (a 4-page version is milionis2022quantifying). Note: "LVR" is loss-versus-*rebalancing*. |
| 2 | milionis2025fees (10.1007/978-3-031-78676-1_9; arXiv 2305.14604) | recommended | Arbitrage profit with fees: no-arbitrage band, fee threshold. Supports the thesis's cost/capacity arbitrage argument. Peer reviewed (FC 2024). |
| 3 | lehar2025uniswap (10.1111/jofi.13405) | recommended | Empirical Uniswap v2/v3 model with fees and liquidity provision; J. Finance. Supports claims on fees, depth, LP behaviour. |
| 4 | capponi2025liquidity (10.1093/rfs/hhaf046) | recommended | LP economics and liquidity provision on DEXs, RFS. Supports LP participation and entry/exit. |
| 5 | bartoletti2022theory (10.46298/lmcs-18(4:12)2022) | recommended | Formal theory of AMMs (swap rates, arbitrage, solvability); peer reviewed. Supports mechanics of the constant-product rule. |
| 6 | angeris2023replicating, park2023flaws, cartea2024predictable, hasbrouck2026fees, heimbach2022risks | reserve | Peer-reviewed alternatives for convexity/replication, critique of CPMMs, predictable loss, fee effects on volume, Uniswap v3 LP returns. Cite only for the matching claim. |
| 7 | adams2021uniswapv3 | reserve | Whitepaper for concentrated liquidity; only if v3 is discussed. Not peer reviewed. |
| 8 | zhou2021hft, daian2020flash | reserve | On-chain ordering/MEV/frontrunning; supports the statement that execution frictions exist, not a price-tracking claim. |
| 9 | shleifer1997limits, hautsch2024building | recommended | Theory and crypto evidence of limits to arbitrage (capital, risk). Supports the "arbitrage is capacity- and cost-limited" claim. |
| 10 | diamond1983bank | recommended (analogy only) | Run dynamics; may be used only as an analogy for LP withdrawal feedback, not as evidence about AMMs. |

### (b) CEX-DEX price discovery

| Rank | Key | Tier | Why relevant / what it can honestly support |
|---|---|---|---|
| 1 | makarov2020trading (10.1016/j.jfineco.2019.07.001) | recommended | Cross-exchange crypto price deviations and arbitrage capital limits (JFE). Supports persistence of cross-venue gaps. |
| 2 | capponi2026price (10.1093/rfs/hhag002) | recommended | Price discovery on DEXs (RFS, online first; volume/pages not yet assigned). Supports claims about DEX vs CEX information flow. |
| 3 | alexander2025price (10.1002/fut.22593) | recommended | Price discovery/efficiency in Uniswap pools (J. Futures Markets). |
| 4 | mestel2025price (10.2139/ssrn.5777295) | reserve | SSRN working paper; use as a "recent working paper" at most. |

### (c) ABM / heterogeneous agents in computational finance

| Rank | Key | Tier | Why relevant / what it can honestly support |
|---|---|---|---|
| 1 | lebaron2006agent (10.1016/s1574-0021(05)02024-1) | recommended | Standard survey of agent-based computational finance (Handbook, vol. 2). |
| 2 | hommes2006heterogeneous (10.1016/s1574-0021(05)02023-x) | recommended | Standard survey of heterogeneous-agent models; pairs with Brock-Hommes [4]. |
| 3 | axtell2025agent (10.1257/jel.20221319) | recommended | Recent J. Econ. Literature review of ABM in economics and finance. |
| 4 | gode1993allocative, farmer2005predictive | recommended | Zero-intelligence traders (JPE; PNAS): justify simple/random agent roles such as the noise trader. |
| 5 | cocco2019agent (IEEE Access) | recommended | Agent-based artificial market for Bitcoin trading; closest crypto-ABM sibling to [7]. |
| 6 | cocco2016mining, lux2000volatility, lebaron2001builder, farmer2009economy, tesfatsion2006handbook, hommes2013behavioral | reserve | Valid supporting sources for specific statements (mining economics; volatility clustering; builder's guide; ABM advocacy; ACE handbook chapter; behavioural-rationality monograph). |

### (d) ABM on AMMs / DeFi (including LP exit)

| Rank | Key | Tier | Why relevant / what it can honestly support |
|---|---|---|---|
| 1 | palit2022shuffled [14] | core | Zero-intelligence agent replay on Uniswap events. |
| 2 | sabatevidales2023variable (10.1007/978-3-031-32415-4_15) | recommended | ABM of variable fees in constant-product markets; peer-reviewed workshop paper; the closest published ABM-on-CPMM. |
| 3 | cohen2023inefficiency (arXiv 2302.04345) | recommended | Hedging view + agent-based simulation of CFM inefficiency; preprint. |
| 4 | bergault2025exit [16], campbell2025optimal [13] | core | LP exit time and optimal fees; the only found formal treatments of LP exit. Both are preprints. |
| 5 | ruan2025agent, struchkov2021agent, dinosse2026mitigating | reserve | DeFi/DAO ABMs of lower relevance or preprint-only. Ruan et al.: Crossref author order differs from the SSRN version. |

No agent-based model of Curve/stableswap or an "LP bank run" ABM was found; the thesis should say that its LP-withdrawal
mechanism is an own modelling choice supported by [16], Lehar-Parlour and (as analogy) Diamond-Dybvig, not by an ABM precedent.
Lehar and Parlour's SSRN "Systemic Fragility in Decentralized Markets" (10.2139/ssrn.4164833) exists in Crossref but has no
abstract/peer-reviewed version; not included.

### (e) Reduced-order / surrogate / equation-free / discrete-time stability

| Rank | Key | Tier | Why relevant / what it can honestly support |
|---|---|---|---|
| 1 | gear2003equationfree (10.4310/cms.2003.v1.n4.a5) | recommended | Equation-free coarse-grained analysis of microscopic simulators: the methodological precedent for fitting a reduced map to ABM output. Crossref typos corrected. |
| 2 | lamperti2018surrogates (10.1016/j.jedc.2018.03.011) | recommended | ML surrogates for ABM calibration; precedent for surrogate-of-ABM claims. |
| 3 | jury1962simplified (10.1109/jrproc.1962.288193), schur1917potenzreihen (10.1515/crll.1917.147.205) | recommended | Original sources of the Jury and Schur criteria. Schur 1917 is in German. |
| 4 | elaydi2005difference (ISBN 9780387230597), franklin1998digital (ISBN 9780201331530) | recommended / reserve | Textbook statements of Schur stability for difference equations / digital control. Verified by OpenLibrary only (no DOI). Franklin et al. not needed if Elaydi is cited. |
| 5 | takagi1985fuzzy (10.1109/TSMC.1985.6313399) | recommended | Replaces [20] for "blend of local linear models". |
| 6 | platt2020comparison, brunton2016sindy | reserve | ABM calibration comparison; SINDy for discovering reduced equations. |

Not included because they could not be verified: Ogata, *Discrete-Time Control Systems* (not found by OpenLibrary search); Jury and
Blanchard 1961 (guessed DOI 10.1109/JRPROC.1961.287622 has no record); Murray-Smith and Johansen (no ID check); Kevrekidis-Gear-Hummer.
The arXiv preprint physics/0209043 of the equation-free paper has a different title/author order; the journal version is cited.

### (f) ABM validation, experiment design, sensitivity, statistics

| Rank | Key | Tier | Why relevant / what it can honestly support |
|---|---|---|---|
| 1 | fagiolo2007critical [18], windrum2007empirical | core / recommended | ABM empirical validation. Windrum et al. has NO DOI: cite by URL https://www.jasss.org/10/2/8.html (a guessed DOI returned no record). |
| 2 | grimm2020odd [19] | core | ODD (2nd update). grimm2006standard and grimm2010odd are the earlier versions (reserve). |
| 3 | sargent2013verification (10.1057/jos.2012.20) | recommended | Verification and validation of simulation models. |
| 4 | thiele2014facilitating, lorscheid2012opening | recommended | Sensitivity analysis and design of experiments for ABMs. |
| 5 | saltelli2010variance | recommended | Variance-based sensitivity (total-effect estimator). sobol2001global, morris1991factorial are reserve. |
| 6 | efron1979bootstrap, holm1979simple | recommended | Bootstrap and Holm correction, both used by `experiments/cex_dex_mvp/confirm.py` (percentile bootstrap, sign-flip randomisation test, Holm). Holm: see unverifiable list. |
| 7 | railsback2019agent, kleijnen2015design, law2014simulation, hevner2004design | recommended / reserve | Textbook ABM practice, simulation DOE, general simulation text, design-science research. Law and Kleijnen edition numbers not machine-confirmed. |

### (g) Methodology texts and advisor publications

| Key | Tier | Note |
|---|---|---|
| hernandez2014metodologia | recommended | 6th ed., McGraw-Hill 2014, ISBN 9781456223960 (checksum valid; OpenLibrary title "6. edición"). Author list from OpenLibrary search records. The 2018 edition with Mendoza was NOT verified, so it is not included. |
| creswell2018research | recommended | 5th ed. 2018, ISBN 9781506386706 (valid). OpenLibrary shows 2014 for this ISBN, which conflicts with the 5th-ed. date; the 2018 date comes from a Crossref book review. Check the title page. |
| ardia2011jump, hernandez2010multidynamics, berggrun2020profitability | reserve | Publications by the advisor Juan David Ospina Arango, all real and verified. None concerns AMMs or ABMs, so they should not be cited for the thesis argument; cite at most for the optimisation/calibration (differential evolution) or financial-analytics background. Said plainly: no advisor publication on AMMs/ABMs was found. |

### Drop / do-not-use list

| Item | Reason |
|---|---|
| medina2009multimodelos [20] | Exists, but is a fault-diagnosis paper; thesis explicitly does not use that part; better alternative above. |
| DOIs 10.18564/jasss.1621, 10.1016/bs.hescom.2018.02.007, 10.1146/annurev.financial.050808.114537, 10.1007/0-387-27602-5, 10.1109/JRPROC.1961.287622, 10.1145/3560832.3563435 | Guessed identifiers; Crossref has no record. Never cite them. |
| Hernandez-Sampieri and Mendoza 2018, Ogata, Curve ABM | Could not be confirmed to exist as described. |
| ASUM-DM chapter (10.1007/978-3-319-95204-8_51) | Seen only in OpenAlex; not Crossref-verified. |

## 4. Entries that remain unverifiable or only partially verified

1. Holm 1979 (`holm1979simple`): OpenAlex gives title/author/vol 6/pp 65-70 and DOI 10.2307/4615733, but Crossref and doi.org do not resolve that DOI and JSTOR serves a bot challenge. No `doi` is given; the .bib omits the issue number. Mark UNVERIFIED DETAIL.
2. Schär 2021 pages 153-174: inferred from the DOI suffix.
3. Angeris et al. 2020 (Cryptoeconomic Systems): volume/issue not confirmed (PubPub 403).
4. Dean et al. 2022 [15]: author-name conflict between Crossref and OpenAlex; SSRN page not readable.
5. Books checked by ISBN only (Holland, Elaydi, Franklin et al., Law, Hernandez Sampieri et al., Creswell and Creswell): the title/publisher matched, but edition/author fields are partly from OpenLibrary search records, not from the book itself.
6. Medina et al. 2009: no DOI; verified on the publisher page only.
7. Kleijnen 2015 and Law 2014: edition numbers not machine-confirmed.
8. Jury 1962: Crossref gives author as "Jury, E."; initial "I." follows the standard citation.

## 5. Counts

88 entries in `references_verified.bib`: 20 core (19 originals + repository), 36 recommended, 31 reserve, 1 drop (Medina 2009). Main-text set = 56; with `medina2009multimodelos` removed the thesis list never needs more than 87 entries. 76 entries carry a DOI/arXiv id and were machine-checked; 12 were checked by hand (books/URLs/whitepapers).

## 6. Output of `python3 -I verify_references.py` (run 2026-11-23)

```
Checked references_verified.bib (88 entries): 76 with DOI/arXiv, 12 skipped

key                         id                                      source     title  bib~registry year    status
tesfatsion2003agent         doi:10.1016/S0020-0255(02)00280-3       crossref   1.00   2003~2003            PASS
palmer1994artificial        doi:10.1016/0167-2789(94)90287-9        crossref   1.00   1994~1994/2002       PASS
brock1998heterogeneous      doi:10.1016/S0165-1889(98)00011-6       crossref   1.00   1998~1998/2002       PASS
lux1999scaling              doi:10.1038/17290                       crossref   1.00   1999~1999/2002       PASS
cont2001empirical           doi:10.1080/713665670                   crossref   1.00   2001~2001/2007       PASS
cocco2017artificial         doi:10.1007/s11403-015-0168-2           crossref   1.00   2017~2015/2017       PASS
schar2021defi               doi:10.20955/r.103.153-74               crossref   1.00   2021~2021            PASS
xu2023sok                   doi:10.1145/3570639                     crossref   1.00   2023~2022/2023       PASS
angeris2020cfmm             doi:10.1145/3419614.3423251             crossref   1.00   2020~2020            PASS
angeris2020uniswap          doi:10.21428/58320208.c9738e64          crossref   1.00   2020~2020/2021       PASS
angeris2020uniswap          arXiv:1911.03380                        arxiv-api  1.00   2020~2019            PASS
campbell2025optimal         doi:10.2139/ssrn.5387290                crossref   1.00   2025~2025            PASS
campbell2025optimal         arXiv:2508.08152                        arxiv-api  1.00   2025~2025            PASS
palit2022shuffled           doi:10.3389/fbloc.2022.745101           crossref   1.00   2022~2022            PASS
dean2022arbitrage           doi:10.2139/ssrn.4247283                crossref   1.00   2022~2022            PASS
bergault2025exit            doi:10.2139/ssrn.5456614                crossref   1.00   2025~2025            PASS
bergault2025exit            arXiv:2509.06510                        arxiv-api  1.00   2025~2025            PASS
roubal2010linearization     doi:10.1109/TE.2009.2026427             crossref   1.00   2010~2009/2010       PASS
fagiolo2007critical         doi:10.1007/s10614-007-9104-4           crossref   1.00   2007~2007            PASS
grimm2020odd                doi:10.18564/jasss.4259                 crossref   1.00   2020~2020            PASS
milionis2022lvr             arXiv:2208.06046                        arxiv-api  1.00   2022~2022            PASS
milionis2022quantifying     doi:10.1145/3560832.3563441             crossref   1.00   2022~2022            PASS
milionis2025fees            doi:10.1007/978-3-031-78676-1_9         crossref   1.00   2025~2025            PASS
milionis2025fees            arXiv:2305.14604                        arxiv-api  1.00   2025~2023            PASS
lehar2025uniswap            doi:10.1111/jofi.13405                  crossref   1.00   2025~2024/2025       PASS
capponi2025liquidity        doi:10.1093/rfs/hhaf046                 crossref   1.00   2025~2025            PASS
hasbrouck2026fees           doi:10.1287/mnsc.2023.00726             crossref   1.00   2026~2026            PASS
bartoletti2022theory        doi:10.46298/lmcs-18(4:12)2022          crossref   1.00   2022~2022            PASS
angeris2023replicating      doi:10.1007/s42521-023-00082-0          crossref   1.00   2023~2023            PASS
park2023flaws               doi:10.1287/mnsc.2021.02802             crossref   1.00   2023~2023            PASS
cartea2024predictable       doi:10.1137/23m1602103                  crossref   1.00   2024~2024            PASS
heimbach2022risks           doi:10.1145/3558535.3559772             crossref   1.00   2022~2022/2023       PASS
zhou2021hft                 doi:10.1109/sp40001.2021.00027          crossref   1.00   2021~2021            PASS
zhou2021hft                 arXiv:2009.14021                        arxiv-api  1.00   2021~2020            PASS
daian2020flash              doi:10.1109/sp40000.2020.00040          crossref   1.00   2020~2020            PASS
shleifer1997limits          doi:10.1111/j.1540-6261.1997.tb03807.x  crossref   1.00   1997~1997/2012       PASS
hautsch2024building         doi:10.1093/rof/rfae004                 crossref   1.00   2024~2024            PASS
diamond1983bank             doi:10.1086/261155                      crossref   1.00   1983~1983/2002       PASS
makarov2020trading          doi:10.1016/j.jfineco.2019.07.001       crossref   1.00   2020~2019/2020       PASS
capponi2026price            doi:10.1093/rfs/hhag002                 crossref   1.00   2026~2026            PASS
alexander2025price          doi:10.1002/fut.22593                   crossref   1.00   2025~2025            PASS
mestel2025price             doi:10.2139/ssrn.5777295                crossref   1.00   2025~2025            PASS
lebaron2006agent            doi:10.1016/s1574-0021(05)02024-1       crossref   1.00   2006~2006            PASS
hommes2006heterogeneous     doi:10.1016/s1574-0021(05)02023-x       crossref   1.00   2006~2006            PASS
tesfatsion2006handbook      doi:10.1016/s1574-0021(05)02016-2       crossref   1.00   2006~2006            PASS
farmer2009economy           doi:10.1038/460685a                     crossref   1.00   2009~2009            PASS
gode1993allocative          doi:10.1086/261868                      crossref   1.00   1993~1993/2002       PASS
farmer2005predictive        doi:10.1073/pnas.0409157102             crossref   1.00   2005~2005            PASS
lebaron2001builder          doi:10.1088/1469-7688/1/2/307           crossref   1.00   2001~2001/2002       PASS
lux2000volatility           doi:10.1142/s0219024900000826           crossref   1.00   2000~2000/2002/2011  PASS
hommes2013behavioral        doi:10.1017/cbo9781139094276            crossref   1.00   2013~2013            PASS
axtell2025agent             doi:10.1257/jel.20221319                crossref   1.00   2025~2025            PASS
cocco2019agent              doi:10.1109/access.2019.2907880         crossref   1.00   2019~2019            PASS
cocco2016mining             doi:10.1371/journal.pone.0164603        crossref   1.00   2016~2016            PASS
sabatevidales2023variable   doi:10.1007/978-3-031-32415-4_15        crossref   1.00   2023~2023            PASS
cohen2023inefficiency       doi:10.2139/ssrn.4352120                crossref   1.00   2023~2023            PASS
cohen2023inefficiency       arXiv:2302.04345                        arxiv-api  1.00   2023~2023            PASS
struchkov2021agent          doi:10.23919/fruct52173.2021.9435601    crossref   1.00   2021~2021            PASS
ruan2025agent               doi:10.21314/jcr.2025.009               crossref   1.00   2025~2025            PASS
dinosse2026mitigating       arXiv:2606.23070                        arxiv-api  1.00   2026~2026            PASS
gear2003equationfree        doi:10.4310/cms.2003.v1.n4.a5           crossref   0.99   2003~2003/2013       PASS
lamperti2018surrogates      doi:10.1016/j.jedc.2018.03.011          crossref   1.00   2018~2018            PASS
platt2020comparison         doi:10.1016/j.jedc.2020.103859          crossref   1.00   2020~2020            PASS
brunton2016sindy            doi:10.1073/pnas.1517384113             crossref   1.00   2016~2016            PASS
jury1962simplified          doi:10.1109/jrproc.1962.288193          crossref   1.00   1962~1962/2007       PASS
schur1917potenzreihen       doi:10.1515/crll.1917.147.205           crossref   1.00   1917~1917/2009       PASS
takagi1985fuzzy             doi:10.1109/TSMC.1985.6313399           crossref   1.00   1985~1985/2012       PASS
sargent2013verification     doi:10.1057/jos.2012.20                 crossref   1.00   2013~2012/2013/2017  PASS
saltelli2010variance        doi:10.1016/j.cpc.2009.09.018           crossref   1.00   2010~2009/2010       PASS
sobol2001global             doi:10.1016/S0378-4754(00)00270-6       crossref   1.00   2001~2001/2002       PASS
morris1991factorial         doi:10.1080/00401706.1991.10484804      crossref   1.00   1991~1991/2012       PASS
thiele2014facilitating      doi:10.18564/jasss.2503                 crossref   1.00   2014~2014/2015       PASS
lorscheid2012opening        doi:10.1007/s10588-011-9097-3           crossref   1.00   2012~2011/2012       PASS
efron1979bootstrap          doi:10.1214/aos/1176344552              crossref   1.00   1979~1979/2007       PASS
railsback2019agent          doi:10.2307/jj.28274141                 crossref   0.92   2019~2019/2025       PASS
kleijnen2015design          doi:10.1007/978-3-319-18087-8           crossref   1.00   2015~2015            PASS
grimm2006standard           doi:10.1016/j.ecolmodel.2006.04.023     crossref   1.00   2006~2006            PASS
grimm2010odd                doi:10.1016/j.ecolmodel.2010.08.019     crossref   1.00   2010~2010            PASS
hevner2004design            doi:10.2307/25148625                    crossref   1.00   2004~2004/2017       PASS
ardia2011jump               doi:10.1002/wilm.10034                  crossref   1.00   2011~2011            PASS
hernandez2010multidynamics  doi:10.1016/j.mcm.2010.03.024           crossref   1.00   2010~2010            PASS
berggrun2020profitability   doi:10.1016/j.frl.2019.101387           crossref   1.00   2020~2019/2020       PASS

SKIPPED (no DOI / arXiv id; verified by hand, see REFERENCE_AUDIT.md): holland1995hidden, adams2020uniswap, medina2009multimodelos, calderon2026repository, adams2021uniswapv3, elaydi2005difference, franklin1998digital, holm1979simple, law2014simulation, windrum2007empirical, hernandez2014metodologia, creswell2018research

RESULT: 82 checks, 82 passed, 0 failed
```
