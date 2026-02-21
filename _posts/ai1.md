---
title: AI is Dead, and We Have Killed It
date: 2026-02-20 14:54:00 +/-TTTT
image:
  path: assets/img/favicons/1_yVPk4XHXefuKVVOrGEvJiQ.webp
  class: "img-right"
categories: [AI]
tags: [AI, theory]  
---

Before you close this tab, let me be precise about what this is. This is not a claim that AI does not work, GPT-4 exists. AlphaFold cracked the protein folding problem that stumped biologists for fifty years, Machine translation works, Nobody serious disputes those achievements, But this is about what we destroyed to get there.

Between 2012 and 2024, AI research went from exploring six or seven competing paradigms to optimizing exactly one. Not because that paradigm was proven superior. Because it happened to fit hardware we already owned. We built an entire scientific field around what was convenient, called it progress, and buried everything else.

The researchers who built alternative frameworks for intelligence, rigorous, mathematically complete, historically documented frameworks and retired without training successors. The grad students who might have carried that knowledge forward never learned it, because universities stopped teaching it. The infrastructure needed to test those ideas does not exist anymore, because nobody funded it. So when I say AI is dead, I mean it the way a monoculture is dead. Biologically alive, Ecologically extinct.

---

## The Hardware Lottery

Sara Hooker at Google Brain named this, A research idea wins the hardware lottery when it succeeds because it fits whatever hardware exists at the time, not because it is the best solution to the problem.

History is full of this. Charles Babbage designed the Analytical Engine in 1837. The design was mathematically correct. Victorian fabrication precision could not build it. Perceptrons worked conceptually when Rosenblatt published them in 1958, died when Minsky and Papert proved they could not solve XOR in 1969, then got resurrected in the 1980s when hardware finally existed that could train multi-layer networks. Backpropagation was theoretically viable since Rumelhart, Hinton, and Williams published it in 1986. Nobody could scale it until GPUs arrived.

NVIDIA released CUDA in 2007. You could suddenly do general-purpose computing on graphics cards. GPUs turned out to be extraordinarily fast at one specific operation: dense matrix multiplication. Take a large grid of numbers, multiply it by another large grid, do it thousands of times in parallel. That is what GPUs were built for. Games need that. Intelligence, it turns out, may not.

Fei-Fei Li released ImageNet in 2009. 1.2 million labeled images. Three years later, Alex Krizhevsky trained a neural network on two consumer GPUs and won the ImageNet competition by 10.9 percentage points. In machine learning competitions, improvements of half a percent are notable. Krizhevsky won by eleven, Everyone noticed. 

What followed was not a scientific revolution, It was a hardware revolution wearing scientific clothing.

The lock-in mechanism is worth understanding because it explains everything that came after. GPUs make dense matrix multiplication cheap, so architectures optimized for that operation win benchmarks. Venture capital floods toward benchmark winners. Companies hire for GPU expertise because results live there. Universities train students in GPU methods because industry demands it. Doctoral programs drop coursework in alternative approaches because nobody hires for those skills. The professors who know symbolic AI, neuromorphic computing, probabilistic systems, they retire. Nobody replaces them. The knowledge dies.

Now look at what GPUs do well versus what intelligence might actually require.

GPUs are fast at dense matrix operations, parallel processing of identical computations, backpropagation through smooth differentiable functions. They are slow at sparse event-driven computation, irregular memory access, sequential dependencies, symbolic manipulation, logical reasoning.

Biological brains do most of that second list. Your brain does not activate all neurons simultaneously. It uses sparse, event-driven signaling. Roughly 1 to 4 percent of neurons fire at any given moment. Information encodes in spike timing, not continuous values. The human brain runs 86 billion neurons on 20 watts through extreme sparsity and parallelism. We built our field on algorithms that activate every single parameter for every single computation, consuming megawatts to train and kilowatts to run.

We did not choose algorithms that fit intelligence. We chose algorithms that fit our silicon. After 2012, over 95 percent of machine learning papers used architectures optimized for dense matrix operations. Funding proposals requiring non-GPU hardware faced rejection rates ten times higher than GPU-compatible proposals.

Cloud economics made it worse. AWS, Azure, Google Cloud sell compute by the hour, by the FLOP, by the terabyte. Revenue scales with consumption. Efficient algorithms mean less compute sold, which means lower revenue. Compute-intensive algorithms mean more compute sold. Cloud providers did not maliciously suppress efficient methods. They responded rationally to their pricing model, which naturally rewards waste. Not one major cloud provider offers pricing advantages for sample-efficient or energy-efficient approaches.

The feedback loop closed completely. Researchers need compute, so they use cloud infrastructure. They optimize for the GPUs those platforms provide. They publish results showing better performance with scale. Other researchers adopt the same approach. Cloud providers see more usage and invest in more GPUs. No coordination required. Just locally rational decisions producing a globally irrational outcome.

---

## September 30, 2012

AlexNet won ImageNet with a 15.3 percent error rate. Second place got 26.2 percent. The architecture was 8 layers deep, roughly 60 million parameters. Training hardware was two NVIDIA GTX 580 GPUs, consumer cards available at retail. Training time was six days.

