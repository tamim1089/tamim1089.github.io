---
title: AI is Dead, and We Have Killed It
date: 2026-02-19 14:54:00 +/-TTTT
image:
  path: assets/img/favicons/1_yVPk4XHXefuKVVOrGEvJiQ.webp
  class: "img-right"
categories: [AI]
tags: [AI]  
---
Before you roll your eyes and close this tab, let me be precise about what this is, This is not a claim that AI does not work. GPT-4 exists. AlphaFold cracked the protein folding problem that stumped biologists for fifty years. Machine translation works. Nobody serious disputes those achievements. This is about what we destroyed to get there.

Between 2012 and 2024, AI research went from exploring six or seven competing paradigms to optimizing exactly one. Not because that paradigm was proven superior, but because it happened to fit hardware we already owned. We built an entire scientific field around what was convenient, called it progress, and buried everything else. The researchers who built alternative frameworks for intelligence — rigorous, mathematically complete, historically documented frameworks — retired without training successors. The grad students who might have carried that knowledge forward never learned it, because universities stopped teaching it. The infrastructure needed to test those ideas does not exist anymore, because nobody funded it.

When I say AI is dead, I mean it the way a monoculture is dead. Biologically alive, But ecologically extinct.

---

## The Hardware Lottery

Sara Hooker at Google Brain named this. A research idea wins the hardware lottery when it succeeds because it fits whatever hardware exists at the time, not because it is the best solution to the problem.

History is full of this. Charles Babbage designed the Analytical Engine in 1837, and the design was mathematically correct, but Victorian fabrication precision could not build it. Perceptrons worked conceptually when Rosenblatt published them in 1958, died when Minsky and Papert proved they could not solve XOR in 1969, then got resurrected in the 1980s when hardware finally existed that could train multi-layer networks. Backpropagation was theoretically viable since Rumelhart, Hinton, and Williams published it in 1986, but nobody could scale it until GPUs arrived.

NVIDIA released CUDA in 2007. You could suddenly do general-purpose computing on graphics cards. GPUs turned out to be extraordinarily fast at one specific operation: dense matrix multiplication. Take a large grid of numbers, multiply it by another large grid, do it thousands of times in parallel. That is what GPUs were built for. Games need that. Intelligence, it turns out, may not.

Fei-Fei Li released ImageNet in 2009 with 1.2 million labeled images. Three years later, Alex Krizhevsky trained a neural network on two consumer GPUs and won the ImageNet competition by 10.9 percentage points. In machine learning competitions, improvements of half a percent are notable. Krizhevsky won by eleven. Everyone noticed. What followed was not a scientific revolution. It was a hardware revolution wearing scientific clothing.

The lock-in mechanism is worth understanding because it explains everything that came after. GPUs make dense matrix multiplication cheap, so architectures optimized for that operation win benchmarks. Venture capital floods toward benchmark winners. Companies hire for GPU expertise because results live there. Universities train students in GPU methods because industry demands it. Doctoral programs drop coursework in alternative approaches because nobody hires for those skills. The professors who know symbolic AI, neuromorphic computing, and probabilistic systems retire, nobody replaces them, and the knowledge dies.

Now look at what GPUs do well versus what intelligence might actually require. GPUs are fast at dense matrix operations, parallel processing of identical computations, and backpropagation through smooth differentiable functions. They are slow at sparse event-driven computation, irregular memory access, sequential dependencies, symbolic manipulation, and logical reasoning. Biological brains do most of that second list. Your brain does not activate all neurons simultaneously — it uses sparse, event-driven signaling, with roughly 1 to 4 percent of neurons firing at any given moment. Information encodes in spike timing, not continuous values. The human brain runs 86 billion neurons on 20 watts through extreme sparsity and parallelism. We built our field on algorithms that activate every single parameter for every single computation, consuming megawatts to train and kilowatts to run. We did not choose algorithms that fit intelligence. We chose algorithms that fit our silicon.

Cloud economics made it worse. AWS, Azure, and Google Cloud sell compute by the hour, by the FLOP, by the terabyte. Revenue scales with consumption. Efficient algorithms mean less compute sold, and compute-intensive algorithms mean more compute sold. Cloud providers did not maliciously suppress efficient methods; they responded rationally to their pricing model, which naturally rewards waste. Not one major cloud provider offers pricing advantages for sample-efficient or energy-efficient approaches. The feedback loop closed completely. Researchers need compute, so they use cloud infrastructure. They optimize for the GPUs those platforms provide. They publish results showing better performance with scale. Other researchers adopt the same approach. Cloud providers see more usage and invest in more GPUs. No coordination required. Just locally rational decisions producing a globally irrational outcome.

---

## September 30, 2012

AlexNet won ImageNet with a 15.3 percent error rate. Second place got 26.2 percent. The architecture was 8 layers deep, roughly 60 million parameters, trained on two NVIDIA GTX 580 GPUs available at retail. Training time was six days.

The cascading effects took about eighteen months. November 2012, Hinton starts consulting for Google. March 2013, Google acquires his company DNNresearch. January 2014, Google acquires DeepMind for roughly 500 million dollars. September 2013, Facebook hires Yann LeCun. Microsoft, Baidu, and Amazon launch major AI hiring programs. The field got strip-mined for talent inside two years.

Yoshua Bengio estimated in 2014 that roughly 50 world-class deep learning experts existed globally. Not 5,000. Not 500. Fifty. DeepMind hired approximately twelve of them. That is 24 percent of global expertise in one acquisition. By 2015, Google employed somewhere between 5 and 50 percent of the field according to Peter Norvig's carefully worded public statements. This was not hiring. This was monopolizing epistemic capacity. If Google pays 500 million dollars for 50 people, that is 10 million dollars per researcher, at a time when academic salaries ran 100,000 to 200,000 dollars. The industry premium was 50x to 100x. Universities lost the only places where alternative AI approaches could be explored outside quarterly earnings pressure.

The hidden cost was not just that researchers moved, it is that they stopped teaching alternatives entirely. Knowledge about symbolic AI, hybrid systems, neuromorphic computing, and sample-efficient learning died with the generation that held it. Nobody trained replacements because industry hired only for GPU expertise, and universities taught only what industry would hire.

Before 2012, research evaluation was multidimensional. People measured sample efficiency, proved theoretical guarantees about convergence and generalization, ran computational complexity analysis with real Big-O notation, and checked biological plausibility. After 2012, evaluation collapsed into leaderboard position. ImageNet top-5 accuracy became the number everyone optimized. Scientific understanding got replaced by competitive gaming.

Goodhart's Law: when a measure becomes a target, it stops being a good measure. Benchmarks were designed to evaluate progress toward understanding intelligence. Once funding and careers depended on benchmark scores, research optimized for benchmarks instead of intelligence. What stopped being measured — sample efficiency, energy per task, compositional generalization, causal reasoning, and systematic generalization beyond the training distribution — disappeared not because it stopped mattering, but because existing scaling approaches would show weaker results and the incentives pointed elsewhere.

---

## What AI Looked Like Before Benchmarks Ate Everything

Most people reading this were not alive when AI actually worked inside hospitals. That history deserves more than a paragraph.

