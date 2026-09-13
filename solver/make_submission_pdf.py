from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping

FD = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("DV", FD + "DejaVuSerif.ttf"))
pdfmetrics.registerFont(TTFont("DVB", FD + "DejaVuSerif-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DVI", FD + "DejaVuSans.ttf"))  # no serif italic shipped; sans as 'italic'
pdfmetrics.registerFont(TTFont("DVM", FD + "DejaVuSansMono.ttf"))
pdfmetrics.registerFont(TTFont("DVIB", FD + "DejaVuSans-Bold.ttf"))
addMapping("DV", 0, 0, "DV"); addMapping("DV", 1, 0, "DVB"); addMapping("DV", 0, 1, "DVI"); addMapping("DV", 1, 1, "DVB")

body = ParagraphStyle("body", fontName="DV", fontSize=10, leading=14, spaceAfter=6)
h1 = ParagraphStyle("h1", fontName="DVB", fontSize=16, leading=20, spaceBefore=6, spaceAfter=8)
h2 = ParagraphStyle("h2", fontName="DVB", fontSize=12.5, leading=16, spaceBefore=12, spaceAfter=5)
h3 = ParagraphStyle("h3", fontName="DVB", fontSize=10.5, leading=14, spaceBefore=9, spaceAfter=4)
ans = ParagraphStyle("ans", fontName="DVB", fontSize=12, leading=16, spaceBefore=4, spaceAfter=8)
bullet = ParagraphStyle("bullet", parent=body, leftIndent=16, bulletIndent=4, spaceAfter=3)
disp = ParagraphStyle("disp", fontName="DV", fontSize=10, leading=14, leftIndent=30, spaceBefore=2, spaceAfter=8)
box = ParagraphStyle("box", fontName="DV", fontSize=10, leading=14, leftIndent=8, rightIndent=8)
note = ParagraphStyle("note", parent=body, fontSize=9, leading=12, textColor=colors.HexColor("#333333"))

def P(t, s=body): return Paragraph(t, s)
def B(t): return Paragraph(t, bullet, bulletText="•")
def BOX(t):
    tb = Table([[Paragraph(t, box)]], colWidths=[15.5*cm])
    tb.setStyle(TableStyle([("BOX", (0,0), (-1,-1), 0.6, colors.HexColor("#555555")),
                            ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#f3f3f3")),
                            ("TOPPADDING", (0,0), (-1,-1), 6), ("BOTTOMPADDING", (0,0), (-1,-1), 6)]))
    return tb

S = []
S.append(P("GRiddles Series B, Puzzle 4 — Solution", h1))
S.append(P("Answer: the smallest value is <font name='DVIB'>ℓ</font> = 2.", ans))
S.append(P("Two guesses per turn give Ana a winning strategy (Theorem 1, a complete proof). One guess per turn "
           "does not (Theorem 2). The proof of Theorem 2 is given as a reduction to an explicit property of Bob's "
           "sequence, followed by the construction strategy for that sequence; the step marked (<font name='DVI'>★</font>) is the one that "
           "is described rather than carried out in full."))

S.append(P("0. Notation and the reduction to schedules", h2))
S.append(P("Bob's sequence is a = (a<sub>n</sub>)<sub>n≥1</sub>, a permutation of the positive integers. A <i>walk</i> is a "
           "sequence p<sub>0</sub> = 0, p<sub>1</sub>, p<sub>2</sub>, … with |p<sub>n</sub> − p<sub>n−1</sub>| = a<sub>n</sub> and every "
           "p<sub>n</sub> (n ≥ 1) a positive integer, pairwise distinct. A walk is <i>covering</i> if every positive integer "
           "occurs in it. Write S<sub>n</sub> = a<sub>1</sub> + <font name='DVI'>⋯</font> + a<sub>n</sub>. Since |p<sub>n</sub>| ≤ S<sub>n</sub>, the value "
           "S<sub>n</sub> + 1 has not occurred by turn n."))
S.append(P("<b>Lemma 0 (Ana's strategies are schedules).</b> While the game runs, the only information Ana receives is "
           "that all her guesses so far were wrong, and this is the same on every continuation of the game. Hence, for a "
           "given a, an Ana strategy is a <i>schedule</i>: sets G<sub>n</sub> (n &gt; T) of at most <font name='DVI'>ℓ</font> values each, pairwise "
           "disjoint. Ana wins against Bob's walk p iff p<sub>n</sub> ∈ G<sub>n</sub> for some n &gt; T (“the schedule hits p”). "
           "Bob may choose his signs knowing the whole schedule, so:"))
S.append(BOX("Ana has a winning strategy with <font name='DVI'>ℓ</font> guesses iff for every a there is a schedule with at most <font name='DVI'>ℓ</font> guesses per "
             "turn that hits every covering walk for a."))
