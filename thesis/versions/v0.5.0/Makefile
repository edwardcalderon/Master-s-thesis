TEX=pdflatex
MAIN=main.tex
BIB=bibtex

.PHONY: pdf pdf-en pdf-es clean

# The language-pair checker validates the live manuscript in ../../, not this snapshot,
# so it is not a prerequisite here.
pdf: pdf-en pdf-es

pdf-en:
	$(TEX) -interaction=nonstopmode -halt-on-error $(MAIN)
	$(BIB) main
	$(TEX) -interaction=nonstopmode -halt-on-error $(MAIN)
	$(TEX) -interaction=nonstopmode -halt-on-error $(MAIN)

pdf-es:
	cd es && $(TEX) -interaction=nonstopmode -halt-on-error main.tex
	cd es && $(BIB) main
	cd es && $(TEX) -interaction=nonstopmode -halt-on-error main.tex
	cd es && $(TEX) -interaction=nonstopmode -halt-on-error main.tex

clean:
	rm -f *.aux *.log *.out *.toc *.fls *.fdb_latexmk *.synctex.gz *.pdf
	rm -f es/*.aux es/*.log es/*.out es/*.toc es/*.fls es/*.fdb_latexmk es/*.synctex.gz es/*.pdf
	rm -f es/*.bbl es/*.blg