Edward Shortliffe began building MYCIN at Stanford University in 1972 as his doctoral dissertation. The system diagnosed bacterial infections of the blood and meningitis by asking physicians a structured sequence of questions, then working backward through roughly 600 production rules encoded as IF-THEN statements to identify the likely organism and recommend the appropriate antibiotic at the correct dosage for the patient's body weight. Every conclusion came with a certainty factor, and every recommendation came with an explanation. If a physician asked why MYCIN suggested a particular drug, the system walked through precisely which rules it had fired and why.

In the formal evaluation published in JAMA in 1979, Shortliffe presented ten real patient cases involving life-threatening blood infections to eight human evaluators and MYCIN. The results went to eight expert infectious disease specialists around the country who did not know which recommendations came from the computer and which came from humans. MYCIN received an acceptability rating of 65 percent. The five Stanford Medical School faculty members in the evaluation scored between 42.5 and 62.5 percent. The expert judges actually agreed more with MYCIN's recommendations than with those of the Stanford faculty, and a separate accuracy study found MYCIN selected appropriate antimicrobial therapy in 90.9 percent of cases. The system performed at specialist level using 600 human-readable rules that any physician could read, audit, or challenge.

MYCIN was never deployed in hospitals. Not because it did not work, but because nobody could figure out who bore legal liability if it made a wrong call.

John McDermott at Carnegie Mellon University built XCON in 1978 for Digital Equipment Corporation. DEC faced a specific problem: configuring VAX computer systems for customers required selecting the right components from a catalog of 420 possible parts, and technicians made enough errors that DEC regularly shipped free replacement parts at significant cost. DEC had already tried and failed twice to write a conventional program to solve this, first in FORTRAN and then in BASIC. McDermott encoded the configuration expertise of DEC's engineers as approximately 2,500 production rules written in the OPS5 language. XCON first went into production use in 1980 at DEC's plant in Salem, New Hampshire. By 1986, it had processed 80,000 customer orders and achieved 95 to 98 percent accuracy, saving DEC an estimated 25 million dollars per year by reducing errors, speeding assembly, and eliminating the cost of fixing misconfigurations after delivery.

XCON worked. It was deployed. It ran in production for years. And it did so using interpretable rules that any engineer could read, audit, and modify.

Today, in 2026, you cannot deploy a neural AI system for medical diagnosis in most regulated healthcare environments because you cannot explain its decisions. The EU AI Act, the FDA's guidance on AI-based medical devices, and hospital liability frameworks all require the ability to trace how a conclusion was reached. MYCIN could do that in 1974. Modern deep learning systems generally cannot. We had explainable AI that worked at specialist-level accuracy in clinical settings, and we abandoned it because it did not produce impressive demo numbers on benchmarks. Now explainability is a research frontier we are trying to recover. This is not progress. This is a circle.

---

## The Soviet AI Program Nobody Taught You About

Western AI history has a significant gap in it, and filling that gap changes how you understand what knowledge was lost.

In the early 1950s, cybernetics was politically suspect in the Soviet Union, labeled by Stalin-era ideologues as a bourgeois pseudoscience. After Stalin's death in 1953, that changed dramatically. Cybernetics became not just acceptable but a national priority, and what followed was a parallel AI research program that the Western field has almost entirely erased from its own history.

Viktor Glushkov was born in Rostov-on-Don in 1923, the son of a mining engineer. He survived the German occupation during the war — he lost his mother, who was helping partisans — and for this reason was barred from studying in Moscow or Leningrad after the war, because all those who had been encircled by German forces were treated as politically suspect in the USSR. He found his way to Rostov University instead, passed four years of exams in a single year to accelerate his studies, and graduated with degrees in both technical and mathematical sciences in 1948. In 1952, working at a forestry institute in the Urals, he solved a generalization of Hilbert's fifth problem — each of Hilbert's 23 problems represented a frontier of world mathematics, and solving even one was a career-defining achievement. It made him suddenly famous. He was offered positions in Moscow, Leningrad, and Kyiv. His wife chose Kyiv because she wanted to go south, and as it later turned out, that was a lifelong choice — in Kyiv, Glushkov found the environment he needed.

He pivoted entirely to computing after reading Anatoly Kitov's book *Electronic Digital Machines*, published in 1956, which he described as the moment that changed everything. In 1962 he established the Institute of Cybernetics of the Ukrainian Academy of Sciences and became its first director. He filled it with ambitious young researchers — the average age was about 25 — and set them to work on problems the West was not yet taking seriously: automated theorem proving, formal verification of programs, algebraic models of computation, and intelligent management of complex systems. His institute produced the MIR series of computers — essentially personal computers for engineers, with keyboards and cathode-ray tube screens, a decade before personal computers existed in the West. In 1960, Glushkov conducted experiments with remote industrial control using his Kyiv computer, guiding processes at a facility 500 kilometers away. He published nearly 800 works over his career and trained over a hundred doctoral students.

His most ambitious project was OGAS — the All-State Automated System for the Gathering and Processing of Information for the Accounting, Planning and Governance of the National Economy. First proposed in 1962, OGAS was designed as a real-time national computer network spanning the entire Soviet Union, with a central computing center in Moscow connected to up to 200 regional centers and up to 20,000 local terminals. Glushkov estimated that if paper-based Soviet planning methods continued unchanged, the planning bureaucracy would need to grow fortyfold by 1980 just to keep functioning. The network was the only alternative. He designed it with deliberate decentralization: any authorized node could contact any other node without routing through the central hub — distributed network architecture, built independently, at the same time ARPANET was being constructed on the other side of the Iron Curtain. The US government noticed. Arthur Schlesinger Jr., historian and special assistant to President Kennedy, described an all-out Soviet commitment to cybernetics as providing a potential tremendous advantage in production technology, complex industries, feedback control, and self-teaching computers. The CIA monitored Glushkov's work closely.

On the morning of October 1, 1970, Glushkov walked into Stalin's former office in the Kremlin to present his funding request to the Politburo. He was an alert man with piercing eyes behind black-rimmed glasses, with the kind of mind that, given one problem, derived a method for solving all similar problems. He warned the assembled officials directly: if the full OGAS was not built now, the Soviet economy would encounter such difficulties in the second half of the 1970s that they would have to return to the question regardless. But when he looked around the room, the two chairs that mattered most were empty. Brezhnev and Kosygin — General Secretary and Prime Minister, the two most powerful men in the Soviet state and the most likely supporters of the project — were absent from the meeting, ostensibly on diplomatic business. The vacuum was filled by Finance Minister Vasily Garbuzov, who had no interest in a nationwide computer network that would shift economic power away from his ministry. Garbuzov argued against the project, at one point suggesting that computers were already being used effectively on chicken farms and perhaps that was the right scale to consider first. He had reportedly threatened Kosygin privately before the meeting that if the Central Statistical Administration retained control over OGAS, his ministry would block the whole thing. With the two supporters gone, the Politburo sided with Garbuzov. The full project was denied. Glushkov was offered a compromise: build disconnected systems for individual ministries, with no network connecting them. The planning bureaucracy was retained. A reviewer writing for MIT later put it precisely: Soviet attempts to build a national computer network were undone by socialists who behaved like competitive capitalists.

Glushkov spent the rest of his life spending half the week in Moscow and half in Kyiv, pushing truncated versions of the project through defense ministries that wanted the efficiency gains without the distributed network. He died in January 1982, still working, of a brain tumor. He was 58 years old. In the last nine days of his life, having regained consciousness from a coma, he dictated his memories and ideas to his daughter Olga.

