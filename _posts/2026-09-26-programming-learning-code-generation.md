---
title: "Programming, learning, and code generation"
description: "What decades of research on learning to program and on maintaining software say about code that now costs almost nothing to produce."
date: 2026-09-26 12:00:00 +04:00
image:
  path: assets/img/prog-learning/banner.png
  alt: "Box-and-pointer diagram: two names bound to one list, and a faint dashed copy that only exists in a beginner's head"
categories: [Programming]
tags: [Learning, Code Generation, Software Engineering, AI]
math: false
---

Two posts on this blog never showed up on the site. The build log says why:

```text
Skipping: _posts/2025-09-2-c-day1.md has a future date
```

I asked an AI assistant about it and it blamed the filename, the day in `2025-09-2` isn't zero-padded. That's not it. Inside the file the front matter says `date: 2095-09-2`, Jekyll uses that date over the filename, and a post from the future doesn't get published. The other one says `2079`. The assistant never opened the file, it answered from what it could see.

Small thing, but I keep coming back to it, because it's the whole argument of this post in one bug. Producing an answer and knowing what produced it are two different things, and code generation made the first one almost free while leaving the second one exactly as expensive as before. That gap shows up in two places people usually talk about separately: how people learn to program, and how teams keep understanding the systems they own. Both have decades of research behind them, mostly older than language models, and I think that research already tells us most of what to expect. I'll try to show why, and I'll also put down a few predictions of my own that could turn out wrong.

## The picture in your head

Trace this before you run it. What do the two prints show?

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

They look almost the same. A beginner can use both for weeks and not notice they do different things. `reset` points its own local name at a new list and the caller's list doesn't change; `clear` changes the list both names point to. If you think a variable is a box holding a value you'll get at least one of these wrong, and you might still have passed every exercise so far. It's not a syntax problem, it's a wrong picture of the machine.

Du Boulay, O'Shea and Monk called that machine the **notional machine**, "the idealized model of the computer implied by the constructs of the programming language" [\[1\]](#ref-1). Not the processor, not the compiler, but the teaching-level story of what the language does, and every learner builds their own model of it. Later du Boulay listed understanding this machine, and how the real machine relates to it, as one of the main places novices get stuck, with assignment as his example [\[2\]](#ref-2). Sorva argues courses should teach it directly instead of hoping students pick it up [\[3\]](#ref-3). I agree, and I wonder how many working programmers could actually draw theirs.

The research says most beginners can't run their model reliably. In one multi-national study, 941 students at 12 institutions in 7 countries, most near the end of their first semester, answered 12 multiple-choice questions about tracing or completing short programs [\[4\]](#ref-4). Of the 556 who answered all 12, 23% got 4 or less, and the completion questions were the worst. The wrong models are specific enough to catalogue: Progmiscon, from the computing-education group in Lugano, lists 247 misconceptions across 58 concepts in Java, Python, JavaScript and Scratch [\[5\]](#ref-5). And experts carry structure beginners don't even see. Jorma Sajaniemi noticed experienced programmers read variables by what they do, and named the common uses:

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

