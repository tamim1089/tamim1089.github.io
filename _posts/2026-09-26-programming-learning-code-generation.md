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

Small thing, but it's the thing I keep thinking about. You can get an answer now without the knowledge that would make the answer reliable, and code generation made answers basically free. So what changes? There are two old research areas that already asked this in other forms. Education research asks which parts of a task a learner has to do themselves to actually learn from it. Software-maintenance research asks how much of a system the people maintaining it can know well enough to change it. Most of that work is older than language models, some of it by decades, and I think it's worth reading before deciding anything about them.

## What beginners think the computer is doing

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

They look almost the same. A beginner can use both for weeks and not notice they do different things. `reset` points its own local name at a new list and the caller's list doesn't change; `clear` changes the list that both names point to. If you think a variable is a box holding a value you'll get at least one of these wrong, and you might still have passed every exercise until now. So it's not a syntax problem, it's a wrong picture of the machine.

Du Boulay, O'Shea and Monk called that machine the **notional machine**, "the idealized model of the computer implied by the constructs of the programming language" [\[1\]](#ref-1). It's not the processor and not the compiler, it's the teaching-level story of what the language does, and every learner builds their own model of it, often a wrong one. Later du Boulay listed understanding this machine, and how the real machine relates to it, as one of the main places novices get stuck, and he used assignment as his example [\[2\]](#ref-2). Sorva's review says courses should teach the notional machine directly instead of hoping students pick it up [\[3\]](#ref-3). I agree with him, and I also wonder how many experienced programmers could draw theirs if you asked.

Tracing code by hand is the most direct test of that model, and beginners are bad at it. In one multi-national study, 941 students at 12 institutions in 7 countries, most near the end of their first semester, answered 12 multiple-choice questions about tracing or completing short programs [\[4\]](#ref-4). Of the 556 who answered all 12, 23% got 4 or less. The completion questions were the worst. If someone can't say what a short program does, asking them to design a bigger one stacks everything at once: the language, how to split the task, data structures, control flow, debugging.

The wrong models are specific enough that people catalogue them. Progmiscon, from the computing-education group in Lugano, lists 247 misconceptions across 58 concepts in Java, Python, JavaScript and Scratch [\[5\]](#ref-5).

Experts see structure beginners don't. Jorma Sajaniemi noticed experienced programmers read variables by what they do, and he named the common uses. One small function has most of them:

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

He pointed out textbooks usually describe two patterns, the counter and the temporary. In his 2002 analysis of 109 novice-level programs, nine roles covered 99% of the variables [\[6\]](#ref-6); the current list has 11. When 91 first-semester students were taught the usual way, with the roles, or with the roles plus an animator, the usual-way group wrote fewer program summaries that connected the code to the problem it solved [\[7\]](#ref-7). A beginner sees `prev` and it's just a name. Someone experienced sees a follower and already checks what it holds on the first loop.

So the real problem is representation: what model of execution the learner has, what the environment shows them, and what they have to keep in their head alone. A debugger shows state, a visualizer draws the stack. Each of these can show a mechanism that the learner then learns, or it can hand over the next value and the learner never builds the model. An AI assistant is the same thing but much bigger. You ask why your recursive function fails, you get a fixed one back, you have working code, and maybe the exact same wrong picture that made the bug.

## Failure before instruction

Being stuck comes in two kinds. Sometimes you're stuck because you need a distinction you don't have yet. Sometimes you're stuck on parts of the task that teach nothing. From inside they feel the same, which is annoying.

Manu Kapur studied the first kind with tasks like this one. Three players played six games each. Which one is the most consistent? Before reading on, try to make up a measure, some number you can compute for each player.

![Points per game for three players](/assets/img/prog-learning/consistency.png)
_Figure 1. Six games each for three invented players. All three average 15 points._

Most people's first ideas are like the ones Kapur's students came up with. The range, highest minus lowest. How far each game is from the average, added up. Something like the average distance. It's a few lines to compute them ([`consistency.py`](/assets/code/prog-learning/consistency.py)):

```text
         range  sum dev    MAD     SD
Ana          2        0   0.33   0.58
Bilal       14        0   2.33   4.04
Chen        10        0    3.0   3.42
```

The second idea dies right away, the distances above and below the mean always cancel to zero. The others don't agree with each other. Range says Chen is steadier than Bilal. Mean absolute deviation says Bilal is steadier than Chen. Standard deviation, which nobody in the room was taught yet, goes with the range here. To pick one you have to decide what "consistent" even means; is one crazy game worse than a slow drift? That decision is the concept. The formula is the easy part.

In one of Kapur's randomized studies, ninth-graders in India who hadn't learned standard deviation did an hour on a problem like this and an hour of instruction, only the order was different [\[8\]](#ref-8). The group that struggled first, alone and without help, found no correct method at all. On the posttest both groups were about the same on procedure, and the struggle-first group did a lot better on concepts and on transfer.

![Posttest scores in Kapur 2014](/assets/img/prog-learning/kapur2014.png)
_Figure 2. Kapur (2014), study 1: posttest scores out of 10 for students who attempted the problem before instruction and for students taught first. Data from [\[8\]](#ref-8)._

A second study added a group that looked at and critiqued other students' failed attempts instead of making their own. They beat direct instruction on concepts only, and did worse than the ones who made the failures themselves. So the failures were wrong and making them still did more than looking at them. My guess, which fits the result but the study didn't test it: the attempt gives the lesson something to stick to, because the students already hit the problem's constraints with their own ideas.

Schwartz and Bransford found something close with a different setup [\[9\]](#ref-9). Students either analyzed contrasting cases from memory experiments or summarized a text, then everyone heard the same lecture. In their third experiment, 36 students, the ones who analyzed cases before the lecture made 43.8% of the possible predictions on a later task, against 14.6% for the ones who summarized first and 16.7% for the ones who analyzed the cases twice and skipped the lecture. The cases didn't teach the concepts alone. They prepared distinctions for the lecture to explain. Their first experiment shows why this is easy to miss: recognizing the concepts was near ceiling, 93%, in both groups, and only the case group used them on a prediction task a week later. If you judged both lessons on the day, both worked.

This doesn't mean struggling is good in general. A novice can spend hours searching around without ever seeing the structure an expert would use, burning working memory on guesses, syntax errors and dead ends. That's why worked examples help beginners so reliably. In programming it's the difference between asking a beginner to invent a recursive tree traversal and giving them one where only the recursive case is missing. And the help stops helping as people get better. Kalyuga, Ayres, Chandler and Sweller put it as "instructional techniques that are highly effective with inexperienced learners can lose their effectiveness and even have negative consequences when used with more experienced learners" [\[10\]](#ref-10).

A language model removes way more difficulty than any worked example. Decomposition, implementation, debugging, explanation and the answer, in one reply. If you just need a working program that's often exactly right. If the goal is learning, the question is which step the student still does. Someone learning linked lists who struggles with syntax loses nothing when the model writes the constructor. Someone who struggles with pointer updates loses the whole lesson when it writes the insertion. "Don't use AI" and "use AI freely" are both too blunt for this.

Put these studies next to each other and one rule comes out, even though none of them says it: keep the steps that carry the concept with the learner, take away the rest.

I'm honestly not sure the rule survives a real course though. Nobody tells you in advance which step carries the concept. In the linked-list example I assumed pointer updates. For some students it's the idea that a node is an object at all, and a generated constructor takes that away too.

## Lectures

A lecture can carry one argument with a flow that separate exercises can't really match. Listening to an argument is still a different thing from learning to use it.

Donald Bligh spent a long time comparing lectures with other methods. His conclusion: the lecture "is as effective as any other method for transmitting information, but not more effective", and most lectures do worse than discussion at getting people to think [\[11\]](#ref-11). His advice is pretty blunt: "Use lectures to teach information. Do not rely on them to promote thought, change attitudes, or develop behavioral skills if you can help it."

Bigger studies say the same. Freeman and colleagues pooled 225 studies of undergraduate science, engineering and math courses, failure rates were 21.8% with active learning and 33.8% with traditional lecturing [\[12\]](#ref-12). That says adding student activity helps. It doesn't say which activity. Chi and Wylie's ICAP framework is more careful here [\[13\]](#ref-13). It splits engagement by what the learner actually does: passive (listening), active (highlighting, copying), constructive (making an inference the material didn't state), interactive (arguing with someone and changing your mind). It predicts learning goes up in that order. In a programming class, watching the teacher live-code is passive, retyping it is active, predicting the output before it runs is constructive, debugging it with a partner is interactive, and all four can happen in the same room in the same hour.

Peer Instruction puts the constructive step inside the lecture. As Crouch and Mazur describe it, a short presentation stops for a conceptual question. Students answer alone within 1 to 2 minutes, then spend 2 to 4 minutes trying to convince their neighbors, answer again, and only then hear the explanation [\[14\]](#ref-14). In the calculus-based physics course they report on, the normalized gain on the Force Concept Inventory went from 0.25 with traditional teaching in 1990, with 121 students, to 0.49 in the first Peer Instruction year, with 177. Different years too, and the 1990 class had no pretest, so I'd read the jump carefully. The `reset`/`clear` puzzle at the top is basically a ConcepTest. Every wrong answer to it is a specific wrong notional machine, which is exactly why arguing about it with your neighbor is useful.

Teaching also changes what learners go looking for. Bonawitz and colleagues gave 85 preschoolers a toy with four hidden functions [\[15\]](#ref-15). When an adult showed one function the way a teacher would, the kids found on average 0.72 of the other three, against 1.15 to 1.3 in the other conditions, and they played with it for less time. You shouldn't stretch a preschool study to university lectures. But the mechanism is general I think: learners read the teacher's choices as a signal of what matters, and stop searching elsewhere. Sometimes you want that; a novice learning memory safety shouldn't have to rediscover every failure mode. Sometimes it quietly closes off the next question they would have asked.

So "lecture or no lecture" is the wrong question. Better to ask what, in a given hour, is transmitted, what the student has to produce, when they have to commit to a prediction, and where a misunderstanding can hide. One thing a live class has that a recording doesn't is feedback; questions, hesitation and wrong answers can change what happens next.

## Feedback

Feedback can come while you still remember the decision that caused the error, or after that's gone from your head. A compiler error comes right away. A unit test a few seconds later. A code review comment the next day. A grade after you moved on to something else. All four are feedback, and each one lands with a different amount of context still in your head.

Timing matters but not in a simple way. Kulik and Kulik reviewed 53 studies [\[16\]](#ref-16): classroom studies with real quizzes mostly favored immediate feedback, experiments on learning test content mostly favored delayed. Butler and Winne put feedback inside a loop of self-regulation, where your own monitoring is the first source of it [\[17\]](#ref-17). You set a goal, try, look, compare, adjust. Outside feedback helps as much as it changes the next try. So, and they didn't test this, a comment that arrives after the reasoning is forgotten has to rebuild the reasoning before it can change anything.

The study I find most useful on this is about what feedback is measured against. Mathan and Koedinger built two versions of a spreadsheet-formula tutor [\[18\]](#ref-18). One judged each step against an expert model. The other modeled an "intelligent novice", someone who makes reasonable errors and then catches and fixes them, and it let learners make those errors before guiding them through catching them. Students with the intelligent-novice version ended up with deeper conceptual understanding and better transfer and retention. The authors reject the easy reading that this is about delay. What changed was the target: finding your own errors became part of the skill. A tool that always points at the error before you notice anything wrong trains you to respond to alerts, and that's a different skill from finding faults.

Programming tools are full of this trade. A type checker rejects a program before a test can fail. A debugger shows state after a crash. A property-based testing library gives back a minimal counterexample, and a reviewer asks why an invariant holds. Each shows different information at a different moment. AI adds a new case, a corrected function that arrives before you even said what the error is. It can save an hour. It can also skip isolating the fault, which was the actual lesson of that hour.

Shute's review of formative feedback turns the research into guidance [\[19\]](#ref-19): immediate feedback for hard tasks and weaker learners, delayed or softer feedback for simple tasks and stronger ones, and feedback after the learner tried, not in the middle of their thinking. For programming I'd say timing is one of four dials. The others are how precisely the feedback points at the error, whether it gives a verdict, a hint, an explanation or a fix, and whether the learner already knows what kind of mistake they made. A good tutor sets the dials so the next useful piece of work stays with the learner.

## Worked examples and problem solving

A solved problem removes search. Whether that helps depends on what the learner would have searched for, and on what they do with the example while reading it.

Chi and colleagues had students study worked physics examples and then solve problems [\[20\]](#ref-20). The four who later solved problems best made 15.3 explanations per example. The four who solved worst made 2.8. The good ones kept asking why a step followed, tied steps back to principles, noticed when part of an example didn't make sense to them. Only 8 students, grouped after the fact, so this is a correlation. A later experiment got closer to cause [\[21\]](#ref-21). Twenty-four eighth-graders read a 101-sentence text on the circulatory system. The 14 who were prompted to explain each sentence to themselves gained 32% from pretest to posttest, the 10 who just read it twice gained 22%, and the gap was bigger on the hardest questions. But the prompted group also studied about twice as long, and the paper doesn't describe random assignment, so time on task is still a real alternative explanation.

So "show the solution" isn't one thing. A worked example can be copied, inspected, compared to another one, explained, completed or modified, and each asks something different of the reader. van Merriënboer and de Croock tested one of these [\[22\]](#ref-22). They taught 40 novices a 2.5-hour computer-based programming course where one group wrote whole programs and the other completed partial ones. The completion group used programming templates better on both a construction test and a multiple-choice test. Completion also has a side effect the study didn't measure: it makes students read existing code, which is most of what programmers actually do all day.

The idea extends to fading. Early examples show every step, later ones leave more steps to the learner. Renkl, Atkinson and Große found learners learned most about exactly the principles whose steps were faded, and think-aloud data showed fewer unproductive learning events with fading [\[23\]](#ref-23). In code, a faded sequence on tree recursion could look like this:

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

Koedinger and Aleven call the underlying problem the assistance dilemma: how a learning environment should balance giving help and holding it back [\[24\]](#ref-24). Too much, and the learner finishes without the work that teaches. Too little, and they spend effort on search that teaches nothing. They treat the balance as an open problem that depends on the learner, the task and the skill.

A concrete case. Someone learning property-based testing has one real thing to learn, the difference between an example and an invariant. If an AI writes the harness, the generator, the property and the explanation, the exercise becomes reading. If it writes the harness and the generator and leaves the property empty, the student still has to say what must always be true. A coding assistant made for teaching would need to know which of those pieces is the lesson.

## What counts as learning

"Understand recursion" isn't a measurement. A student can recognize a correct recursive function, trace one, write one from a template, debug one, explain why it stops, choose recursion for a new problem, or see when it's the wrong choice. Those are separate abilities, and a course that tests one learns little about the others.

Bloom's mastery learning insisted learning be shown, not assumed from time spent. A course is cut into short units, each ends with a diagnostic test marked mastery or nonmastery, and a student who isn't there yet gets a specific prescription [\[25\]](#ref-25). Corbett and Anderson's knowledge tracing made that into a model a tutor can actually run [\[26\]](#ref-26). In their ACT Programming Tutor each skill has four parameters: the chance it's already known, the chance of learning it at each step, and the chances of a lucky guess and of a slip. After every attempt the tutor updates its belief with Bayes' rule and calls the skill mastered when the estimate reaches 0.95. The whole model is a dozen lines ([`bkt.py`](/assets/code/prog-learning/bkt.py), the parameters are illustrative, not fitted):

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

Run it on two students. One gets the first two wrong, then one right, then another wrong, then everything right from attempt five. The other is right every time.

![Knowledge tracing estimates for two learners](/assets/img/prog-learning/bkt.png)
_Figure 3. Estimated probability that the skill is known, attempt by attempt. The student who struggles reaches the threshold at attempt 7, the one who is always right at attempt 3._

The sequence carries information a final answer doesn't: the dip at attempt 4 says the first student's skill wasn't stable yet. Now say the second student's answers came from a chatbot. The model can't tell. It sees correct answers, raises its estimate, and by attempt 3 it declares mastery of a skill nobody practised. Any tutor built on performance evidence has this problem once something other than the student can produce the evidence.

Education isn't the only place this happens. METR's developers, below, judged their own speed from how the work felt, and the feeling pointed the wrong way. A tutor judges knowledge from correct answers. A team judges productivity from merged code. Each one uses an output as evidence of a capacity, and each measure breaks once something other than the capacity can make the output. My reading, not something any of these studies claims: most arguments about AI and skill are really arguments about which output still counts as evidence of which capacity.

Assessment has a related blind spot. A student can often tell which method to use because the chapter title already said it. The National Research Council's review of learning research says knowledge tied too closely to one context transfers less, and teaching across several contexts helps [\[27\]](#ref-27). If every binary-search exercise sits under a heading called "Binary search", nobody ever has to notice that binary search applies. Ask instead for the smallest truck capacity that ships a list of packages, in order, within a given number of days, and the student has to see that the capacities form a sorted space you can search. That noticing is the part that transfers.

Performance and retention come apart too. A student can do better with a tool and worse once it's gone. At work, where the tool stays, maybe that's fine. In a course that claims to teach a capability, it's the whole question, and a course should say which capabilities it expects to stay when the tool is gone and which ones it expects to be done with the tool.

## Editors

An editor decides which facts about a codebase are close at hand. Take one function call. With no tooling you search for the definition by hand. With go-to-definition it's one keypress. Find-references gives the callers, inferred types give the values flowing through, blame gives the change that added the line. None of this changes the code. It changes what it costs to ask questions about the code, and people ask the cheap questions way more often than the expensive ones.

Green and Petre's cognitive dimensions framework gives words for these costs [\[28\]](#ref-28). The original paper lists 13 dimensions. Visibility asks if every part of the code can be seen at once or put side by side. Hidden dependencies asks if every dependency is shown in both directions. Viscosity is the effort one change takes. Premature commitment is having to decide before the information you need exists. They made it for visual programming environments, but it describes a normal editor fine, and honestly a chat window too.

Some questions stay expensive in any editor. "Where is this called?" costs one keypress. "Why is it written this way?" usually needs history, an issue thread or a colleague. For the two missing posts on this blog, one command answers part of it:

```text
$ git log -S '2095' --format='%h %an %ad %s' --date=short -- _posts/2025-09-2-c-day1.md
7e5f16f Abdulrahman Tamim 2026-01-25 Update date in C programming post
```

That's the what, the who and the when. The why isn't in the repository.

Jane Street built its tooling around the idea that the editor is where these questions should be cheap. Their code review runs inside Emacs through Iron, their review system, and reviewers leave comments in the code itself. A 2018 post from them argues that "code review that takes place in a browser" is "often shallower" [\[29\]](#ref-29). If review, navigation, history and editing are in one place, you go from noticing something to changing it without rebuilding the context in another tab. AI assistants should get the same test. A chat panel can explain code fluently, but if the explanation isn't tied to definitions, references, types, tests and history, it's describing the code without being connected to it. The explanation of the missing posts at the top had exactly that problem.

## Development tools

A tool changes how expensive an action is, and after years those costs turn into habits. If following a definition is cheap, people follow definitions. If review means leaving the editor and rebuilding the change in a browser, review practice forms around that friction, the same friction Jane Street moved review into the editor to avoid. If branching is cheap and rewriting history is expensive, workflows bend to match.

Peter Naur argued in 1985 that what a team builds isn't really the code. It's a theory of how the problem and the program match, and the theory lives in the programmers [\[30\]](#ref-30). His main example is a compiler handed from one group to another with full documentation. The new group's extensions were patches that, in Naur's words, "destroyed its power and simplicity", and the original authors saw it immediately. About 10 years later, with the original group gone, the structure had been "made entirely ineffective". You can have every source file and not have the theory, which is why replacing the team that built something costs more than the files suggest.

Parnas made the architecture version of this in 1972. Using a small program that builds a KWIC index, he argued for splitting a system so each module hides a design decision that is difficult or likely to change [\[31\]](#ref-31). So modularity is a bet about future change, more than a way to organize files. A tool that shows a system only as files and symbols can miss the boundary that actually matters, maybe a deployment unit, a service owner, a data contract or a failure boundary. Conway added the organization: organizations, he wrote, "are constrained to produce designs which are copies of the communication structures of these organizations" [\[32\]](#ref-32). Tools sit inside organizations that already shape the code. A review tool that assumes each file has one owner fits one kind of team, a tool built for editing together fits another.

"Developer experience" is too small a phrase for all of this. The real question is what a tool makes visible, what it makes cheap, and what those costs become after a few years. Some engineering habits that look cultural are partly infrastructure. AI tools will do the same. A generator that makes implementation cheap probably means more code. An assistant that makes explanation cheap may mean reviewers ask each other less. An agent that answers architecture questions may mean fewer people ever learn the architecture. None of that is necessarily bad. All of it comes from a changed cost.

## Build it or depend on it

An internal implementation and an external dependency differ in where the maintenance knowledge lives, not only in who owns the code.

The costs of a dependency are easy to list: its API, the upgrades, security exposure, upstream decisions you don't control. The costs of writing it yourself are spread thin and easy to miss. Someone has to hit every edge case the external project already hit, write the tests, read the bug reports, reproduce the weird behavior, and remember why old decisions were made.

Mockus, Fielding and Herbsleb looked at what that knowledge looks like in two big open-source projects, using source history and problem reports [\[33\]](#ref-33). In Apache, 15 of 388 code contributors made over 83% of the changes and 88% of the added lines, but only 66% of the fixes to reported problems. Mozilla had bigger core teams, 22 to 35 people, with more formal ownership and inspection. Mature projects build up process, specialization and review, and when you depend on one you inherit that problem history along with the code.

So building it yourself gives full control only if the team keeps the knowledge to use that control, and an abandoned internal library can be less controllable than a maintained external one. A dependency buys you an interface to someone else's accumulated knowledge, spread over releases, discussions, issue trackers, tests and maintainers. The interface is always incomplete, but the knowledge is there on the other side. McIlroy saw the economics at the 1968 NATO conference [\[34\]](#ref-34). He proposed a components industry with catalogues of routine families, parameterized by precision, robustness, generality and time-space trade-offs, and pointed out that Bell Labs alone ran about 100 machines from a dozen makers, each one needing the same support software written again.

The practical questions come from that. How specific is the requirement, and how bad would a wrong answer be? How mature and stable is the external thing? How much would the team need to learn to maintain its own replacement, and which future changes need local control? What happens if upstream disappears?

## Code generation

Automatic programming is older than language models. Compilers automated translating higher-level programs into machine instructions. Program-synthesis research tried to derive programs from specifications, examples and domain knowledge. Macro systems generated code, CASE tools generated boilerplate, domain-specific languages moved decisions into another notation.

In 1988 Rich and Waters listed six myths about automatic programming [\[35\]](#ref-35). One is that a system can be end-user oriented, general purpose and fully automatic at once; they argue every approach gives up one of the three. Another is that requirements can be complete: "At best," they write, "requirements are only approximations." Requirements change during implementation, and some only show up once there's a prototype. The hard part was rarely translating a clear specification into code. It was getting a specification worth translating.

Language models change the scale and the interface. Plain language now gives you plausible code for a lot of ordinary tasks, no formal specification needed. The old problem is still there, and now it comes with tests attached. This is roughly what you get when you ask a model to split a restaurant bill ([`split_bill.py`](/assets/code/prog-learning/split_bill.py), [`test_split_bill.py`](/assets/code/prog-learning/test_split_bill.py)):

```python
def split_bill(total, people):
    share = round(total / people, 2)
    return [share] * people

def test_even_split():
    assert split_bill(90, 3) == [30.0, 30.0, 30.0]

def test_two_people():
    assert split_bill(50, 2) == [25.0, 25.0]
```

Both tests pass. Nobody asked for the invariant that makes it correct, that the shares add up to the bill to the cent, so nobody wrote it. Write it as a property, give it to Hypothesis, and it fails right away, and Hypothesis shrinks the failure to the smallest case it can find:

```text
E       assert 2 == 1
E       Failing test case: test_shares_add_up(
E           cents=1,
E           people=2,
```

Split one cent between two people and each is charged a cent, so the bill becomes two. Split 100 between three and each pays 33.33, and the restaurant is a cent short. The code does what the prompt said, the tests confirm the code's own reading of the prompt, and the constraint that makes it correct was never written down anywhere.

That's also why productivity numbers need care. METR ran a randomized study in 2025 with 16 experienced open-source developers doing 246 tasks from large open-source repositories [\[36\]](#ref-36). With AI tools allowed, tasks took 19% longer, with a confidence interval from 2% to 39% longer. Before the study the developers expected a 24% speedup, and afterwards they still believed they'd been 20% faster.

![METR 2025 forecasts versus measurement](/assets/img/prog-learning/metr2025.png)
_Figure 4. Change in task completion time with AI in METR's 2025 study: what economists, ML experts and the developers predicted, what the developers believed afterwards, and what was measured, with its confidence interval. Data from [\[36\]](#ref-36)._

That shouldn't be read as "AI makes developers slower". In February 2026 METR said it was changing the study design. In the follow-up, 30% to 50% of developers said they'd held back some tasks because they didn't want to do them without AI, which biases a randomized comparison, and the new estimates, 18% faster for returning developers and 4% faster for new ones, have confidence intervals that include no effect [\[37\]](#ref-37). METR expects to keep redesigning as models get better. What the first study showed is less about AI and more about people: the developers' sense of their own speed pointed the wrong way.

DORA's surveys look at whole teams. In the 2024 report, each 25% increase in AI adoption was associated with an estimated 1.5% drop in delivery throughput and a 7.2% drop in delivery stability [\[38\]](#ref-38). In the 2025 survey of about 5,000 respondents, AI adoption was associated with higher throughput and still with lower stability [\[39\]](#ref-39). Writing code faster and delivering working software are different measures and they can go opposite ways. "Code generation" is really specification, collecting context, implementation, testing, review, integration and maintenance, and a model can speed up one of those while slowing another. One productivity number hides which.

I trust the DORA numbers less than METR's though. An association across thousands of survey answers mixes teams that adopted AI because they were struggling with teams that adopted it because they were doing well, and a survey can't separate them. METR randomized, which is why its result, and also its later problems with who agreed to take part, tell you more.

## Reading unfamiliar code

Nobody needs to understand a whole codebase. You need to understand enough to make one change safely, and the hard part is you don't know in advance what "enough" is. A bug shows up in a parser and the cause is a cache rule. A UI glitch comes from a data contract. A function looks unused until a reflective loader calls it. You start from a local symptom and have to discover which parts of the system are part of the explanation.

Robillard, Coelho and Murphy watched 5 developers change the autosave feature of jEdit, a 65 KLOC Java editor [\[40\]](#ref-40). Two succeeded. The successful ones built a picture of the relevant structure first, made a detailed plan, and searched by following structural relations in the code. The others skimmed and guessed. It's a small study, and the two who succeeded were also the more experienced ones, so it describes strategies more than it proves them. Still, you'll recognize them if you ever watched a senior engineer open a repo they don't know.

Sillito, Murphy and De Volder catalogued the questions themselves: 44 types, from two studies, one with 9 graduate students working in pairs on the open-source ArgoUML code base and one with 16 industrial programmers working on their own code [\[41\]](#ref-41). The questions fall into 4 groups, going from finding a starting point, to building out from it, to understanding how a connected region works, to questions across several regions. "Where is this method called or type referenced?" is one of them. A follow-up paper looked at how existing tools did and didn't help answer them [\[42\]](#ref-42). Ko, DeLine and Venolia watched 17 developers at Microsoft and found 21 kinds of information they went looking for [\[43\]](#ref-43). The needs developers most often had to put off were about design and behavior: why code was written a certain way, what it was supposed to do, what caused some state. They put them off because the only source was a colleague who wasn't available.

The missing posts at the top have this shape. The symptom was a missing page. The first answer explained it from the nearest object, the filename. The real explanation needed two more hops, into the front matter and then into Jekyll's rule that front-matter dates win. An assistant can answer a local question fluently without ever figuring out the scope of the problem. The way I'd put it: an answer gives you a proposition, and an investigation changes which things you think are relevant. With unfamiliar code the investigation is usually the hard part, and it's exactly the part a fluent answer lets you skip.

## Knowledge that is not in the code

Source code records decisions unevenly. It records that a condition exists, often not why it was added. It records that two blocks are duplicated, not that the duplication is on purpose because the cases are expected to split later. It records a call to a service, not that the service boundary exists because of a regulation, a deployment constraint or a deal between two teams.

LaToza, Venolia and DeLine surveyed developers at Microsoft, 157 and 187 responses to two surveys, and interviewed 11 [\[44\]](#ref-44). In the survey, 66% said understanding the rationale behind a piece of code was a serious problem. Developers went to the code first and then to colleagues, and many teams had an informal "team historian". The same developers said they spent most of their time on things other than understanding existing code. So I read it as: rationale is expensive because it's hard to get back when you need it, more than because you need it often. Aranda and Venolia reconstructed the histories of 10 bugs at Microsoft by interviewing 26 of the people involved [\[45\]](#ref-45). The histories depended on social, organizational and technical knowledge, and the repository records gave "incomplete and often erroneous accounts" of what happened. A bug report is only a partial record of how a bug got fixed.

Naur's theory building explains why. The theory connecting a program to its problem lives in the people who built it, and the source can outlive the theory. A rewrite can keep every behavior and lose the operational knowledge. Documentation can describe every interface and miss why a constraint exists. A refactor that removes some duplication can bring back a bug that the duplication was there to prevent. A new team can inherit every repository and still spend months learning the system.

The notional machine from the first section and Naur's theory are the same kind of thing at two sizes. A student holds a model of what the language does. A team holds a model of what the system is for and why it looks the way it does. Neither is in the source, both get built by working with the code, and both can be wrong while the code still runs. I like that connection more than either idea alone.

The two posts on this blog are a small example. The history says the dates were changed on purpose, by me, in commits titled `Update date in C programming post` and `Update post date to 2079-09-06`. The code knows what changed, the history knows who and when, and the reason is only in my head. That's the easy case, I'm still here to ask.

![Where knowledge about a line of code is kept](/assets/img/prog-learning/knowledge-location.png)
_Figure 5. What a line does is in the code, who changed it and when is in the history, and why is usually only in someone's memory._

Code generation adds a harder case: a decision whose reason maybe never was in any human head. If an agent picks an implementation and a developer accepts it because the tests pass, who holds the reason? The model can produce an explanation afterwards, but a generated explanation isn't necessarily the history of the decision. The practical answer is old and boring: write the reason down with the change. For agent-written code that means a commit message that says more than what changed:

```text
Split bills in integer cents; give the remainder to the first diners

Constraint: shares must sum exactly to the total (found by a property
test; the earlier float version lost or added a cent).
Rejected: rounding each share and adjusting the last one, because the
last diner could end up paying noticeably more than the others.
Assumes: amounts under 10^9 cents; one currency per bill.
Written by: coding agent, reviewed by a human who read the property test.
```

## Incomplete programs and hints

An educational coding assistant doesn't have to choose between giving the answer and giving nothing. The worked-example and tutoring research already maps the space in between: completion problems, fading, the assistance dilemma, tutors that let learners catch their own errors.

Turned into assistant behavior, that space is big. It can generate the project scaffolding and leave the core algorithm unfinished. It can write the tests and ask the student which one fails first. It can answer "why is this wrong?" with a failing input instead of a fixed function, or point at the region with the fault instead of rewriting it. It can ask for the invariant before writing any code, and fill in routine API calls while leaving the data-structure logic to the student. What makes an assistant educational is control over which of these it does. A "learning mode" that only changes its tone doesn't give that.

![The range of help between nothing and the answer](/assets/img/prog-learning/help-range.png)
_Figure 6. Help as a range, not a switch. Moving right moves work, and whatever that work would have taught, from the learner to the helper._

It can also do something a textbook can't: make a near-miss on purpose. Like this binary search that's almost right ([`near_miss.py`](/assets/code/prog-learning/near_miss.py)). It should return the index of the first element at least as large as the target, or the length of the list if there isn't one:

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

It passes the obvious checks. `first_at_least([1, 3, 5, 7], 5)` returns 2, and so does searching for 4. Search for 9 and it returns 3 instead of 4, because `hi` starts one position too early and the "past the end" answer can never be reached. Asking a student to find the input that breaks it trains exactly the tracing skill from the start. How good the exercise is depends on the defect: it has to isolate the concept being taught, not add random confusion.

The same hint can help the first time and be useless the fifth, so the assistant also has to track the learner. Knowledge tracing gives a way to decide when to fade support, with the caveat from before: it only works if the evidence it reads came from the student. Looked at through this research, "make the AI Socratic" turns into a design problem with named parts: which step is held back, when help fades, and what evidence triggers the change.

## Automation and skill

Automation can take the routine work and leave the rare failure to a person. Lisanne Bainbridge wrote about this in 1983, about industrial process control [\[46\]](#ref-46). Manual skills "deteriorate when they are not used", and the operator is called in exactly when the automation meets a situation it can't handle. In her words, "by taking away the easy parts of his task, automation can make the difficult parts ... more difficult". Endsley and Kiris tested a version of this with a car-navigation decision task at five levels of automation, from fully manual to fully automated [\[47\]](#ref-47). When the automation failed, people who had worked with more automation had lower situation awareness and took longer to decide, and it was worst under full automation.

Neither study is about programming, and the comparison only works because both change how work is split between a person and a machine. But if a coding agent takes the ordinary implementation, what's left for the programmer is the unclear requirement, the integration failure, the weird performance cliff, the security edge case, the incident, the bug caused by assumptions spread over three components. A lot of those need exactly the system knowledge that routine implementation used to build on the side. That's my inference from Bainbridge, not a measured result in programming. Automation changes what work is left, and it changes the experience through which you become able to do that work.

![Schematic of Bainbridge's irony](/assets/img/prog-learning/automation-irony.png)
_Figure 7. A schematic of Bainbridge's argument, not data. Before automation, the frequent routine work is also practice for the rare failure. After it, the rare failure is the only practice left._

And this is the same thing as Kapur's result, which surprised me when I noticed it. Productive failure says the attempt is where the concept forms. Bainbridge says routine operation is where the operator's model of the plant forms. In both, the work that looks removable is the work that builds the model, and removing it saves time now and costs the model later.

Supervising the automation has its own failure mode. Parasuraman and Manzey's review found that automation bias, when people follow an automated aid's mistakes or miss problems it doesn't flag, "cannot be prevented by training or instructions" [\[48\]](#ref-48). Anyone reviewing a big generated diff is in that spot.

None of this is an argument against tools. Risko and Gilbert define cognitive offloading as "the use of physical action to alter the information processing requirements of a task so as to reduce cognitive demand" [\[49\]](#ref-49), and people do it all the time with notes, calculators, reminders and documentation. Offloading is part of thinking well. The real question is whether you still need the thing you offloaded for some other part of the job. You don't need to memorize an API, the documentation holds it. You do need to understand aliasing, because it shows up in debugging, concurrency, ownership and performance. A team doesn't need everyone to remember the deploy commands, the pipeline holds them, but someone needs to understand the deployment model the day the pipeline breaks.

Deciding which skills to let go and which to keep is the design problem, and I don't know how to settle it for programming. Aliasing seems obviously necessary to keep. I'm less sure about reading assembly or writing regular expressions by hand, and I suspect my own list is mostly a list of what I happened to learn.

## Learning programming with AI

The first careful studies of students programming with generative AI are starting to separate finishing the task from learning from it.

Rahe and Maalej watched 37 first-semester students work on one comprehension-heavy exercise that was designed so the chatbot would mostly fail at it: only 8.8% of its generated solutions were correct [\[50\]](#ref-50). Of the 37, 23 used the bot. Of their first prompts, 39.1% asked it to just solve the task, and most eventually asked for a full solution. The most common pattern was a loop: paste the generated code, watch it fail, ask the bot to fix it. No student asked why their own solution failed. It's one exercise, built to beat the model, so it shows how students act when AI help fails, which is narrower than how they use it in general. Within that limit, it shows investigation getting replaced by retries.

Asking for a complete solution is often the right move at work. In a course it depends on what the exercise was for. If it's about recursion and the student asks for the function, copies it, runs the tests and reads the explanation, maybe they learned something. The finished assignment still can't tell you if they can trace the calls, find the base case in a new problem, or design a recursive split on their own.

Treating AI as an experimental condition instead of a moral question makes this workable. Does it improve completion today? Performance a month later? Transfer to a problem that looks different? Can students explain the generated code, or find a planted bug in it? Do they ask for different kinds of help as they improve, and which kinds of request go with better learning later? What happens when you take the model away? Liu, Fan and Pan look at the same split from the qualitative side [\[51\]](#ref-51). Their grounded-theory study followed a semester of undergraduate Java, comparing a section that used AI, with 24 students, against a pair-programming section, with 17, using interaction logs, concept maps and interviews. It proposes things rather than measuring them: a split between mastery of the domain and mastery of the tool, and two loops, one where the AI scaffolds the student's thinking and one where it takes the thinking over. That's vocabulary later studies can test.

The older research already explains most of what these studies see. Productive failure says why an early answer can cost something. The worked-example research says why a complete example can still help a beginner. The assistance dilemma frames how much help to give, and the automation research says why working well with a tool and working without it come apart. A course can use all of it directly: AI unrestricted for boilerplate setup, limited to hints the first time a student implements a data structure, allowed for review once the student has a working solution, banned in a test of unaided tracing, and required in a separate test of how well the student supervises generated code.

## How much code a team can know

Software can grow faster than the people maintaining it can take in.

Meir Lehman saw this in big systems that had been evolving for years. One of his laws of software evolution, conservation of familiarity, says the content of successive releases of an evolving program stays statistically invariant [\[52\]](#ref-52). His explanation was that every release forces the people working on the system to get familiar with it again, and the effort grows at least quadratically with the size of the release. The next part is mine, not Lehman's: growth works against familiarity unless the organization also pays for learning, restructuring, documentation or specialization.

Size is only one input. A small system with lots of hidden dependencies can be harder to know than a bigger one with stable interfaces. What counts is how much structure the team has to keep usable. The studies about unfamiliar code and missing rationale above are the same problem seen from one developer's desk, and Naur explains why keeping the files doesn't solve it.

Brooks separated essential from accidental difficulty [\[53\]](#ref-53). Better tools can remove a lot of accidental work: syntax, boilerplate, translation, search, repetitive implementation. The essential difficulty is, in his words, "the specification, design, and testing of this conceptual construct, not the labor of representing it", and tools don't remove it. Code generation is a very good tool for the labor of representing.

Which leaves the question I think matters most for teams now. Cheap generation raises the rate new code can enter a repository. At what rate can the team turn that code into shared working knowledge? Nobody has a validated measure for it yet. Review time, the time until a second engineer successfully changes a piece of code, the number of people who can explain a subsystem, incident recovery time, how concentrated ownership is, how often changes get reverted, all of them are candidates. If code volume goes up while those get worse, a team may be piling up structure faster than it can understand it, and its productivity dashboard will show that as a gain.

![Generation and assimilation as a bathtub](/assets/img/prog-learning/bathtub.png)
_Figure 8. The level in the tub is code nobody on the team understands yet. It rises whenever generation outpaces assimilation, however fast either one is._

Generation rate and assimilation rate are different quantities, and nothing here says generate less code. A person can also write code faster than a team can take it in. An agent just makes that imbalance a lot easier to reach.

I don't know what a team's assimilation rate actually is, how to measure it well, or if it can be raised much. That's the part of this I'd most like someone to study.

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
11. <span id="ref-11"></span>D. A. Bligh, *What's the Use of Lectures?*, first U.S. edition, Jossey-Bass, 2000 (first edition 1971). ISBN 0-7879-5162-5.
12. <span id="ref-12"></span>S. Freeman, S. L. Eddy, M. McDonough, M. K. Smith, N. Okoroafor, H. Jordt and M. P. Wenderoth, "Active learning increases student performance in science, engineering, and mathematics," *PNAS* 111(23), 2014. <https://doi.org/10.1073/pnas.1319030111>
13. <span id="ref-13"></span>M. T. H. Chi and R. Wylie, "The ICAP framework: linking cognitive engagement to active learning outcomes," *Educational Psychologist* 49(4), 2014. <https://doi.org/10.1080/00461520.2014.965823>
14. <span id="ref-14"></span>C. H. Crouch and E. Mazur, "Peer Instruction: ten years of experience and results," *American Journal of Physics* 69(9), 2001. <https://doi.org/10.1119/1.1374249>
15. <span id="ref-15"></span>E. Bonawitz, P. Shafto, H. Gweon, N. D. Goodman, E. Spelke and L. Schulz, "The double-edged sword of pedagogy: instruction limits spontaneous exploration and discovery," *Cognition* 120(3), 2011. <https://doi.org/10.1016/j.cognition.2010.10.001>
16. <span id="ref-16"></span>J. A. Kulik and C.-L. C. Kulik, "Timing of feedback and verbal learning," *Review of Educational Research* 58(1), 1988. <https://doi.org/10.3102/00346543058001079>
17. <span id="ref-17"></span>D. L. Butler and P. H. Winne, "Feedback and self-regulated learning: a theoretical synthesis," *Review of Educational Research* 65(3), 1995. <https://doi.org/10.3102/00346543065003245>
18. <span id="ref-18"></span>S. A. Mathan and K. R. Koedinger, "Fostering the intelligent novice: learning from errors with metacognitive tutoring," *Educational Psychologist* 40(4), 2005. <https://doi.org/10.1207/s15326985ep4004_7>
19. <span id="ref-19"></span>V. J. Shute, "Focus on formative feedback," *Review of Educational Research* 78(1), 2008. <https://doi.org/10.3102/0034654307313795>
20. <span id="ref-20"></span>M. T. H. Chi, M. Bassok, M. W. Lewis, P. Reimann and R. Glaser, "Self-explanations: how students study and use examples in learning to solve problems," *Cognitive Science* 13(2), 1989. <https://doi.org/10.1207/s15516709cog1302_1>
21. <span id="ref-21"></span>M. T. H. Chi, N. de Leeuw, M.-H. Chiu and C. LaVancher, "Eliciting self-explanations improves understanding," *Cognitive Science* 18(3), 1994. <https://doi.org/10.1207/s15516709cog1803_3>
22. <span id="ref-22"></span>J. J. G. van Merriënboer and M. B. M. de Croock, "Strategies for computer-based programming instruction: program completion vs. program generation," *Journal of Educational Computing Research* 8(3), 1992. <https://doi.org/10.2190/MJDX-9PP4-KFMT-09PM>
23. <span id="ref-23"></span>A. Renkl, R. K. Atkinson and C. S. Große, "How fading worked solution steps works: a cognitive load perspective," *Instructional Science* 32, 2004. <https://doi.org/10.1023/B:TRUC.0000021815.74806.F6>
24. <span id="ref-24"></span>K. R. Koedinger and V. Aleven, "Exploring the assistance dilemma in experiments with Cognitive Tutors," *Educational Psychology Review* 19(3), 2007. <https://doi.org/10.1007/s10648-007-9049-0>
25. <span id="ref-25"></span>B. S. Bloom, "Learning for mastery," *Evaluation Comment* 1(2), 1968. <https://eric.ed.gov/?id=ED053419>
26. <span id="ref-26"></span>A. T. Corbett and J. R. Anderson, "Knowledge tracing: modeling the acquisition of procedural knowledge," *User Modeling and User-Adapted Interaction* 4, 1995. <https://doi.org/10.1007/BF01099821>
27. <span id="ref-27"></span>National Research Council, *How People Learn: Brain, Mind, Experience, and School*, expanded edition, chapter 3, "Learning and transfer," National Academy Press, 2000. <https://doi.org/10.17226/9853>
28. <span id="ref-28"></span>T. R. G. Green and M. Petre, "Usability analysis of visual programming environments: a 'cognitive dimensions' framework," *Journal of Visual Languages and Computing* 7(2), 1996. <https://doi.org/10.1006/jvlc.1996.0009>
29. <span id="ref-29"></span>J. Somers, "Putting the I back in IDE: towards a GitHub explorer," Jane Street Tech Blog, 27 March 2018. <https://blog.janestreet.com/putting-the-i-back-in-ide-towards-a-github-explorer/>
30. <span id="ref-30"></span>P. Naur, "Programming as theory building," *Microprocessing and Microprogramming* 15(5), 1985. <https://doi.org/10.1016/0165-6074(85)90032-8>
31. <span id="ref-31"></span>D. L. Parnas, "On the criteria to be used in decomposing systems into modules," *Communications of the ACM* 15(12), 1972. <https://doi.org/10.1145/361598.361623>
32. <span id="ref-32"></span>M. E. Conway, "How do committees invent?," *Datamation*, April 1968. <https://www.melconway.com/Home/Committees_Paper.html>
33. <span id="ref-33"></span>A. Mockus, R. T. Fielding and J. D. Herbsleb, "Two case studies of open source software development: Apache and Mozilla," *ACM Transactions on Software Engineering and Methodology* 11(3), 2002. <https://doi.org/10.1145/567793.567795>
34. <span id="ref-34"></span>M. D. McIlroy, "Mass produced software components," NATO Software Engineering Conference, Garmisch, 1968. <https://mcilroy.cs.dartmouth.edu/components.txt>
35. <span id="ref-35"></span>C. Rich and R. C. Waters, "Automatic programming: myths and prospects," *IEEE Computer* 21(8), 1988. <https://doi.org/10.1109/2.75>
36. <span id="ref-36"></span>J. Becker et al., "Measuring the impact of early-2025 AI on experienced open-source developer productivity," METR, July 2025. <https://arxiv.org/abs/2507.09089>
37. <span id="ref-37"></span>METR, "We are changing our developer productivity experiment design," METR blog, 24 February 2026. <https://metr.org/blog/2026-02-24-uplift-update/>
38. <span id="ref-38"></span>DORA, *Accelerate State of DevOps Report 2024*, Google Cloud, 2024. <https://dora.dev/research/2024/dora-report/>
39. <span id="ref-39"></span>DORA, *2025 State of AI-assisted Software Development*, Google, 2025. <https://research.google/pubs/dora-2025-state-of-ai-assisted-software-development-report/>
40. <span id="ref-40"></span>M. P. Robillard, W. Coelho and G. C. Murphy, "How effective developers investigate source code: an exploratory study," *IEEE Transactions on Software Engineering* 30(12), 2004. <https://doi.org/10.1109/TSE.2004.101>
41. <span id="ref-41"></span>J. Sillito, G. C. Murphy and K. De Volder, "Questions programmers ask during software evolution tasks," *Proc. FSE-14*, 2006. <https://doi.org/10.1145/1181775.1181779>
42. <span id="ref-42"></span>J. Sillito, G. C. Murphy and K. De Volder, "Asking and answering questions during a programming change task," *IEEE Transactions on Software Engineering* 34(4), 2008. <https://doi.org/10.1109/TSE.2008.26>
43. <span id="ref-43"></span>A. J. Ko, R. DeLine and G. Venolia, "Information needs in collocated software development teams," *Proc. ICSE*, 2007. <https://doi.org/10.1109/ICSE.2007.45>
44. <span id="ref-44"></span>T. D. LaToza, G. Venolia and R. DeLine, "Maintaining mental models: a study of developer work habits," *Proc. ICSE*, 2006. <https://doi.org/10.1145/1134285.1134355>
45. <span id="ref-45"></span>J. Aranda and G. Venolia, "The secret life of bugs: going past the errors and omissions in software repositories," *Proc. ICSE*, 2009. <https://doi.org/10.1109/ICSE.2009.5070530>
46. <span id="ref-46"></span>L. Bainbridge, "Ironies of automation," *Automatica* 19(6), 1983. <https://doi.org/10.1016/0005-1098(83)90046-8>
47. <span id="ref-47"></span>M. R. Endsley and E. O. Kiris, "The out-of-the-loop performance problem and level of control in automation," *Human Factors* 37(2), 1995. <https://doi.org/10.1518/001872095779064555>
48. <span id="ref-48"></span>R. Parasuraman and D. H. Manzey, "Complacency and bias in human use of automation: an attentional integration," *Human Factors* 52(3), 2010. <https://doi.org/10.1177/0018720810376055>
49. <span id="ref-49"></span>E. F. Risko and S. J. Gilbert, "Cognitive offloading," *Trends in Cognitive Sciences* 20(9), 2016. <https://doi.org/10.1016/j.tics.2016.07.002>
50. <span id="ref-50"></span>C. Rahe and W. Maalej, "How do programming students use generative AI?," *Proceedings of the ACM on Software Engineering* 2(FSE), 2025. <https://doi.org/10.1145/3715762>
51. <span id="ref-51"></span>D. Liu, G. Fan and L. Pan, "Tool, tutor, or crutch?: A grounded theory of cognitive scaffolding and offloading in AI-assisted programming education," *International Journal of STEM Education* 13, article 10, 2026. <https://doi.org/10.1186/s40594-025-00592-w>
52. <span id="ref-52"></span>M. M. Lehman, "On understanding laws, evolution, and conservation in the large-program life cycle," *Journal of Systems and Software* 1, 1980. <https://doi.org/10.1016/0164-1212(79)90022-0>
53. <span id="ref-53"></span>F. P. Brooks, "No silver bullet: essence and accidents of software engineering," *Proc. IFIP Congress*, 1986, reprinted in *IEEE Computer* 20(4), 1987. Link is the IFIP text. <https://worrydream.com/refs/Brooks-NoSilverBullet.pdf>