But this section is not actually about OGAS. OGAS is the famous part of the story because it is dramatic — a Soviet internet, denied by bureaucrats, lost to history. The connection to this essay's argument runs deeper, through the people who worked in Glushkov's institute and what they were building.

One of them was Kateryna Yushchenko. She was born in 1919 in Chyhyryn, central Ukraine. In 1937 her father was arrested as a Ukrainian nationalist and died in a gulag. When her mother went to authorities to inquire, she too was arrested and imprisoned for ten years. Yushchenko was eighteen and had just started at Kyiv University, which expelled her as the daughter of enemies of the people. The only institution that would accept her on a full scholarship was a university in Samarkand, Uzbekistan. She made her way there, survived the war, returned to Ukraine, and in 1950 defended a doctorate from the Kyiv Institute of Mathematics — the first woman in the USSR to earn a PhD in physical and mathematical sciences in programming.

In 1955, working with the MESM computer — one of the first computers in continental Europe — she created the Address Programming Language. The language introduced indirect addressing, the ability to refer to a memory cell that holds the address of data rather than the data itself. This is the pointer, one of the fundamental concepts in all of modern computer science, present in every systems language written since. Her language appeared in 1955, two years before FORTRAN, three years before COBOL, five years before ALGOL. Western computer science credits Harold Lawson with inventing the pointer variable in 1964 for PL/1. Lawson received the Computer Pioneer Award from the IEEE in 2000 for this invention. Yushchenko had done it nine years earlier and run it on production hardware. Her language was implemented on most Soviet and Chinese computers for over twenty years and controlled the Apollo-Soyuz space mission in 1975. She supervised 45 doctoral students and wrote more than 200 publications, translated into German, Czech, Hungarian, French, and Danish. She died in 2001. In Western computer science curricula, she is essentially unknown.

Glushkov's institute was not primarily doing what we would today call neural network research. It was doing formal methods, symbolic reasoning, automated theorem proving, distributed systems, and explainable computational logic — exactly the tradition this essay argues was killed by the hardware lottery. When the Soviet Union collapsed in 1991, that entire research tradition was archived in Russian-language journals, associated with a political system that had just failed, and therefore easy to dismiss. Solomonoff worked in isolation from it. Pearl did not know it existed. The theoretical foundations built in Kyiv, Novosibirsk, and Moscow throughout the 1960s and 1970s were not absorbed into Western AI at the moment the field was consolidating around neural networks. We did not just fail to build on that work. We did not even know it existed.

The hardware lottery has a geopolitical dimension. It was not only Western economic incentives that narrowed the possibility space of AI. It was also the accident of which civilization's research tradition happened to survive the Cold War. One tradition went through Bell Labs, MIT, and Stanford. The other went through Kyiv and Novosibirsk, and it ended.

---

## The People We Buried

We talk about this as a graveyard of ideas. We should talk about it as a graveyard of people — specific human beings who built rigorous, working, mathematically complete frameworks for intelligence, and watched those frameworks get defunded because they did not run fast on gaming cards.

### Judea Pearl and the Mathematics We Refused to Use

Judea Pearl won the Turing Award in 2011, the highest honor in computer science, for building the formal mathematical framework for reasoning about cause and effect. His do-calculus, structural causal models, and the ladder of causation are not philosophical speculation. They are precise mathematical machinery with decades of verified application in medicine, economics, and policy.

His argument against current AI is specific and devastating. Every large language model, every image classifier, every recommendation system operates at what Pearl calls the first rung of the ladder of causation: association. It learns P(Y|X), the probability of Y given that we observe X. That is all it does.

The second rung is intervention. What happens to Y if we actively change X? The notation P(Y|do(X)) is not the same as P(Y|X). You cannot compute intervention from observation using observational data alone. You need a causal model. Pearl built the mathematics to do this in the 1980s and 1990s. Here is why this matters in practice: a medical AI trained on hospital data observes that sicker patients receive more treatment, and learns that more treatment correlates with worse outcomes. Ask it a first-rung question about what outcomes patients with these symptoms typically see, and it answers correctly. Ask it whether to give this patient more treatment, and it gives you the systematically wrong answer, because treatment and outcome are confounded by severity. This is not a training data problem. No amount of additional data fixes it. Pearl proved this mathematically in 1995.

The third rung is counterfactual: given that X happened and Y resulted, what would Y have been if X had been different? Legal reasoning, scientific inference, moral responsibility, and individual treatment estimation all require this. Language models produce text that sounds like counterfactual reasoning because they trained on humans who do it, but when a problem requires genuinely novel causal inference outside the training distribution, they fail. Pearl published a paper in 2018 listing specific tasks provably impossible for systems that only learn correlations. The field's response was largely silence — not refutation, just silence. Because integrating causal structure into neural networks is hard, produces no benchmark improvements on ImageNet, and runs inefficiently on GPU matrix operations. Pearl is 88 years old and still publishing. The field is still not listening.

### Vladimir Vapnik and the Guarantees We Threw Away

Vladimir Vapnik, working with Alexey Chervonenkis at the Institute of Control Sciences in Moscow in the 1960s, built VC theory: a rigorous mathematical framework for understanding when a learning algorithm generalizes from training data to new data. The VC dimension measures hypothesis class complexity, structural risk minimization tells you how to balance fit against complexity to get provable generalization guarantees, and sample complexity bounds take the form O(d/epsilon) for VC dimension d, meaning you can calculate in advance exactly how much data you need to achieve a given error rate with a given probability.

At AT&T Bell Labs in 1995, Vapnik introduced Support Vector Machines with Corinna Cortes. SVMs find the maximum margin hyperplane separating classes, using the kernel trick for nonlinear problems, and they came with theoretical guarantees you could actually prove. SVMs dominated machine learning through the mid-2000s, and then AlexNet happened. Within three years the field stopped caring. Not because SVMs were proven wrong, not because anyone showed the theory was flawed, but because neural networks given enough GPU compute and labeled data scored higher on benchmarks, and the guarantees became inconvenient. Before 2012, you could calculate sample complexity bounds in advance. After 2012, nobody knows. The deep learning community genuinely cannot tell you in advance how much data a model needs, whether it will generalize, or when it will fail. We traded provable guarantees for higher benchmark numbers.

Vapnik, incidentally, was also working in Moscow. The Institute of Control Sciences sits in the same intellectual tradition as Glushkov's Kyiv institute — formal, mathematically grounded, focused on theoretical guarantees rather than empirical performance. The hardware lottery did not just kill Western alternatives. It killed an entire hemisphere's worth of them.

### Jürgen Schmidhuber and the Framework That Got Stolen Without Credit

Schmidhuber invented Long Short-Term Memory networks in 1997 with Sepp Hochreiter, solving the vanishing gradient problem that made training deep recurrent networks impossible. His broader research program asked a more fundamental question: how do you assign credit across long causal chains, when the action that produced a good outcome happened many steps ago? His 1991 PhD thesis was titled "Dynamic Neural Networks and the Fundamental Spatio-Temporal Credit Assignment Problem." He spent his career on this, building meta-learning systems that learn how to learn, and formal theories of curiosity and intrinsic motivation grounded in information-theoretic compression. His argument: intelligence is the construction of compressed, predictive models of the environment.