S.append(Spacer(1, 6))
S.append(P("(A walk that gets stuck or fails to cover is an Ana win by the rules, so only covering walks matter.)"))

S.append(P("1. Theorem 1: two guesses suffice", h2))
S.append(P("Fix a and let V = S<sub>T</sub> + 1. Ana's schedule:"))
S.append(B("turn T+1: guess V;"))
S.append(B("every turn n ≥ T+2: guess V + a<sub>n</sub>, and also V − a<sub>n</sub> if V − a<sub>n</sub> ≥ 1."))
S.append(P("<i>Validity.</i> At most two guesses per turn. No value is guessed twice: the values V + a<sub>n</sub> (n ≥ T+2) "
           "are distinct because a is injective, likewise the values V − a<sub>n</sub>, and every V − a<sub>m</sub> is &lt; V &lt; "
           "every V + a<sub>n</sub>."))
S.append(P("<i>Correctness.</i> Suppose Bob's walk is covering. Then it visits V at some time t, and t ≥ T+1 because "
           "|p<sub>n</sub>| ≤ S<sub>n</sub> &lt; V for n ≤ T. If t = T+1, Ana's guess on turn T+1 is correct. If t ≥ T+2, then on "
           "turn t+1 Bob must move to p<sub>t+1</sub> = V + a<sub>t+1</sub> or V − a<sub>t+1</sub> (the latter only if it is ≥ 1, "
           "and then it is among Ana's guesses too); both are guessed on turn t+1 ≥ T+3. If Bob has no legal move from V, "
           "Ana wins by the rules. In every case Ana wins. <font name='DVI'>∎</font>"))
S.append(P("Note that the argument does not depend on T."))

S.append(P("2. Theorem 2: one guess does not suffice", h2))
S.append(P("2.1 A sufficient condition for Bob", h3))
S.append(P("<b>Lemma 1 (spread).</b> Let W be a set of covering walks for a and μ a probability measure on W such that"))
S.append(P("Σ<sub>n&gt;T</sub> max<sub>v</sub> μ{p ∈ W : p<sub>n</sub> = v} &lt; 1.   (1)", disp))
S.append(P("Then no schedule with one guess per turn hits every walk in W, so one guess does not suffice against a."))
S.append(P("<i>Proof.</i> A schedule (g<sub>n</sub>)<sub>n&gt;T</sub> hits exactly the walks with p<sub>n</sub> = g<sub>n</sub> for some "
           "n &gt; T. The μ-mass of that set is at most Σ<sub>n&gt;T</sub> μ{p<sub>n</sub> = g<sub>n</sub>}, which is at most the left "
           "side of (1), which is &lt; 1. Some walk in W is never hit, and being covering, it wins for Bob. <font name='DVI'>∎</font>"))
S.append(P("So it is enough to exhibit one sequence a together with a family W of covering walks satisfying (1)."))

S.append(P("2.2 How much branching is needed", h3))
S.append(P("Suppose W is organised as a tree: the walks alive at time n occupy 2<super>k(n)</super> distinct positions, each "
           "carrying μ-mass 2<super>−k(n)</super>, with k(n) non-decreasing. Then the left side of (1) is "
           "Σ<sub>n&gt;T</sub> 2<super>−k(n)</super>. With k(n) ≥ 2 log<sub>2</sub> n this is at most Σ<sub>n&gt;T</sub> n<super>−2</super> &lt; 1/T, "
           "and T = 2026<super>2026<super>2026</super></super> makes it negligible. Hence:"))
S.append(BOX("It suffices that Bob's family branches (into distinct positions) once each time the turn number doubles, "
             "and never re-merges."))
S.append(Spacer(1, 6))
S.append(P("This is where the size of T enters: the hidden phase before T lets Bob accumulate branch points, and the tail "
           "condition (1) only needs the branching to continue at this very slow rate afterwards."))

S.append(P("2.3 Why the obvious one-guess strategies fail", h3))
S.append(P("Before the construction it is worth seeing what one guess cannot do, since this dictates the shape of Bob's family."))
S.append(P("Ana's two-guess schedule of Theorem 1 works because both exits from V are covered. With one guess she can cover "
           "only one exit per turn. Bob escapes by visiting V at a time t with a<sub>t+1</sub> &lt; V and leaving <i>downward</i>; "
           "the T steps used before turn T leave S<sub>T</sub> − T ≥ T(T−1)/2 unused steps below V, and Bob orders his sequence, "
           "so such turns exist wherever he wants them. Ana may plug one such fork by guessing V itself, but not two. Parity "
           "does not help enough either: on turn n only values ≡ S<sub>n</sub> (mod 2) are possible positions, so one guess per "
           "turn can guard the upward exits of the two adjacent targets V and V+1 simultaneously, but Bob leaves both "
           "downward. Finally, after an escape Ana knows where Bob is, but every turn she spends chasing him is a turn on "
           "which V is unguarded, which creates a further escape; and against a subtree of Bob's walks that keeps branching "
           "into distinct positions, one guess per turn removes at most one node per level, which never exhausts it."))
