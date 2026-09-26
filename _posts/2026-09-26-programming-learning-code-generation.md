---
title: "Programming, learning, and code generation"
description: "What decades of research on learning to program and on maintaining software say about code that now costs almost nothing to produce."
date: 2026-09-26 12:00:00 +04:00
image:
  path: assets/img/prog-learning/banner.jpg
  alt: "Two women operating ENIAC, U.S. Army photograph, public domain"
categories: [Programming]
tags: [Learning, Code Generation, Software Engineering, AI]
math: false
---

two posts on this blog never showed up on the site. the build log says why:

```text
Skipping: _posts/2025-09-2-c-day1.md has a future date
```

i asked an AI assistant and it blamed the filename, said the day in `2025-09-2` isn't zero-padded. nope. inside the file the front matter says `date: 2095-09-2`, jekyll trusts that over the filename, and a post from the future doesn't get published. the other one says `2079`. the assistant never opened the file. it answered from what files usually look like.

small bug but it's basically this whole post. getting an answer and knowing what made the answer true are two different things, and code generation made the first one free while the second one costs exactly what it always did. that gap shows up in two places people usually talk about separately: how people learn to program, and how teams keep understanding the stuff they own. both have decades of research, most of it older than LLMs, and tbh it already tells us most of what to expect. i'll go through it and also drop some predictions of mine that could be wrong.