He also built practical systems that won international competitions on handwriting recognition, speech recognition, and sequence prediction before deep learning became mainstream. When the field exploded after 2012, Schmidhuber found himself writing public documents arguing that the dominant figures had systematically failed to credit earlier work. He was not wrong about the credit. The practical cost was that his work on meta-learning and on compression as intelligence stayed marginal for years. These ideas are finally getting serious attention in 2025 under different branding, but without the theoretical framework he built.

### Ray Solomonoff and the Optimal Theory Nobody Uses

Ray Solomonoff died in 2009. He invented algorithmic probability in 1960 and published the first formal theory of inductive inference in 1964. The core idea: given a sequence of observations, the best prediction of the next observation is a weighted average over all computable theories consistent with the data, weighted by their simplicity in bits. This is Solomonoff induction. It is provably the optimal inductive inference algorithm. It is also uncomputable, which is why nobody uses it directly.

But it provides the theoretical ideal against which all practical learning algorithms can be measured. Jorma Rissanen's Minimum Description Length from 1978 is a computable approximation: choose the hypothesis that minimizes the combined length of the model description plus the data description given the model. This formalizes Occam's Razor precisely. Good learning is compression. If a model genuinely understands a pattern, it compresses the data that instantiates that pattern. Current deep learning models are poor at compression by this measure. A GPT-class model has 1.8 trillion parameters trained on a few trillion tokens, and the compression ratio is bad. A model that understood language at the level human linguists do would represent those patterns with vastly fewer bits. Nobody measures this. Bits-per-parameter does not appear on a leaderboard. Solomonoff is essentially unknown outside theoretical computer science.

### The Alchemy Accusation

Ali Rahimi, a Google researcher, stood up at NeurIPS 2017 to accept his Test of Time award and told the assembled audience that machine learning had become alchemy. He showed that researchers had stripped most of the complexity from a state-of-the-art translation algorithm and it translated better — meaning the original creators did not understand what they had built. He meant practitioners who add batch normalization, dropout, or a particular learning rate schedule because it always works, with no understanding of why it works or when it will fail. His precise statement: "We are building systems that govern healthcare and mediate our civic dialogue. We can influence elections. I would like to live in a society whose systems are built on top of verifiable, rigorous, thorough knowledge, and not on alchemy." The audience gave him a standing ovation. Yann LeCun called it insulting. Citation counts on benchmark papers continued to climb.

---

## The Architecture Graveyard

The following approaches meet four specific criteria: published peer-reviewed research proving they worked, theoretical advantages in at least one measurable dimension, documented evidence of funding decline, and an identifiable mechanism explaining why they lost the hardware lottery. No speculation. Just things that worked and died anyway.

### Spiking Neural Networks

Real neurons do not do continuous mathematics. They spike — discrete voltage spikes, that is the entire mechanism. The human brain achieves 86 billion neurons on 20 watts through event-driven computation where energy gets consumed only when neurons actually fire, sparse activation where only 1 to 4 percent of neurons are active at any moment, and temporal coding where information encodes in spike timing rather than activation magnitude.

The efficiency numbers are real. Best-case measurements on neuromorphic hardware show spiking neural networks on Intel's Loihi chips using roughly 10 to the power of negative 11 joules per synaptic operation. Standard deep neural networks on GPUs use 10 to the power of negative 6 to negative 9 joules per multiply-accumulate operation. On compatible tasks, the gap is 100 to 1,000 times. The caveat matters: that advantage only appears on tasks matching spike-compatible processing like temporal pattern recognition or event-driven perception. Dense matrix multiplication on a spiking network is actually worse than standard approaches.

SNNs failed to scale because spike generation is non-differentiable, which breaks backpropagation, and event-driven processing does not map to dense matrix operations. PyTorch and TensorFlow do not support spike-timing-dependent plasticity — the learning rule spiking networks actually use — and no mature developer ecosystem exists. In 2015, roughly 20 research groups globally worked on spiking neural networks. By 2024, maybe 12 remained. Neuromorphic VC investment finally exceeded 200 million dollars in 2025, while GPU infrastructure investment that same year was roughly 580 billion dollars. The ratio is 2,900 to 1.

The opportunity cost is concrete. If neuromorphic hardware had received GPU-level development investment from 2012 to 2024, equivalent model training runs at 100 times lower energy — 50,000 megawatt-hours becomes 500 megawatt-hours. We did not fund that path because nobody's quarterly revenue depended on it.

### Capsule Networks

In 2017, Geoffrey Hinton published "Dynamic Routing Between Capsules." This requires a moment. Hinton co-created backpropagation in 1986. His student created AlexNet in 2012. He architected modern deep learning. In 2017, he published a paper saying we made a fundamental mistake.

The problem he identified: convolutional neural networks use max pooling for translation invariance, which lets you detect a cat anywhere in an image but discards spatial relationships between features entirely. CNNs detect eyes, nose, and mouth without caring whether those features are arranged in any anatomically coherent configuration. They will happily classify a scrambled face as a face because the individual features are present. Capsule networks output vectors instead of scalars, encoding pose information including position, orientation, and size, and use dynamic routing to create part-whole hierarchies. On MNIST overlapping digits, capsule networks outperformed CNNs using 100 times less training data.

Two explanations exist for why they failed, and intellectual honesty requires presenting both. The infrastructure explanation: dynamic routing does not map efficiently to GPU matrix operations, requiring completely new tooling and expertise, and no benchmark breakthrough justified the switching costs. The fundamental limitation explanation: the routing mechanism has O(n squared) computational complexity, which might be intrinsic to the approach regardless of hardware. Attempts to scale capsules to ImageNet hit 100x compute overhead. What we actually know is that capsules work on MNIST, address a real CNN limitation regarding spatial reasoning, and failed to scale to ImageNet with 2017 to 2020 methods. Whether the scaling issues are fundamental or fixable is unknown, because research stopped. Between 2017 and 2020, roughly 50 papers examined capsule networks. Between 2020 and 2024, about 20. No major lab adopted them at scale.

### Neuro-Symbolic Integration

Combining neural networks for pattern recognition with symbolic reasoning for logic and knowledge makes obvious theoretical sense. Neural components handle noisy perceptual data, symbolic components provide explainability, logical guarantees, and compositional reasoning. This is not a new idea: Sun and Bookman wrote "Computational Architectures Integrating Neural and Symbolic Processes" in the 1990s, and Gary Marcus argued in 2018 that we could not construct rich cognitive models without hybrid architecture. He turned out to be right.

Systems that actually worked and received inadequate funding: DeepProbLog in 2018 combined neural networks with logic programming and produced promising results. MIT-IBM's Gen in 2019 combined probabilistic and deep learning, and Intel used it for real applications. The funding imbalance was roughly 100 to 1. Pure deep learning investment from 2012 to 2024 ran around 100 billion dollars; neuro-symbolic research received perhaps 1 billion. The knowledge extinction is measurable separately: in 1990, 60 percent of computer science departments offered a course in logic programming. By 2000, 40 percent. By 2010, 15 percent. By 2024, fewer than 5 percent. The expertise required to build neuro-symbolic systems is vanishing from universities in real time.

### Backpropagation's Biological Impossibility