The cascading effects took about eighteen months. November 2012, Hinton starts consulting for Google. March 2013, Google acquires his company DNNresearch. January 2014, Google acquires DeepMind for roughly 500 million dollars. September 2013, Facebook hires Yann LeCun. Microsoft, Baidu, and Amazon launch major AI hiring programs. The field got strip-mined for talent inside two years.

Yoshua Bengio estimated in 2014 that roughly 50 world-class deep learning experts existed globally. Not 5,000. Not 500. Fifty. DeepMind hired approximately twelve of them. That is 24 percent of global expertise in one acquisition. By 2015, Google employed somewhere between 5 and 50 percent of the field according to Peter Norvig's carefully worded public statements. This was not hiring. This was monopolizing epistemic capacity.

If Google pays 500 million dollars for 50 people, that is 10 million dollars per researcher. Academic salaries at the time ran 100,000 to 200,000 dollars. The industry premium was 50x to 100x. Universities lost the only places where alternative AI approaches could be explored outside quarterly earnings pressure.

The hidden cost was not just that researchers moved. It is that they stopped teaching alternatives entirely. Knowledge about symbolic AI, hybrid systems, neuromorphic computing, sample-efficient learning, it died with the generation that held it. Nobody trained replacements because industry hired only for GPU expertise, and universities taught only what industry would hire.

Before 2012, research evaluation was multidimensional. People measured sample efficiency: how much data does this actually require? They proved theoretical guarantees about convergence and generalization. They ran computational complexity analysis with real Big-O notation. They checked biological plausibility. Multiple competing metrics existed.

After 2012, evaluation collapsed into leaderboard position. ImageNet top-5 accuracy became the number everyone optimized. Scientific understanding got replaced by competitive gaming.

Goodhart's Law: when a measure becomes a target, it stops being a good measure. Benchmarks were designed to evaluate progress toward understanding intelligence. Once funding and careers depended on benchmark scores, research optimized for benchmarks instead of intelligence. The thing being measured and the thing we cared about diverged completely.

What stopped being measured: sample efficiency, energy per task, compositional generalization, causal reasoning, systematic generalization beyond training distribution. Why did these disappear? Existing scaling approaches would show weaker results. No clean winner story for publicity. Harder to optimize, so no competitive advantage.

---

## The People We Buried

We talk about this as a graveyard of ideas. We should talk about it as a graveyard of people. Specific human beings who built rigorous, working, mathematically complete frameworks for intelligence, and watched those frameworks get defunded because they did not run fast on gaming cards.

### Judea Pearl, and the Mathematics We Refused to Use

Judea Pearl won the Turing Award in 2011, the highest honor in computer science, for building the formal mathematical framework for reasoning about cause and effect. His do-calculus, structural causal models, and the ladder of causation are not philosophical speculation. They are precise mathematical machinery with decades of verified application in medicine, economics, and policy.

His argument against current AI is specific and devastating.

Every large language model, every image classifier, every recommendation system operates at what Pearl calls the first rung of the ladder of causation: association. It learns P(Y|X), the probability of Y given that we observe X. That is all it does.

The second rung is intervention. What happens to Y if we actively change X? The notation P(Y|do(X)) is not the same as P(Y|X). You cannot compute intervention from observation using observational data alone. You need a causal model. Pearl built the mathematics to do this in the 1980s and 1990s.

Here is why this matters in practice. A medical AI trained on hospital data observes that sicker patients receive more treatment. It learns the correlation: more treatment correlates with worse outcomes. Ask it a first-rung question, "among patients with these symptoms, what outcomes do we typically see," and it answers correctly. Ask it a second-rung question, "should I give this patient more treatment," and it gives you the systematically wrong answer. Treatment and outcome are confounded by severity. This is not a training data problem. No amount of additional data fixes it. Pearl proved this mathematically in 1995. The proof has been in the literature ever since.

The third rung is counterfactual. Given that X happened and Y resulted, what would Y have been if X had been different? Legal reasoning, scientific inference, moral responsibility, individual treatment estimation: all require this. Language models produce text that sounds like counterfactual reasoning because they trained on humans who do it. When a problem requires genuinely novel causal inference outside the training distribution, they fail. The empirical evidence is extensive now.

Pearl published a paper in 2018 listing specific tasks provably impossible for systems that only learn correlations. The field's response was largely silence. Not refutation. Silence. Because integrating causal structure into neural networks is hard, produces no benchmark improvements on ImageNet, and runs inefficiently on GPU matrix operations.

Pearl is 88 years old and still publishing. The field is still not listening.

### Vladimir Vapnik, and the Guarantees We Threw Away

Vladimir Vapnik, with Alexey Chervonenkis at the Institute of Control Sciences in Moscow in the 1960s, built VC theory: a rigorous mathematical framework for understanding when a learning algorithm generalizes from training data to new data. The VC dimension measures hypothesis class complexity. Structural risk minimization tells you how to balance fit against complexity to get provable generalization guarantees. Sample complexity bounds take the form O(d/epsilon) for VC dimension d, which means you can calculate in advance exactly how much data you need to achieve a given error rate with a given probability.

At AT&T Bell Labs in 1995, Vapnik introduced Support Vector Machines with Corinna Cortes. SVMs find the maximum margin hyperplane separating classes using the kernel trick for nonlinear problems. They came with theoretical guarantees. You could prove they would generalize under specified conditions. The theory was complete, rigorous, grounded in combinatorial geometry and statistical mechanics.