He pointed out textbooks usually describe two patterns, the counter and the temporary. In his 2002 analysis of 109 novice-level programs, nine roles covered 99% of the variables [\[6\]](#ref-6); the current list has 11. When 91 first-semester students were taught the usual way, with the roles, or with the roles plus an animator, the usual-way group wrote fewer program summaries that connected the code to the problem it solved [\[7\]](#ref-7). A beginner sees `prev` and it's a name. Someone experienced sees a follower and already checks what it holds on the first loop, because followers are always wrong on the first loop.

The claim I want to build the rest of the post on is this. Every tool you use while programming either helps you build this model or stands in for it. A debugger that shows state can do either: you can watch it to check your prediction, or watch it instead of predicting. A visualizer, an autocomplete, a Stack Overflow answer, all the same. The test I use is simple: if the tool vanished tomorrow, what could you still do? An AI assistant is the strongest version of this so far, because it stands in for the model at every level at once. You ask why your recursive function fails, you get a fixed one back, and you keep the exact picture that made the bug. The Jekyll answer at the top was the same thing from the other side: the assistant had no model of the file, only of what files usually look like, and it answered anyway.

## Where learning happens

Being stuck comes in two kinds. Sometimes you're stuck because you need a distinction you don't have yet. Sometimes you're stuck on parts of the task that teach nothing. From inside they feel the same, and most arguments about AI in education are really about telling them apart.

Manu Kapur studied the first kind with tasks like this one. Three players played six games each. Which one is the most consistent? Before reading on, try to make up a measure.

![Points per game for three players](/assets/img/prog-learning/consistency.png)
_Figure 1. Six games each for three invented players. All three average 15 points._

Most people's first ideas look like the ones Kapur's students came up with: the range, how far each game is from the average added up, something like the average distance. It's a few lines to compute them ([`consistency.py`](/assets/code/prog-learning/consistency.py)):

```text
         range  sum dev    MAD     SD
Ana          2        0   0.33   0.58
Bilal       14        0   2.33   4.04
Chen        10        0    3.0   3.42
```

The second idea dies right away, the distances above and below the mean always cancel to zero. The others disagree. Range says Chen is steadier than Bilal, mean absolute deviation says Bilal is steadier than Chen, and standard deviation, which nobody was taught yet, goes with the range. To pick one you have to decide what "consistent" even means; is one crazy game worse than a slow drift? That decision is the concept. The formula is the easy part, and it's also the part a textbook, or a chatbot, gives you first.

In one of Kapur's randomized studies, ninth-graders in India who hadn't learned standard deviation did an hour on a problem like this and an hour of instruction, only the order differed [\[8\]](#ref-8). The struggle-first group found no correct method at all. On the posttest both groups were about the same on procedure, and the struggle-first group did a lot better on concepts and on transfer.

![Posttest scores in Kapur 2014](/assets/img/prog-learning/kapur2014.png)
_Figure 2. Kapur (2014), study 1: posttest scores out of 10 for students who attempted the problem before instruction and for students taught first. Data from [\[8\]](#ref-8)._

The detail I find most telling is in his second study. A group that critiqued other students' failed attempts, instead of making their own, beat direct instruction on concepts only and did worse than the students who made the failures themselves. Seeing mistakes isn't the same as making them. Schwartz and Bransford got something similar with a different design [\[9\]](#ref-9). Students either analyzed contrasting cases from memory experiments or summarized a text, then everyone heard the same lecture. In their third experiment, 36 students, the case group made 43.8% of the possible predictions on a later task, against 14.6% for the summary group and 16.7% for a group that analyzed the cases twice and skipped the lecture. So the cases alone didn't teach it and the lecture alone didn't teach it; the cases prepared distinctions the lecture could land on. Their first experiment shows why nobody notices this in normal teaching: recognition of the concepts was near ceiling, 93%, in both groups, and only the case group used them on a prediction task a week later. Judged on the day, both lessons worked.

The counterweight is just as solid. A novice can burn hours searching without ever seeing the structure an expert would use, which is why worked examples help beginners so reliably. And help that works for novices stops working as people improve: Kalyuga, Ayres, Chandler and Sweller found that "instructional techniques that are highly effective with inexperienced learners can lose their effectiveness and even have negative consequences when used with more experienced learners" [\[10\]](#ref-10). So struggle isn't good and help isn't bad. It depends on which operation the struggle is about.

This is where I think the usual AI debate gets confused. A generated solution looks exactly like a worked example, and worked examples are good for beginners, so what's the problem? Chi and colleagues answered that in 1989 without knowing it [\[11\]](#ref-11). Students studied worked physics examples and then solved problems. The four who later solved best made 15.3 explanations per example, the four who solved worst made 2.8. Same examples. The good students kept asking why a step followed and tied it back to principles. With only 8 students grouped after the fact that's a correlation, but a later experiment got closer to cause [\[12\]](#ref-12): twenty-four eighth-graders read a 101-sentence text on the circulatory system, the 14 prompted to explain each sentence to themselves gained 32% from pretest to posttest, and the 10 who read it twice gained 22% (the prompted ones also studied about twice as long, and assignment wasn't described as random, so time is still a competing explanation). The text doesn't teach. What the reader does with the text teaches. A worked example is something you study; a generated answer is usually something you submit. Same characters on the screen, different operation.

That gives a prediction I'd bet on, and it's cheap to test: students who get AI-generated code and are required to explain every line of it before using it will learn clearly more than students who get the same code without that requirement, and most of the gap between AI users and non-users on later tests will turn out to be about that.

The practical tools for controlling which operation stays with the learner already exist. van Merriënboer and de Croock taught 40 novices a 2.5-hour programming course where one group wrote whole programs and the other completed partial ones, and the completion group used programming templates better on both a construction test and a multiple-choice test [\[13\]](#ref-13). Renkl, Atkinson and Große studied fading, where early examples show every step and later ones leave more to the learner, and found learners learned most about exactly the principles whose steps were faded [\[14\]](#ref-14). A faded sequence on tree recursion could look like this:

```python
# 1. Worked: every step shown
def depth(tree):
    if tree is None:            # an empty tree has depth 0
        return 0
    left = depth(tree.left)     # trust the recursion on each subtree
    right = depth(tree.right)
    return 1 + max(left, right)

# 2. Faded: the recursive case is yours
def size(tree):
    if tree is None:
        return 0
    ...                         # this node, plus both subtrees

# 3. Only the contract
def leaves(tree):
    """Number of nodes with no children."""
```

Koedinger and Aleven call the general problem the assistance dilemma, how to balance giving help and holding it back, and they treat it as open [\[15\]](#ref-15). It helps to stop thinking of help as on or off.

![The range of help between nothing and the answer](/assets/img/prog-learning/help-range.png)
_Figure 3. Help as a range, not a switch. Moving right moves work, and whatever that work would have taught, from the learner to the helper._

An assistant built for teaching would live on the left half of that picture on purpose. It could write the test harness and leave the property to the student, answer "why is this wrong?" with a failing input instead of a fix, or hand over a near-miss like this binary search ([`near_miss.py`](/assets/code/prog-learning/near_miss.py)), which should return the index of the first element at least as large as the target, or the length of the list if there isn't one:

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

`first_at_least([1, 3, 5, 7], 5)` returns 2, and so does searching for 4. Search for 9 and it returns 3 instead of 4, because `hi` starts one position too early and "past the end" can never come back. Finding that input is pure notional-machine work, the skill from the first section.

My honest doubt about all this: nobody tells you in advance which operation carries the concept. In a linked-list exercise I'd guess pointer updates. For some students it's the idea that a node is an object at all, and then even a generated constructor takes the lesson away.

## Teaching, feedback and attention

If the unit of learning is an operation, then teaching is mostly about arranging who performs which operation when, and feedback is about what information arrives at what moment. Both have been studied a lot, and both have results that sound obvious only after you hear them.

Donald Bligh spent a long time comparing lectures with other methods. His conclusion: the lecture "is as effective as any other method for transmitting information, but not more effective", and most lectures do worse than discussion at getting people to think [\[16\]](#ref-16). His advice is blunt: "Use lectures to teach information. Do not rely on them to promote thought, change attitudes, or develop behavioral skills if you can help it." Freeman and colleagues pooled 225 studies of undergraduate science, engineering and math courses and found failure rates of 21.8% with active learning against 33.8% with traditional lecturing [\[17\]](#ref-17). But "active" hides a lot. Chi and Wylie's ICAP framework splits it by what the learner actually does: passive (listening), active (copying, highlighting), constructive (making an inference the material didn't state), interactive (arguing and changing your mind), and predicts learning goes up in that order [\[18\]](#ref-18). In a programming class that's watching the teacher live-code, retyping it, predicting its output before it runs, and debugging it with a partner. Four different activities with the same code on the same projector.

Peer Instruction puts the constructive step inside the lecture. As Crouch and Mazur describe it, a short presentation stops for a conceptual question, students answer alone within 1 to 2 minutes, spend 2 to 4 minutes trying to convince their neighbors, answer again, and only then hear the explanation [\[19\]](#ref-19). In the physics course they report on, the normalized gain on the Force Concept Inventory went from 0.25 with traditional teaching in 1990, with 121 students, to 0.49 in the first Peer Instruction year, with 177. Different years and no 1990 pretest, so read it carefully. The `reset`/`clear` puzzle is a ConcepTest in all but name; every wrong answer to it is a specific wrong notional machine, which is exactly what makes arguing about it useful.

Teaching also steers attention in ways nobody intends. Bonawitz and colleagues gave 85 preschoolers a toy with four hidden functions [\[20\]](#ref-20). When an adult showed one function the way a teacher would, the kids found on average 0.72 of the other three, against 1.15 to 1.3 in the other conditions, and played with it for less time. Preschoolers aren't undergraduates, but the mechanism looks general: people read a teacher's choices as a signal of what matters and stop searching. An AI answer is an extreme case of confident, specific demonstration. My guess is it narrows search the same way, and that's fine when you want the narrowing and bad when the thing worth finding was somewhere else.

Feedback has the same shape. It can arrive while you still remember the decision that caused the error, or after that's gone. Kulik and Kulik reviewed 53 studies [\[21\]](#ref-21): classroom studies with real quizzes mostly favored immediate feedback, experiments on learning test content mostly favored delayed. Butler and Winne put feedback inside a loop of self-regulation where your own monitoring comes first [\[22\]](#ref-22), so outside feedback only helps as much as it changes the next attempt. Shute's review turns this into guidance: immediate feedback for hard tasks and weaker learners, delayed or softer feedback for simple tasks and stronger ones, and feedback after an attempt, not in the middle of thinking [\[23\]](#ref-23).

The study that changed how I think about it is Mathan and Koedinger's [\[24\]](#ref-24). They built two versions of a spreadsheet-formula tutor. One judged each step against an expert model. The other modeled an "intelligent novice", someone who makes reasonable errors and then catches and fixes them, and let learners make those errors before guiding them through catching them. The intelligent-novice group ended up with deeper conceptual understanding and better transfer and retention. The authors reject the easy reading that this is about delay; what changed was the target, because finding your own errors became part of the skill. A tool that always points at the error before you notice anything wrong trains you to respond to alerts.

You can see the different kinds of feedback side by side on one small bug. Ask a model to split a restaurant bill and you get something like this ([`split_bill.py`](/assets/code/prog-learning/split_bill.py), [`test_split_bill.py`](/assets/code/prog-learning/test_split_bill.py)):

```python
def split_bill(total, people):
    share = round(total / people, 2)
    return [share] * people

def test_even_split():
    assert split_bill(90, 3) == [30.0, 30.0, 30.0]

def test_two_people():
    assert split_bill(50, 2) == [25.0, 25.0]
```

The example tests pass, which is feedback, and it says nothing. A property, "the shares add up to the bill, to the cent", given to Hypothesis fails at once and shrinks to the smallest case it can find:

```text
E       assert 2 == 1
E       Failing test case: test_shares_add_up(
E           cents=1,
E           people=2,
```

One cent split between two people charges each a cent. Split 100 between three and each pays 33.33, a cent short. That counterexample is high-resolution feedback that still leaves the diagnosis to you. A chatbot that sees the failure and hands back a fixed function is also feedback, the most complete kind, and it removes the part that would have taught you anything about money and floating point. Same bug, three dials: timing, how precisely it points, and how much of the fix it does for you.

## Measuring what someone knows

"Understand recursion" isn't a measurement. You can recognize a correct recursive function, trace one, write one from a template, debug one, explain why it stops, choose recursion for a new problem, or see when it's wrong. Those are separate abilities, and a test of one tells you little about the rest.

Bloom's mastery learning insisted that learning be shown, not assumed from time spent, with short units ending in diagnostic tests marked mastery or nonmastery and a specific prescription for anyone not there yet [\[25\]](#ref-25). Corbett and Anderson turned that into a model a tutor can run [\[26\]](#ref-26). In their ACT Programming Tutor each skill has four parameters, the chance it's already known, the chance of learning it at each step, and the chances of a lucky guess and a slip, and after every attempt the tutor updates its belief with Bayes' rule and calls the skill mastered at 0.95. The whole model is a dozen lines ([`bkt.py`](/assets/code/prog-learning/bkt.py), parameters illustrative, not fitted):

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

Run it on two students. One gets the first two wrong, one right, another wrong, then everything right from attempt five. The other is right every time.

![Knowledge tracing estimates for two learners](/assets/img/prog-learning/bkt.png)
_Figure 4. Estimated probability that the skill is known, attempt by attempt. The student who struggles reaches the threshold at attempt 7, the one who is always right at attempt 3._

The dip at attempt 4 carries information a final answer never would. Now say the second student's answers came from a chatbot. The model can't tell. It raises its estimate and by attempt 3 declares mastery of a skill nobody practised.

I think this is the most general problem in the whole topic, and I'd call it evidence inflation. Every measure of skill we use is an output that used to be expensive to produce without the skill: a correct answer, a working program, a merged pull request, a well-written explanation. When something else can produce the output cheaply, the output stops carrying information about the person, the same way a recommendation letter means little once everyone can get one. METR's developers, below, are the same pattern from inside: they judged their own speed from how the work felt, and the feeling pointed the wrong way. Most arguments about AI and skill are really arguments about which outputs still count as evidence of which capacities. My prediction, which is easy to check with data schools already have: take-home programming assignments will lose most of their power to predict performance on proctored exams, and the loss will be largest for exactly the courses that never changed their assignments.

Assessment already had a related blind spot before AI. A student can often tell which method to use because the chapter title said it. The National Research Council's review of learning research says knowledge tied too closely to one context transfers less, and teaching across several contexts helps [\[27\]](#ref-27). If every binary-search exercise sits under a heading called "Binary search", nobody has to notice binary search applies. Ask instead for the smallest truck capacity that ships a list of packages, in order, within a given number of days, and the student has to see that the capacities form a sorted space. That noticing is the part that transfers, and it's the part that's still hard to outsource because the question doesn't announce what it is.

Performance and retention come apart too. You can do better with a tool and worse once it's gone. At work, where the tool stays, maybe that's fine. In a course that claims to teach a capability, it's the whole question.

## Where a system's knowledge lives

Scale all of this up from one student to a team and the notional machine becomes something bigger. Peter Naur argued in 1985 that what a team builds isn't really the code, it's a theory of how the problem and the program match, and the theory lives in the programmers [\[28\]](#ref-28). His main example is a compiler handed from one group to another with full documentation. The new group's extensions were patches that, in Naur's words, "destroyed its power and simplicity", and the original authors saw it immediately. About 10 years later, with the original group gone, the structure had been "made entirely ineffective". A student's notional machine and Naur's theory are the same kind of object at two sizes. Neither is in the source, both are built by working with the code, and both can be wrong while the code still runs.

The most expensive version of this I know of is Knight Capital [\[29\]](#ref-29). On 1 August 2012 Knight deployed new trading code that reused a flag which had once turned on an old function called Power Peg. Knight had stopped using Power Peg many years earlier, but the code was still there and still callable. Seven of the eight servers got the new code. The eighth didn't, so orders carrying the reused flag woke up Power Peg, which sent millions of orders in about 45 minutes, and Knight lost more than $460 million. The code knew what the flag did. What nobody held anymore was the theory: that this particular flag still meant something on any server running the old version. That's Naur's compiler story at market speed.

Parnas saw the architectural side in 1972. Using a small program that builds a KWIC index, he argued for splitting a system so each module hides a design decision that is difficult or likely to change [\[30\]](#ref-30). So a module boundary is a bet about the future. Conway added the organization: organizations "are constrained to produce designs which are copies of the communication structures of these organizations" [\[31\]](#ref-31). So the theory of a system is spread across people, the boundaries between their modules, and the boundaries between their teams, and the source code is a projection of all that.

Where does that knowledge actually sit? The studies are pretty consistent. LaToza, Venolia and DeLine surveyed developers at Microsoft (157 and 187 responses to two surveys) and interviewed 11; 66% said understanding the rationale behind a piece of code was a serious problem, developers went to the code first and then to colleagues, and many teams had an informal "team historian" [\[32\]](#ref-32). The same developers said they spent most of their time on other things, so I read it as: rationale is expensive because it's hard to get back when you need it, not because you need it all day. Ko, DeLine and Venolia watched 17 developers and found 21 kinds of information they went looking for; the ones most often put off were why code was written a certain way, what it was supposed to do, and what caused some state, because the only source was a colleague who wasn't available [\[33\]](#ref-33). Aranda and Venolia reconstructed the histories of 10 bugs by interviewing 26 of the people involved and found the repository records gave "incomplete and often erroneous accounts" of what happened [\[34\]](#ref-34).

![Where knowledge about a line of code is kept](/assets/img/prog-learning/knowledge-location.png)
_Figure 5. What a line does is in the code, who changed it and when is in the history, and why is usually only in someone's memory._

My two missing posts are a tiny example of the same layering:

```text
$ git log -S '2095' --format='%h %an %ad %s' --date=short -- _posts/2025-09-2-c-day1.md
7e5f16f Abdulrahman Tamim 2026-01-25 Update date in C programming post
```

The code knows what the date is. The history knows I changed it, and when. The reason is only in my head, which is the easy case, since I'm still here to ask.

Reading unfamiliar code is the act of rebuilding that theory from the outside. Robillard, Coelho and Murphy watched 5 developers change the autosave feature of jEdit, a 65 KLOC Java editor; two succeeded, and those two built a picture of the relevant structure first, planned, and searched by following structural relations, while the others skimmed and guessed (the two were also the more experienced, so this describes strategies more than it proves them) [\[35\]](#ref-35). Sillito, Murphy and De Volder catalogued the questions people ask while doing this, 44 types from two studies, one with 9 graduate students in pairs on the ArgoUML code base and one with 16 industrial programmers on their own code, in 4 groups going from finding a starting point to understanding how several regions relate [\[36\]](#ref-36), and a follow-up looked at which of those questions tools actually help answer [\[37\]](#ref-37).

Tools decide which of those questions are cheap. Green and Petre's cognitive dimensions give words for it [\[38\]](#ref-38); their original paper lists 13, including visibility (can you see the parts side by side), hidden dependencies (is every dependency shown in both directions), viscosity (how much effort one change takes) and premature commitment (deciding before the information exists). "Where is this called?" is one keypress in any editor. "Why is it like this?" isn't cheap anywhere. Jane Street built its tooling around making more of these questions cheap in one place: its code review runs inside Emacs through Iron, reviewers comment in the code itself, and a 2018 post from the company argues that "code review that takes place in a browser" is "often shallower" [\[39\]](#ref-39). A chat assistant that explains code without being tied to definitions, references, tests and history is the opposite design, it answers the expensive question in the voice of the cheap one. The Jekyll answer at the top was exactly that.

Dependencies are the same problem pointed outward. When you depend on a library you depend on someone else's theory of it. Mockus, Fielding and Herbsleb looked at Apache and Mozilla through source history and problem reports [\[40\]](#ref-40): in Apache, 15 of 388 code contributors made over 83% of the changes and 88% of the added lines, but only 66% of the fixes to reported problems, and Mozilla had bigger core teams of 22 to 35 people with more formal ownership and inspection. So a mature dependency is mostly accumulated problem history held by a small group. McIlroy wanted exactly that in 1968, a components industry with catalogues of routine families parameterized by precision, robustness, generality and time-space trade-offs, because Bell Labs alone ran about 100 machines from a dozen makers each needing the same support software written again [\[41\]](#ref-41). The left-pad incident showed the cost side of that trade [\[42\]](#ref-42). In March 2016 one developer unpublished his kik package and 272 others, left-pad among them, and many thousands of projects broke. The code was tiny. What people had actually been depending on was one person's decision to keep publishing it.

So the build-or-depend question is really about which theory you want to hold yourself and which you're willing to rent. Code generation adds a third option that didn't exist before: code that nobody holds a theory of at all, not the author, not a maintainer upstream, because the author was a model. That's the new thing, and it's why I think the practical answer is old and boring, write the reason down with the change:

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

Automatic programming is older than language models. Compilers automated translating higher-level programs into machine instructions, program synthesis tried to derive programs from specifications and examples, macros and CASE tools generated code and boilerplate. In 1988 Rich and Waters listed six myths about it [\[43\]](#ref-43). One is that a system can be end-user oriented, general purpose and fully automatic at once; they argue every approach gives up one of the three. Another is that requirements can be complete: "At best," they write, "requirements are only approximations." The hard part was never translating a clear specification into code, it was getting a specification worth translating. The `split_bill` example is that myth in six lines: the code matches the prompt, the tests match the code, and the one requirement that mattered was never stated.

So what does cheap code actually change? The best direct measurement I know is METR's randomized study from 2025: 16 experienced open-source developers, 246 tasks from large open-source repositories [\[44\]](#ref-44). With AI tools allowed, tasks took 19% longer, with a confidence interval from 2% to 39% longer. Before the study they expected a 24% speedup, and afterwards they still believed they'd been 20% faster.

![METR 2025 forecasts versus measurement](/assets/img/prog-learning/metr2025.png)
_Figure 6. Change in task completion time with AI in METR's 2025 study: what economists, ML experts and the developers predicted, what the developers believed afterwards, and what was measured, with its confidence interval. Data from [\[44\]](#ref-44)._

That shouldn't be read as "AI makes developers slower". In February 2026 METR changed its design; in the follow-up, 30% to 50% of developers said they'd held back some tasks because they didn't want to do them without AI, which biases a randomized comparison, and the new estimates, 18% faster for returning developers and 4% faster for new ones, have confidence intervals that include no effect [\[45\]](#ref-45). What survives both studies is the perception gap, and it's the evidence-inflation problem from earlier pointed at yourself. DORA's surveys look at whole teams: in the 2024 report, each 25% increase in AI adoption was associated with an estimated 1.5% drop in delivery throughput and a 7.2% drop in delivery stability [\[46\]](#ref-46), and in the 2025 survey of about 5,000 respondents AI adoption was associated with higher throughput and still with lower stability [\[47\]](#ref-47). I trust DORA less than METR, because a survey can't separate teams that adopted AI because they were struggling from teams that adopted it because they were doing well. But both point the same way on one thing: writing code faster and delivering working software are different measures and can move in opposite directions.

The deeper reason goes back to automation research that has nothing to do with software. Lisanne Bainbridge wrote in 1983, about industrial process control, that manual skills "deteriorate when they are not used", that the operator is called in exactly when the automation meets something it can't handle, and that "by taking away the easy parts of his task, automation can make the difficult parts ... more difficult" [\[48\]](#ref-48). Endsley and Kiris tested a version of it with a car-navigation decision task at five levels of automation; when the automation failed, people who had worked with more of it had lower situation awareness and took longer to decide, worst under full automation [\[49\]](#ref-49).

![Schematic of Bainbridge's irony](/assets/img/prog-learning/automation-irony.png)
_Figure 7. A schematic of Bainbridge's argument, not data. Before automation, the frequent routine work is also practice for the rare failure. After it, the rare failure is the only practice left._

Put Bainbridge next to Kapur and they're the same claim in two fields. Kapur says the attempt is where the concept forms. Bainbridge says routine operation is where the operator's model of the plant forms. In both, the work that looks removable is the work that builds the model. If a coding agent takes the ordinary implementation, what's left for the programmer is the unclear requirement, the integration failure, the weird performance cliff, the incident at 3 a.m., and those need exactly the model that ordinary implementation used to build as a side effect. That's my inference, not a measured result in programming.

And the job that's left, supervising generated code, is one people are measurably bad at. Parasuraman and Manzey's review found that automation bias, following an automated aid's mistakes or missing problems it doesn't flag, "cannot be prevented by training or instructions" [\[50\]](#ref-50). My second prediction: as generation gets cheaper, review becomes the scarce skill, and it's a skill that degrades precisely when the automation is right most of the time. Teams that don't deliberately keep some implementation work human will find their reviewers getting worse at the one job left to them.

None of this is an argument against tools. Risko and Gilbert define cognitive offloading as "the use of physical action to alter the information processing requirements of a task so as to reduce cognitive demand" [\[51\]](#ref-51), and people do it constantly with notes, calculators and documentation; it's part of thinking well. The real question is whether you still need the offloaded capacity for some other part of the job. You don't need to memorize an API. You do need aliasing, because it shows up in debugging, concurrency and ownership. I don't know how to draw that line for all of programming, and I suspect my own list is mostly a list of what I happened to learn.

Students show the same pattern early. Rahe and Maalej watched 37 first-semester students on one comprehension-heavy exercise that was built so the chatbot would mostly fail, only 8.8% of its generated solutions were correct [\[52\]](#ref-52). Of the 37, 23 used the bot; 39.1% of their first prompts asked it to just solve the task, most eventually asked for a full solution, and the most common pattern was a loop: paste the generated code, watch it fail, ask the bot to fix it. No student asked why their own solution failed. It's one exercise designed to beat the model, so it shows how students act when AI help fails, not in general. Inside that limit, it's investigation getting replaced by retries, the Jekyll answer again but done by people. Liu, Fan and Pan's grounded-theory study of a semester of undergraduate Java, comparing a section using AI (24 students) with a pair-programming section (17), proposes vocabulary for this rather than measuring it: a split between mastery of the domain and mastery of the tool, and two loops, one where the AI scaffolds the student's thinking and one where it takes the thinking over [\[53\]](#ref-53).

So a course that wants to keep teaching has to decide per operation, not per tool: AI unrestricted for boilerplate setup, limited to hints the first time a student implements a data structure, allowed for review once the student has a working solution, banned in a test of unaided tracing, and required in a separate test of how well the student supervises generated code. That last one is the skill the industry will actually need, and almost nobody teaches it.

## How much code a team can know

Software can grow faster than the people maintaining it can take in. Meir Lehman saw this in large systems that had been evolving for years. One of his laws of software evolution, conservation of familiarity, says the content of successive releases stays statistically invariant, because every release forces the people working on the system to get familiar with it again, with effort growing at least quadratically with the size of the release [\[54\]](#ref-54). The next part is mine, not Lehman's: growth works against familiarity unless the organization pays for learning, restructuring, documentation or specialization.

Brooks separated essential from accidental difficulty [\[55\]](#ref-55). Better tools remove accidental work: syntax, boilerplate, search, repetitive implementation. The essential difficulty is, in his words, "the specification, design, and testing of this conceptual construct, not the labor of representing it", and tools don't remove that. Code generation is a very good tool for the labor of representing. Which means it speeds up exactly the part that was never the bottleneck, and floods the part that was.

Put Lehman and Brooks together with Naur and you get a simple picture.

![Generation and assimilation as a bathtub](/assets/img/prog-learning/bathtub.png)
_Figure 8. The level in the tub is code nobody on the team understands yet. It rises whenever generation outpaces assimilation, however fast either one is._

Code flows in at the generation rate. It drains out, becomes something the team actually understands, at the assimilation rate. The level in the tub is code nobody holds a theory of, Knight's eighth server waiting to happen. It doesn't matter how fast either rate is, only which one is bigger. A person can also write code faster than a team can absorb it; an agent just makes that easy.

My third prediction: in teams that adopt heavy code generation, the first metric to get worse won't be incidents or bug counts, it'll be the time until a second engineer can successfully change a piece of code someone else merged. That's the assimilation rate showing up in a place you can measure, and it should move months before anything breaks. Other candidates are the number of people who can explain a subsystem, how concentrated ownership gets, and how often changes are reverted. If code volume goes up while those get worse, the dashboard will show productivity and the tub will be filling.

I don't actually know what a team's assimilation rate is, how to measure it well, or whether it can be raised much, and that's the part of this I'd most like someone to study. The machines can write the code. What I want to know is how much of it we can still understand well enough to change.

## References

1. <span id="ref-1"></span>B. du Boulay, T. O'Shea and J. Monk, "The black box inside the glass box: presenting computing concepts to novices," *International Journal of Man-Machine Studies* 14(3), 1981. <https://doi.org/10.1016/S0020-7373(81)80056-9>
2. <span id="ref-2"></span>B. du Boulay, "Some difficulties of learning to program," *Journal of Educational Computing Research* 2(1), 1986. <https://doi.org/10.2190/3LFX-9RRF-67T8-UVK9>
3. <span id="ref-3"></span>J. Sorva, "Notional machines and introductory programming education," *ACM Transactions on Computing Education* 13(2), 2013. <https://doi.org/10.1145/2483710.2483713>
4. <span id="ref-4"></span>R. Lister et al., "A multi-national study of reading and tracing skills in novice programmers," *Working Group Reports from ITiCSE*, 2004. <https://doi.org/10.1145/1044550.1041673>
5. <span id="ref-5"></span>Progmiscon, "A curated inventory of programming language misconceptions," Lugano Computing Education Research Lab, accessed September 2026. <https://progmiscon.org/>
6. <span id="ref-6"></span>J. Sajaniemi, "An empirical analysis of roles of variables in novice-level procedural programs," *Proc. IEEE Symposia on Human Centric Computing Languages and Environments*, 2002. <https://doi.org/10.1109/HCC.2002.1046340>
7. <span id="ref-7"></span>J. Sajaniemi and M. Kuittinen, "An experiment on using roles of variables in teaching introductory programming," *Computer Science Education* 15(1), 2005. <https://doi.org/10.1080/08993400500056563>
8. <span id="ref-8"></span>M. Kapur, "Productive failure in learning math," *Cognitive Science* 38(5), 2014. <https://doi.org/10.1111/cogs.12107>
9. <span id="ref-9"></span>D. L. Schwartz and J. D. Bransford, "A time for telling," *Cognition and Instruction* 16(4), 1998. <https://doi.org/10.1207/s1532690xci1604_4>
10. <span id="ref-10"></span>S. Kalyuga, P. Ayres, P. Chandler and J. Sweller, "The expertise reversal effect," *Educational Psychologist* 38(1), 2003. <https://doi.org/10.1207/S15326985EP3801_4>
11. <span id="ref-11"></span>M. T. H. Chi, M. Bassok, M. W. Lewis, P. Reimann and R. Glaser, "Self-explanations: how students study and use examples in learning to solve problems," *Cognitive Science* 13(2), 1989. <https://doi.org/10.1207/s15516709cog1302_1>
12. <span id="ref-12"></span>M. T. H. Chi, N. de Leeuw, M.-H. Chiu and C. LaVancher, "Eliciting self-explanations improves understanding," *Cognitive Science* 18(3), 1994. <https://doi.org/10.1207/s15516709cog1803_3>
13. <span id="ref-13"></span>J. J. G. van Merriënboer and M. B. M. de Croock, "Strategies for computer-based programming instruction: program completion vs. program generation," *Journal of Educational Computing Research* 8(3), 1992. <https://doi.org/10.2190/MJDX-9PP4-KFMT-09PM>
14. <span id="ref-14"></span>A. Renkl, R. K. Atkinson and C. S. Große, "How fading worked solution steps works: a cognitive load perspective," *Instructional Science* 32, 2004. <https://doi.org/10.1023/B:TRUC.0000021815.74806.F6>
15. <span id="ref-15"></span>K. R. Koedinger and V. Aleven, "Exploring the assistance dilemma in experiments with Cognitive Tutors," *Educational Psychology Review* 19(3), 2007. <https://doi.org/10.1007/s10648-007-9049-0>
16. <span id="ref-16"></span>D. A. Bligh, *What's the Use of Lectures?*, first U.S. edition, Jossey-Bass, 2000 (first edition 1971). ISBN 0-7879-5162-5.
17. <span id="ref-17"></span>S. Freeman, S. L. Eddy, M. McDonough, M. K. Smith, N. Okoroafor, H. Jordt and M. P. Wenderoth, "Active learning increases student performance in science, engineering, and mathematics," *PNAS* 111(23), 2014. <https://doi.org/10.1073/pnas.1319030111>
18. <span id="ref-18"></span>M. T. H. Chi and R. Wylie, "The ICAP framework: linking cognitive engagement to active learning outcomes," *Educational Psychologist* 49(4), 2014. <https://doi.org/10.1080/00461520.2014.965823>
19. <span id="ref-19"></span>C. H. Crouch and E. Mazur, "Peer Instruction: ten years of experience and results," *American Journal of Physics* 69(9), 2001. <https://doi.org/10.1119/1.1374249>
20. <span id="ref-20"></span>E. Bonawitz, P. Shafto, H. Gweon, N. D. Goodman, E. Spelke and L. Schulz, "The double-edged sword of pedagogy: instruction limits spontaneous exploration and discovery," *Cognition* 120(3), 2011. <https://doi.org/10.1016/j.cognition.2010.10.001>
21. <span id="ref-21"></span>J. A. Kulik and C.-L. C. Kulik, "Timing of feedback and verbal learning," *Review of Educational Research* 58(1), 1988. <https://doi.org/10.3102/00346543058001079>
22. <span id="ref-22"></span>D. L. Butler and P. H. Winne, "Feedback and self-regulated learning: a theoretical synthesis," *Review of Educational Research* 65(3), 1995. <https://doi.org/10.3102/00346543065003245>
23. <span id="ref-23"></span>V. J. Shute, "Focus on formative feedback," *Review of Educational Research* 78(1), 2008. <https://doi.org/10.3102/0034654307313795>
24. <span id="ref-24"></span>S. A. Mathan and K. R. Koedinger, "Fostering the intelligent novice: learning from errors with metacognitive tutoring," *Educational Psychologist* 40(4), 2005. <https://doi.org/10.1207/s15326985ep4004_7>
25. <span id="ref-25"></span>B. S. Bloom, "Learning for mastery," *Evaluation Comment* 1(2), 1968. <https://eric.ed.gov/?id=ED053419>
26. <span id="ref-26"></span>A. T. Corbett and J. R. Anderson, "Knowledge tracing: modeling the acquisition of procedural knowledge," *User Modeling and User-Adapted Interaction* 4, 1995. <https://doi.org/10.1007/BF01099821>
27. <span id="ref-27"></span>National Research Council, *How People Learn: Brain, Mind, Experience, and School*, expanded edition, chapter 3, "Learning and transfer," National Academy Press, 2000. <https://doi.org/10.17226/9853>
28. <span id="ref-28"></span>P. Naur, "Programming as theory building," *Microprocessing and Microprogramming* 15(5), 1985. <https://doi.org/10.1016/0165-6074(85)90032-8>
29. <span id="ref-29"></span>U.S. Securities and Exchange Commission, "In the Matter of Knight Capital Americas LLC," Release No. 34-70694, 16 October 2013. <https://www.sec.gov/litigation/admin/2013/34-70694.pdf>
30. <span id="ref-30"></span>D. L. Parnas, "On the criteria to be used in decomposing systems into modules," *Communications of the ACM* 15(12), 1972. <https://doi.org/10.1145/361598.361623>
31. <span id="ref-31"></span>M. E. Conway, "How do committees invent?," *Datamation*, April 1968. <https://www.melconway.com/Home/Committees_Paper.html>
32. <span id="ref-32"></span>T. D. LaToza, G. Venolia and R. DeLine, "Maintaining mental models: a study of developer work habits," *Proc. ICSE*, 2006. <https://doi.org/10.1145/1134285.1134355>
33. <span id="ref-33"></span>A. J. Ko, R. DeLine and G. Venolia, "Information needs in collocated software development teams," *Proc. ICSE*, 2007. <https://doi.org/10.1109/ICSE.2007.45>
34. <span id="ref-34"></span>J. Aranda and G. Venolia, "The secret life of bugs: going past the errors and omissions in software repositories," *Proc. ICSE*, 2009. <https://doi.org/10.1109/ICSE.2009.5070530>
35. <span id="ref-35"></span>M. P. Robillard, W. Coelho and G. C. Murphy, "How effective developers investigate source code: an exploratory study," *IEEE Transactions on Software Engineering* 30(12), 2004. <https://doi.org/10.1109/TSE.2004.101>
36. <span id="ref-36"></span>J. Sillito, G. C. Murphy and K. De Volder, "Questions programmers ask during software evolution tasks," *Proc. FSE-14*, 2006. <https://doi.org/10.1145/1181775.1181779>
37. <span id="ref-37"></span>J. Sillito, G. C. Murphy and K. De Volder, "Asking and answering questions during a programming change task," *IEEE Transactions on Software Engineering* 34(4), 2008. <https://doi.org/10.1109/TSE.2008.26>
38. <span id="ref-38"></span>T. R. G. Green and M. Petre, "Usability analysis of visual programming environments: a 'cognitive dimensions' framework," *Journal of Visual Languages and Computing* 7(2), 1996. <https://doi.org/10.1006/jvlc.1996.0009>
39. <span id="ref-39"></span>J. Somers, "Putting the I back in IDE: towards a GitHub explorer," Jane Street Tech Blog, 27 March 2018. <https://blog.janestreet.com/putting-the-i-back-in-ide-towards-a-github-explorer/>
40. <span id="ref-40"></span>A. Mockus, R. T. Fielding and J. D. Herbsleb, "Two case studies of open source software development: Apache and Mozilla," *ACM Transactions on Software Engineering and Methodology* 11(3), 2002. <https://doi.org/10.1145/567793.567795>
41. <span id="ref-41"></span>M. D. McIlroy, "Mass produced software components," NATO Software Engineering Conference, Garmisch, 1968. <https://mcilroy.cs.dartmouth.edu/components.txt>
42. <span id="ref-42"></span>npm, Inc., "kik, left-pad, and npm," npm blog, March 2016. <https://blog.npmjs.org/post/141577284765/kik-left-pad-and-npm>
43. <span id="ref-43"></span>C. Rich and R. C. Waters, "Automatic programming: myths and prospects," *IEEE Computer* 21(8), 1988. <https://doi.org/10.1109/2.75>
44. <span id="ref-44"></span>J. Becker et al., "Measuring the impact of early-2025 AI on experienced open-source developer productivity," METR, July 2025. <https://arxiv.org/abs/2507.09089>
45. <span id="ref-45"></span>METR, "We are changing our developer productivity experiment design," METR blog, 24 February 2026. <https://metr.org/blog/2026-02-24-uplift-update/>
46. <span id="ref-46"></span>DORA, *Accelerate State of DevOps Report 2024*, Google Cloud, 2024. <https://dora.dev/research/2024/dora-report/>
47. <span id="ref-47"></span>DORA, *2025 State of AI-assisted Software Development*, Google, 2025. <https://research.google/pubs/dora-2025-state-of-ai-assisted-software-development-report/>
48. <span id="ref-48"></span>L. Bainbridge, "Ironies of automation," *Automatica* 19(6), 1983. <https://doi.org/10.1016/0005-1098(83)90046-8>
49. <span id="ref-49"></span>M. R. Endsley and E. O. Kiris, "The out-of-the-loop performance problem and level of control in automation," *Human Factors* 37(2), 1995. <https://doi.org/10.1518/001872095779064555>
50. <span id="ref-50"></span>R. Parasuraman and D. H. Manzey, "Complacency and bias in human use of automation: an attentional integration," *Human Factors* 52(3), 2010. <https://doi.org/10.1177/0018720810376055>
51. <span id="ref-51"></span>E. F. Risko and S. J. Gilbert, "Cognitive offloading," *Trends in Cognitive Sciences* 20(9), 2016. <https://doi.org/10.1016/j.tics.2016.07.002>
52. <span id="ref-52"></span>C. Rahe and W. Maalej, "How do programming students use generative AI?," *Proceedings of the ACM on Software Engineering* 2(FSE), 2025. <https://doi.org/10.1145/3715762>
53. <span id="ref-53"></span>D. Liu, G. Fan and L. Pan, "Tool, tutor, or crutch?: A grounded theory of cognitive scaffolding and offloading in AI-assisted programming education," *International Journal of STEM Education* 13, article 10, 2026. <https://doi.org/10.1186/s40594-025-00592-w>
54. <span id="ref-54"></span>M. M. Lehman, "On understanding laws, evolution, and conservation in the large-program life cycle," *Journal of Systems and Software* 1, 1980. <https://doi.org/10.1016/0164-1212(79)90022-0>
55. <span id="ref-55"></span>F. P. Brooks, "No silver bullet: essence and accidents of software engineering," *Proc. IFIP Congress*, 1986, reprinted in *IEEE Computer* 20(4), 1987. Link is the IFIP text. <https://worrydream.com/refs/Brooks-NoSilverBullet.pdf>