Francis Crick, Nobel laureate and co-discoverer of DNA structure, identified in 1989 that backpropagation is fundamentally incompatible with biological neural architecture. Backpropagation requires the gradient of the loss with respect to a weight to depend on the transpose of the forward weights, but forward synapses go axon to dendrite in a unidirectional physical structure, and no known biological mechanism maintains symmetric feedback across billions of synapses. Timothy Lillicrap showed in 2014 that feedback alignment using random feedback weights instead of the transpose still allows networks to learn. Rao and Ballard documented predictive coding in 1999, showing how hierarchical prediction-error signals could drive learning locally, consistent with neuroscience. Predictive coding research received less than 0.5 percent of deep learning funding. We built an entire field on an algorithm that Crick told us in 1989 cannot be how biological intelligence works.

### Mixture-of-Experts: Thirty Years Late

Robert Jacobs, Michael Jordan, Steven Nowlan, and Geoffrey Hinton published "Adaptive Mixtures of Local Experts" in 1991. Multiple specialist networks, a gating mechanism routing each input to relevant experts, only a fraction of parameters activating for any given input: computational efficiency through sparse activation. This paper was effectively ignored for thirty years, because dense networks were good enough, GPU infrastructure was optimized for dense computation, and no financial incentive existed to invest in routing mechanisms.

In 2017, Google's Noam Shazeer published "Outrageously Large Neural Networks," rediscovering the same idea with modern tools. GPT-4 reportedly uses MoE architecture. DeepSeek's R1 model uses MoE with 671 billion total parameters but only 37 billion active per token, achieving GPT-4-class performance at approximately 6 million dollars in training cost versus hundreds of millions spent on comparable OpenAI training runs. The efficient architecture was published in 1991. It saw serious use starting in 2017. Twenty-six years lost. Not because the idea was wrong, but because inefficiency was not penalized.

---

## The Economic Structure That Produced This

This section does not claim tech companies intentionally suppressed superior technologies. It analyzes how profit models structurally favored certain research directions, and how rational individual decisions produced a collectively irrational outcome.

Cloud providers sell compute by the hour. Revenue scales with consumption. Efficient algorithms mean less compute sold, and compute-intensive algorithms mean more compute sold. This is not malicious design; it is how usage-based pricing works. The pricing model that would have changed everything — accuracy-per-joule instead of compute-per-hour — was never economically viable for cloud providers because it would mean selling less compute.

Venture capital selection pressures compounded this. Time to demo for GPU-scalable deep learning: three to six months, fine-tuning something that already exists. Time to demo for sample-efficient hybrids: one to two years to build new architecture. VC fund cycles run two to three years. The math makes alternative approaches structurally unfundable regardless of technical merit. Between 2012 and 2022, over 50 billion dollars went into AI startups, roughly 95 percent focused on scaling existing architectures, and zero unicorns got built on neuromorphic, symbolic, or hybrid approaches.

Academic career incentives completed the loop. PhD programs run four to five years, three to five top-venue publications are required to graduate, and review cycles run three to six months per paper. You must show publishable results within twelve to eighteen months per project. Industry machine learning positions pay 300,000 to 500,000 dollars for PyTorch expertise; neuromorphic and symbolic research positions pay 150,000 dollars where they exist at all. The rational student learns skills with the highest job market value. The knowledge extinction spiral follows directly: professors who know symbolic AI and formal methods retire, grad students avoid learning fields with no job market, universities stop hiring in those areas, course offerings disappear, and the next generation has zero exposure to the ideas. Institutional knowledge dies completely.

Research funding tiers created a capital intensity filter. Symbolic, hybrid, and neuromorphic approaches can demonstrate ideas at the 10,000 to 1 million dollar tier. Scaling approaches require 1 million to 10 million to show competitive results. Funding committees prefer approaches with proven scale at the 10 to 100 million dollar tier. Alternative approaches need tier-3 funding to prove viability, but to get tier-3 funding you must show tier-4 results. DARPA's program for probabilistic programming got 50 million dollars over four years from 2013 to 2017, then ended. DeepMind's budget runs roughly 1 billion dollars per year, sustained. The funding ratio for incumbent versus alternative is approximately 100 to 1.

The open source counterargument deserves an honest response. PyTorch is free. TensorFlow is free. Hugging Face hosts thousands of models. Doesn't democratized access undermine the monopolization claim? No, it does not. You can download GPT-2 for free and train it from scratch if you have 50,000 dollars in cloud credits. Knowledge is open. Experimentation is gated by capital. PyTorch is optimized for GPU operations; implementing capsule networks in it is painful and slow, and implementing spiking neural networks is ten times harder than standard DNNs. Open source infrastructure encodes architectural assumptions. Open-sourcing every automobile design does not help if you want to build a bicycle.

---

## What Your PhD Program Stopped Teaching

Compare two students. One enters a Stanford computer science PhD program in 2008. The other enters the same program in 2024.

The 2008 student takes courses in logic programming, learning Prolog and building systems that reason through formal rules. They study formal verification, learning to prove properties of programs mathematically before running them. They take probabilistic graphical models, covering Bayesian networks, Markov random fields, and inference algorithms. They study computational learning theory, working through PAC learning, VC dimension, and sample complexity bounds. They take a cognitive architectures course examining how symbolic and connectionist models of cognition interact.

The 2024 student takes courses in deep learning fundamentals using PyTorch. They study transformer architectures and attention mechanisms. They learn fine-tuning and RLHF. They take benchmark evaluation courses examining how to measure model performance on standard datasets. Optional electives cover diffusion models and foundation model deployment.

The 2008 curriculum asked: what is intelligence and how does learning work mathematically? The 2024 curriculum asks: how do you use the tools that already exist?

Stanford's course catalog is publicly archived. In 2008, Stanford offered CS 221 (Artificial Intelligence: Principles and Techniques, covering search, knowledge representation, logic, and planning), CS 228 (Probabilistic Graphical Models), CS 229 (Machine Learning including theoretical analysis), and CS 154 (Formal Languages and Automata). By 2024, CS 221 still exists but the curriculum shifted heavily toward learning methods. Courses focused on sample complexity theory, formal verification of AI systems, and cognitive modeling either vanished or became obscure electives with minimal enrollment. The expertise required to build hybrid neuro-symbolic systems, to reason about generalization bounds, to design interpretable rule-based systems — this is no longer produced by graduate training.

This is not a critique of individual professors or administrators. Each decision was locally rational. Students wanted jobs, industry hired for PyTorch, universities hired professors who could attract grants, and grants went to GPU-compatible research. No single person decided to stop teaching logic programming. It just became, slowly and then all at once, something nobody needed to know.

The result is a generation of AI researchers who genuinely cannot read Prolog, cannot reason about formal guarantees, do not know what VC dimension means, and have never built a system that could explain its own reasoning. They are expert engineers of a specific technology stack. They are not, in the scientific sense, students of intelligence. What this costs is not just theoretical elegance. MYCIN could explain its reasoning in 1974. Modern hospital AI systems are being blocked from deployment by regulators in 2026 because they cannot explain their reasoning. The knowledge that would solve this problem — causal modeling, formal rule systems, symbolic verification — was taught in 2008 and dropped by 2024.

---

## The Scaling Myth

Scaling laws are not laws. They are empirical observations that performance improves with model size, data, and compute within a specific regime. The 2020 narrative from Kaplan et al. at OpenAI claimed smooth power-law scaling would continue indefinitely. Venture capital and media amplified this into a Moore's Law for AI.