SVMs dominated machine learning through the mid-2000s. Then AlexNet happened, and within three years the field stopped caring. Not because SVMs were proven wrong. Not because anyone showed the theory was flawed. Neural networks given enough GPU compute and labeled data scored higher on benchmarks. The guarantees became inconvenient. The theory became noise.

Here is what we actually lost. Before 2012, you could calculate sample complexity bounds in advance. How much data does this model need to generalize? After 2012, nobody knows. The deep learning community genuinely cannot tell you in advance how much data a model needs, whether it will generalize, or when it will fail. We traded provable guarantees for higher benchmark numbers.

Vapnik is now at Columbia. He continued developing extensions including Learning Using Privileged Information. Production systems do not use it.

### Jürgen Schmidhuber, and the Framework That Got Stolen Without Credit

Schmidhuber invented Long Short-Term Memory networks in 1997 with Sepp Hochreiter, solving the vanishing gradient problem that made training deep recurrent networks impossible. LSTMs dominated natural language processing for nearly twenty years.

His broader research program asked a more fundamental question that the field dropped: how do you assign credit across long causal chains, when the action that produced a good outcome happened many steps ago? His 1991 PhD thesis was titled "Dynamic Neural Networks and the Fundamental Spatio-Temporal Credit Assignment Problem." He spent his career on this. He built meta-learning systems, models that learn how to learn. He developed formal theories of curiosity and intrinsic motivation grounded in information-theoretic compression. His argument: intelligence is the construction of compressed, predictive models of the environment.

He also built practical systems that won international competitions on handwriting recognition, speech recognition, and sequence prediction before deep learning became mainstream. He was doing deep learning before anyone called it that.

When the field exploded after 2012, Schmidhuber found himself writing public documents arguing that the dominant figures had systematically failed to credit earlier work. He was not wrong about the credit. He was not entirely sympathetic in how he made the argument, and the community tuned him out.

The practical cost: his work on meta-learning, on learning to learn, on compression as intelligence, stayed marginal for years. These ideas are finally getting serious attention in 2025 under different branding, but without the theoretical framework he built.

### Ray Solomonoff, and the Optimal Theory Nobody Uses

Ray Solomonoff died in 2009. He invented algorithmic probability in 1960 and published the first formal theory of inductive inference in 1964. Combined with Andrey Kolmogorov's formalization of complexity and Gregory Chaitin's extensions, this created algorithmic information theory.

The core idea: given a sequence of observations, the best prediction of the next observation is a weighted average over all computable theories consistent with the data, weighted by their simplicity in bits. This is Solomonoff induction. It is provably the optimal inductive inference algorithm. It is also uncomputable, which is why nobody uses it directly.

But it provides the theoretical ideal against which all practical learning algorithms can be measured. Jorma Rissanen's Minimum Description Length from 1978 is a computable approximation: choose the hypothesis that minimizes the combined length of the model description plus the data description given the model. This formalizes Occam's Razor precisely. Good learning is compression. If a model genuinely understands a pattern, it compresses the data that instantiates that pattern.

Current deep learning models are poor at compression by this measure. A GPT-class model has 1.8 trillion parameters trained on a few trillion tokens. The compression ratio is bad. A model that understood language at the level human linguists do would represent patterns with vastly fewer bits. Nobody measures this. Nobody funds research into it. Bits-per-parameter does not appear on a leaderboard.

Solomonoff is essentially unknown outside theoretical computer science. His theory is the foundation that modern machine learning built on and then abandoned.

### The Alchemy Accusation

Ali Rahimi, a Google researcher, stood up at NeurIPS 2017 to accept his Test of Time award and told the assembled audience that machine learning had become alchemy. His precise statement: "We are building systems that govern healthcare and mediate our civic dialogue. We can influence elections. I would like to live in a society whose systems are built on top of verifiable, rigorous, thorough knowledge, and not on alchemy."

He meant practitioners who add batch normalization, dropout, or a particular learning rate schedule because it "always works," with no understanding of why it works or when it will fail. He showed that researchers had stripped most of the complexity from a state-of-the-art translation algorithm and it translated better, which meant the original creators did not understand what they had built.

The audience gave him a standing ovation. Yann LeCun called it "insulting." Citation counts on benchmark papers continued to climb.

---

## The Architecture Graveyard

The following approaches meet four specific criteria: published peer-reviewed research proving they worked, theoretical advantages in at least one measurable dimension, documented evidence of funding decline, and an identifiable mechanism explaining why they lost the hardware lottery. No speculation. Just things that worked and died anyway.

### Spiking Neural Networks

Real neurons do not do continuous mathematics. They spike. Discrete voltage spikes. That is the entire mechanism.

The human brain achieves 86 billion neurons on 20 watts through event-driven computation where energy gets consumed only when neurons actually fire, sparse activation where only 1 to 4 percent of neurons are active at any moment, and temporal coding where information encodes in spike timing rather than activation magnitude.

The efficiency numbers are real. Best-case measurements on neuromorphic hardware show spiking neural networks on Intel's Loihi chips using roughly 10 to the power of negative 11 joules per synaptic operation. Standard deep neural networks on GPUs use 10 to the power of negative 6 to negative 9 joules per multiply-accumulate operation. On compatible tasks, the gap is 100 to 1,000 times. The caveat matters: that advantage only appears on tasks matching spike-compatible processing like temporal pattern recognition or event-driven perception. Dense matrix multiplication on a spiking network is actually worse than standard approaches.

