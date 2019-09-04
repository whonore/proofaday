from pylatexenc.latex2text import (  # type: ignore
    LatexNodes2Text,
    MacroTextSpec,
    get_default_latex_context_db as l2t_ctx,
)
from pylatexenc.latex2text._defaultspecs import make_accented_char  # type: ignore
from pylatexenc.latexwalker import (  # type: ignore
    get_default_latex_context_db as lwalk_ctx,
)
from pylatexenc.macrospec import std_macro  # type: ignore

MACROS = [
    MacroTextSpec(name, simplify_repl=repl)
    for name, repl in (
        # MathJax
        ("above", "%s/%s"),
        ("aleph", "\N{ALEF SYMBOL}"),
        ("alpha", "\N{GREEK SMALL LETTER ALPHA}"),
        ("amalg", "\N{AMALGAMATION OR COPRODUCT}"),
        ("And", "\N{AMPERSAND}"),
        ("angle", "\N{ANGLE}"),
        ("approx", "\N{ALMOST EQUAL TO}"),
        ("approxeq", "\N{ALMOST EQUAL OR EQUAL TO}"),
        ("arccos", "arccos"),
        ("arcsin", "arcsin"),
        ("arctan", "arctan"),
        ("arg", "arg"),
        ("Arrowvert", "\N{DOUBLE VERTICAL LINE}"),
        ("arrowvert", "\N{VERTICAL LINE EXTENSION}"),
        ("ast", "\N{ASTERISK OPERATOR}"),
        ("asymp", "\N{EQUIVALENT TO}"),
        ("backepsilon", "\N{SMALL CONTAINS AS MEMBER}"),
        ("backprime", "\N{REVERSED PRIME}"),
        ("backsim", "\N{REVERSED TILDE}"),
        ("backsimeq", "\N{REVERSED TILDE EQUALS}"),
        ("backslash", "\N{SET MINUS}"),
        ("bar", "\N{MODIFIER LETTER MACRON}"),
        ("barwedge", "\N{NAND}"),
        ("because", "\N{BECAUSE}"),
        ("beta", "\N{GREEK SMALL LETTER BETA}"),
        ("beth", "\N{BET SYMBOL}"),
        ("between", "\N{BETWEEN}"),
        ("bigcap", "\N{N-ARY INTERSECTION}"),
        ("bigcirc", "\N{LARGE CIRCLE}"),
        ("bigcup", "\N{N-ARY UNION}"),
        ("bigodot", "\N{N-ARY CIRCLED DOT OPERATOR}"),
        ("bigoplus", "\N{N-ARY CIRCLED PLUS OPERATOR}"),
        ("bigotimes", "\N{N-ARY CIRCLED TIMES OPERATOR}"),
        ("bigsqcup", "\N{N-ARY SQUARE UNION OPERATOR}"),
        ("bigstar", "\N{BLACK STAR}"),
        ("bigtriangledown", "\N{WHITE DOWN-POINTING TRIANGLE}"),
        ("bigtriangleup", "\N{WHITE UP-POINTING TRIANGLE}"),
        ("biguplus", "\N{N-ARY UNION OPERATOR WITH PLUS}"),
        ("bigvee", "\N{N-ARY LOGICAL OR}"),
        ("bigwedge", "\N{N-ARY LOGICAL AND}"),
        ("blacklozenge", "\N{BLACK LOZENGE}"),
        ("blacksquare", "\N{BLACK SQUARE}"),
        ("blacktriangle", "\N{BLACK UP-POINTING TRIANGLE}"),
        ("blacktriangledown", "\N{BLACK DOWN-POINTING TRIANGLE}"),
        ("blacktriangleleft", "\N{BLACK LEFT-POINTING TRIANGLE}"),
        ("blacktriangleright", "\N{BLACK RIGHT-POINTING TRIANGLE}"),
        ("bmod", "mod"),
        ("bot", "\N{UP TACK}"),
        ("bowtie", "\N{BOWTIE}"),
        ("Box", "\N{WHITE SQUARE}"),
        ("boxdot", "\N{SQUARED DOT OPERATOR}"),
        ("boxminus", "\N{SQUARED MINUS}"),
        ("boxplus", "\N{SQUARED PLUS}"),
        ("boxtimes", "\N{SQUARED TIMES}"),
        ("bullet", "\N{BULLET OPERATOR}"),
        ("Bumpeq", "\N{GEOMETRICALLY EQUIVALENT TO}"),
        ("bumpeq", "\N{DIFFERENCE BETWEEN}"),
        ("Cap", "\N{DOUBLE INTERSECTION}"),
        ("cap", "\N{INTERSECTION}"),
        ("cdot", "\N{DOT OPERATOR}"),
        ("cdotp", "\N{DOT OPERATOR}"),
        ("cdots", "\N{MIDLINE HORIZONTAL ELLIPSIS}"),
        ("centerdot", "\N{DOT OPERATOR}"),
        ("cfrac", "%s/%s"),
        ("checkmark", "\N{CHECK MARK}"),
        ("chi", "\N{GREEK SMALL LETTER CHI}"),
        ("circ", "\N{RING OPERATOR}"),
        ("circeq", "\N{RING EQUAL TO}"),
        ("circlearrowleft", "\N{ANTICLOCKWISE OPEN CIRCLE ARROW}"),
        ("circlearrowright", "\N{CLOCKWISE OPEN CIRCLE ARROW}"),
        ("circledR", "\N{REGISTERED SIGN}"),
        ("circledS", "\N{CIRCLED LATIN CAPITAL LETTER S}"),
        ("circledast", "\N{CIRCLED ASTERISK OPERATOR}"),
        ("circledcirc", "\N{CIRCLED RING OPERATOR}"),
        ("circleddash", "\N{CIRCLED DASH}"),
        ("clubsuit", "\N{BLACK CLUB SUIT}"),
        ("colon", "\N{COLON}"),
        ("complement", "\N{COMPLEMENT}"),
        ("cong", "\N{APPROXIMATELY EQUAL TO}"),
        ("coprod", "\N{N-ARY COPRODUCT}"),
        ("cos", "cos"),
        ("cosh", "cosh"),
        ("cot", "cot"),
        ("coth", "coth"),
        ("cr", "\n"),
        ("csc", "csc"),
        ("Cup", "\N{DOUBLE UNION}"),
        ("cup", "\N{UNION}"),
        ("curlyeqprec", "\N{EQUAL TO OR PRECEDES}"),
        ("curlyeqsucc", "\N{EQUAL TO OR SUCCEEDS}"),
        ("curlyvee", "\N{CURLY LOGICAL OR}"),
        ("curlywedge", "\N{CURLY LOGICAL AND}"),
        ("curvearrowleft", "\N{ANTICLOCKWISE TOP SEMICIRCLE ARROW}"),
        ("curvearrowright", "\N{CLOCKWISE TOP SEMICIRCLE ARROW}"),
        ("dagger", "\N{DAGGER}"),
        ("daleth", "\N{DALET SYMBOL}"),
        ("dashleftarrow", "\N{LEFTWARDS DASHED ARROW}"),
        ("dashrightarrow", "\N{RIGHTWARDS DASHED ARROW}"),
        ("dashv", "\N{LEFT TACK}"),
        ("ddagger", "\N{DOUBLE DAGGER}"),
        ("ddots", "\N{DOWN RIGHT DIAGONAL ELLIPSIS}"),
        ("deg", "deg"),
        ("Delta", "\N{GREEK CAPITAL LETTER DELTA}"),
        ("delta", "\N{GREEK SMALL LETTER DELTA}"),
        ("det", "det"),
        ("dfrac", "%s/%s"),
        ("diagdown", "\N{BOX DRAWINGS LIGHT DIAGONAL UPPER LEFT TO LOWER RIGHT}"),
        ("diagup", "\N{BOX DRAWINGS LIGHT DIAGONAL UPPER RIGHT TO LOWER LEFT}"),
        ("Diamond", "\N{LOZENGE}"),
        ("diamond", "\N{DIAMOND OPERATOR}"),
        ("diamondsuit", "\N{WHITE DIAMOND SUIT}"),
        ("digamma", "\N{GREEK SMALL LETTER DIGAMMA}"),
        ("dim", "dim"),
        ("div", "\N{DIVISION SIGN}"),
        ("divideontimes", "\N{DIVISION TIMES}"),
        ("Doteq", "\N{GEOMETRICALLY EQUAL TO}"),
        ("doteq", "\N{APPROACHES THE LIMIT}"),
        ("dotplus", "\N{DOT PLUS}"),
        ("dots", "\N{HORIZONTAL ELLIPSIS}"),
        ("dotsb", "\N{MIDLINE HORIZONTAL ELLIPSIS}"),
        ("dotsc", "\N{HORIZONTAL ELLIPSIS}"),
        ("dotsi", "\N{MIDLINE HORIZONTAL ELLIPSIS}"),
        ("dotsm", "\N{MIDLINE HORIZONTAL ELLIPSIS}"),
        ("dotso", "\N{HORIZONTAL ELLIPSIS}"),
        ("doublebarwedge", "\N{LOGICAL AND WITH DOUBLE OVERBAR}"),
        ("doublecap", "\N{DOUBLE INTERSECTION}"),
        ("doublecup", "\N{DOUBLE UNION}"),
        ("Downarrow", "\N{DOWNWARDS DOUBLE ARROW}"),
        ("downarrow", "\N{DOWNWARDS ARROW}"),
        ("downdownarrows", "\N{DOWNWARDS PAIRED ARROWS}"),
        ("downharpoonleft", "\N{DOWNWARDS HARPOON WITH BARB LEFTWARDS}"),
        ("downharpoonright", "\N{DOWNWARDS HARPOON WITH BARB RIGHTWARDS}"),
        ("ell", "\N{SCRIPT SMALL L}"),
        ("emptyset", "\N{EMPTY SET}"),
        ("enspace", " "),
        ("epsilon", "\N{GREEK LUNATE EPSILON SYMBOL}"),
        ("eqcirc", "\N{RING IN EQUAL TO}"),
        ("eqsim", "\N{MINUS TILDE}"),
        ("eqslantgtr", "\N{SLANTED EQUAL TO OR GREATER-THAN}"),
        ("eqslantless", "\N{SLANTED EQUAL TO OR LESS-THAN}"),
        ("equiv", "\N{IDENTICAL TO}"),
        ("eta", "\N{GREEK SMALL LETTER ETA}"),
        ("eth", "\N{LATIN SMALL LETTER ETH}"),
        ("exists", "\N{THERE EXISTS}"),
        ("exp", "exp"),
        ("fallingdotseq", "\N{APPROXIMATELY EQUAL TO OR THE IMAGE OF}"),
        ("Finv", "\N{TURNED CAPITAL F}"),
        ("flat", "\N{MUSIC FLAT SIGN}"),
        ("forall", "\N{FOR ALL}"),
        ("frown", "\N{FROWN}"),
        ("Game", "\N{TURNED SANS-SERIF CAPITAL G}"),
        ("Gamma", "\N{GREEK CAPITAL LETTER GAMMA}"),
        ("gamma", "\N{GREEK SMALL LETTER GAMMA}"),
        ("gcd", "gcd"),
        ("ge", "\N{GREATER-THAN OR EQUAL TO}"),
        ("geq", "\N{GREATER-THAN OR EQUAL TO}"),
        ("geqq", "\N{GREATER-THAN OVER EQUAL TO}"),
        ("geqslant", "\N{GREATER-THAN OR SLANTED EQUAL TO}"),
        ("gets", "\N{LEFTWARDS ARROW}"),
        ("gg", "\N{MUCH GREATER-THAN}"),
        ("ggg", "\N{VERY MUCH GREATER-THAN}"),
        ("gggtr", "\N{VERY MUCH GREATER-THAN}"),
        ("gimel", "\N{GIMEL SYMBOL}"),
        ("gnapprox", "\N{GREATER-THAN AND NOT APPROXIMATE}"),
        ("gneq", "\N{GREATER-THAN AND SINGLE-LINE NOT EQUAL TO}"),
        ("gneqq", "\N{GREATER-THAN BUT NOT EQUAL TO}"),
        ("gnsim", "\N{GREATER-THAN BUT NOT EQUIVALENT TO}"),
        ("gt", "\N{GREATER-THAN SIGN}"),
        ("gtrapprox", "\N{GREATER-THAN OR APPROXIMATE}"),
        ("gtrdot", "\N{GREATER-THAN WITH DOT}"),
        ("gtreqless", "\N{GREATER-THAN EQUAL TO OR LESS-THAN}"),
        ("gtreqqless", "\N{GREATER-THAN ABOVE DOUBLE-LINE EQUAL ABOVE LESS-THAN}"),
        ("gtrless", "\N{GREATER-THAN OR LESS-THAN}"),
        ("gtrsim", "\N{GREATER-THAN OR EQUIVALENT TO}"),
        ("gvertneqq", "\N{GREATER-THAN BUT NOT EQUAL TO}"),
        ("hbar", "\N{PLANCK CONSTANT OVER TWO PI}"),
        ("heartsuit", "\N{WHITE HEART SUIT}"),
        ("hom", "hom"),
        ("hookleftarrow", "\N{LEFTWARDS ARROW WITH HOOK}"),
        ("hookrightarrow", "\N{RIGHTWARDS ARROW WITH HOOK}"),
        ("hskip", " "),
        ("hslash", "\N{PLANCK CONSTANT OVER TWO PI}"),
        ("hspace", " "),
        ("iff", "\N{LONG LEFT RIGHT DOUBLE ARROW}"),
        ("iiiint", "\N{INTEGRAL}" * 4),
        ("iiint", "\N{TRIPLE INTEGRAL}"),
        ("iint", "\N{DOUBLE INTEGRAL}"),
        ("Im", "\N{BLACK-LETTER CAPITAL I}"),
        ("imath", "\N{LATIN SMALL LETTER DOTLESS I}"),
        ("impliedby", "\N{LONG LEFTWARDS DOUBLE ARROW}"),
        ("implies", "\N{LONG RIGHTWARDS DOUBLE ARROW}"),
        ("in", "\N{ELEMENT OF}"),
        ("inf", "inf"),
        ("infty", "\N{INFINITY}"),
        ("injlim", "inj lim"),
        ("int", "\N{INTEGRAL}"),
        ("intercal", "\N{INTERCALATE}"),
        ("intop", "\N{INTEGRAL}"),
        ("iota", "\N{GREEK SMALL LETTER IOTA}"),
        ("jmath", "\N{LATIN SMALL LETTER DOTLESS J}"),
        ("Join", "\N{BOWTIE}"),
        ("kappa", "\N{GREEK SMALL LETTER KAPPA}"),
        ("ker", "ker"),
        ("kern", " "),
        ("Lambda", "\N{GREEK CAPITAL LETTER LAMDA}"),
        ("lambda", "\N{GREEK SMALL LETTER LAMDA}"),
        ("land", "\N{LOGICAL AND}"),
        ("langle", "\N{MATHEMATICAL LEFT ANGLE BRACKET}"),
        ("lbrace", "{"),
        ("lbrack", "["),
        ("lceil", "\N{LEFT CEILING}"),
        ("ldotp", "\N{FULL STOP}"),
        ("ldots", "\N{HORIZONTAL ELLIPSIS}"),
        ("le", "\N{LESS-THAN OR EQUAL TO}"),
        ("leadsto", "\N{RIGHTWARDS SQUIGGLE ARROW}"),
        ("Leftarrow", "\N{LEFTWARDS DOUBLE ARROW}"),
        ("leftarrow", "\N{LEFTWARDS ARROW}"),
        ("leftarrowtail", "\N{LEFTWARDS ARROW WITH TAIL}"),
        ("leftharpoondown", "\N{LEFTWARDS HARPOON WITH BARB DOWNWARDS}"),
        ("leftharpoonup", "\N{LEFTWARDS HARPOON WITH BARB UPWARDS}"),
        ("leftleftarrows", "\N{LEFTWARDS PAIRED ARROWS}"),
        ("Leftrightarrow", "\N{LEFT RIGHT DOUBLE ARROW}"),
        ("leftrightarrow", "\N{LEFT RIGHT ARROW}"),
        ("leftrightarrows", "\N{LEFTWARDS ARROW OVER RIGHTWARDS ARROW}"),
        ("leftrightharpoons", "\N{LEFTWARDS HARPOON OVER RIGHTWARDS HARPOON}"),
        ("leftrightsquigarrow", "\N{LEFT RIGHT WAVE ARROW}"),
        ("leftthreetimes", "\N{LEFT SEMIDIRECT PRODUCT}"),
        ("leq", "\N{LESS-THAN OR EQUAL TO}"),
        ("leqq", "\N{LESS-THAN OVER EQUAL TO}"),
        ("leqslant", "\N{LESS-THAN OR SLANTED EQUAL TO}"),
        ("lessapprox", "\N{LESS-THAN OR APPROXIMATE}"),
        ("lessdot", "\N{LESS-THAN WITH DOT}"),
        ("lesseqgtr", "\N{LESS-THAN EQUAL TO OR GREATER-THAN}"),
        ("lesseqqgtr", "\N{LESS-THAN ABOVE DOUBLE-LINE EQUAL ABOVE GREATER-THAN}"),
        ("lessgtr", "\N{LESS-THAN OR GREATER-THAN}"),
        ("lesssim", "\N{LESS-THAN OR EQUIVALENT TO}"),
        ("lfloor", "\N{LEFT FLOOR}"),
        ("lg", "lg"),
        ("lgroup", "\N{MATHEMATICAL LEFT FLATTENED PARENTHESIS}"),
        ("lhd", "\N{NORMAL SUBGROUP OF}"),
        ("lim", "lim"),
        ("liminf", "lim inf"),
        ("limsup", "lim sup"),
        ("ll", "\N{MUCH LESS-THAN}"),
        ("llcorner", "\N{BOX DRAWINGS LIGHT UP AND RIGHT}"),
        ("Lleftarrow", "\N{LEFTWARDS TRIPLE ARROW}"),
        ("lll", "\N{VERY MUCH LESS-THAN}"),
        ("llless", "\N{VERY MUCH LESS-THAN}"),
        ("lmoustache", "\N{UPPER LEFT OR LOWER RIGHT CURLY BRACKET SECTION}"),
        ("ln", "ln"),
        ("lnapprox", "\N{LESS-THAN AND NOT APPROXIMATE}"),
        ("lneq", "\N{LESS-THAN AND SINGLE-LINE NOT EQUAL TO}"),
        ("lneqq", "\N{LESS-THAN BUT NOT EQUAL TO}"),
        ("lnot", "\N{NOT SIGN}"),
        ("lnsim", "\N{LESS-THAN BUT NOT EQUIVALENT TO}"),
        ("log", "log"),
        ("Longleftarrow", "\N{LONG LEFTWARDS DOUBLE ARROW}"),
        ("longleftarrow", "\N{LONG LEFTWARDS ARROW}"),
        ("Longleftrightarrow", "\N{LONG LEFT RIGHT DOUBLE ARROW}"),
        ("longleftrightarrow", "\N{LONG LEFT RIGHT ARROW}"),
        ("longmapsto", "\N{LONG RIGHTWARDS ARROW FROM BAR}"),
        ("Longrightarrow", "\N{LONG RIGHTWARDS DOUBLE ARROW}"),
        ("longrightarrow", "\N{LONG RIGHTWARDS ARROW}"),
        ("looparrowleft", "\N{LEFTWARDS ARROW WITH LOOP}"),
        ("looparrowright", "\N{RIGHTWARDS ARROW WITH LOOP}"),
        ("lor", "\N{LOGICAL OR}"),
        ("lozenge", "\N{LOZENGE}"),
        ("lrcorner", "\N{BOX DRAWINGS LIGHT UP AND LEFT}"),
        ("Lsh", "\N{UPWARDS ARROW WITH TIP LEFTWARDS}"),
        ("lt", "\N{LESS-THAN SIGN}"),
        ("ltimes", "\N{LEFT NORMAL FACTOR SEMIDIRECT PRODUCT}"),
        ("lVert", "\N{PARALLEL TO}"),
        ("lvert", "\N{DIVIDES}"),
        ("lvertneqq", "\N{LESS-THAN BUT NOT EQUAL TO}"),
        ("maltese", "\N{MALTESE CROSS}"),
        ("mapsto", "\N{RIGHTWARDS ARROW FROM BAR}"),
        ("max", "max"),
        ("measuredangle", "\N{MEASURED ANGLE}"),
        ("mho", "\N{INVERTED OHM SIGN}"),
        ("mid", "\N{DIVIDES}"),
        ("min", "min"),
        ("mkern", " "),
        ("mod", "mod"),
        ("models", "\N{TRUE}"),
        ("mp", "\N{MINUS-OR-PLUS SIGN}"),
        ("mskip", " "),
        ("mspace", " "),
        ("mu", "\N{GREEK SMALL LETTER MU}"),
        ("multimap", "\N{MULTIMAP}"),
        ("nabla", "\N{NABLA}"),
        ("natural", "\N{MUSIC NATURAL SIGN}"),
        ("ncong", "\N{APPROXIMATELY BUT NOT ACTUALLY EQUAL TO}"),
        ("ne", "\N{NOT EQUAL TO}"),
        ("nearrow", "\N{NORTH EAST ARROW}"),
        ("neg", "\N{NOT SIGN}"),
        ("neq", "\N{NOT EQUAL TO}"),
        ("newline", "\n"),
        ("nexists", "\N{THERE DOES NOT EXIST}"),
        ("ngeq", "\N{NEITHER GREATER-THAN NOR EQUAL TO}"),
        ("ngeqq", "\N{NEITHER GREATER-THAN NOR EQUAL TO}"),
        ("ngeqslant", "\N{GREATER-THAN AND SINGLE-LINE NOT EQUAL TO}"),
        ("ngtr", "\N{NOT GREATER-THAN}"),
        ("ni", "\N{CONTAINS AS MEMBER}"),
        ("nLeftarrow", "\N{LEFTWARDS DOUBLE ARROW WITH STROKE}"),
        ("nleftarrow", "\N{LEFTWARDS ARROW WITH STROKE}"),
        ("nLeftrightarrow", "\N{LEFT RIGHT DOUBLE ARROW WITH STROKE}"),
        ("nleftrightarrow", "\N{LEFT RIGHT ARROW WITH STROKE}"),
        ("nleq", "\N{NEITHER LESS-THAN NOR EQUAL TO}"),
        ("nleqq", "\N{NEITHER LESS-THAN NOR EQUAL TO}"),
        ("nleqslant", "\N{LESS-THAN AND SINGLE-LINE NOT EQUAL TO}"),
        ("nless", "\N{NOT LESS-THAN}"),
        ("nmid", "\N{DOES NOT DIVIDE}"),
        ("nobreakspace", " "),
        ("notin", "\N{NOT AN ELEMENT OF}"),
        ("nparallel", "\N{NOT PARALLEL TO}"),
        ("nprec", "\N{DOES NOT PRECEDE}"),
        ("npreceq", "\N{DOES NOT PRECEDE OR EQUAL}"),
        ("nRightarrow", "\N{RIGHTWARDS DOUBLE ARROW WITH STROKE}"),
        ("nrightarrow", "\N{RIGHTWARDS ARROW WITH STROKE}"),
        ("nshortmid", "\N{DOES NOT DIVIDE}"),
        ("nshortparallel", "\N{NOT PARALLEL TO}"),
        ("nsim", "\N{NOT TILDE}"),
        ("nsubseteq", "\N{NEITHER A SUBSET OF NOR EQUAL TO}"),
        ("nsubseteqq", "\N{NEITHER A SUBSET OF NOR EQUAL TO}"),
        ("nsucc", "\N{DOES NOT SUCCEED}"),
        ("nsucceq", "\N{DOES NOT SUCCEED OR EQUAL}"),
        ("nsupseteq", "\N{NEITHER A SUPERSET OF NOR EQUAL TO}"),
        ("nsupseteqq", "\N{NEITHER A SUPERSET OF NOR EQUAL TO}"),
        ("ntriangleleft", "\N{NOT NORMAL SUBGROUP OF}"),
        ("ntrianglelefteq", "\N{NOT NORMAL SUBGROUP OF OR EQUAL TO}"),
        ("ntriangleright", "\N{DOES NOT CONTAIN AS NORMAL SUBGROUP}"),
        ("ntrianglerighteq", "\N{DOES NOT CONTAIN AS NORMAL SUBGROUP OR EQUAL}"),
        ("nu", "\N{GREEK SMALL LETTER NU}"),
        ("nVDash", "\N{NEGATED DOUBLE VERTICAL BAR DOUBLE RIGHT TURNSTILE}"),
        ("nVdash", "\N{DOES NOT FORCE}"),
        ("nvDash", "\N{NOT TRUE}"),
        ("nvdash", "\N{DOES NOT PROVE}"),
        ("nwarrow", "\N{NORTH WEST ARROW}"),
        ("odot", "\N{CIRCLED DOT OPERATOR}"),
        ("oint", "\N{CONTOUR INTEGRAL}"),
        ("of", "of"),
        ("Omega", "\N{GREEK CAPITAL LETTER OMEGA}"),
        ("omega", "\N{GREEK SMALL LETTER OMEGA}"),
        ("omicron", "\N{GREEK SMALL LETTER OMICRON}"),
        ("ominus", "\N{CIRCLED MINUS}"),
        ("oplus", "\N{CIRCLED PLUS}"),
        ("oslash", "\N{CIRCLED DIVISION SLASH}"),
        ("otimes", "\N{CIRCLED TIMES}"),
        ("over", "%s/%s"),
        ("owns", "\N{CONTAINS AS MEMBER}"),
        ("parallel", "\N{PARALLEL TO}"),
        ("partial", "\N{PARTIAL DIFFERENTIAL}"),
        ("perp", "\N{UP TACK}"),
        ("Phi", "\N{GREEK CAPITAL LETTER PHI}"),
        ("phi", "\N{GREEK PHI SYMBOL}"),
        ("Pi", "\N{GREEK CAPITAL LETTER PI}"),
        ("pi", "\N{GREEK SMALL LETTER PI}"),
        ("pitchfork", "\N{PITCHFORK}"),
        ("pm", "\N{PLUS-MINUS SIGN}"),
        ("pmod", "mod"),
        ("Pr", "Pr"),
        ("prec", "\N{PRECEDES}"),
        ("precapprox", "\N{PRECEDES ABOVE ALMOST EQUAL TO}"),
        ("preccurlyeq", "\N{PRECEDES OR EQUAL TO}"),
        ("preceq", "\N{PRECEDES ABOVE SINGLE-LINE EQUALS SIGN}"),
        ("precnapprox", "\N{PRECEDES ABOVE NOT ALMOST EQUAL TO}"),
        ("precneqq", "\N{PRECEDES ABOVE NOT EQUAL TO}"),
        ("precnsim", "\N{PRECEDES BUT NOT EQUIVALENT TO}"),
        ("precsim", "\N{PRECEDES OR EQUIVALENT TO}"),
        ("prime", "\N{PRIME}"),
        ("prod", "\N{N-ARY PRODUCT}"),
        ("projlim", "proj lim"),
        ("propto", "\N{PROPORTIONAL TO}"),
        ("Psi", "\N{GREEK CAPITAL LETTER PSI}"),
        ("psi", "\N{GREEK SMALL LETTER PSI}"),
        ("quad", "  "),
        ("qquad", "    "),
        ("rangle", "\N{MATHEMATICAL RIGHT ANGLE BRACKET}"),
        ("rbrace", "}"),
        ("rbrack", "]"),
        ("rceil", "\N{RIGHT CEILING}"),
        ("Re", "\N{BLACK-LETTER CAPITAL R}"),
        ("restriction", "\N{UPWARDS HARPOON WITH BARB RIGHTWARDS}"),
        ("rfloor", "\N{RIGHT FLOOR}"),
        ("rgroup", "\N{MATHEMATICAL RIGHT FLATTENED PARENTHESIS}"),
        ("rhd", "\N{CONTAINS AS NORMAL SUBGROUP}"),
        ("rho", "\N{GREEK SMALL LETTER RHO}"),
        ("Rightarrow", "\N{RIGHTWARDS DOUBLE ARROW}"),
        ("rightarrow", "\N{RIGHTWARDS ARROW}"),
        ("rightarrowtail", "\N{RIGHTWARDS ARROW WITH TAIL}"),
        ("rightharpoondown", "\N{RIGHTWARDS HARPOON WITH BARB DOWNWARDS}"),
        ("rightharpoonup", "\N{RIGHTWARDS HARPOON WITH BARB UPWARDS}"),
        ("rightleftarrows", "\N{RIGHTWARDS ARROW OVER LEFTWARDS ARROW}"),
        ("rightleftharpoons", "\N{RIGHTWARDS HARPOON OVER LEFTWARDS HARPOON}"),
        ("rightrightarrows", "\N{RIGHTWARDS PAIRED ARROWS}"),
        ("rightsquigarrow", "\N{RIGHTWARDS SQUIGGLE ARROW}"),
        ("rightthreetimes", "\N{RIGHT SEMIDIRECT PRODUCT}"),
        ("risingdotseq", "\N{IMAGE OF OR APPROXIMATELY EQUAL TO}"),
        ("rmoustache", "\N{UPPER RIGHT OR LOWER LEFT CURLY BRACKET SECTION}"),
        ("root", "root"),
        ("Rrightarrow", "\N{RIGHTWARDS TRIPLE ARROW}"),
        ("Rsh", "\N{UPWARDS ARROW WITH TIP RIGHTWARDS}"),
        ("rtimes", "\N{RIGHT NORMAL FACTOR SEMIDIRECT PRODUCT}"),
        ("rVert", "\N{PARALLEL TO}"),
        ("rvert", "\N{DIVIDES}"),
        ("S", "\N{SECTION SIGN}"),
        ("searrow", "\N{SOUTH EAST ARROW}"),
        ("sec", "sec"),
        ("setminus", "\N{SET MINUS}"),
        ("sharp", "\N{MUSIC SHARP SIGN}"),
        ("shortmid", "\N{DIVIDES}"),
        ("shortparallel", "\N{PARALLEL TO}"),
        ("Sigma", "\N{GREEK CAPITAL LETTER SIGMA}"),
        ("sigma", "\N{GREEK SMALL LETTER SIGMA}"),
        ("sim", "\N{TILDE OPERATOR}"),
        ("simeq", "\N{ASYMPTOTICALLY EQUAL TO}"),
        ("sin", "sin"),
        ("sinh", "sinh"),
        ("smallfrown", "\N{FROWN}"),
        ("smallint", "\N{INTEGRAL}"),
        ("smallsetminus", "\N{SET MINUS}"),
        ("smallsmile", "\N{SMILE}"),
        ("smile", "\N{SMILE}"),
        ("space", " "),
        ("spadesuit", "\N{BLACK SPADE SUIT}"),
        ("sphericalangle", "\N{SPHERICAL ANGLE}"),
        ("sqcap", "\N{SQUARE CAP}"),
        ("sqcup", "\N{SQUARE CUP}"),
        ("sqrt", u"\N{SQUARE ROOT}(%(2)s)"),
        ("sqsubset", "\N{SQUARE IMAGE OF}"),
        ("sqsubseteq", "\N{SQUARE IMAGE OF OR EQUAL TO}"),
        ("sqsupset", "\N{SQUARE ORIGINAL OF}"),
        ("sqsupseteq", "\N{SQUARE ORIGINAL OF OR EQUAL TO}"),
        ("square", "\N{WHITE SQUARE}"),
        ("star", "\N{STAR OPERATOR}"),
        ("Subset", "\N{DOUBLE SUBSET}"),
        ("subset", "\N{SUBSET OF}"),
        ("subseteq", "\N{SUBSET OF OR EQUAL TO}"),
        ("subseteqq", "\N{SUBSET OF ABOVE EQUALS SIGN}"),
        ("subsetneq", "\N{SUBSET OF WITH NOT EQUAL TO}"),
        ("subsetneqq", "\N{SUBSET OF ABOVE NOT EQUAL TO}"),
        ("succ", "\N{SUCCEEDS}"),
        ("succapprox", "\N{SUCCEEDS ABOVE ALMOST EQUAL TO}"),
        ("succcurlyeq", "\N{SUCCEEDS OR EQUAL TO}"),
        ("succeq", "\N{SUCCEEDS ABOVE SINGLE-LINE EQUALS SIGN}"),
        ("succnapprox", "\N{SUCCEEDS ABOVE NOT ALMOST EQUAL TO}"),
        ("succneqq", "\N{SUCCEEDS ABOVE NOT EQUAL TO}"),
        ("succnsim", "\N{SUCCEEDS BUT NOT EQUIVALENT TO}"),
        ("succsim", "\N{SUCCEEDS OR EQUIVALENT TO}"),
        ("sum", "\N{N-ARY SUMMATION}"),
        ("sup", "sup"),
        ("Supset", "\N{DOUBLE SUPERSET}"),
        ("supset", "\N{SUPERSET OF}"),
        ("supseteq", "\N{SUPERSET OF OR EQUAL TO}"),
        ("supseteqq", "\N{SUPERSET OF ABOVE EQUALS SIGN}"),
        ("supsetneq", "\N{SUPERSET OF WITH NOT EQUAL TO}"),
        ("supsetneqq", "\N{SUPERSET OF ABOVE NOT EQUAL TO}"),
        ("surd", "\N{SQUARE ROOT}"),
        ("swarrow", "\N{SOUTH WEST ARROW}"),
        ("tan", "tan"),
        ("tanh", "tanh"),
        ("tau", "\N{GREEK SMALL LETTER TAU}"),
        ("tfrac", "%s/%s"),
        ("therefore", "\N{THEREFORE}"),
        ("Theta", "\N{GREEK CAPITAL LETTER THETA}"),
        ("theta", "\N{GREEK SMALL LETTER THETA}"),
        ("thickapprox", "\N{ALMOST EQUAL TO}"),
        ("thicksim", "\N{TILDE OPERATOR}"),
        ("thinspace", " "),
        ("tilde", "\N{SMALL TILDE}"),
        ("times", "\N{MULTIPLICATION SIGN}"),
        ("to", "\N{RIGHTWARDS ARROW}"),
        ("top", "\N{DOWN TACK}"),
        ("triangle", "\N{WHITE UP-POINTING TRIANGLE}"),
        ("triangledown", "\N{WHITE DOWN-POINTING TRIANGLE}"),
        ("triangleleft", "\N{WHITE LEFT-POINTING SMALL TRIANGLE}"),
        ("trianglelefteq", "\N{NORMAL SUBGROUP OF OR EQUAL TO}"),
        ("triangleq", "\N{DELTA EQUAL TO}"),
        ("triangleright", "\N{WHITE RIGHT-POINTING SMALL TRIANGLE}"),
        ("trianglerighteq", "\N{CONTAINS AS NORMAL SUBGROUP OR EQUAL TO}"),
        ("twoheadleftarrow", "\N{LEFTWARDS TWO HEADED ARROW}"),
        ("twoheadrightarrow", "\N{RIGHTWARDS TWO HEADED ARROW}"),
        ("ulcorner", "\N{BOX DRAWINGS LIGHT DOWN AND RIGHT}"),
        ("unlhd", "\N{NORMAL SUBGROUP OF OR EQUAL TO}"),
        ("unrhd", "\N{CONTAINS AS NORMAL SUBGROUP OR EQUAL TO}"),
        ("Uparrow", "\N{UPWARDS DOUBLE ARROW}"),
        ("uparrow", "\N{UPWARDS ARROW}"),
        ("Updownarrow", "\N{UP DOWN DOUBLE ARROW}"),
        ("updownarrow", "\N{UP DOWN ARROW}"),
        ("upharpoonleft", "\N{UPWARDS HARPOON WITH BARB LEFTWARDS}"),
        ("upharpoonright", "\N{UPWARDS HARPOON WITH BARB RIGHTWARDS}"),
        ("uplus", "\N{MULTISET UNION}"),
        ("Upsilon", "\N{GREEK CAPITAL LETTER UPSILON}"),
        ("upsilon", "\N{GREEK SMALL LETTER UPSILON}"),
        ("upuparrows", "\N{UPWARDS PAIRED ARROWS}"),
        ("urcorner", "\N{BOX DRAWINGS LIGHT DOWN AND LEFT}"),
        ("varDelta", "\N{GREEK CAPITAL LETTER DELTA}"),
        ("varepsilon", "\N{GREEK SMALL LETTER EPSILON}"),
        ("varGamma", "\N{GREEK CAPITAL LETTER GAMMA}"),
        ("varinjlim", "lim inj"),
        ("varkappa", "\N{GREEK KAPPA SYMBOL}"),
        ("varLambda", "\N{GREEK CAPITAL LETTER LAMDA}"),
        ("varliminf", "lim inf"),
        ("varlimsup", "lim sup"),
        ("varnothing", "\N{EMPTY SET}"),
        ("varOmega", "\N{GREEK CAPITAL LETTER OMEGA}"),
        ("varPhi", "\N{GREEK CAPITAL LETTER PHI}"),
        ("varphi", "\N{GREEK SMALL LETTER PHI}"),
        ("varPi", "\N{GREEK CAPITAL LETTER PI}"),
        ("varpi", "\N{GREEK PI SYMBOL}"),
        ("varprojlim", "varprojlim"),
        ("varpropto", "\N{PROPORTIONAL TO}"),
        ("varPsi", "\N{GREEK CAPITAL LETTER PSI}"),
        ("varrho", "\N{GREEK RHO SYMBOL}"),
        ("varSigma", "\N{GREEK CAPITAL LETTER SIGMA}"),
        ("varsigma", "\N{GREEK SMALL LETTER FINAL SIGMA}"),
        ("varsubsetneq", "\N{SUBSET OF WITH NOT EQUAL TO}"),
        ("varsubsetneqq", "\N{SUBSET OF ABOVE NOT EQUAL TO}"),
        ("varsupsetneq", "\N{SUPERSET OF WITH NOT EQUAL TO}"),
        ("varsupsetneqq", "\N{SUPERSET OF ABOVE NOT EQUAL TO}"),
        ("varTheta", "\N{GREEK CAPITAL LETTER THETA}"),
        ("vartheta", "\N{GREEK THETA SYMBOL}"),
        ("vartriangle", "\N{WHITE UP-POINTING TRIANGLE}"),
        ("vartriangleleft", "\N{NORMAL SUBGROUP OF}"),
        ("vartriangleright", "\N{CONTAINS AS NORMAL SUBGROUP}"),
        ("varUpsilon", "\N{GREEK CAPITAL LETTER UPSILON}"),
        ("varXi", "\N{GREEK CAPITAL LETTER XI}"),
        ("Vdash", "\N{FORCES}"),
        ("vDash", "\N{TRUE}"),
        ("vdash", "\N{RIGHT TACK}"),
        ("vdots", "\N{VERTICAL ELLIPSIS}"),
        ("vee", "\N{LOGICAL OR}"),
        ("veebar", "\N{XOR}"),
        ("Vert", "\N{PARALLEL TO}"),
        ("vert", "\N{DIVIDES}"),
        ("Vvdash", "\N{TRIPLE VERTICAL BAR RIGHT TURNSTILE}"),
        ("wedge", "\N{LOGICAL AND}"),
        ("wp", "\N{SCRIPT CAPITAL P}"),
        ("wr", "\N{WREATH PRODUCT}"),
        ("Xi", "\N{GREEK CAPITAL LETTER XI}"),
        ("xi", "\N{GREEK SMALL LETTER XI}"),
        ("yen", "\N{YEN SIGN}"),
        ("zeta", "\N{GREEK SMALL LETTER ZETA}"),
        # ProofWiki
        ("paren", "(%s)"),
        ("N", "\N{DOUBLE-STRUCK CAPITAL N}"),
        ("R", "\N{DOUBLE-STRUCK CAPITAL R}"),
        ("Z", "\N{DOUBLE-STRUCK CAPITAL Z}"),
        ("set", "{%s}"),
        ("sqbrk", "[%s]"),
        ("tuple", "(%s)"),
        # Overrides
        ("implies", "\N{RIGHTWARDS DOUBLE ARROW}"),
    )
]