Scaling law papers show log-log plots. A straight line on a log-log plot looks like continuous progress, but what it actually means is that to reduce loss by 2x, you need roughly 1,000,000x more compute — exponential resource requirements for linear gains. GPT-3 training used 1,287 megawatt-hours and represented a large capability leap. GPT-4 training used roughly 50,000 megawatt-hours, forty times more energy, for a smaller leap. GPT-5 training estimates run around 500,000 megawatt-hours. The S-curve appeared exactly when scaling law proponents said it would not.

The Lottery Ticket Hypothesis from Frankle and Carlin in 2018 proves the waste was measurable. Dense networks contain sparse subnetworks at initialization that are 10 to 20 percent of the original size and match the full network's performance. We trained 5 to 10 times more parameters than necessary. Pruning after training removes 90 percent of weights with minimal accuracy loss. Quantization from 32-bit to 8-bit delivers 4x compression with minimal accuracy loss. Knowledge distillation produces models 100 times smaller with 95 percent of the performance. All of these retrofit solutions prove waste was baked in from the start. Waste was economically rational given cloud pricing that rewards consumption.

In November 2024, Ilya Sutskever, OpenAI co-founder, told Reuters that the age of scaling was over and everyone was looking for the next thing. The next thing they are looking for is what the researchers described in the previous sections were building in 2013.

---

## The Energy Crisis

Your electricity bill went up this year. In Virginia it jumped 30 percent since 2021. In New Jersey, PSE&G warned customers about a 17 percent hike. A man in Baltimore named Kevin Stanley, living on disability payments, told Bloomberg his energy costs are 80 percent higher than three years ago. PJM's own independent market monitor documented that consumers across 13 states will pay 16.6 billion dollars extra from 2025 to 2027 to secure power for data centers, and called it, in writing, a massive wealth transfer from ordinary people to the data center industry.

Google, Amazon, and Microsoft are the data center industry.

Human brain: 86 billion neurons, roughly 100 trillion synapses, 20 watts continuous power, roughly 10 to the power of negative 11 joules per synaptic operation. GPT-4 training: approximately 50,000 megawatt-hours, 1.8 trillion parameters, roughly 10 to the power of negative 6 joules per operation. That is 100,000 times worse than biological computation. GPT-4 inference at 700 million queries per day equals roughly 35,000 US homes' daily electricity consumption. The gap comes from dense activation — deep learning activates all parameters for every computation while biological brains activate roughly 1 to 4 percent of neurons at any moment. Dense won because GPUs optimize for dense matrix multiplication and existing libraries built for dense operations. Hardware determined the algorithm.

US data centers consumed approximately 183 terawatt-hours in 2024, more than 4 percent of national electricity, comparable to Pakistan's entire annual demand. Data center electricity consumption is projected to grow at approximately 15 percent per year from 2024 to 2030, four times faster than all other electricity sectors combined. In Texas, grid interconnection requests from data centers exploded from 56 gigawatts in September 2024 to 205 gigawatts in October 2025, nearly quadrupling in thirteen months. The CEO of Exelon warned publicly that AI could cause a 900 percent jump in power demand in the Chicago area. Texas passed legislation allowing its grid operator to remotely disconnect data centers during emergencies. The grid itself is becoming the limiting factor.

If Intel Loihi 2 had received GPU-level investment starting in 2012, equivalent model training runs at 100 times lower energy would be 500 megawatt-hours instead of 50,000. We did not fund that path because nobody's quarterly revenue depended on it.

---

## The Scientific Method We Abandoned

Science and engineering ask different questions. Engineering: does it work, can we build it, does it scale? Science: why does it work, through what mechanism, when will it fail given which boundary conditions? Why do transformers work? Engineering says they achieve 90 percent accuracy on GLUE. Science would answer: because self-attention approximates X which enables Y. We do not have that explanation. When will scaling stop? Engineering says when we run out of compute. Science would answer: at architectural capacity C given data distribution D. We do not have those bounds.

Pre-2012 research had scientific frameworks. PAC learning gave sample complexity bounds growing as O(d/epsilon) for VC dimension d. VC theory bounded generalization error by model complexity. These were falsifiable, testable, and predictive. Post-2012 deep learning has empirical observations: bigger models perform better usually, more data helps usually, overparameterization does not hurt somehow. Descriptive, not explanatory. NeurIPS 2012 had 30 percent of papers including theoretical analysis. NeurIPS 2023 had less than 10 percent. Rich Sutton's "bitter lesson" from 2019 stated that general methods leveraging computation are ultimately most effective — translation: theory does not matter, just scale. This is engineering philosophy, not science. No theory means no predictions. No predictions means no science. Just empirical tuning. This is what Rahimi called alchemy.

---

## The Replication Crisis Nobody Talks About

Every mature science has mechanisms for verifying claims. In physics, independent labs replicate experiments. In biology, findings require confirmation from multiple research groups before entering the canon. In chemistry, synthesis procedures are published in enough detail that any competent lab can reproduce them. AI has a replication crisis built into its economics, and the scale of the problem is qualitatively different from anything in the history of science.

GPT-3 cost approximately 4.6 million dollars to train. GPT-4 cost somewhere above 100 million dollars by Sam Altman's own public statement, with the amortized hardware cost for the full development process estimated at around 90 million dollars in an Epoch AI 2024 analysis, not counting the hundreds of millions in staff costs and infrastructure. Epoch AI found that the amortized cost of training frontier AI models has grown at roughly 2.4x per year since 2016, and concluded that training runs will exceed 1 billion dollars by 2027, meaning that only the most well-funded organizations will be able to finance them. The organizations that can independently verify claims made about frontier AI models today are: OpenAI, Google DeepMind, Microsoft, Meta, and possibly Anthropic and xAI. That is approximately five to seven entities on the entire planet. Every university, every national research lab, every government agency, and every independent researcher must simply trust what these companies report about their models, because the cost of verification is prohibitive.

The GPT-4 technical report, published by OpenAI in March 2023, states explicitly in its own text that given both the competitive landscape and the safety implications of large-scale models like GPT-4, the report contains no further details about the architecture — including model size, hardware, training compute, dataset construction, training method, or similar. The paper that introduced one of the most consequential AI systems in history provides no information that would allow independent replication. This is not a minor procedural issue. It is the difference between science and product announcement. When challenged, OpenAI's Chief Scientist Ilya Sutskever told The Verge that publishing technical details was wrong and that the company had been wrong to be open-source in the beginning. He said this about a company named OpenAI.

Consider what this means for safety research. When a lab claims their model is safe for deployment, or that it has certain capabilities or lacks others, or that their alignment technique works, there is no independent verification mechanism at scale. The organizations doing safety evaluations are largely funded by or affiliated with the same labs building the systems. Independent academics cannot train models at the scale needed to test the claims. Governments cannot verify technical assertions without access to weights, training data, and infrastructure that companies refuse to share.

Nuclear power plants have independent safety regulators with technical expertise and legal access to facilities. Pharmaceutical companies must submit clinical trial data to regulators before drugs can be approved. Aircraft manufacturers certify systems through independent testing requirements. AI systems are being deployed in healthcare, credit decisions, hiring, criminal justice, and national security with verification mechanisms that would be considered absurd in any of those other domains. The contrast with physics is precise: the Large Hadron Collider at CERN cost approximately 4.75 billion dollars to build and is operated by thousands of scientists from 100 countries. Every measurement is independently verifiable by competing teams within the same facility. The most expensive AI training runs cost comparably and are operated in complete secrecy by single companies with commercial interests in the results.