SNNs failed to scale because spike generation is non-differentiable, which breaks backpropagation. Event-driven processing does not map to dense matrix operations. PyTorch and TensorFlow do not support spike-timing-dependent plasticity, the learning rule spiking networks actually use. No mature developer ecosystem exists.

In 2015, roughly 20 research groups globally worked on spiking neural networks. By 2024, maybe 12 remained. Research funding stayed below 1 percent of deep learning investment. Neuromorphic VC investment finally exceeded 200 million dollars in 2025. GPU infrastructure investment that same year was roughly 580 billion dollars globally. The ratio is 2,900 to 1.

The opportunity cost is concrete. If neuromorphic hardware had received GPU-level development investment from 2012 to 2024, GPT-4 training might have gone from 50 gigawatt-hours to somewhere between 500 and 5,000 megawatt-hours. We did not fund that path. Nobody's quarterly revenue depended on it.

### Capsule Networks

In 2017, Geoffrey Hinton published "Dynamic Routing Between Capsules." This requires a moment.

Hinton co-created backpropagation in 1986. His student created AlexNet in 2012. He architected modern deep learning. In 2017, he published a paper saying we made a fundamental mistake.

The problem he identified: convolutional neural networks use max pooling for translation invariance. Max pooling lets you detect a cat anywhere in an image. But it discards spatial relationships between features entirely. CNNs detect eyes, nose, mouth without caring whether those features are arranged in any anatomically coherent configuration. They will happily classify a scrambled face as a face because the individual features are present.

Capsule networks output vectors instead of scalars, encoding pose information including position, orientation, and size. Dynamic routing creates part-whole hierarchies. On MNIST overlapping digits, capsule networks outperformed CNNs using 100 times less training data.

Why did they fail? Two explanations exist, and intellectual honesty requires presenting both.

The infrastructure explanation: dynamic routing does not map efficiently to GPU matrix operations. The approach required completely new tooling and expertise. No benchmark breakthrough justified the switching costs. Even Hinton, with enormous credibility and the resources of Google, could not overcome the "scale the existing proven approach" incentive.

The fundamental limitation explanation: the routing mechanism has O(n squared) computational complexity for n capsules. This might be intrinsic to the approach regardless of hardware. Attempts to scale capsules to ImageNet hit 100x compute overhead. Maybe pooling is not actually a disaster, and routing is the problem.

What we actually know: capsules work on MNIST, proven. They address a real CNN limitation regarding spatial relationships, proven. They failed to scale to ImageNet with 2017 to 2020 methods, proven. Whether the scaling issues are fundamental or fixable: unknown, because research stopped. Between 2017 and 2020, roughly 50 papers examined capsule networks. Between 2020 and 2024, about 20. No major lab adopted them at scale.

### Neuro-Symbolic Integration

Combining neural networks for pattern recognition with symbolic reasoning for logic and knowledge makes obvious sense. Neural components handle noisy perceptual data. Symbolic components provide explainability, logical guarantees, and compositional reasoning.

This is not a new idea. Sun and Bookman wrote "Computational Architectures Integrating Neural and Symbolic Processes" in the 1990s. Annual neuro-symbolic workshops ran from 2005. Gary Marcus argued in 2018 that we could not construct rich cognitive models without hybrid architecture. He turned out to be right.

Systems that actually worked and received inadequate funding: DeepProbLog in 2018 combined neural networks with logic programming and produced promising results. MIT's Gen in 2019 combined probabilistic and deep learning, and Intel used it for real applications. Microsoft Research built Infer.Net starting in 2004. It worked. It never went mainstream.

The funding imbalance was roughly 100 to 1. Pure deep learning investment from 2012 to 2024 ran around 100 billion dollars across corporate R&D, venture capital, and government grants. Neuro-symbolic research received maybe 1 billion dollars. The knowledge extinction is measurable in a different way: in 1990, 60 percent of computer science departments offered a course in logic programming. By 2000, 40 percent. By 2010, 15 percent. By 2024, fewer than 5 percent. The expertise required to build neuro-symbolic systems is vanishing from universities in real time.

What we lost between 2012 and 2020: explainable AI deployable in regulated domains. Sample-efficient learning from small datasets. Causal reasoning. Systems that could justify their decisions with something better than "the neural network said so."

### Backpropagation's Biological Impossibility

Francis Crick, Nobel laureate, co-discoverer of DNA structure, identified in 1989 that backpropagation is fundamentally incompatible with biological neural architecture.

Backpropagation requires the gradient of the loss with respect to a weight to depend on the transpose of the forward weights. Forward synapses go axon to dendrite in a unidirectional physical structure. Backpropagation would require symmetric feedback maintaining W equals W-transpose across billions of synapses. No known biological mechanism does this.

Timothy Lillicrap showed in 2014 that feedback alignment, using random feedback weights instead of the transpose, still allows networks to learn. Rao and Ballard documented predictive coding in 1999, showing how hierarchical prediction-error signals could drive learning locally, consistent with neuroscience.

Predictive coding research received less than 0.5 percent of deep learning funding. Hebbian learning got less than 0.1 percent.

