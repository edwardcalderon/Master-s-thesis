TEX=pdflatex
MAIN=main.tex

.PHONY: pdf clean

pdf:
	$(TEX) -interaction=nonstopmode -halt-on-error $(MAIN)
	$(TEX) -interaction=nonstopmode -halt-on-error $(MAIN)

clean:
	rm -f *.aux *.log *.out *.toc *.fls *.fdb_latexmk *.synctex.gz