---

## Where Scaling Actually Worked

Credibility requires acknowledging genuine success.

AlphaFold solved the 50-year protein structure prediction problem. This was genuinely transformative for biology, and the compute investment was justified. Machine translation through Google Translate handles over 100 languages and provides real utility for billions of people. Image recognition achieves cancer detection at dermatologist-level accuracy. Speech recognition made voice interfaces reliable. These are real achievements that benefited real people.

The steel-man argument for concentration deserves honest engagement. Spreading 100 billion dollars across ten approaches might have produced ten mediocre outcomes. Concentrating on one approach produced transformative capabilities in twelve years. Neural scaling needed massive datasets, massive compute, and massive models simultaneously, and fragmented approaches cannot achieve the coordination needed for ImageNet, PyTorch, and CUDA optimization together. The monoculture enabled the ecosystem. That argument has real force.

The counter-position is narrower: even if concentration was optimal from 2012 to 2020, it is not optimal now. Scaling is hitting physical limits from energy, cost, and data availability. We have no backup plan. The 100 billion dollars invested in scaling might have been allocated differently — 50 billion to scaling to still achieve major successes, 25 billion to neuro-symbolic for sample-efficient systems, 15 billion to neuromorphic for 100x energy reduction, 10 billion to theoretical foundations. Same practical capabilities. A fraction of the energy cost. And a field with options.

---

## The Collapse Becoming Visible

November 2024. Ilya Sutskever told Reuters the age of scaling was over. Anonymous sources reported to Bloomberg and The Information that OpenAI's GPT-5 training was not meeting expectations, Google's Gemini was falling short internally, and Anthropic delayed its next-generation Claude.

The test-time compute pivot tells you something important. OpenAI's o1 and o3 models do not scale model size. They scale inference-time computation, letting the model think longer before responding. This is an admission that pre-training scaling is hitting limits. The irony is precise: 1980s symbolic AI used search at inference time. From 2012 to 2024, the field declared search obsolete and claimed you just needed to scale neural networks. In 2024, search came back, rebranded as test-time compute.

DeepSeek proved the waste was a choice. In January 2025, a Chinese lab released a model matching GPT-4-class performance at approximately 5 to 6 million dollars in training cost, against hundreds of millions reportedly spent on comparable OpenAI runs. DeepSeek used mixture-of-experts architecture from 1991. They were forced to be efficient because US export restrictions blocked access to the highest-end NVIDIA hardware. Constrained away from the expensive path, they built the cheap path. NVIDIA's stock dropped 17 percent the day of the release, because if efficient AI works as well as wasteful AI, the premise that you need to keep buying more GPUs indefinitely becomes questionable.

Geoffrey Hinton left Google in May 2023. His stated reason was that he wanted to discuss AI safety without worrying about how it interacted with Google's business. He said part of him regrets his life's work. He won the 2024 Nobel Prize in Physics for foundational work in neural networks, and he regrets what that work became.

---

## What Is Coming Back

Publication trends show exponential growth from a small base: 53 neuro-symbolic papers in 2020, 236 in 2023, a 66 percent annual increase. LLM limitations around reasoning, factuality, and explainability are becoming obvious. Regulation is demanding transparency through the EU AI Act. Scaling is hitting limits, making efficiency matter again.

DeepMind's AlphaGeometry in 2024 solves International Mathematical Olympiad geometry problems by combining a neural language model with a symbolic deduction engine. Performance approaches human gold medalists. MIT-IBM's Neuro-Symbolic Concept Learner does visual reasoning with compositional structure, learns from few examples, and provides interpretable reasoning chains. Sample efficiency is roughly 100 times better than pure neural approaches in structured domains. Healthcare applications combining GPT-4 with rule-based expert systems show 90-plus percent accuracy with full audit trails.

The techniques exist now. We will never know what else might have existed, and when, because the exploration stopped. That is the actual tragedy of the hardware lottery — not that we definitely chose wrong, but that we stopped asking whether we had.

---

## What Needs to Happen

Funding structure needs timeline separation. Basic research deserves ten-year grants with no product expectations. Applied research gets three to five year grants with clear milestones. Product development uses commercial funding. All three are currently collapsed into two-year cycles. New metrics need to be required across the field: sample efficiency measured as examples needed per task, energy per task in joules per inference, compositional generalization through systematic tests, not just benchmark accuracy.

A reasonable funding allocation: 40 percent to scaling existing approaches to maintain progress, 30 percent to neuro-symbolic integration, 20 percent to neuromorphic computing, 10 percent to theoretical foundations. Current allocation is roughly 95 percent to scaling. Hardware ecosystem investment requires roughly 10 billion dollars for neuromorphic fabrication comparable to a TSMC node development, 5 billion for software tools equivalent to a PyTorch for spiking networks, and 2 billion for workforce retraining. Total roughly 20 billion dollars — a fraction of the cost of one GPT-4 training run — to build a complete alternative ecosystem. The barrier is a chicken-and-egg problem: no chips means no developers means no demand means no chips. This requires government or consortium investment to bootstrap.

Academic institutions need tenure criteria that value theoretical contributions equally with benchmark results, PhD timelines extended to six or seven years for fundamental work, and course offerings restored in logic programming and formal methods. In industry, research needs separation from product development the way Bell Labs operated. Negative results need publication. Benchmarks need to include efficiency and generalization metrics.

---

## What We Actually Know

The peer-reviewed record is unambiguous on certain points. Spiking neural networks achieve 100 to 1,000 times energy efficiency on compatible tasks. Neuro-symbolic systems learn from 10,000 to 100,000 times less data in structured domains. Capsule networks address spatial reasoning problems that CNNs demonstrably fail on. Mixture-of-experts provides ten times compute efficiency and was proven viable in 1991. And biological brains run on 20 watts while achieving general intelligence — a fact that sits there quietly, indicting every architectural choice we made.

Technical debt compounds. GPT-3 to GPT-4 was forty times the energy for marginal capability gain. GPT-4 to GPT-5 is ten times more energy for diminishing returns. Exponential cost for logarithmic improvement. Physical limits approach regardless of willingness to pay. When scaling stops, by choice or by force, the efficient alternatives will still be there. The mathematics does not care about funding decisions. Spiking networks will still be 100 times more efficient. Hybrids will still learn from less data. Vapnik's generalization bounds will still be provable. Pearl's causal calculus will still be the only rigorous framework for interventional reasoning.

This is one feedback loop. CUDA releases in 2007. AlexNet wins ImageNet in 2012. Venture capital floods toward GPU-compatible approaches. Cloud providers build GPU infrastructure where revenue scales with consumption. Benchmarks get designed around GPU tasks. Papers optimize for benchmarks. Corporate hiring targets benchmark winners. PhD students learn what gets jobs. Professors in symbolic and neuromorphic retire without replacements. Universities drop courses in dead fields. Funding committees see no proposals in alternatives and conclude nobody is working on them. Path dependency completes. The loop reinforces. Breaking it requires intervention at multiple points simultaneously.

We chose algorithms fitting available hardware over algorithms fitting intelligence. We chose architectures scaling compute over architectures scaling understanding. We chose training maximizing cloud revenue over training minimizing energy. We chose benchmarks measuring GPU performance over benchmarks measuring cognition.