We built an entire field on an algorithm that Crick told us in 1989 cannot be how biological intelligence works. The most efficient intelligence we know of runs on biology.

### Mixture-of-Experts: Thirty Years Late

Robert Jacobs, Michael Jordan, Steven Nowlan, and Geoffrey Hinton published "Adaptive Mixtures of Local Experts" in 1991. Multiple specialist networks, a gating mechanism routing each input to relevant experts, only a fraction of parameters activating for any given input. Computational efficiency through sparse activation.

This paper was effectively ignored for thirty years. Dense networks were good enough. GPU infrastructure was optimized for dense computation. No financial incentive existed to invest in routing mechanisms.

In 2017, Google's Noam Shazeer published "Outrageously Large Neural Networks," rediscovering the same idea with modern tools. GPT-4 reportedly uses MoE architecture. DeepSeek's R1 model uses MoE with 671 billion total parameters but only 37 billion active per token, achieving GPT-4-class performance at approximately 6 million dollars in training cost versus hundreds of millions spent on comparable OpenAI training runs.

The efficient architecture was published in 1991. It saw serious use starting in 2017. Twenty-six years lost. Not because the idea was wrong. Because inefficiency was not penalized.

---

## The Economic Structure That Produced This

This section does not claim tech companies intentionally suppressed superior technologies. It analyzes how profit models structurally favored certain research directions, and how rational individual decisions produced a collectively irrational outcome.

Cloud providers sell compute by the hour. Revenue scales with consumption. Efficient algorithms mean less compute sold. Compute-intensive algorithms mean more compute sold. This is not malicious design. It is how usage-based pricing works. The pricing model that would have changed everything, accuracy-per-joule instead of compute-per-hour, performance-per-training-example instead of GPU-hours, was never economically viable for cloud providers because it would mean selling less compute.

Venture capital selection pressures compounded this. Time to demo for GPU-scalable deep learning: three to six months, fine-tuning something that already exists. Time to demo for sample-efficient hybrids: one to two years to build new architecture. VC fund cycles run two to three years. The math makes alternative approaches structurally unfundable regardless of technical merit. Between 2012 and 2022, over 50 billion dollars went into "AI" startups. Roughly 95 percent focused on scaling existing architectures. Zero unicorns got built on neuromorphic, symbolic, or hybrid approaches.

Academic career incentives completed the loop. PhD programs run four to five years. Three to five top-venue publications required to graduate. Review cycles run three to six months per paper. You must show publishable results within twelve to eighteen months per project. Industry machine learning positions pay 300,000 to 500,000 dollars for PyTorch expertise. Neuromorphic and symbolic research positions pay 150,000 dollars where they exist at all. The rational student learns skills with the highest job market value.

The knowledge extinction spiral follows directly. Professors who know symbolic AI, logic programming, and formal methods retire. Grad students avoid learning fields with no job market. Universities stop hiring in those areas. Course offerings disappear. The next generation has zero exposure to the ideas. Institutional knowledge dies completely.

Research funding tiers created a capital intensity filter. Symbolic, hybrid, and neuromorphic approaches can demonstrate ideas at the 10,000 to 1 million dollar tier. Scaling approaches require 1 million to 10 million to show competitive results. Funding committees prefer approaches with proven scale at the 10 to 100 million dollar tier. Alternative approaches need tier-3 funding to prove viability, but to get tier-3 funding you must show tier-4 results. DARPA's program for probabilistic programming got 50 million dollars over four years from 2013 to 2017, then ended. DeepMind's budget runs roughly 1 billion dollars per year, sustained. The funding ratio for incumbent versus alternative is approximately 100 to 1.

The open source counterargument deserves an honest response. PyTorch is free. TensorFlow is free. Hugging Face hosts thousands of models. Doesn't democratized access undermine the monopolization claim?

No. You can download GPT-2 for free and train it from scratch if you have 50,000 dollars in cloud credits. Knowledge is open. Experimentation is gated by capital. PyTorch is optimized for GPU operations; implementing capsule networks in it is painful and slow. Implementing spiking neural networks is ten times harder than standard DNNs. Open source infrastructure encodes architectural assumptions. Open-sourcing every automobile design does not help if you want to build a bicycle. The tools, infrastructure, and expertise are all automotive.

---

## The Scaling Myth

Scaling laws are not laws. They are empirical observations that performance improves with model size, data, and compute, within a specific regime. The 2020 narrative from Kaplan et al. at OpenAI claimed smooth power-law scaling would continue indefinitely. Venture capital and media amplified this into "Moore's Law for AI."

Scaling law papers show log-log plots. A straight line on a log-log plot looks like continuous progress. What it actually means: to reduce loss by 2x, you need roughly 1,000,000x more compute according to Toby Ord's analysis. Exponential resource requirements for linear gains.

GPT-3 training used 1,287 megawatt-hours and represented a large capability leap. GPT-4 training used roughly 50,000 megawatt-hours, forty times more energy, for a smaller leap. GPT-5 training estimates run around 500,000 megawatt-hours. The S-curve appeared exactly when scaling law proponents said it wouldn't.

