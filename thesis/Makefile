TEX=pdflatex
MAIN=main.tex
BIB=bibtex

.PHONY: pdf pdf-en pdf-es pdf-en-blind pdf-es-blind pdf-blind language-check question-check layout-check clean

pdf: language-check question-check pdf-en pdf-es
	$(MAKE) layout-check

ifeq ($(BLIND),1)
pdf: pdf-blind
endif

layout-check:
	python3 ../scripts/check-thesis-layout.py

language-check:
	node ../scripts/check-language-pair.mjs

question-check:
	node ../scripts/check-thesis-questions.mjs

pdf-en: question-check
	$(TEX) -interaction=nonstopmode -halt-on-error $(MAIN)
	$(BIB) main
	$(TEX) -interaction=nonstopmode -halt-on-error $(MAIN)
	$(TEX) -interaction=nonstopmode -halt-on-error $(MAIN)

pdf-es: question-check
	cd es && $(TEX) -interaction=nonstopmode -halt-on-error main.tex
	cd es && $(BIB) main
	cd es && $(TEX) -interaction=nonstopmode -halt-on-error main.tex
	cd es && $(TEX) -interaction=nonstopmode -halt-on-error main.tex

pdf-en-blind: question-check
	node ../scripts/prepare-thesis-blind.mjs en
	cd build/en-blind/en && $(TEX) -jobname=main-blind -interaction=nonstopmode -halt-on-error '\def\blindreviewmode{1}\input{main.tex}'
	cd build/en-blind/en && $(BIB) main-blind
	cd build/en-blind/en && $(TEX) -jobname=main-blind -interaction=nonstopmode -halt-on-error '\def\blindreviewmode{1}\input{main.tex}'
	cd build/en-blind/en && $(TEX) -jobname=main-blind -interaction=nonstopmode -halt-on-error '\def\blindreviewmode{1}\input{main.tex}'
	cp build/en-blind/en/main-blind.pdf build/manuscript-en-double-blind.pdf
	pdftotext -layout build/manuscript-en-double-blind.pdf build/en-blind/manuscript.txt
	pdfinfo build/manuscript-en-double-blind.pdf > build/en-blind/pdfinfo.txt
	node ../scripts/check-thesis-blind.mjs build/en-blind/manuscript.txt build/en-blind/pdfinfo.txt

pdf-es-blind: question-check
	node ../scripts/prepare-thesis-blind.mjs es
	cd build/es-blind/es && $(TEX) -jobname=main-blind -interaction=nonstopmode -halt-on-error '\def\blindreviewmode{1}\input{main.tex}'
	cd build/es-blind/es && $(BIB) main-blind
	cd build/es-blind/es && $(TEX) -jobname=main-blind -interaction=nonstopmode -halt-on-error '\def\blindreviewmode{1}\input{main.tex}'
	cd build/es-blind/es && $(TEX) -jobname=main-blind -interaction=nonstopmode -halt-on-error '\def\blindreviewmode{1}\input{main.tex}'
	cp build/es-blind/es/main-blind.pdf build/manuscrito-es-doble-ciego.pdf
	pdftotext -layout build/manuscrito-es-doble-ciego.pdf build/es-blind/manuscrito.txt
	pdfinfo build/manuscrito-es-doble-ciego.pdf > build/es-blind/pdfinfo.txt
	node ../scripts/check-thesis-blind.mjs build/es-blind/manuscrito.txt build/es-blind/pdfinfo.txt

pdf-blind: pdf-en-blind pdf-es-blind
	python3 ../scripts/check-thesis-layout.py --en-pdf build/en-blind/en/main-blind.pdf --es-pdf build/es-blind/es/main-blind.pdf

clean:
	rm -f *.aux *.log *.out *.toc *.fls *.fdb_latexmk *.synctex.gz *.pdf
	rm -f es/*.aux es/*.log es/*.out es/*.toc es/*.fls es/*.fdb_latexmk es/*.synctex.gz es/*.pdf
	rm -f es/*.bbl es/*.blg