Judea Pearl built the mathematics of cause and effect and is still publishing at 88 while the field ignores him. Vladimir Vapnik proved the generalization bounds that deep learning abandoned when they became inconvenient — the West adopted his work, then discarded it the moment GPU benchmarks offered a more convenient measure of progress. Jürgen Schmidhuber was working on meta-learning and compression as intelligence before anyone used the phrase "deep learning." Ray Solomonoff proved the optimal theory of inductive inference in 1964 and is essentially unknown to working machine learning practitioners in 2026. Viktor Glushkov built distributed networked systems in Kyiv in the 1960s that anticipated remote industrial control, distributed computing, and automated management — his entire tradition erased from Western AI history when the Cold War ended. Kateryna Yushchenko invented the pointer in 1955, nine years before the man Western computer science credits for the same idea, and her language ran on the computers that controlled Apollo-Soyuz while the West was busy crediting someone else. Edward Shortliffe built a system in 1974 that diagnosed infections as accurately as specialists and could explain every step of its reasoning. We cannot deploy its modern equivalent in hospitals today because we abandoned the principles that made explainability possible.

These people built rigorous frameworks for intelligence. We had the frameworks. We chose the gaming cards.

The question is not who was right about AI. The question is whether we explored enough of the possibility space to know what we were doing. The answer, measurably, is no.

---

## References

1. Hooker, S. (2020). "The Hardware Lottery." arXiv:2009.06489
2. Krizhevsky, A., Sutskever, I., and Hinton, G.E. (2012). "ImageNet Classification with Deep Convolutional Neural Networks." NeurIPS 2012
3. Pearl, J. (2018). "Theoretical Impediments to Machine Learning With Seven Sparks from the Causal Revolution." arXiv:1801.04016
4. Pearl, J. and Mackenzie, D. (2018). The Book of Why. Basic Books
5. Vapnik, V. and Chervonenkis, A. (1971). "On the Uniform Convergence of Relative Frequencies of Events to Their Probabilities." Theory of Probability and Its Applications
6. Cortes, C. and Vapnik, V. (1995). "Support-Vector Networks." Machine Learning, 20(3)
7. Hochreiter, S. and Schmidhuber, J. (1997). "Long Short-Term Memory." Neural Computation, 9(8)
8. Schmidhuber, J. (2022). "Annotated History of Modern AI and Deep Learning." arXiv:2212.11279
9. Solomonoff, R. (1964). "A Formal Theory of Inductive Inference." Information and Control, 7(1)
10. Rissanen, J. (1978). "Modeling by Shortest Data Description." Automatica, 14(5)
11. Kaplan, J. et al. (2020). "Scaling Laws for Neural Language Models." arXiv:2001.08361
12. Frankle, J. and Carlin, M. (2018). "The Lottery Ticket Hypothesis." arXiv:1803.03635
13. Jacobs, R. et al. (1991). "Adaptive Mixtures of Local Experts." Neural Computation, 3(1)
14. Shazeer, N. et al. (2017). "Outrageously Large Neural Networks." arXiv:1701.06538
15. Sabour, S., Frosst, N., and Hinton, G. (2017). "Dynamic Routing Between Capsules." NeurIPS 2017
16. Davies, M. et al. (2018). "Loihi: A Neuromorphic Manycore Processor." IEEE Micro, 38(1)
17. Lillicrap, T. et al. (2014). "Random Feedback Weights Support Learning." arXiv:1411.0247
18. Rao, R. and Ballard, D. (1999). "Predictive Coding in the Visual Cortex." Nature Neuroscience, 2(1)
19. Crick, F. (1989). "The Recent Excitement About Neural Networks." Nature, 337
20. Marcus, G. (2018). "Deep Learning: A Critical Appraisal." arXiv:1801.00631
21. Rahimi, A. (2017). NeurIPS Test of Time Award Talk. "Machine Learning is Alchemy."
22. Strubell, E. et al. (2019). "Energy and Policy Considerations for Deep Learning in NLP." ACL 2019
23. Patterson, D. et al. (2021). "Carbon Emissions and Large Neural Network Training." arXiv:2104.10350
24. Li, P. et al. (2023). "Making AI Less Thirsty." arXiv:2304.03271
25. PJM Independent Market Monitor (2025). Capacity Market Report. monitoringanalytics.com
26. IEA (2025). Energy and AI. iea.org/reports/energy-and-ai
27. Hinton, G. (2023). BBC and MIT Technology Review interviews, May 2023
28. Sutskever, I. (2024). Interview with Reuters, November 2024
29. Deng, J. et al. (2009). "ImageNet: A Large-Scale Hierarchical Image Database." CVPR 2009
30. Rumelhart, D.E., Hinton, G.E., and Williams, R.J. (1986). "Learning Representations by Back-Propagating Errors." Nature, 323
31. Herculano-Houzel, S. (2009). "The Human Brain in Numbers." Frontiers in Human Neuroscience, 3
32. Shortliffe, E.H. (1976). Computer-Based Medical Consultations: MYCIN. Elsevier
33. Yu, V.L. et al. (1979). "Antimicrobial Selection by a Computer." JAMA, 242(12)
34. Buchanan, B. and Shortliffe, E.H. (1984). Rule-Based Expert Systems: The MYCIN Experiments. Addison-Wesley
35. McDermott, J. (1980). "R1: An Expert in the Computer Systems Domain." AAAI-80
36. Barker, V.E. and O'Connor, D.E. (1989). "Expert Systems for Configuration at Digital: XCON and Beyond." Communications of the ACM, 32(3)
37. Peters, B. (2016). How Not to Network a Nation: The Uneasy History of the Soviet Internet. MIT Press
38. Glushkov, V.M. (1975). Macroeconomic Models and Principles of Building OGAS. Statistics Publishing House, Moscow
39. Kitova, O.V. and Kitov, V.A. (2018). "Anatoly Kitov and Victor Glushkov: Pioneers of Russian Digital Economy and Informatics." IFIP History of Computing Conference. Springer
40. Cottier, B. et al. (2024). "The Rising Costs of Training Frontier AI Models." arXiv:2405.21015
41. OpenAI (2023). "GPT-4 Technical Report." arXiv:2303.08774
42. Sutskever, I. (2023). Interview with The Verge, March 2023
43. IEA (2025). Energy and AI Report. iea.org
44. Heinrich Böll Foundation (2025). "AI Wants Our Water." eu.boell.org
46. Epoch AI (2024). "Tracking Large-Scale AI Models." epoch.ai
47. Binder, A. et al. (2018). "DeepProbLog: Neural Probabilistic Logic Programming." NeurIPS 2018
48. Cusumano-Towner, M. et al. (2019). "Gen: A General-Purpose Probabilistic Programming System." ACM SIGPLAN 2019
49. Gerovitch, S. (2008). "InterNyet: Why the Soviet Union Did Not Build a Nationwide Computer Network." History and Technology
50. Pikhorovich, V. (2022). "Glushkov and His Ideas: Cybernetics of the Future." Cosmonaut Magazine
51. Yushchenko biography and Address Programming Language. Wikipedia; Ada Lovelace Day 2022; A Computer of One's Own (Medium, 2018)
52. OGAS project documentation and Glushkov biography. glushkov.su
53. Peters, B. (2016). Aeon Essays: "How the Soviets invented the internet and why it didn't work." aeon.co