The Lottery Ticket Hypothesis from Frankle and Carlin in 2018 proves the waste was measurable. Dense networks contain sparse subnetworks at initialization that are 10 to 20 percent of the original size and match the full network's performance. We trained 5 to 10 times more parameters than necessary. Pruning after training removes 90 percent of weights with minimal accuracy loss. Quantization from 32-bit to 8-bit delivers 4x compression with minimal accuracy loss. Knowledge distillation produces models 100 times smaller with 95 percent of the performance.

All of these retrofit solutions prove waste was baked in. Waste was economically rational given cloud pricing that rewards consumption.

In November 2024, Ilya Sutskever, OpenAI co-founder, told Reuters that the age of scaling was over and everyone was looking for the next thing. The next thing they are looking for is what the researchers in the previous section were building in 2013.

---

## The Energy Crisis

Your electricity bill went up this year. In Virginia it jumped 30 percent since 2021. In New Jersey, PSE&G warned customers about a 17 percent hike. A man in Baltimore named Kevin Stanley, living on disability payments, told Bloomberg his energy costs are 80 percent higher than three years ago. PJM's own independent market monitor documented that consumers across 13 states will pay 16.6 billion dollars extra from 2025 to 2027 to secure power for data centers. The PJM watchdog called it, in writing, a massive wealth transfer from ordinary people to the data center industry.

Google, Amazon, and Microsoft are the data center industry.

Human brain: 86 billion neurons, roughly 100 trillion synapses, 20 watts continuous power, roughly 10 to the power of negative 11 joules per synaptic operation. GPT-4 training: approximately 50,000 megawatt-hours, 1.8 trillion parameters, roughly 10 to the power of negative 6 joules per operation. That is 100,000 times worse than biological computation. GPT-4 inference at 700 million queries per day equals roughly 35,000 US homes' daily electricity consumption.

The gap comes from dense activation. Deep learning activates all parameters for every computation. Biological brains activate roughly 1 to 4 percent of neurons at any moment. The factor difference in energy consumption is 25 to 100 times. Dense won because GPUs optimize for dense matrix multiplication and existing libraries built for dense operations. Hardware determined the algorithm.

US data centers consumed approximately 183 terawatt-hours in 2024, more than 4 percent of national electricity, comparable to Pakistan's entire annual demand. Data center electricity consumption is projected to grow at approximately 15 percent per year from 2024 to 2030, four times faster than all other electricity sectors combined. A GPT-5 successor in 2028 might require 5,000,000 megawatt-hours for a single training run. Denmark's entire annual economy uses 33 terawatt-hours.

If Intel Loihi 2 had received GPU-level investment starting in 2012, equivalent model training runs at 100 times lower energy. 50,000 megawatt-hours becomes 500 megawatt-hours. Grid impact of AI becomes roughly equivalent to a medium-sized industrial facility rather than a new major city.

We did not fund that path. Nobody's quarterly revenue depended on it.

---

## The Scientific Method We Abandoned

Science and engineering ask different questions. Engineering: does it work? Can we build it? Does it scale? Science: why does it work, through what mechanism? When will it fail, given which boundary conditions? What principles generalize, via what theoretical framework?

Why do transformers work? Engineering: they achieve 90 percent accuracy on GLUE. Science would answer: because self-attention approximates X which enables Y. We do not have that explanation. When will scaling stop? Engineering: when we run out of compute. Science would answer: at architectural capacity C given data distribution D. We do not have those bounds.

Pre-2012 research had scientific frameworks. PAC learning gave sample complexity bounds growing as O(d/epsilon) for VC dimension d. VC theory bounded generalization error by model complexity. These were falsifiable, testable, predictive. Post-2012 deep learning has empirical observations: bigger models perform better usually, more data helps usually, overparameterization does not hurt somehow. Descriptive, not explanatory.

NeurIPS 2012 had 30 percent of papers including theoretical analysis. NeurIPS 2023 had less than 10 percent. The shift is documented and measurable.

Rich Sutton's "bitter lesson" from 2019 stated that general methods leveraging computation are ultimately most effective. Translation: theory does not matter, just scale. This is engineering philosophy, not science. No theory means no predictions. No predictions means no science. Just empirical tuning. This is what Rahimi called alchemy.

AI also has a replication crisis built into its economics. Physics replicates experiments. Biology requires multiple labs to confirm findings. AI says: reproduce our results with 10 million dollars of compute. GPT-3 cost 4.6 million dollars to train. GPT-4 cost roughly 50 million. About five organizations globally can afford to verify frontier claims. Without mechanistic understanding, you cannot predict when an approach will fail until it actually fails. You cannot design systems for safety-critical applications because you have no guarantees.

---

## Where Scaling Actually Worked

Credibility requires acknowledging genuine success.

AlphaFold solved the 50-year protein structure prediction problem. This was genuinely transformative for biology. The compute investment was justified. Machine translation through Google Translate handles over 100 languages and provides real utility for billions of people. Image recognition achieves cancer detection at dermatologist-level accuracy. Speech recognition made voice interfaces reliable. These are real achievements that benefited real people.

The steel-man argument for concentration deserves honest engagement. Spreading 100 billion dollars across ten approaches might have produced ten mediocre outcomes. Concentrating on one approach produced transformative capabilities in twelve years. Neural scaling needed massive datasets, massive compute, and massive models simultaneously. Fragmented approaches cannot achieve the coordination needed for ImageNet, PyTorch, and CUDA optimization. The monoculture enabled the ecosystem.