ARGS = [
    # MathJax
    std_macro("above", False, 2),
    std_macro("cfrac", False, 2),
    std_macro("dfrac", False, 2),
    std_macro("frac", False, 2),
    std_macro("over", False, 2),
    std_macro("sqrt", True, 1),
    std_macro("tfrac", False, 2),
    # ProofWiki
    std_macro("paren", False, 1),
    std_macro("set", False, 1),
    std_macro("sqbrk", False, 1),
    std_macro("tuple", False, 1),
]

ACCENTS = (
    ("bcancel", "\N{COMBINING LONG SOLIDUS OVERLAY}"),
    ("cancel", "\N{COMBINING LONG SOLIDUS OVERLAY}"),
    ("mathring", "\N{COMBINING RING ABOVE}"),
    ("overleftarrow", "\N{COMBINING LEFT ARROW ABOVE}"),
    ("overleftrightarrow", "\N{COMBINING LEFT RIGHT ARROW ABOVE}"),
    ("overline", "\N{COMBINING OVERLINE}"),
    ("overrightarrow", "\N{COMBINING RIGHT ARROW ABOVE}"),
    ("overparen", "\N{COMBINING PARENTHESES ABOVE}"),
    ("underleftarrow", "\N{COMBINING LEFT ARROW BELOW}"),
    ("underleftrightarrow", "\N{COMBINING LEFT RIGHT ARROW BELOW}"),
    ("underline", "\N{COMBINING LOW LINE}"),
    ("underrightarrow", "\N{COMBINING RIGHT ARROW BELOW}"),
    ("underparen", "\N{COMBINING PARENTHESES BELOW}"),
    ("widehat", "\N{COMBINING CIRCUMFLEX ACCENT}"),
    ("widetilde", "\N{COMBINING TILDE}"),
)

for name, combine in ACCENTS:
    MACROS.append(
        MacroTextSpec(
            name, lambda x, l2tobj, c=combine: make_accented_char(x, c, l2tobj)
        )
    )
    ARGS.append(std_macro(name, False, 1))

CTX = l2t_ctx()
CTX_ARGS = lwalk_ctx()

CTX.add_context_category("mathjax", macros=MACROS, prepend=True)
CTX_ARGS.add_context_category("mathjax", macros=ARGS, prepend=True)

L2T = LatexNodes2Text(CTX, math_mode="text")


def latex_to_text(latex: str) -> str:
    return L2T.latex_to_text(latex, latex_context=CTX_ARGS)  # type: ignore