(the banner is a public-domain army photo of two women programming ENIAC around 1946 [\[1\]](#ref-1). the people who knew how that machine actually worked were the ones plugging the cables, which fits.)

## The picture in your head

trace this before you run it. what do the two prints show?

```python
def reset(board):
    board = [0, 0, 0]

def clear(board):
    board[:] = [0, 0, 0]

b = [1, 2, 3]
reset(b)
print(b)
clear(b)
print(b)
```

```text
[1, 2, 3]
[0, 0, 0]
```

they look almost the same. a beginner can use both for weeks and never notice. `reset` points its own local name at a new list, the caller's list doesn't change; `clear` changes the list both names point to. if you think a variable is a box holding a value you'll get one of these wrong, and you might still have passed every exercise so far. not a syntax problem, a wrong picture of the machine.

SICP drew this exact thing back in the 80s. same printed list, two totally different structures underneath:

![SICP figure 3.16: z1 formed by (cons x x)](/assets/img/prog-learning/sicp-sharing.gif)
_Figure 1. SICP figure 3.16: `z1`, built with `(cons x x)`. both halves point at the same list. From Abelson and Sussman [\[2\]](#ref-2), CC BY-SA 4.0._

![SICP figure 3.17: z2 formed from two separate lists](/assets/img/prog-learning/sicp-copies.gif)
_Figure 2. SICP figure 3.17: `z2`, built from two separate lists that print the same. change one and the other doesn't move. From [\[2\]](#ref-2), CC BY-SA 4.0._

du boulay, o'shea and monk called the thing in your head the **notional machine**, "the idealized model of the computer implied by the constructs of the programming language" [\[3\]](#ref-3). not the CPU, not the compiler, the teaching-level story of what the language does, and everyone builds their own version. later du boulay listed understanding it, and how the real machine relates to it, as one of the main places novices get stuck, with assignment as his example [\[4\]](#ref-4). sorva says courses should teach it directly instead of hoping people absorb it [\[5\]](#ref-5). i agree, and ngl i wonder how many working devs could draw theirs.

most beginners can't run their model reliably. in one multi-national study, 941 students at 12 institutions in 7 countries, most near the end of first semester, did 12 multiple-choice questions on tracing or completing short programs [\[6\]](#ref-6). of the 556 who answered all 12, 23% got 4 or less, and completing code was the worst part. the wrong models are specific enough that people catalogue them: progmiscon, from the computing-education group in lugano, lists 247 misconceptions across 58 concepts in Java, Python, JavaScript and Scratch [\[7\]](#ref-7).

experts carry structure beginners don't even see. jorma sajaniemi noticed experienced programmers read variables by what they do, and named the common jobs:

```python
def summarize(temps):
    n = len(temps)             # fixed value
    total = 0                  # gatherer
    hottest = temps[0]         # most-wanted holder
    prev = None                # follower
    fell = False               # one-way flag
    for i in range(n):         # stepper
        t = temps[i]           # most-recent holder
        total += t
        if t > hottest:
            hottest = t
        if prev is not None and t < prev:
            fell = True
        prev = t
    return total / n, hottest, fell
```

he pointed out textbooks usually only describe two patterns, the counter and the temporary. in his 2002 analysis of 109 novice-level programs, nine roles covered 99% of the variables [\[8\]](#ref-8); the list has 11 now. when 91 first-semester students were taught the normal way, with the roles, or with the roles plus an animator, the normal-way group wrote fewer program summaries that connected the code to the actual problem [\[9\]](#ref-9). a beginner sees `prev` and it's a name. someone experienced sees a follower and already checks what it holds on the first loop, because followers are always weird on the first loop.

so the claim i'm building everything else on: every tool you use while coding either helps you build this model or stands in for it. a debugger can go either way, you can watch it to check your prediction or watch it instead of predicting. same for autocomplete, stack overflow, visualizers. my test is simple: if the tool vanished tomorrow, what could you still do? an AI assistant is the strongest stand-in so far because it replaces the model at every level at once. you ask why your recursive function breaks, you get a fixed one, and you keep the exact picture that made the bug. the jekyll answer at the top was the same thing from the other side: no model of the file, just a model of what files usually look like, and it answered anyway.

## Where learning happens

being stuck comes in two kinds. sometimes you need a distinction you don't have yet. sometimes you're stuck on stuff that teaches nothing. from inside they feel the same, and most AI-in-education arguments are really about telling them apart.

manu kapur studied the first kind with tasks like this. three players, six games each. who's the most consistent? try to make up a measure before reading on.

```text
Ana:   14 15 15 16 15 15
Bilal:  8 22 15 15 15 15
Chen:  10 12 14 16 18 20
```

people's first ideas are usually the ones kapur's students came up with: the range, how far each game is from the average added up, something like the average distance. computing them takes a few lines ([`consistency.py`](/assets/code/prog-learning/consistency.py)):

```text
         range  sum dev    MAD     SD
Ana          2        0   0.33   0.58
Bilal       14        0   2.33   4.04
Chen        10        0    3.0   3.42
```

(all three average 15.) the "add up the distances" idea dies instantly, above and below the mean always cancel to zero. the rest disagree with each other. range says Chen is steadier than Bilal, mean absolute deviation says Bilal is steadier than Chen, and standard deviation, which nobody was taught yet, sides with the range. to pick one you have to decide what "consistent" even means; is one crazy game worse than a slow drift? that decision IS the concept. the formula is the easy part, and it's also the part a textbook or a chatbot gives you first.

in one of kapur's randomized studies, ninth-graders in india who hadn't learned standard deviation did an hour on a problem like this and an hour of instruction, only the order was different [\[10\]](#ref-10). the struggle-first group found no correct method at all. on the posttest both groups were about the same on procedure, and the struggle-first group did way better on concepts (6.33 vs 3.84 out of 10) and transfer (5.37 vs 3.11).

the detail i like most is from his second study. a group that critiqued other students' failed attempts, instead of making their own, beat direct instruction on concepts only and did worse than the kids who made the failures themselves. seeing mistakes isn't the same as making them. schwartz and bransford got something close with a different setup [\[11\]](#ref-11). students either analyzed contrasting cases from memory experiments or summarized a text, then everyone heard the same lecture. in their third experiment, 36 students, the case group made 43.8% of the possible predictions on a later task, vs 14.6% for the summary group and 16.7% for a group that analyzed cases twice and skipped the lecture. so neither the cases nor the lecture did it alone. their first experiment shows why normal teaching never notices: recognizing the concepts was near ceiling, 93%, in both groups, and only the case group actually used them a week later. judged on the day, both lessons "worked".

the other side is just as solid though. a novice can burn hours searching without ever seeing the structure an expert would use, which is why worked examples help beginners so reliably. and help that works for novices stops working as people improve: kalyuga, ayres, chandler and sweller found "instructional techniques that are highly effective with inexperienced learners can lose their effectiveness and even have negative consequences when used with more experienced learners" [\[12\]](#ref-12). so struggle isn't good and help isn't bad. it depends which operation the struggle is about.

this is where i think the AI debate gets confused. a generated solution looks exactly like a worked example, and worked examples are good for beginners, so what's the problem? chi and colleagues kind of answered it in 1989 [\[13\]](#ref-13). students studied worked physics examples then solved problems. the four who later solved best made 15.3 explanations per example, the four worst made 2.8. same examples. the good ones kept asking why each step followed. only 8 students grouped after the fact, so it's a correlation, but a later experiment got closer to cause [\[14\]](#ref-14): twenty-four eighth-graders read a 101-sentence text on the circulatory system, the 14 prompted to explain each sentence to themselves gained 32% from pretest to posttest, the 10 who just read it twice gained 22% (the prompted ones also studied about twice as long and assignment wasn't described as random, so time is still a competing explanation). the text doesn't teach. what you do with the text teaches. a worked example is something you study; a generated answer is usually something you submit. same characters on the screen, different operation.

so prediction #1, and it's cheap to test: students who get AI-generated code and have to explain every line before using it will learn clearly more than students who get the same code without that rule, and most of the gap between AI users and non-users on later tests will turn out to be about that.

the tools to control which operation stays with the learner already exist. van merriënboer and de croock taught 40 novices a 2.5-hour programming course, one group wrote whole programs, the other completed partial ones, and the completion group used programming templates better on both a construction test and a multiple-choice test [\[15\]](#ref-15). renkl, atkinson and große studied fading, where early examples show every step and later ones leave more to you, and people learned most about exactly the principles whose steps were faded [\[16\]](#ref-16). for tree recursion it'd look like:

```python
# 1. worked: every step shown
def depth(tree):
    if tree is None:            # an empty tree has depth 0
        return 0
    left = depth(tree.left)     # trust the recursion on each subtree
    right = depth(tree.right)
    return 1 + max(left, right)

# 2. faded: the recursive case is yours
def size(tree):
    if tree is None:
        return 0
    ...                         # this node, plus both subtrees

# 3. only the contract
def leaves(tree):
    """Number of nodes with no children."""
```

koedinger and aleven call the general problem the assistance dilemma, how to balance giving help and holding it back, and they treat it as open [\[17\]](#ref-17). a teaching assistant built on this would give you a failing input instead of a fix, or hand you a near-miss like this binary search ([`near_miss.py`](/assets/code/prog-learning/near_miss.py)), which should return the index of the first element at least as large as the target, or the list length if there isn't one:

```python
def first_at_least(xs, target):
    lo, hi = 0, len(xs) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if xs[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo
```

`first_at_least([1, 3, 5, 7], 5)` gives 2, searching 4 also gives 2. search 9 and you get 3 instead of 4, because `hi` starts one spot too early and "past the end" can never come back. finding that input is pure notional-machine work.

honest doubt though: nobody tells you in advance which operation carries the concept. for linked lists i'd guess pointer updates. for some students it's the idea that a node is an object at all, and then even a generated constructor takes the lesson away.

## Teaching, feedback and attention

if the unit of learning is an operation, then teaching is mostly about who does which operation when, and feedback is about what info shows up at what moment.

donald bligh spent ages comparing lectures with other methods. his conclusion: the lecture "is as effective as any other method for transmitting information, but not more effective", and most lectures are worse than discussion at getting people to think [\[18\]](#ref-18). his advice is blunt: "Use lectures to teach information. Do not rely on them to promote thought, change attitudes, or develop behavioral skills if you can help it." freeman and colleagues pooled 225 studies of undergrad science, engineering and math courses: failure rates were 21.8% with active learning vs 33.8% with traditional lecturing [\[19\]](#ref-19). but "active" hides a lot. chi and wylie's ICAP framework splits it by what you actually do: passive (listening), active (copying, highlighting), constructive (making an inference the material didn't say), interactive (arguing and changing your mind), and predicts learning goes up in that order [\[20\]](#ref-20). in a coding class that's watching the teacher live-code, retyping it, predicting the output before it runs, and debugging it with a friend. four different activities, same code on the same projector.

peer instruction puts the constructive part inside the lecture. as crouch and mazur describe it, the talk stops for a conceptual question, students answer alone within 1 to 2 minutes, spend 2 to 4 minutes trying to convince their neighbors, answer again, and only then get the explanation [\[21\]](#ref-21). in the physics course they report on, the normalized gain on the Force Concept Inventory went from 0.25 with traditional teaching in 1990, with 121 students, to 0.49 in the first peer instruction year, with 177. different years and no 1990 pretest, so read it carefully. the `reset`/`clear` thing at the top is basically one of those questions; every wrong answer is a specific wrong notional machine, which is exactly why arguing about it with your neighbor works.

teaching also steers attention in ways nobody means to. bonawitz and colleagues gave 85 preschoolers a toy with four hidden functions [\[22\]](#ref-22). when an adult showed one function like a teacher would, the kids found on average 0.72 of the other three, vs 1.15 to 1.3 in the other conditions, and played with it less. preschoolers aren't undergrads, but the mechanism looks general: people read a teacher's choices as "this is what matters" and stop searching. an AI answer is an extreme version of confident, specific demonstration. my guess is it narrows search the same way, which is fine when you want the narrowing and bad when the thing worth finding was somewhere else.

feedback's the same shape. it can land while you still remember the decision that caused the error, or after that's gone. kulik and kulik reviewed 53 studies [\[23\]](#ref-23): classroom studies with real quizzes mostly favored immediate feedback, experiments on learning test content mostly favored delayed. butler and winne put feedback inside a self-regulation loop where your own monitoring comes first [\[24\]](#ref-24), so outside feedback only helps as much as it changes your next try. shute's review turns it into guidance: immediate for hard tasks and weaker learners, delayed or softer for easy tasks and stronger ones, and after an attempt, not mid-thought [\[25\]](#ref-25).

the study that changed how i think about it is mathan and koedinger's [\[26\]](#ref-26). two versions of a spreadsheet-formula tutor. one judged each step against an expert model. the other modeled an "intelligent novice", someone who makes reasonable errors then catches and fixes them, and let learners make those errors before guiding them through catching them. the intelligent-novice group ended up with deeper conceptual understanding and better transfer and retention. the authors reject the lazy reading that it's about delay; what changed was the target, finding your own errors became part of the skill. a tool that always points at the error before you notice anything trains you to respond to alerts.

you can see the kinds of feedback side by side on one small bug. ask a model to split a restaurant bill and you get something like this ([`split_bill.py`](/assets/code/prog-learning/split_bill.py), [`test_split_bill.py`](/assets/code/prog-learning/test_split_bill.py)):

```python
def split_bill(total, people):
    share = round(total / people, 2)
    return [share] * people

def test_even_split():
    assert split_bill(90, 3) == [30.0, 30.0, 30.0]

def test_two_people():
    assert split_bill(50, 2) == [25.0, 25.0]
```

the example tests pass. that's feedback, and it says nothing. a property, "the shares add up to the bill, to the cent", handed to hypothesis fails immediately and shrinks to the smallest case it can find:

```text
E       assert 2 == 1
E       Failing test case: test_shares_add_up(
E           cents=1,
E           people=2,
```

one cent split two ways charges each person a cent. split 100 three ways and everyone pays 33.33, a cent short. that counterexample is super precise feedback that still leaves the diagnosis to you. a chatbot that sees the failure and hands back a fixed function is feedback too, the most complete kind, and it removes the part that would've taught you anything about money and floats. same bug, three dials: timing, how precisely it points, and how much of the fix it does for you.

## Measuring what someone knows

"understand recursion" isn't a measurement. you can recognize a correct recursive function, trace one, write one from a template, debug one, explain why it stops, choose recursion for a new problem, or see when it's wrong. separate abilities, and testing one tells you little about the rest.

bloom's mastery learning said learning has to be shown, not assumed from time spent: short units, a diagnostic test at the end marked mastery or nonmastery, and a specific prescription for anyone not there yet [\[27\]](#ref-27). corbett and anderson turned that into a model a tutor can run [\[28\]](#ref-28). in their ACT Programming Tutor each skill has four numbers, the chance it's already known, the chance of learning it each step, and the chances of a lucky guess and a slip, and after every attempt the tutor updates with bayes' rule and calls it mastered at 0.95. the whole thing is a dozen lines ([`bkt.py`](/assets/code/prog-learning/bkt.py), parameters made up for illustration, not fitted):

```python
L0, T, G, S = 0.2, 0.15, 0.2, 0.1   # known at start, learn per step, guess, slip

def trace(answers):
    p, out = L0, []
    for correct in answers:
        if correct:
            p = p * (1 - S) / (p * (1 - S) + (1 - p) * G)
        else:
            p = p * S / (p * S + (1 - p) * (1 - G))
        p = p + (1 - p) * T
        out.append(round(p, 3))
    return out
```

run it on two students. one gets wrong, wrong, right, wrong, then right from attempt five. the other is right every time:

```text
struggles, then gets it    [0.176, 0.172, 0.561, 0.267, 0.678, 0.919, 0.984, 0.997]  mastered at attempt 7
right every time           [0.6, 0.89, 0.977, 0.996, 0.999, 1.0, 1.0, 1.0]  mastered at attempt 3
```

the dip at attempt 4 tells you something a final answer never would. now say the second student's answers came from a chatbot. the model can't tell. it bumps the estimate and by attempt 3 declares mastery of a skill nobody practised.

i think this is the most general problem in the whole topic, and i'd call it evidence inflation. every measure of skill we use is an output that used to be expensive without the skill: a correct answer, a working program, a merged PR, a decent explanation. once something else can make the output cheaply, the output stops saying anything about the person, like a recommendation letter once everyone can get one. METR's devs (below) are the same thing from the inside: they judged their speed by how the work felt, and the feeling pointed the wrong way. most AI-and-skill arguments are really arguments about which outputs still count as evidence of what. prediction #2, easy to check with data schools already have: take-home coding assignments will lose most of their power to predict proctored exam scores, and it'll be worst in the courses that never changed their assignments.

assessment had a blind spot even before AI. you can often tell which method to use because the chapter title already said it. the national research council's review of learning research says knowledge tied too tightly to one context transfers less, and practising across contexts helps [\[29\]](#ref-29). if every binary-search exercise sits under a "binary search" heading, nobody has to notice binary search applies. ask instead for the smallest truck capacity that ships a list of packages, in order, within some number of days, and now you have to see the capacities form a sorted space. that noticing is the part that transfers, and it's still hard to outsource because the question doesn't announce what it is.

performance and retention come apart too. you can do better with a tool and worse once it's gone. at work, where the tool stays, maybe fine. in a course that claims to teach a capability, that's the whole question.

## Where a system's knowledge lives

scale this up from one student to a team and the notional machine turns into something bigger. peter naur argued in 1985 that what a team builds isn't really the code, it's a theory of how the problem and the program match, and it lives in the programmers [\[30\]](#ref-30). his main example: a compiler handed from one group to another with full documentation. the new group's extensions were patches that, in naur's words, "destroyed its power and simplicity", and the original authors saw it instantly. about 10 years later, with the original group gone, the structure had been "made entirely ineffective". a student's notional machine and naur's theory are the same kind of thing at two sizes. neither is in the source, both get built by working with the code, both can be wrong while the code still runs.

the most expensive version of this i know is knight capital [\[31\]](#ref-31). on 1 august 2012 knight deployed new trading code that reused a flag which used to turn on an old function called power peg. they'd stopped using power peg many years earlier, but the code was still there and still callable. seven of the eight servers got the new code. the eighth didn't, so orders carrying the reused flag woke up power peg, which fired off millions of orders in about 45 minutes, and knight lost more than $460 million. the code knew what the flag did. what nobody held anymore was the theory that this flag still meant something on any server running the old version. naur's compiler story at market speed.

parnas saw the architecture side in 1972. using a little program that builds a KWIC index, he argued for splitting a system so each module hides a design decision that's difficult or likely to change [\[32\]](#ref-32). so a module boundary is a bet on the future. conway added the org: organizations "are constrained to produce designs which are copies of the communication structures of these organizations" [\[33\]](#ref-33). so a system's theory is spread across people, module boundaries and team boundaries, and the source is kind of a projection of all that.

where does that knowledge actually sit? the studies agree pretty well. latoza, venolia and deline surveyed devs at microsoft (157 and 187 responses to two surveys) and interviewed 11; 66% said understanding the rationale behind a piece of code was a serious problem, devs went to the code first and then to colleagues, and lots of teams had an informal "team historian" [\[34\]](#ref-34). the same devs said they spent most of their time on other stuff, so i read it as: rationale is expensive because it's hard to get back when you need it, not because you need it all day. ko, deline and venolia watched 17 devs and found 21 kinds of info they went looking for; the ones they most often put off were why code was written a certain way, what it was supposed to do, and what caused some state, because the only source was a colleague who wasn't around [\[35\]](#ref-35). aranda and venolia rebuilt the histories of 10 bugs by interviewing 26 of the people involved and found the repo records gave "incomplete and often erroneous accounts" of what happened [\[36\]](#ref-36).

my two missing posts are a tiny version:

```text
$ git log -S '2095' --format='%h %an %ad %s' --date=short -- _posts/2025-09-2-c-day1.md
7e5f16f Abdulrahman Tamim 2026-01-25 Update date in C programming post
```

the code knows the date. the history knows i changed it and when. the reason is only in my head, which is the easy case since i'm still here to ask.

reading unfamiliar code is rebuilding that theory from the outside. robillard, coelho and murphy watched 5 devs change the autosave feature of jEdit, a 65 KLOC java editor; two succeeded, and those two built a picture of the relevant structure first, planned, and searched by following structural relations, while the others skimmed and guessed (the two were also the more experienced ones, so it describes strategies more than proves them) [\[37\]](#ref-37). sillito, murphy and de volder catalogued the questions people ask while doing this, 44 types from two studies, one with 9 grad students in pairs on the ArgoUML code base and one with 16 industrial devs on their own code, in 4 groups going from finding a starting point to understanding how several parts relate [\[38\]](#ref-38), and a follow-up looked at which of those questions tools actually help with [\[39\]](#ref-39).

tools decide which questions are cheap. green and petre's cognitive dimensions give words for it [\[40\]](#ref-40); their original paper has 13, like visibility (can you see the parts side by side), hidden dependencies (is every dependency shown both ways), viscosity (how much effort one change takes) and premature commitment (deciding before the info exists). "where is this called?" is one keypress anywhere. "why is it like this?" isn't cheap anywhere. jane street built its tooling around making more of those cheap in one place: code review happens inside emacs through Iron, reviewers comment in the code itself, and a 2018 post from them says "code review that takes place in a browser" is "often shallower" [\[41\]](#ref-41). a chat assistant that explains code without being tied to definitions, references, tests and history is the opposite design; it answers the expensive question in the voice of the cheap one. the jekyll answer at the top was exactly that.

dependencies are the same problem pointed outward. depending on a library means depending on someone else's theory of it. mockus, fielding and herbsleb looked at apache and mozilla through source history and bug reports [\[42\]](#ref-42): in apache, 15 of 388 contributors made over 83% of the changes and 88% of the added lines, but only 66% of the fixes to reported problems, and mozilla had bigger core teams of 22 to 35 people with more formal ownership and inspection. so a mature dependency is mostly problem history held by a small group. mcilroy wanted exactly that back in 1968, a components industry with catalogues of routine families parameterized by precision, robustness, generality and time-space trade-offs, because bell labs alone ran about 100 machines from a dozen makers each needing the same support software written again [\[43\]](#ref-43). left-pad showed the cost side [\[44\]](#ref-44). in march 2016 one developer unpublished his kik package and 272 others, left-pad among them, and many thousands of projects broke. the code was tiny. what people were actually depending on was one guy's decision to keep publishing it.

so build-or-depend is really about which theory you hold yourself and which one you rent. code generation adds a third option that didn't exist before: code nobody holds a theory of at all, not the author, not an upstream maintainer, because the author was a model. that's the actually new thing, and the fix is old and boring, write the reason down with the change:

```text
Split bills in integer cents; give the remainder to the first diners

Constraint: shares must sum exactly to the total (found by a property
test; the earlier float version lost or added a cent).
Rejected: rounding each share and adjusting the last one, because the
last diner could end up paying noticeably more than the others.
Assumes: amounts under 10^9 cents; one currency per bill.
Written by: coding agent, reviewed by a human who read the property test.
```

## Code that costs nothing

automatic programming is way older than LLMs. compilers automated translating high-level code into machine instructions, program synthesis tried to derive programs from specs and examples, macros and CASE tools generated code and boilerplate. in 1988 rich and waters listed six myths about it [\[45\]](#ref-45). one: a system can be end-user oriented, general purpose and fully automatic at once; they argue every approach gives up one of the three. another: requirements can be complete. "At best," they write, "requirements are only approximations." the hard part was never turning a clear spec into code, it was getting a spec worth turning into code. `split_bill` is that myth in six lines: code matches the prompt, tests match the code, the one requirement that mattered was never said.

so what does cheap code actually change? the best direct measurement i know is METR's randomized study from 2025: 16 experienced open-source devs, 246 tasks from big open-source repos [\[46\]](#ref-46). with AI allowed, tasks took 19% longer, confidence interval 2% to 39% longer. before the study they expected a 24% speedup, and afterwards they still believed they'd been 20% faster. this is their own chart:

![METR: forecasts and estimates of AI speedup vs the observed result](/assets/img/prog-learning/metr-forecast.png)
_Figure 3. METR's figure: forecasts by economists, ML experts and the developers, the developers' estimate after the study, and the observed change in completion time. From Becker et al. [\[46\]](#ref-46), CC BY 4.0._

and this one tells me more, it's where their time actually went, from labeled screen recordings:

![METR: percentage of time per activity with and without AI](/assets/img/prog-learning/metr-time.png)
_Figure 4. METR's figure: share of time per activity in labeled screen recordings, AI-disallowed vs AI-allowed. From [\[46\]](#ref-46), CC BY 4.0._

with AI, active coding and reading & searching both drop, and new chunks show up for prompting, waiting on AI and reviewing its output. the drop in reading & searching is the one that connects to everything above: that's the activity where you build naur's theory of a codebase, and it's the one that quietly shrank.

don't read the headline as "AI makes devs slower" though. in february 2026 METR changed its design; in the follow-up, 30% to 50% of devs said they'd held back some tasks because they didn't want to do them without AI, which biases a randomized comparison, and the new estimates, 18% faster for returning devs and 4% faster for new ones, have confidence intervals that include no effect [\[47\]](#ref-47). what survives both studies is the perception gap, which is evidence inflation pointed at yourself. DORA's surveys look at whole teams: in the 2024 report each 25% increase in AI adoption was associated with an estimated 1.5% drop in delivery throughput and a 7.2% drop in stability [\[48\]](#ref-48), and in the 2025 survey of about 5,000 people AI adoption went with higher throughput and still lower stability [\[49\]](#ref-49). i trust DORA less than METR, a survey can't tell apart teams that adopted AI because they were struggling from teams that adopted it because they were doing well. but both agree on one thing: writing code faster and delivering working software are different measures and can move in opposite directions.

the deeper reason comes from automation research that has nothing to do with software. lisanne bainbridge wrote in 1983, about industrial process control, that manual skills "deteriorate when they are not used", that the operator gets called in exactly when the automation hits something it can't handle, and that "by taking away the easy parts of his task, automation can make the difficult parts ... more difficult" [\[50\]](#ref-50). endsley and kiris tested a version of it with a car-navigation decision task at five levels of automation; when the automation failed, people who'd worked with more of it had lower situation awareness and took longer to decide, worst under full automation [\[51\]](#ref-51).

put bainbridge next to kapur and it's the same claim in two fields. kapur: the attempt is where the concept forms. bainbridge: routine operation is where the operator's model of the plant forms. in both, the work that looks removable is the work that builds the model. if a coding agent takes the ordinary implementation, what's left for the dev is the unclear requirement, the integration failure, the weird perf cliff, the 3am incident, and those need exactly the model that ordinary implementation used to build on the side. that's my inference, not a measured result in programming.

and the job that's left, supervising generated code, is one people are measurably bad at. parasuraman and manzey's review found that automation bias, following an automated aid's mistakes or missing problems it doesn't flag, "cannot be prevented by training or instructions" [\[52\]](#ref-52). prediction #3: as generation gets cheaper, review becomes the scarce skill, and it's a skill that degrades exactly when the automation is right most of the time. teams that don't deliberately keep some implementation human will watch their reviewers get worse at the one job left.

none of this is anti-tool. risko and gilbert define cognitive offloading as "the use of physical action to alter the information processing requirements of a task so as to reduce cognitive demand" [\[53\]](#ref-53), and everyone does it all day with notes, calculators and docs; it's part of thinking well. the real question is whether you still need the offloaded thing for some other part of the job. you don't need to memorize an API. you do need aliasing, because it shows up in debugging, concurrency and ownership. idk how to draw that line for all of programming, and i suspect my list is mostly a list of what i happened to learn.

students show the pattern early. rahe and maalej watched 37 first-semester students on one comprehension-heavy exercise that was built so the chatbot would mostly fail, only 8.8% of its generated solutions were correct [\[54\]](#ref-54). of the 37, 23 used the bot; 39.1% of their first prompts asked it to just solve it, most eventually asked for a full solution, and the most common pattern was a loop: paste the generated code, watch it fail, ask the bot to fix it. no student asked why their own solution failed. it's one exercise built to beat the model, so it shows how students act when AI help fails, not in general. inside that limit it's investigation getting replaced by retries, the jekyll answer again but done by people. liu, fan and pan's grounded-theory study of a semester of undergrad java, an AI section (24 students) vs a pair-programming section (17), proposes vocabulary for this instead of measuring it: domain mastery vs tool mastery, and two loops, one where the AI scaffolds your thinking and one where it takes the thinking over [\[55\]](#ref-55).

so a course that wants to keep teaching has to decide per operation, not per tool: AI unrestricted for boilerplate setup, hints only the first time you implement a data structure, allowed for review once you have a working solution, banned in a test of unaided tracing, and required in a separate test of how well you supervise generated code. that last one is the skill the industry will actually need and almost nobody teaches it.

## Other people got here first

programming isn't the first field to hand a core skill to a machine, and other fields already have data.

medicine has the cleanest recent one. at four endoscopy centres in poland that started using AI to spot polyps during colonoscopy, researchers compared doctors' normal colonoscopies, the ones done without the AI, in the 3 months before and the 3 months after it arrived [\[56\]](#ref-56). across 1443 patients, the rate at which doctors found adenomas without the AI fell from 28.4% to 22.4%. it's observational, the window is short, and other stuff could've changed in those months, so don't lean on the exact number. but it's the bainbridge pattern in a hospital: people who got used to the machine pointing at the polyp got worse at finding polyps when it wasn't there.

navigation shows the slow version, and the study is open so you can see what they actually tested:

![Dahmani and Bohbot, figure 1: the virtual navigation tasks](/assets/img/prog-learning/gps-fig1.png)
_Figure 5. The virtual navigation tasks used to measure spatial memory. From Dahmani and Bohbot [\[57\]](#ref-57), CC BY 4.0._

dahmani and bohbot measured 50 regular drivers and found the ones with more lifetime GPS use had worse spatial memory when they had to find their way without it [\[57\]](#ref-57). they retested 13 of them three years later, and more GPS use in between went with a steeper decline:

![Dahmani and Bohbot, figure 6: longitudinal decline with GPS use](/assets/img/prog-learning/gps-fig6.png)
_Figure 6. Change in spatial memory over three years as a function of GPS use in that period, 13 retested participants. From [\[57\]](#ref-57), CC BY 4.0._

the part i find most useful: the heavy users didn't say they used GPS because they had a bad sense of direction, which makes "people who were already bad at it used it more" a weaker explanation. the 13-person follow-up is a real limit though.

and then the counterexample, which i think counts for more than the other two. in 1986 hembree and dessart pooled 79 research reports on calculators in school math, back when everyone was sure calculators would ruin arithmetic [\[58\]](#ref-58). except in grade four, calculators used together with normal instruction improved average students' paper-and-pencil skills. the panic was wrong.

put the three next to each other and the difference isn't the tool, it's whether the practice kept going. the endoscopists stopped doing the searching themselves. the GPS drivers stopped building mental maps. the calculator kids kept doing paper arithmetic in class and the calculator took the tedious part around it. same line i drew with kapur and worked examples, just in three fields that have nothing to do with code. so my claim for programming is concrete: AI will deskill exactly the operations people stop practising, and leave alone the ones they keep doing next to it. which operations those are is a choice teams and courses make, mostly without noticing they made one.

## How much code a team can know

software can grow faster than the people maintaining it can take in. meir lehman saw this in big systems that had been evolving for years. one of his laws of software evolution, conservation of familiarity, says the content of successive releases stays statistically invariant, because every release forces the people on the system to get familiar with it again, with effort growing at least quadratically with release size [\[59\]](#ref-59). the next part is mine, not lehman's: growth works against familiarity unless the org pays for learning, restructuring, docs or specialization.

brooks split difficulty into essential and accidental [\[60\]](#ref-60). better tools remove accidental work: syntax, boilerplate, search, repetitive implementation. the essential part is, in his words, "the specification, design, and testing of this conceptual construct, not the labor of representing it", and tools don't touch it. code generation is a really good tool for the labor of representing. so it speeds up exactly the part that was never the bottleneck, and floods the part that was.

put lehman and brooks next to naur and you get a simple picture. code flows in at the generation rate. it turns into something the team actually understands at the assimilation rate. whatever's in between is code nobody holds a theory of, knight's eighth server waiting to happen. doesn't matter how fast either rate is, only which one's bigger. a person can also write code faster than a team can absorb; an agent just makes it easy.

prediction #4: in teams that go heavy on code generation, the first metric to slip won't be incidents or bug counts, it'll be the time until a second engineer can successfully change a piece of code someone else merged. that's the assimilation rate showing up somewhere you can measure, and it should move months before anything breaks. other candidates: how many people can explain a subsystem, how concentrated ownership gets, how often changes get reverted. if code volume goes up while those get worse, the dashboard says productivity and the backlog of not-understood code is quietly growing.

i honestly don't know what a team's assimilation rate is, how to measure it well, or if it can be raised much, and that's the part i'd most like someone to study. the machines can write the code. what i want to know is how much of it we can still understand well enough to change.

## References

1. <span id="ref-1"></span>U.S. Army photograph, "Two women operating ENIAC," c. 1946, public domain, via Wikimedia Commons. <https://commons.wikimedia.org/wiki/File:Two_women_operating_ENIAC_(full_resolution).jpg>
2. <span id="ref-2"></span>H. Abelson and G. J. Sussman with J. Sussman, *Structure and Interpretation of Computer Programs*, 2nd edition, MIT Press, 1996, section 3.3.1, figures 3.16 and 3.17. Licensed CC BY-SA 4.0. <https://mitp-content-server.mit.edu/books/content/sectbyfn/books_pres_0/6515/sicp.zip/full-text/book/book-Z-H-22.html>
3. <span id="ref-3"></span>B. du Boulay, T. O'Shea and J. Monk, "The black box inside the glass box: presenting computing concepts to novices," *International Journal of Man-Machine Studies* 14(3), 1981. <https://doi.org/10.1016/S0020-7373(81)80056-9>
4. <span id="ref-4"></span>B. du Boulay, "Some difficulties of learning to program," *Journal of Educational Computing Research* 2(1), 1986. <https://doi.org/10.2190/3LFX-9RRF-67T8-UVK9>
5. <span id="ref-5"></span>J. Sorva, "Notional machines and introductory programming education," *ACM Transactions on Computing Education* 13(2), 2013. <https://doi.org/10.1145/2483710.2483713>
6. <span id="ref-6"></span>R. Lister et al., "A multi-national study of reading and tracing skills in novice programmers," *Working Group Reports from ITiCSE*, 2004. <https://doi.org/10.1145/1044550.1041673>
7. <span id="ref-7"></span>Progmiscon, "A curated inventory of programming language misconceptions," Lugano Computing Education Research Lab, accessed September 2026. <https://progmiscon.org/>
8. <span id="ref-8"></span>J. Sajaniemi, "An empirical analysis of roles of variables in novice-level procedural programs," *Proc. IEEE Symposia on Human Centric Computing Languages and Environments*, 2002. <https://doi.org/10.1109/HCC.2002.1046340>
9. <span id="ref-9"></span>J. Sajaniemi and M. Kuittinen, "An experiment on using roles of variables in teaching introductory programming," *Computer Science Education* 15(1), 2005. <https://doi.org/10.1080/08993400500056563>
10. <span id="ref-10"></span>M. Kapur, "Productive failure in learning math," *Cognitive Science* 38(5), 2014. <https://doi.org/10.1111/cogs.12107>
11. <span id="ref-11"></span>D. L. Schwartz and J. D. Bransford, "A time for telling," *Cognition and Instruction* 16(4), 1998. <https://doi.org/10.1207/s1532690xci1604_4>
12. <span id="ref-12"></span>S. Kalyuga, P. Ayres, P. Chandler and J. Sweller, "The expertise reversal effect," *Educational Psychologist* 38(1), 2003. <https://doi.org/10.1207/S15326985EP3801_4>
13. <span id="ref-13"></span>M. T. H. Chi, M. Bassok, M. W. Lewis, P. Reimann and R. Glaser, "Self-explanations: how students study and use examples in learning to solve problems," *Cognitive Science* 13(2), 1989. <https://doi.org/10.1207/s15516709cog1302_1>
14. <span id="ref-14"></span>M. T. H. Chi, N. de Leeuw, M.-H. Chiu and C. LaVancher, "Eliciting self-explanations improves understanding," *Cognitive Science* 18(3), 1994. <https://doi.org/10.1207/s15516709cog1803_3>
15. <span id="ref-15"></span>J. J. G. van Merriënboer and M. B. M. de Croock, "Strategies for computer-based programming instruction: program completion vs. program generation," *Journal of Educational Computing Research* 8(3), 1992. <https://doi.org/10.2190/MJDX-9PP4-KFMT-09PM>
16. <span id="ref-16"></span>A. Renkl, R. K. Atkinson and C. S. Große, "How fading worked solution steps works: a cognitive load perspective," *Instructional Science* 32, 2004. <https://doi.org/10.1023/B:TRUC.0000021815.74806.F6>
17. <span id="ref-17"></span>K. R. Koedinger and V. Aleven, "Exploring the assistance dilemma in experiments with Cognitive Tutors," *Educational Psychology Review* 19(3), 2007. <https://doi.org/10.1007/s10648-007-9049-0>
18. <span id="ref-18"></span>D. A. Bligh, *What's the Use of Lectures?*, first U.S. edition, Jossey-Bass, 2000 (first edition 1971). ISBN 0-7879-5162-5.
19. <span id="ref-19"></span>S. Freeman, S. L. Eddy, M. McDonough, M. K. Smith, N. Okoroafor, H. Jordt and M. P. Wenderoth, "Active learning increases student performance in science, engineering, and mathematics," *PNAS* 111(23), 2014. <https://doi.org/10.1073/pnas.1319030111>
20. <span id="ref-20"></span>M. T. H. Chi and R. Wylie, "The ICAP framework: linking cognitive engagement to active learning outcomes," *Educational Psychologist* 49(4), 2014. <https://doi.org/10.1080/00461520.2014.965823>
21. <span id="ref-21"></span>C. H. Crouch and E. Mazur, "Peer Instruction: ten years of experience and results," *American Journal of Physics* 69(9), 2001. <https://doi.org/10.1119/1.1374249>
22. <span id="ref-22"></span>E. Bonawitz, P. Shafto, H. Gweon, N. D. Goodman, E. Spelke and L. Schulz, "The double-edged sword of pedagogy: instruction limits spontaneous exploration and discovery," *Cognition* 120(3), 2011. <https://doi.org/10.1016/j.cognition.2010.10.001>
23. <span id="ref-23"></span>J. A. Kulik and C.-L. C. Kulik, "Timing of feedback and verbal learning," *Review of Educational Research* 58(1), 1988. <https://doi.org/10.3102/00346543058001079>
24. <span id="ref-24"></span>D. L. Butler and P. H. Winne, "Feedback and self-regulated learning: a theoretical synthesis," *Review of Educational Research* 65(3), 1995. <https://doi.org/10.3102/00346543065003245>
25. <span id="ref-25"></span>V. J. Shute, "Focus on formative feedback," *Review of Educational Research* 78(1), 2008. <https://doi.org/10.3102/0034654307313795>
26. <span id="ref-26"></span>S. A. Mathan and K. R. Koedinger, "Fostering the intelligent novice: learning from errors with metacognitive tutoring," *Educational Psychologist* 40(4), 2005. <https://doi.org/10.1207/s15326985ep4004_7>
27. <span id="ref-27"></span>B. S. Bloom, "Learning for mastery," *Evaluation Comment* 1(2), 1968. <https://eric.ed.gov/?id=ED053419>
28. <span id="ref-28"></span>A. T. Corbett and J. R. Anderson, "Knowledge tracing: modeling the acquisition of procedural knowledge," *User Modeling and User-Adapted Interaction* 4, 1995. <https://doi.org/10.1007/BF01099821>
29. <span id="ref-29"></span>National Research Council, *How People Learn: Brain, Mind, Experience, and School*, expanded edition, chapter 3, "Learning and transfer," National Academy Press, 2000. <https://doi.org/10.17226/9853>
30. <span id="ref-30"></span>P. Naur, "Programming as theory building," *Microprocessing and Microprogramming* 15(5), 1985. <https://doi.org/10.1016/0165-6074(85)90032-8>
31. <span id="ref-31"></span>U.S. Securities and Exchange Commission, "In the Matter of Knight Capital Americas LLC," Release No. 34-70694, 16 October 2013. <https://www.sec.gov/litigation/admin/2013/34-70694.pdf>
32. <span id="ref-32"></span>D. L. Parnas, "On the criteria to be used in decomposing systems into modules," *Communications of the ACM* 15(12), 1972. <https://doi.org/10.1145/361598.361623>
33. <span id="ref-33"></span>M. E. Conway, "How do committees invent?," *Datamation*, April 1968. <https://www.melconway.com/Home/Committees_Paper.html>
34. <span id="ref-34"></span>T. D. LaToza, G. Venolia and R. DeLine, "Maintaining mental models: a study of developer work habits," *Proc. ICSE*, 2006. <https://doi.org/10.1145/1134285.1134355>
35. <span id="ref-35"></span>A. J. Ko, R. DeLine and G. Venolia, "Information needs in collocated software development teams," *Proc. ICSE*, 2007. <https://doi.org/10.1109/ICSE.2007.45>
36. <span id="ref-36"></span>J. Aranda and G. Venolia, "The secret life of bugs: going past the errors and omissions in software repositories," *Proc. ICSE*, 2009. <https://doi.org/10.1109/ICSE.2009.5070530>
37. <span id="ref-37"></span>M. P. Robillard, W. Coelho and G. C. Murphy, "How effective developers investigate source code: an exploratory study," *IEEE Transactions on Software Engineering* 30(12), 2004. <https://doi.org/10.1109/TSE.2004.101>
38. <span id="ref-38"></span>J. Sillito, G. C. Murphy and K. De Volder, "Questions programmers ask during software evolution tasks," *Proc. FSE-14*, 2006. <https://doi.org/10.1145/1181775.1181779>
39. <span id="ref-39"></span>J. Sillito, G. C. Murphy and K. De Volder, "Asking and answering questions during a programming change task," *IEEE Transactions on Software Engineering* 34(4), 2008. <https://doi.org/10.1109/TSE.2008.26>
40. <span id="ref-40"></span>T. R. G. Green and M. Petre, "Usability analysis of visual programming environments: a 'cognitive dimensions' framework," *Journal of Visual Languages and Computing* 7(2), 1996. <https://doi.org/10.1006/jvlc.1996.0009>
41. <span id="ref-41"></span>J. Somers, "Putting the I back in IDE: towards a GitHub explorer," Jane Street Tech Blog, 27 March 2018. <https://blog.janestreet.com/putting-the-i-back-in-ide-towards-a-github-explorer/>
42. <span id="ref-42"></span>A. Mockus, R. T. Fielding and J. D. Herbsleb, "Two case studies of open source software development: Apache and Mozilla," *ACM Transactions on Software Engineering and Methodology* 11(3), 2002. <https://doi.org/10.1145/567793.567795>
43. <span id="ref-43"></span>M. D. McIlroy, "Mass produced software components," NATO Software Engineering Conference, Garmisch, 1968. <https://mcilroy.cs.dartmouth.edu/components.txt>
44. <span id="ref-44"></span>npm, Inc., "kik, left-pad, and npm," npm blog, March 2016. <https://blog.npmjs.org/post/141577284765/kik-left-pad-and-npm>
45. <span id="ref-45"></span>C. Rich and R. C. Waters, "Automatic programming: myths and prospects," *IEEE Computer* 21(8), 1988. <https://doi.org/10.1109/2.75>
46. <span id="ref-46"></span>J. Becker et al., "Measuring the impact of early-2025 AI on experienced open-source developer productivity," METR, July 2025. <https://arxiv.org/abs/2507.09089>
47. <span id="ref-47"></span>METR, "We are changing our developer productivity experiment design," METR blog, 24 February 2026. <https://metr.org/blog/2026-02-24-uplift-update/>
48. <span id="ref-48"></span>DORA, *Accelerate State of DevOps Report 2024*, Google Cloud, 2024. <https://dora.dev/research/2024/dora-report/>
49. <span id="ref-49"></span>DORA, *2025 State of AI-assisted Software Development*, Google, 2025. <https://research.google/pubs/dora-2025-state-of-ai-assisted-software-development-report/>
50. <span id="ref-50"></span>L. Bainbridge, "Ironies of automation," *Automatica* 19(6), 1983. <https://doi.org/10.1016/0005-1098(83)90046-8>
51. <span id="ref-51"></span>M. R. Endsley and E. O. Kiris, "The out-of-the-loop performance problem and level of control in automation," *Human Factors* 37(2), 1995. <https://doi.org/10.1518/001872095779064555>
52. <span id="ref-52"></span>R. Parasuraman and D. H. Manzey, "Complacency and bias in human use of automation: an attentional integration," *Human Factors* 52(3), 2010. <https://doi.org/10.1177/0018720810376055>
53. <span id="ref-53"></span>E. F. Risko and S. J. Gilbert, "Cognitive offloading," *Trends in Cognitive Sciences* 20(9), 2016. <https://doi.org/10.1016/j.tics.2016.07.002>
54. <span id="ref-54"></span>C. Rahe and W. Maalej, "How do programming students use generative AI?," *Proceedings of the ACM on Software Engineering* 2(FSE), 2025. <https://doi.org/10.1145/3715762>
55. <span id="ref-55"></span>D. Liu, G. Fan and L. Pan, "Tool, tutor, or crutch?: A grounded theory of cognitive scaffolding and offloading in AI-assisted programming education," *International Journal of STEM Education* 13, article 10, 2026. <https://doi.org/10.1186/s40594-025-00592-w>
56. <span id="ref-56"></span>K. Budzyń et al., "Endoscopist deskilling risk after exposure to artificial intelligence in colonoscopy: a multicentre, observational study," *Lancet Gastroenterology and Hepatology* 10(10), 2025. <https://doi.org/10.1016/S2468-1253(25)00133-5>
57. <span id="ref-57"></span>L. Dahmani and V. D. Bohbot, "Habitual use of GPS negatively impacts spatial memory during self-guided navigation," *Scientific Reports* 10, 2020. <https://doi.org/10.1038/s41598-020-62877-0>
58. <span id="ref-58"></span>R. Hembree and D. J. Dessart, "Effects of hand-held calculators in precollege mathematics education: a meta-analysis," *Journal for Research in Mathematics Education* 17(2), 1986. <https://doi.org/10.2307/749255>
59. <span id="ref-59"></span>M. M. Lehman, "On understanding laws, evolution, and conservation in the large-program life cycle," *Journal of Systems and Software* 1, 1980. <https://doi.org/10.1016/0164-1212(79)90022-0>
60. <span id="ref-60"></span>F. P. Brooks, "No silver bullet: essence and accidents of software engineering," *Proc. IFIP Congress*, 1986, reprinted in *IEEE Computer* 20(4), 1987. Link is the IFIP text. <https://worrydream.com/refs/Brooks-NoSilverBullet.pdf>