That argument has real force. The counter-position is narrower: even if concentration was optimal from 2012 to 2020, it is not optimal now. Scaling is hitting physical limits from energy, cost, and data availability. We have no backup plan. The 100 billion dollars invested in scaling might have been allocated differently: 50 billion to scaling to still achieve major successes, 25 billion to neuro-symbolic for sample-efficient systems, 15 billion to neuromorphic for 100x energy reduction, 10 billion to theoretical foundations. Same practical capabilities. Fraction of the energy cost. And a field with options.

---

## The Collapse Becoming Visible

November 2024. Ilya Sutskever told Reuters the age of scaling was over. Anonymous sources reported to Bloomberg and The Information that OpenAI's GPT-5 training was not meeting expectations, Google's Gemini was falling short internally, and Anthropic delayed its next-generation Claude.

The test-time compute pivot tells you something important. OpenAI's o1 and o3 models do not scale model size. They scale inference-time computation, letting the model process longer before responding. This is an admission that pre-training scaling is hitting limits.

The irony is precise. 1980s symbolic AI used search at inference time. From 2012 to 2024, the field declared search obsolete and claimed you just needed to scale neural networks. In 2024, search is back. Rebranded as test-time compute.

DeepSeek proved the waste was a choice. In January 2025, a Chinese lab released a model matching GPT-4-class performance at approximately 5 to 6 million dollars in training cost, against hundreds of millions reportedly spent on comparable OpenAI runs. DeepSeek used mixture-of-experts architecture from 1991. They were forced to be efficient because US export restrictions blocked access to the highest-end NVIDIA hardware. Constrained away from the expensive path, they built the cheap path. NVIDIA's stock dropped 17 percent the day of the release, because if efficient AI works as well as wasteful AI, the premise that you need to keep buying more GPUs indefinitely becomes questionable.

Geoffrey Hinton left Google in May 2023. His stated reason: he wanted to discuss AI safety without worrying about how it interacted with Google's business. He said part of him regrets his life's work. He said the probability of AI systems becoming more intelligent than humans and taking control is very likely more than 1 percent and very likely less than 99 percent. He said the big companies are lobbying for less AI regulation while almost none exists.

This is the person who built backpropagation. Who supervised AlexNet. Who architected the modern field. He won the 2024 Nobel Prize in Physics for foundational work in neural networks, and he regrets what that work became.

---

## What Is Coming Back

Publication trends show exponential growth from a small base. 53 neuro-symbolic papers in 2020. 236 in 2023, a 66 percent annual increase. LLM limitations around reasoning, factuality, and explainability are becoming obvious. Regulation is demanding transparency through the EU AI Act. Scaling is hitting limits, making efficiency matter again.

DeepMind's AlphaGeometry in 2024 solves International Mathematical Olympiad geometry problems by combining a neural language model with a symbolic deduction engine. Performance approaches human gold medalists. MIT-IBM's Neuro-Symbolic Concept Learner does visual reasoning with compositional structure, learns from few examples, and provides interpretable reasoning chains. Sample efficiency is roughly 100 times better than pure neural approaches in structured domains. Healthcare applications combining GPT-4 with rule-based expert systems show 90-plus percent accuracy with full audit trails.

If neuro-symbolic approaches had received equal funding from 2012 to 2024, roughly 50 billion dollars over twelve years, AlphaGeometry-level systems likely existed by 2018. Medical AI deployable in regulated settings likely existed by 2020. Sample-efficient learning would be standard practice, not a research frontier. Explainable AI would be the default, not an open problem.

The techniques exist now. They could have existed a decade earlier.

---

## What Needs to Happen

What will not work: making transformers bigger is hitting physical limits. Throwing more data at the problem runs into quality data becoming scarce. Waiting for the market to self-correct ignores that the incentives remain broken.

Funding structure needs timeline separation. Basic research deserves ten-year grants with no product expectations. Applied research gets three to five year grants with clear milestones. Product development uses commercial funding. All three are currently collapsed into two-year cycles.

New metrics need to be required: sample efficiency measured as examples needed per task, energy per task in joules per inference, compositional generalization through systematic tests. Not just benchmark accuracy.

A reasonable funding allocation: 40 percent to scaling existing approaches to maintain progress, 30 percent to neuro-symbolic integration, 20 percent to neuromorphic computing, 10 percent to theoretical foundations. Current allocation is roughly 95 percent to scaling.

Hardware ecosystem investment: neuromorphic fabrication needs roughly 10 billion dollars comparable to a TSMC node development, software tools need 5 billion for a PyTorch equivalent for spiking networks, developer training needs 2 billion to retrain the workforce. Total roughly 20 billion dollars, 0.2 times the cost of one GPT-4 training run, to build a complete alternative ecosystem. The barrier is a chicken-and-egg problem: no chips means no developers means no demand means no chips. This requires government or consortium investment to bootstrap.

Academic institutions need tenure criteria that value theoretical contributions equally with benchmark results. PhD timelines need extension to six or seven years for fundamental work. Course offerings need to restore logic programming and formal methods. In industry, research needs separation from product development the way Bell Labs operated. Negative results need publication. Benchmarks need to include efficiency and generalization metrics.

