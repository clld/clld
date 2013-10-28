# -*- encoding: latin1 -*-

from PIL import Image

from pyx import *

text.set(mode="latex", texdebug='debug.tex')
text.preamble(r"""%
\usepackage[latin1]{inputenc}
\usepackage{type1cm,pifont}
\renewcommand\labelitemi{\ding{51}}
\renewcommand{\familydefault}{\sfdefault}
\newcommand\head[1]{{\fontsize{70}{75}\selectfont\bfseries#1\vspace{5mm}\par}}
\newcommand\subhead[1]{{\fontsize{41}{44}\selectfont\bfseries#1\par}}
\renewcommand\section[1]{{\fontsize{34}{37}\selectfont\bfseries#1\vspace{5mm}\par}}
\renewcommand\subsection[1]{{\fontsize{32}{33}\vspace{4mm}\selectfont\bfseries#1\vspace{0mm}\par}}
\renewcommand\normalsize{\fontsize{30}{32}\selectfont}\normalsize
\leftmargini2em\labelwidth1em\labelsep0.5em\parindent0pt\parskip1ex
""")

paperformat = document.paperformat.A0
margin = 1.0
background = 2.5
padding = 1.0

leftpos = rightpos = paperformat.height - margin - background


def box(t, col, **images):
    global leftpos
    global rightpos
    width = paperformat.width - 2*margin - 2*background
    if col:
        width = 0.5*(width - background)
    t = text.text(0, 0, t, [text.parbox(width-2*padding)], texmessages=[text.texmessage.load])
    c = canvas.canvas()


    xpos = margin + background
    if col == 2:
        xpos += width + background
    if not col:
        ypos = min(leftpos, rightpos)
    elif col == 1:
        ypos = leftpos
    else:
        assert col == 2
        ypos = rightpos
    ypos -= t.height + t.depth + 2*padding

    c.draw(path.rect(xpos, ypos, width, t.height + t.depth + 2*padding), [deco.filled([color.gray.white])])

    for marker, filespec in images.items():
        filename, height, xoffset = filespec
        if height:
            x, y = t.marker(marker)
            c.insert(bitmap.bitmap(x+xpos+padding+xoffset, y+ypos+t.depth+padding, Image.open(filename), height=height))
        else:
            c.insert(bitmap.bitmap(xpos, ypos, Image.open(filename), width=width, height=t.height+t.depth+2*padding))

    c.draw(path.rect(xpos, ypos, width, t.height + t.depth + 2*padding), [deco.stroked])

    c.insert(t, [trafo.translate(xpos+padding, ypos+t.depth+padding)])
    if col < 2:
        leftpos = ypos - background
    if col != 1:
        rightpos = ypos - background

    return c

c = canvas.canvas()

c.draw(path.rect(margin, margin, paperformat.width-2*margin, paperformat.height-2*margin),
       [deco.stroked(), deco.filled([color.rgb(1.0, 0.98, 0.9)])])

#
# header
#
c.insert(box(r"""
\begin{center}
\head{CLLD -- Cross-Linguistic Linked Data}
\subhead{Robert Forkel}
\subhead{Department of Linguistics, Max Planck Institute for Evolutionary Anthropology}
\vspace{-5.55mm}
\end{center}
\PyXMarker{header}
""", 0, header=('header2.jpg', 0, 0)))

#
#
#
c.insert(box(r"""
\section{Goal}
\bf{Help collecting the world's language diversity heritage by providing interoperable data publication structures}
""", 1))

#
#
#
c.insert(box(r"""
\section{Linguistic databases on the web}
\subsection{Observations}
\begin{itemize}
\item Almost all quantitative papers at ALT 10 used WALS data.
\item Many typologists at ALT 10 have their own typological database.
\end{itemize}
\subsection{CLLD -- The strategy}
Since reuse tends to be the determining factor that keeps resources from vanishing,
we want to bridge the gap between data collection and data reuse by
\begin{itemize}
\item publishing databases thereby incentivizing researchers through recognition;
\item using technology that maximizes exposure of our data in the emerging web of data.
\end{itemize}
\subsection{CLLD -- The implementation}
This twofold strategy is implemented by three service components:
\begin{itemize}
\item infrastructural: Glottolog - a comprehensive language catalog and bibliography,
\item structural: Dictionaria -- a dictionary journal and CrossGram Journal -- a journal publishing typological databases,
\item technological: \texttt{clld} - a software platform for implementing linguistic database applications, which will be used
to serve standalone database publications like IDS, WOLD, ASJP, WALS, APiCS, eWAVE, ValPal as well as the journals.
\end{itemize}
To maximize resuability
\begin{itemize}
\item we provide the data under Open Data Licenses,
\item and the platform as Open Source software under a free license.
\end{itemize}
""", 1))


#
# TODO: The data model
#
c.insert(box(r"""
\section{The data model}
This implementation plan is realistic, because the underlying data model for the target databases is
both reasonably simple and abstract enough to cover many use cases.

The data model comprises the following entities: Dataset, Contribution, Contributor, Language, Parameter, Value, UnitParameter, Unit, Sentence, Source.
""", 1))

c.insert(box(r"""
\subsection{Value -- an APiCS datapoint}
\vspace{12.5cm}
\PyXMarker{valueset}
""", 1, valueset=('valueset.png', 12.5, 0)))

c.insert(box(r"""
\subsection{Unit -- a Dictionaria word}
\vspace{13.5cm}
\PyXMarker{unit}
""", 1, unit=('unit.png', 13.5, 0)))


#
#
#
c.insert(box(r"""
\section{Linked Data - disseminating data in standard formats}
\begin{itemize}
\item Defines a unified data access protocol for the web.
\item Well-suited for distributed data providers
\begin{itemize}
\item identifiers are URLs which are globally unique,
\item RDF and OWL provide the vocabulary to merge resources.
\end{itemize}
\item Provides an easy to implement lowest level of service in a graceful degradation scenario
\end{itemize}
""", 2))

c.insert(box(r"""
\subsection{Use off-the-shelf tools to explore a dataset}
Linked Data Explorer accessing Glottolog Linked Data serialized as RDF/XML.

\vspace{14cm}
\PyXMarker{rdf}
""", 2, rdf=('rdf.png', 14, 0.5)))

c.insert(box(r"""
\subsection{Use off-the-shelf tools to transform a dataset}
The map-making software Tilemill accessing APiCS data in GeoJSON format.

\vspace{14cm}
\PyXMarker{geojson}
""", 2, geojson=('geojson.png', 14, 0.5)))

c.insert(box(r"""
\subsection{Comparing WALS and APiCS data pulled in as GeoJSON}
\vspace{14cm}
\PyXMarker{wa}
""", 2, wa=('wals-apics.png', 14, 0)))




c.insert(box(r"""
\section{Mission accomplished? -- A week's Visitors to Glottolog}
\vspace{9.5cm}
\PyXMarker{gl}
""", 2, gl=('glottolog-users.png', 9.5, 2)))


c.text(paperformat.width-margin-background, 3, r"\fontsize{16}{18}\selectfont Printed at Universit\"atsrechenzentrum Leipzig", [text.halign.right])

c.writeEPSfile("poster_a4", paperformat=document.paperformat.A4, fittosize=1)
c.writePDFfile("poster_a4", paperformat=document.paperformat.A4, fittosize=1)
c.writeEPSfile("poster_a0", paperformat=document.paperformat.A0)
c.writePDFfile("poster_a0", paperformat=document.paperformat.A0)

# print unit.tocm(leftpos), unit.tocm(rightpos)