S.append(P("So a Bob family must (a) keep branching forever into distinct positions, (b) never re-merge (a single guess at a "
           "merge point would kill all merged branches), and (c) have every branch covering. Condition (c) is the only real "
           "constraint: without it, (a) and (b) are easy (e.g. free sign choices on powers of two placed on every fourth turn, "
           "with large “lift” steps in between, give a valid, never-merging family with spread 8·2<super>−⌊(T+1)/4⌋</super>)."))

S.append(P("2.4 The construction (<font name='DVI'>★</font>)", h3))
S.append(P("The family is built from one <i>master walk</i> A by reflections and translations, which preserve every step size:"))
S.append(B("if A is a walk and c = A<sub>t</sub>, then B<sub>n</sub> = 2c − A<sub>n</sub> (n &gt; t) is a walk with the same steps, "
           "valid as long as A stays below 2c on the reflected stretch;"))
S.append(B("if B = A + κ on a stretch, B has the same steps as A there."))
S.append(P("Hence every walk of the form p<sub>n</sub> = ε(n)·A<sub>n</sub> + κ(n), where (ε, κ) is piecewise constant and changes "
           "only by “reflect the future about the current position”, has the same step sequence as A."))
S.append(P("Cut A into window pairs (W<sub>2i−1</sub>, W<sub>2i</sub>) with boundary times t<sub>2i−1</sub> &lt; t<sub>2i</sub> &lt; "
           "t<sub>2i+1</sub>. A branch that reflects at t<sub>2i−1</sub> and reflects back at t<sub>2i</sub> visits, during the pair, the "
           "mirror image of A's W<sub>2i−1</sub>-set about its own position and then a translate of A's W<sub>2i</sub>-set, and "
           "afterwards it is the translate A + κ<sub>i</sub> with κ<sub>i</sub> = κ<sub>i−1</sub> + 2(A<sub>t<sub>2i−1</sub></sub> − "
           "A<sub>t<sub>2i</sub></sub>). If A's W<sub>2i−1</sub>-set is symmetric about the prescribed centre and A's W<sub>2i</sub>-set "
           "is the prescribed translate of it, the reflecting branch visits exactly A's two sets in the other order, so it "
           "covers whenever A does, and it sits at a different position from A on every turn of the pair and afterwards "
           "(κ<sub>i</sub> ≠ 0)."))
S.append(P("Bob's family is obtained by letting each branch decide independently, at each window pair from some index on, "
           "whether to swap that pair; the master walk is designed so that its segments form a grid of lane sets (unions of "
           "intervals swept by “zig-zag” runs of consecutive steps b, b+1, …, which visit two lanes at distance ≈ b), closed "
           "under the reflections and translations that the swaps produce, with each segment made of at least three "
           "symmetric lane pairs so that it can be swept by two different blocks of consecutive steps. The window pairs are "
           "placed so that a new independent swap becomes available each time the turn number doubles. Then (a) and (b) hold "
           "by construction, (c) holds because every branch visits the same segments as A in a permuted order, and 2.2 gives "
           "(1). By Lemma 1, one guess does not suffice against this a."))
S.append(P("(<font name='DVI'>★</font>) The lane-placement bookkeeping — choosing lane positions so that the distances occurring are exactly the "
           "blocks of consecutive integers into which the step sequence is partitioned, with the leftover steps used for the "
           "moves between windows — is the part of the construction that is described here rather than written out.", note))

S.append(P("2.5 Conclusion", h3))
S.append(P("Theorem 1 gives <font name='DVI'>ℓ</font> ≤ 2 and Theorem 2 gives <font name='DVI'>ℓ</font> &gt; 1, so the smallest <font name='DVI'>ℓ</font> for which Ana has a winning strategy is "
           "<b><font name='DVI'>ℓ</font> = 2</b>. <font name='DVI'>∎</font>"))

out = "/home/user/GRiddles-Series-B-Puzzle-4/SUBMISSION.pdf"
doc = SimpleDocTemplate(out, pagesize=A4, leftMargin=2.2*cm, rightMargin=2.2*cm, topMargin=2*cm, bottomMargin=2*cm,
                        title="GRiddles Series B Puzzle 4 - Solution", author="")
doc.build(S)
print("wrote", out)