The 1956 Dartmouth conference founded AI as a field, brought together diverse approaches, and set the research agenda for decades. A 2026 equivalent needs to redefine the scientific goals: understanding intelligence, not just engineering systems. Multiple paradigms funded equally. Energy and sample complexity as required metrics. Reproducibility requirements at costs accessible to more than five organizations.

---

## What We Actually Know

Spiking neural networks achieve 100 to 1,000 times energy efficiency on compatible tasks. This is published research. Neuro-symbolic systems learn from 10,000 to 100,000 times less data in structured domains. Published research. Capsule networks address spatial reasoning problems CNNs fail on. Published research. Mixture-of-experts provides ten times compute efficiency and was proven in 1991. Biological brains run on 20 watts while achieving general intelligence. Observed reality.

These are not speculative. The evidence exists and has existed for years.

Technical debt compounds. GPT-3 to GPT-4 was forty times the energy for marginal capability gain. GPT-4 to GPT-5 is ten times more energy for diminishing returns. Exponential cost for logarithmic improvement. Physical limits approach regardless of willingness to pay. When scaling stops, by choice or by force, the efficient alternatives will still be there. The mathematics does not care about funding decisions. Spiking networks will still be 100 times more efficient. Hybrids will still learn from less data. Vapnik's generalization bounds will still be provable. Pearl's causal calculus will still be the only rigorous framework for interventional reasoning.

This is one feedback loop. CUDA releases in 2007. AlexNet wins ImageNet in 2012. Venture capital floods toward GPU-compatible approaches. Cloud providers build GPU infrastructure where revenue scales with consumption. Benchmarks get designed around GPU tasks. Papers optimize for benchmarks. Corporate hiring targets benchmark winners. PhD students learn what gets jobs. Professors in symbolic and neuromorphic retire without replacements. Universities drop courses in dead fields. Funding committees see no proposals in alternatives and conclude nobody is working on them. Path dependency completes. The loop reinforces.

Breaking it requires intervention at multiple points simultaneously.

We chose algorithms fitting available hardware over algorithms fitting intelligence. We chose architectures scaling compute over architectures scaling understanding. We chose training maximizing cloud revenue over training minimizing energy. We chose benchmarks measuring GPU performance over benchmarks measuring cognition.

Judea Pearl built the mathematics of cause and effect and is still publishing at 88 while the field ignores him. Vladimir Vapnik proved the generalization bounds that deep learning abandoned when they became inconvenient. Jürgen Schmidhuber was working on meta-learning and compression as intelligence before anyone used the phrase "deep learning." Ray Solomonoff proved the optimal theory of inductive inference in 1964 and is essentially unknown to working machine learning practitioners in 2026.

These people built rigorous frameworks for intelligence. We had the frameworks. We chose the gaming cards.

The question is not who was right about AI. The question is whether we explored enough of the possibility space to know what we were doing.

The answer, measurably, is no.

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
12. Frankle, J. and Carbin, M. (2018). "The Lottery Ticket Hypothesis." arXiv:1803.03635
13. Jacobs, R. et al. (1991). "Adaptive Mixtures of Local Experts." Neural Computation, 3(1)
14. Shazeer, N. et al. (2017). "Outrageously Large Neural Networks." arXiv:1701.06538
15. Sabour, S., Frosst, N. and Hinton, G. (2017). "Dynamic Routing Between Capsules." NeurIPS 2017
16. Davies, M. et al. (2018). "Loihi: A Neuromorphic Manycore Processor." IEEE Micro, 38(1)
17. Lillicrap, T. et al. (2014). "Random Feedback Weights Support Learning." arXiv:1411.0247
18. Rao, R. and Ballard, D. (1999). "Predictive Coding in the Visual Cortex." Nature Neuroscience, 2(1)
19. Crick, F. (1989). "The Recent Excitement About Neural Networks." Nature, 337
20. Marcus, G. (2018). "Deep Learning: A Critical Appraisal." arXiv:1801.00631
21. Rahimi, A. and Recht, B. (2017). NeurIPS Test of Time Award Talk
22. Strubell, E. et al. (2019). "Energy and Policy Considerations for Deep Learning in NLP." ACL 2019
23. Patterson, D. et al. (2021). "Carbon Emissions and Large Neural Network Training." arXiv:2104.10350
24. Li, P. et al. (2023). "Making AI Less Thirsty." arXiv:2304.03271
25. PJM Independent Market Monitor (2025). Capacity Market Report
26. IEA (2025). Energy and AI
27. Hinton, G. (2023). MIT Technology Review interview, May 2023
28. Sutskever, I. (2024). Interview with Reuters, November 2024
29. Deng, J. et al. (2009). "ImageNet: A Large-Scale Hierarchical Image Database." CVPR 2009
30. Rumelhart, D.E., Hinton, G.E., and Williams, R.J. (1986). "Learning Representations by Back-Propagating Errors." Nature, 323
31. Herculano-Houzel, S. (2009). "The Human Brain in Numbers." Frontiers in Human Neuroscience, 3
32. Ord, T. (2024). Analysis of scaling law mathematics
33. Binder, A. et al. (2018). "DeepProbLog: Neural Probabilistic Logic Programming." NeurIPS 2018
34. Cusumano-Towner, M. et al. (2019). "Gen: A General-Purpose Probabilistic Programming System." ACM SIGPLAN 2019
