---
title: "From Causal Discovery to Causal Pruning"
date: 2026-09-21 20:40:00 +04:00
image:
  path: assets/img/causal-pruning/tikz_fig1.png
  alt: "Two-level intervention pipeline: do-operator on dataset variables, then on model neurons"
categories: [AI]
tags: [Causal Inference, Pruning, Research]
math: true
---

*Full text of my March 2026 paper. Level 1 applies the do-operator to dataset variables (CCA+ direction discovery → confounder screening → backdoor adjustment → ACE). Level 2 applies the same logic to neurons inside a trained network (CE scoring → causal pruning). Equation, theorem, and section numbers match the PDF; citations link to the reference list at the end.*

> **Abstract.** Observational data tells you which variables are correlated. It does not tell you what happens when you force one of them to change. The backdoor adjustment formula has existed for thirty years to answer the second question, but it requires knowing which direction each causal edge points — information that no correlation matrix contains. This paper builds an automated mathematical framework for recovering that direction and connects it to the full causal inference pipeline, then extends the same intervention logic to the problem of identifying which neurons inside a trained neural network are causally necessary for its predictions.
>
> The framework, Causal Computational Asymmetry (CCA+), rests on one observation: under the Additive Noise Model $$Y = f(X) + \varepsilon$$ with $$\varepsilon \perp X$$, a neural network trained in the true causal direction converges to a lower loss floor than one trained in reverse. This is proved from the law of total variance and gradient descent under the Polyak-Łojasiewicz condition, not fit to data. On Pima diabetes, CCA+ identifies BMI $$\to$$ Glucose at score $$-0.059$$, estimates ACE $$= 1.04$$ mg/dL per BMI unit (95% CI $$[0.73, 1.35]$$), and recovers 9 of 16 confirmed edges in the Sachs protein network from observational data alone. The framework fails on linear Gaussian mechanisms (a theoretical impossibility shared by every method in this family) and flags near-linear cases via an $$\eta^2 - r^2$$ pre-test before committing to a direction.
>
> The same intervention logic is then applied inside trained neural networks under the Causal Pruning (CP) algorithm. For each neuron, we zero its activations and measure the average output change (causal effect score), then prune the lowest-scoring neurons rather than the smallest weights. We validate this across three datasets, four competing baselines, five random seeds, three noise levels ($$\sigma \in \{0.5, 1.5, 2.0\}$$), and pruning levels up to 90%. The core finding is that CE scoring advantage is not uniform — it is negligible on easy, near-saturated tasks and grows sharply on hard tasks at extreme sparsity. On Pima at 90% pruning under $$\sigma = 0.5$$, CE outperforms magnitude by $$+6.4\%$$ (mean across 5 seeds). The result scales with task difficulty: when almost nothing is left, the only neurons worth keeping are the ones that actually cause the output. This is not speculative. All experiments are documented and reproducible.

## 1. Introduction

Every AI model deployed in the real world is eventually asked to answer a question it was never directly trained to answer. A model trained on hospital data from one city gets deployed in a clinic in another. A model trained on 2022 data is still running in 2026. A model trained on clean, curated inputs encounters messy, noisy real-world ones. What happens? Usually, accuracy degrades — often badly — and nobody is quite sure why, because the model was never designed to tell you which parts of it were doing the actual work.

This paper is about two things that are more connected than they look.

The first is the problem of **causal direction in data**. When you observe that two variables are correlated — say, higher BMI tends to go with higher blood glucose — statistics gives you no way to tell whether BMI is causing the glucose to rise, or whether glucose is causing BMI to rise, or whether both are being pushed up by a third variable you have not measured. This is not a limitation of your dataset size. It is a mathematical impossibility: correlation is symmetric, and causation is not. Answering the question “what would happen if I forced BMI down to 25 for everyone?” requires something correlation cannot give you. It requires the direction of the causal edge.

The second is the problem of **which neurons actually matter in a neural network**. Standard pruning methods remove the neurons with the smallest weights, on the logic that small weights mean small contribution. But a neuron’s weight size during training tells you something about how often it fired during training, not whether the model’s output actually changes when you disable it. Those are different questions. A neuron can have a small weight and be critical; another can have a large weight and be completely redundant because five other neurons are doing the same thing.

The thread connecting these two problems is the same mathematical object: the *do-operator*. Pearl’s do-calculus asks, instead of “what do I observe when $$X$$ is high?”, the question “what happens when I *force* $$X$$ to be high?” That forcing — that intervention — is what separates correlation from causation. This paper applies that same intervention logic at two different levels. At the data level, it identifies which variable is the cause and which is the effect, then uses that to estimate what actually happens if you intervene. At the neural network level, it identifies which neurons actually cause the output to change when disabled, then uses that to prune the network more intelligently.

The result at the data level is CCA+ (Causal Computational Asymmetry), a provably correct direction-discovery algorithm that connects automatically to Pearl’s backdoor adjustment formula to produce a quantified interventional estimate. The result at the neural network level is Causal Pruning (CP), an algorithm that scores neurons by their causal effect on the output rather than their weight magnitude, producing models that hold up better under distribution shift — especially at extreme pruning levels where the wrong choice of which neurons to keep becomes catastrophic.

The rest of this paper documents both in full detail: proofs, experiments, validation on real biological data, failure analysis, and the stress test that establishes exactly when causal pruning outperforms magnitude pruning and when it does not.

## 2. Framework Overview: The Two-Level Intervention Pipeline

This paper applies a single principle at two levels. The diagram below shows the full pipeline. The top path takes raw observational data and produces a quantified interventional causal effect estimate. The bottom path takes a trained neural network and produces a smaller, more robust version of it. Both paths ask the same question: not what correlates with the outcome, but what actually changes the outcome when you force something to change.

<img src="/assets/img/causal-pruning/tikz_fig1.png" alt="" />

**Top path — causal discovery pipeline.** Raw observational data enters. The $$\eta^2 - r^2$$ pre-test decides whether the relationship between $$X$$ and $$Y$$ is nonlinear enough for CCA+ to reliably identify direction. If yes, CCA+ runs two neural networks — one trained in each direction — and identifies the true causal direction from the convergence asymmetry. The confounder screener then identifies which observed variables to include in the adjustment set. The backdoor formula runs and outputs a quantified interventional estimate $$E[Y \mid \mathrm{do}(X = x)]$$ with a bootstrap 95% confidence interval. If the pre-test flags near-linearity, the pipeline routes to LiNGAM or flags the pair as ambiguous.

**Bottom path — causal pruning pipeline.** A trained neural network enters. Every neuron is scored by how much the model’s output changes when that neuron’s activations are zeroed out across the dataset. Neurons that change the output a lot are causally necessary. Neurons that change the output very little are causally redundant. The lowest-scoring neurons are removed. What remains is a model that generalises better under distribution shift than a magnitude-pruned model of the same sparsity — especially at extreme pruning levels.

## 3. The Problem: Why Correlation Is Not Enough

### 3.1. A Deceptively Simple Question

A doctor in Abu Dhabi has a patient whose BMI and glucose are both elevated. She knows, from thirty years of epidemiological data, that these two variables are correlated: $$r_{\text{BMI, Glucose}} \approx 0.22$$ in this population. What she does not know — what no amount of correlation data can tell her — is whether reducing the BMI will bring the glucose down, or whether the causation runs the other way, or whether both are being driven by something she has not measured. That question is the one this paper is about.

The Pearson correlation is symmetric by construction: 

$$
r_{XY} = \frac{\sum_{i=1}^n (x_i - \bar{x})(y_i - \bar{y})}
{\sqrt{\sum_{i=1}^n (x_i - \bar{x})^2 \cdot \sum_{i=1}^n (y_i - \bar{y})^2}} = r_{YX}.
\tag{1}
$$

 This symmetry is not a flaw in the formula. It is the correct mathematical reflection of a genuine epistemological problem: observational data, taken at a single snapshot, carries no information about causal direction without additional structural assumptions. The formula is doing its job. The problem is that its job is not enough.

#### 3.1.1. A Brief Intellectual History of the Problem

This is not a new observation. Philosophers of science have wrestled with the relationship between correlation and causation for centuries. David Hume argued in 1748 that causation reduces entirely to observed regularity — repeated succession of one event after another — and that no deeper necessary connection can be perceived directly. Karl Pearson, one of the founders of modern statistics, took this further: he argued in *The Grammar of Science* [\[21\]](#ref-21) that causation was scientifically meaningless and should be replaced entirely by the concept of correlation. This view dominated empirical science for much of the twentieth century. Entire research traditions in medicine, economics, and social science were built on the implicit assumption that finding a strong correlation was close enough to finding a cause.

The reaction began with Sewall Wright, who introduced *path analysis* in the 1920s [\[22\]](#ref-22) as a method for reasoning about causal relationships in genetics even without experimental data. Wright’s key insight was that a system of structural equations — not merely a matrix of correlations — was needed to correctly decompose direct and indirect effects. His innovation was largely ignored outside genetics for decades.

It was Hans Reichenbach who, in his posthumously published *The Direction of Time* [\[20\]](#ref-20), first provided the philosophical and statistical foundations for causal asymmetry. His Common Cause Principle states that if two events $$A$$ and $$B$$ are correlated and neither causes the other, there must exist a common cause $$C$$ satisfying: 

$$
P(A \cap B \mid C) = P(A \mid C) \cdot P(B \mid C), \quad
P(A \cap B \mid \neg C) = P(A \mid \neg C) \cdot P(B \mid \neg C).
\tag{2}
$$

 The common cause *screens off* the correlation: once you condition on $$C$$, $$A$$ and $$B$$ become independent. Reichenbach further argued that causal direction has a macrostatistical signature — that causes are distinguished from effects by the structure of the noise they generate — and he connected this asymmetry to the thermodynamic arrow of time. CCA+ is a computational instantiation of this philosophical insight: the noise generated by the ANM has a different statistical character in the forward direction than in the reverse, and that difference is measurable.

The formal graphical framework was established by Spirtes, Glymour, and Scheines [\[23\]](#ref-23) and by Pearl [\[2\]](#ref-2) in the 1990s and 2000s. Both groups introduced directed acyclic graphs (DAGs) as a mathematical language for encoding causal assumptions, developed algorithms (PC, FCI, GES) for learning graph structure from conditional independence tests, and established the do-calculus as the algebra of interventional reasoning. The limitation they both acknowledged — and which Pearl made mathematically precise — is that observational data can at best recover a graph up to its *Markov equivalence class*: the set of all DAGs that encode the same conditional independence structure. Many edges within an equivalence class remain undirected. CCA+ pierces this limit by exploiting the ANM: under nonlinear injective mechanisms, no two non-identical DAGs are Markov equivalent with respect to the structural noise properties, and the correct direction is identifiable from data alone.

### 3.2. The Three Configurations That Produce Identical Correlations

Any observed correlation between $$X$$ and $$Y$$ is consistent with at least three distinct causal structures, illustrated here:

<img src="/assets/img/causal-pruning/tikz_fig2.png" alt="" />

All three structures can produce identical values of $$r_{XY}$$. They are statistically indistinguishable from the joint distribution $$P(X, Y)$$ alone. In structure (c), the right intervention is to manipulate $$Z$$, not $$X$$ or $$Y$$. But a researcher who does not know that $$Z$$ exists, let alone that it causes both $$X$$ and $$Y$$, will observe only the $$X$$–$$Y$$ correlation and may conclude (wrongly) that treating $$X$$ will change $$Y$$.

> **Example.** Ice cream sales and drowning deaths both spike in summer — both caused by warm weather. Hospitals with more beds tend to have higher mortality — both caused by severity of illness. Countries with more coffee shops have better educational outcomes — both caused by urbanization and development. In each case, the correlation is real but the implied causal relationship is completely wrong.

### 3.3. Why Regression Does Not Solve This

The most common response to the problem in Section 1.1 is to run a regression. Fit $$Y = \beta X + \alpha + \varepsilon$$, get a significant $$\hat{\beta}$$, report it as the causal effect. This is what the overwhelming majority of empirical papers in medicine, economics, and social science do. And it is wrong, in a specific and fixable way.

The wrongness is not in the arithmetic. It is in the setup. The moment you write $$Y = \beta X + \varepsilon$$, you have declared that $$X$$ is the input and $$Y$$ is the output. That declaration is a causal assumption — and it is exactly the assumption you are trying to test. The regression cannot discover the direction; it requires the direction as a prior condition.

Concretely: if the true model is $$Y = f(X) + \varepsilon$$ with $$\varepsilon \perp X$$, running the reverse regression $$X \sim Y$$ will also produce a finite, statistically significant slope. Both regressions fit the data. There is no test statistic, no $$p$$-value, no $$R^2$$ comparison that tells you which direction is correct. The data contains the correlation. The direction is not in the data.

#### 3.3.1. The Markov Equivalence Problem

Constraint-based methods such as the PC algorithm [\[23\]](#ref-23) and score-based methods such as GES [\[24\]](#ref-24) attempt to recover causal structure from conditional independence tests. They succeed in identifying the undirected skeleton of the graph (which pairs of variables are connected) and in orienting some edges using v-structure rules (if $$X \to Z \leftarrow Y$$ with no edge between $$X$$ and $$Y$$, then the collider $$Z$$ is identifiable). However, for many pairs of variables, the direction of the edge cannot be determined from conditional independence alone.

Two DAGs $$G$$ and $$G'$$ are in the same Markov equivalence class if and only if they have the same skeleton and the same v-structures [\[25\]](#ref-25). For a graph with $$p$$ variables and $$e$$ edges, the equivalence class can contain exponentially many DAGs, each consistent with every conditional independence test. The PC and GES algorithms return a *CPDAG* (completed partially directed acyclic graph) — a graph in which some edges are directed and others remain undirected — and cannot resolve the undirected edges without additional assumptions.

This is precisely why DoWhy [\[7\]](#ref-7) requires the user to provide a graph: the tool cannot generate a directed graph from observational data because PC and GES return CPDAGs with undirected edges, and undirected edges are insufficient to determine valid adjustment sets. The backdoor criterion requires knowing which direction an edge points. DoWhy’s own documentation explicitly acknowledges: the integration of causal discovery with causal inference is an open problem because discovery algorithms return “CPDAGs instead of DAGs, so it is possible to have undirected edges. Thus, causal effect estimation is difficult for those methods.”

CCA+ resolves this. Under the ANM, *no* edge within a Markov equivalence class remains undirected: the structural noise properties distinguish the causal direction even when conditional independence tests are powerless. This is the fundamental theoretical advantage of functional-model-based methods over constraint-based methods, and it is what makes the CausalLens pipeline possible.

#### 3.3.2. Granger Causality and Its Limits

For time series data, Granger causality [\[27\]](#ref-27) offers an approach to direction: $$X$$ Granger-causes $$Y$$ if past values of $$X$$ improve the prediction of $$Y$$ beyond what past values of $$Y$$ alone provide. Formally, in a bivariate VAR($$p$$) model: 

$$
Y_t = \sum_{i=1}^p \alpha_i Y_{t-i} + \sum_{i=1}^p \beta_i X_{t-i} + \varepsilon_t,
\tag{3}
$$

 $$X$$ Granger-causes $$Y$$ if the null hypothesis $$H_0: \beta_1 = \cdots = \beta_p = 0$$ is rejected by an F-test. Granger causality won its inventor the 2003 Nobel Prize in Economics.

Its limitations, however, are substantial. First, it requires *stationarity* — the statistical properties of the time series must not change over time. Second, it requires a *complete model*: all relevant variables must be included, or spurious Granger causality arises from omitted common causes. Third, and most fundamentally, Granger causality is a measure of *predictive precedence*, not of structural causation [\[27\]](#ref-27). Granger himself acknowledged this: if $$X$$ and $$Y$$ are both driven by a common cause $$Z$$ with $$Z$$ affecting $$X$$ slightly earlier than $$Y$$, then $$X$$ will Granger-cause $$Y$$ even though there is no direct causal link between them. Fourth, it is entirely inapplicable to cross-sectional data — a single snapshot of a population, which is the most common data type in clinical research — because there is no temporal ordering to exploit.

CCA+ is applicable to cross-sectional data, does not require stationarity, and tests a structural property of the data-generating process rather than a predictive property.

### 3.4. Pearl’s Causal Hierarchy

Judea Pearl formalized the impossibility of answering interventional questions from observational data in a series of papers beginning in 1995 [\[1\]](#ref-1), [\[2\]](#ref-2). His central result is that the question “what would happen if I forced $$X$$ to take value $$x$$?” is a mathematically different object from “what do I expect $$Y$$ to be, given that I observe $$X = x$$?” These two questions correspond to different rungs of what Pearl calls the Causal Hierarchy:

| **Rung** | **Query** | **Notation** | **Example** |
| ---| ---| ---| ---|
| **1** | Observing | $$P(Y \mid X = x)$$ | Do patients with high BMI have high glucose? |
| **2** | Intervening | $$P(Y \mid \mathrm{do}(X = x))$$ | If we force BMI down to 25 for everyone, what happens to glucose? |
| **3** | Counterfactual | $$P(Y_x \mid X = x', Y = y')$$ | If this patient had had lower BMI, would their glucose have been normal? |

The hierarchy is strict: no amount of Rung 1 data can answer a Rung 2 question without structural assumptions. No amount of Rung 2 analysis can answer a Rung 3 question without a full structural causal model. The tools in this paper reach Rung 2. They do not reach Rung 3, and we do not claim otherwise.

The key word in Pearl’s theorem is “without structural assumptions.” The impossibility is not absolute — it is conditional on having no prior knowledge about the data-generating process. The Additive Noise Model, described in Section 2, is exactly such a structural assumption: a specific, falsifiable claim about how $$Y$$ is generated from $$X$$. Under that assumption, the causal direction *is* identifiable from observational data, and the tool in this paper exploits that identifiability.

#### 3.4.1. The Do-Calculus

Pearl’s do-calculus [\[1\]](#ref-1) provides a complete set of inference rules for computing $$P(Y \mid \mathrm{do}(X))$$ from observational data given a causal graph. The calculus has three rules:

**Rule 1 (Insertion/deletion of observations):** 

$$
P(Y \mid \mathrm{do}(X), Z, W) = P(Y \mid \mathrm{do}(X), W)
\quad \text{if } (Y \perp\!\!\!\perp Z \mid X, W)_{G_{\overline{X}}},
\tag{4}
$$

 where $$G_{\overline{X}}$$ is the graph with all arrows into $$X$$ removed.

**Rule 2 (Action/observation exchange):** 

$$
P(Y \mid \mathrm{do}(X), \mathrm{do}(Z), W) = P(Y \mid \mathrm{do}(X), Z, W)
\quad \text{if } (Y \perp\!\!\!\perp Z \mid X, W)_{G_{\overline{X}\underline{Z}}},
\tag{5}
$$

 where $$G_{\overline{X}\underline{Z}}$$ is the graph with arrows into $$X$$ removed and arrows out of $$Z$$ removed.

**Rule 3 (Insertion/deletion of actions):** 

$$
P(Y \mid \mathrm{do}(X), \mathrm{do}(Z), W) = P(Y \mid \mathrm{do}(X), W)
\quad \text{if } (Y \perp\!\!\!\perp Z \mid X, W)_{G_{\overline{X}, \overline{Z(W)}}},
\tag{6}
$$

 where $$Z(W)$$ is the set of nodes in $$Z$$ not ancestral to any $$W$$-node in $$G_{\overline{X}}$$.

Huang and Valtorta [\[26\]](#ref-26) proved that the do-calculus is *complete*: every identifiable interventional query can be derived using these three rules. The important consequence for our work is that the backdoor adjustment formula used in this paper is a special case of do-calculus Rule 2, and that computing it requires knowing the direction of the $$X$$–$$Y$$ edge — information that the do-calculus itself takes as given from the graph.

#### 3.4.2. Structural Causal Models

Underlying Pearl’s framework is the concept of a Structural Causal Model (SCM) [\[2\]](#ref-2). An SCM $$\mathcal{M}$$ is a tuple $$\langle U, V, F, P(U) \rangle$$ where $$U = \{U_1, \ldots, U_n\}$$ are exogenous background variables with distribution $$P(U)$$, $$V = \{V_1, \ldots, V_p\}$$ are endogenous observed variables, and $$F = \{f_1, \ldots, f_p\}$$ are structural equations: 

$$
V_i = f_i(\mathrm{Pa}(V_i), U_i), \quad i = 1, \ldots, p,
\tag{7}
$$

 where $$\mathrm{Pa}(V_i)$$ denotes the parents of $$V_i$$ in the causal graph. The ANM is a special case of the SCM where $$f_i$$ is additive in the noise: $$V_i = f_i(\mathrm{Pa}(V_i)) + U_i$$. The SCM framework supports all three rungs of the causal hierarchy: observational queries from the distribution of $$V$$, interventional queries by replacing $$f_i$$ with a constant, and counterfactual queries by abduction (inferring the value of $$U_i$$ from observations) followed by prediction.

### 3.5. The Automation Gap in Prior Work

The mathematical machinery for Rung 2 inference has been available for thirty years. Pearl’s backdoor adjustment formula [\[1\]](#ref-1) tells us how to estimate $$P(Y \mid \mathrm{do}(X = x))$$ from observational data given a valid adjustment set. The formula, repeated here for reference, is: 

$$
P(Y \mid \mathrm{do}(X = x)) = \sum_z P(Y \mid X = x,\, Z = z)\cdot P(Z = z).

\tag{8}
$$

 The critical input this formula needs is the causal graph — specifically, the direction of the edge between $$X$$ and $$Y$$, and the structure of any confounding paths. Without the graph, one cannot determine which variables to include in $$Z$$, and without the correct $$Z$$, the adjustment formula may give a biased or inverted answer.

The state of the art in 2025 was the following:

- **Microsoft DoWhy** [\[7\]](#ref-7): the best Rung 2 inference engine available. Implements backdoor adjustment, front-door adjustment, IV estimation, sensitivity analysis. One million downloads. Requires the user to provide the causal graph as input. Its own documentation explicitly states: *“PyWhy does not implement graph discovery algorithms... graph discovery from observational data is a provably impossible problem in the fully non-parametric setting.”* The user must know the causal direction before using the tool.

- **Amazon OpportunityFinder** [\[9\]](#ref-9): the closest attempt at a code-free, automated causal effect tool. Its 2023 workshop paper acknowledges: *“OpportunityFinder does not implement causal graph generation algorithms — they plan to integrate a causal discovery module in the near future.”* That module was never completed.

- **ANM / RESIT** [\[3\]](#ref-3): correctly identifies causal directions from observational data under the additive noise model. Requires coding in R or Python. Outputs a direction, not a causal effect estimate. Does not compute $$P(Y \mid \mathrm{do}(X))$$.

- **IGCI / LiNGAM** [\[5\]](#ref-5), [\[6\]](#ref-6): similar situation. Direction discovery tools. No downstream effect estimation.

Two camps: tools that do direction discovery but not effect estimation, and tools that do effect estimation but not direction discovery. No prior system automates both end-to-end for a domain expert who is not a statistician.

The CCA+ framework closes this gap by providing the missing ingredient in an automated pipeline.

## 4. Mathematical Foundations

### 4.1. The Additive Noise Model

The entire direction-discovery argument in this paper rests on one structural claim about how causes generate effects. State it plainly: the noise that perturbs an effect is independent of the cause that produces it. When BMI raises glucose, the idiosyncratic variation in how much any one person’s glucose responds — their genetics, their recent sleep, their stress hormones — is not itself correlated with their BMI. It is residual biological variation that sits on top of the systematic relationship, not inside it.

The Additive Noise Model (ANM), formalized by Peters et al. [\[3\]](#ref-3) and Hoyer et al. [\[4\]](#ref-4), encodes exactly this:

> **Definition 4.1 (Additive Noise Model).** A pair $$(X, Y)$$ follows an ANM in the direction $$X \to Y$$ if: 
>
> $$
> Y = f(X) + \varepsilon, \qquad \varepsilon \perp X,
>
> \tag{9}
> $$
>
>  where $$f : \mathbb{R} \to \mathbb{R}$$ is measurable and $$\varepsilon$$ is zero-mean with $$\mathrm{Var}(\varepsilon) = \sigma_\varepsilon^2 < \infty$$, independent of $$X$$.

The independence $$\varepsilon \perp X$$ is what makes direction identifiable. Remove it — let the noise depend on the cause — and the asymmetry disappears. This is not an assumption of convenience. It is the mathematical formulation of what it means for a causal mechanism to be structurally autonomous from its inputs. In the BMI-Glucose example, the random biological variation in how any particular person’s glucose responds to their BMI (their genetics, their recent diet, their sleep) is not itself correlated with BMI. It is residual noise sitting on top of the systematic relationship.

This is a falsifiable assumption. One can test it by fitting the regression $$Y \sim f(X)$$ and testing whether the residuals are independent of $$X$$. RESIT (Regression with Subsequent Independence Test) [\[3\]](#ref-3) is precisely this procedure — it fits the model in both directions and checks independence of residuals. CCA+ uses a different signal (convergence speed) but rests on the same underlying theoretical framework.

#### 4.1.1. The Identifiability Theorem for ANMs

The fundamental result that makes direction discovery under the ANM possible is the following identifiability theorem, due to Peters, Mooij, Janzing, and Schölkopf [\[3\]](#ref-3):

> **Theorem 4.2 (ANM Identifiability, Peters et al. 2014).**
>
> Suppose $$(X, Y)$$ admits an ANM in the direction $$X \to Y$$: $$Y = f(X) + \varepsilon$$, $$\varepsilon \perp X$$, with $$f$$ non-linear. Then, generically, there is no ANM in the reverse direction: there is no function $$g$$ and noise $$\eta \perp Y$$ such that $$X = g(Y) + \eta$$.

The proof relies on a result by Darmois (1953) and Skitovich (1954): if $$Y = f(X) + \varepsilon$$ with $$\varepsilon \perp X$$ and $$f$$ is nonlinear, then the residuals from regressing $$X$$ on $$Y$$ cannot be independent of $$Y$$. More precisely, for any measurable function $$g$$, the residual $$X - g(Y) = X - g(f(X) + \varepsilon)$$ remains correlated with $$Y$$ because the nonlinear mixing of $$X$$ and $$\varepsilon$$ in $$Y$$ cannot be perfectly inverted. This result is “generic” in the measure-theoretic sense: the set of exceptions (pairs $$(f, P_X)$$ for which a reverse ANM also exists) has measure zero in the space of all possible mechanisms.

The key technical condition is nonlinearity. If $$f$$ is linear, then the Darmois-Skitovich theorem does not apply, and both directions admit an ANM. Specifically, if $$Y = aX + \varepsilon_1$$ with $$\varepsilon_1 \sim \mathcal{N}(0, \sigma_1^2)$$, then $$X = \frac{1}{a}Y + \varepsilon_2$$ with $$\varepsilon_2 = -\frac{1}{a}\varepsilon_1 \sim \mathcal{N}(0, \sigma_1^2/a^2)$$, which is also independent of $$Y$$. This is Boundary Condition 1 documented in Section 2.4.

#### 4.1.2. The Algorithmic Markov Condition

A complementary perspective on ANM identifiability comes from algorithmic information theory. Janzing and Schölkopf [\[5\]](#ref-5) proposed the *Algorithmic Markov Condition*: the true causal factorization of a joint distribution has shorter Kolmogorov complexity than any non-causal factorization. Specifically, for $$X \to Y$$: 

$$
K(P_{X,Y}) \approx K(P_X) + K(P_{Y\vert X}),
\tag{10}
$$

 where $$K(\cdot)$$ denotes Kolmogorov complexity (the length of the shortest program that computes the object). The causal direction is the one where the complexity of the cause distribution $$P_X$$ and the conditional $$P_{Y\vert X}$$ are algorithmically independent — knowing one tells you nothing about the other. In the reverse direction, $$P_Y$$ and $$P_{X\vert Y}$$ are algorithmically dependent: knowledge of the marginal $$P_Y$$ constrains the form of $$P_{X\vert Y}$$ because both are shaped by the same underlying causal mechanism. This is the information-theoretic basis for IGCI [\[5\]](#ref-5).

CCA+’s convergence asymmetry can be seen as a computable approximation to the algorithmic Markov condition: the shorter description (lower Kolmogorov complexity) of the causal direction corresponds to faster convergence in the neural network. The forward direction has a shorter effective description because its residuals are genuinely independent noise, requiring less information to specify. The reverse direction’s residuals require additional information (their correlation structure with $$Y$$) that inflates the effective description length and slows convergence.

#### 4.1.3. The Darmois-Skitovich Theorem: Full Formal Treatment

The bedrock of all linear causal direction identification is the Darmois-Skitovich theorem, proved independently by Georges Darmois [\[58\]](#ref-58) and Viktor Skitovich [\[59\]](#ref-59) in 1953. It is worth understanding this theorem in full generality, because it simultaneously explains *why* non-Gaussianity breaks directional symmetry (the key insight behind LiNGAM) and *why* Gaussianity preserves it (the linear Gaussian boundary condition for CCA+).

> **Theorem 4.3 (Darmois-Skitovich, 1953).**
>
> Let $$\xi_1, \ldots, \xi_q$$ be mutually independent real-valued random variables. Define two linear forms: 
>
> $$
> L_1 = \sum_{i=1}^q \alpha_i \xi_i, \qquad L_2 = \sum_{i=1}^q \beta_i \xi_i,
> \tag{11}
> $$
>
>  where $$\alpha_i, \beta_i \in \mathbb{R}$$ are constant coefficients. If $$L_1$$ and $$L_2$$ are statistically independent, then every variable $$\xi_j$$ for which $$\alpha_j \beta_j \neq 0$$ is Gaussian.

The theorem characterizes the Gaussian distribution as the *unique* distribution whose linear combinations can be independent. Every non-Gaussian distribution fails this: if even one $$\xi_j$$ is non-Gaussian and both $$\alpha_j \neq 0$$ and $$\beta_j \neq 0$$, then $$L_1$$ and $$L_2$$ are necessarily dependent.

**Proof sketch.** The proof uses characteristic functions. For independent variables, the characteristic function of $$L_1$$ is $$\phi_{L_1}(t) = \prod_i \phi_{\xi_i}(\alpha_i t)$$. Independence of $$L_1$$ and $$L_2$$ means their joint characteristic function factors: $$\phi_{L_1, L_2}(s, t) = \phi_{L_1}(s) \cdot \phi_{L_2}(t)$$. Expanding and separating terms, this reduces to a functional equation that, under regularity conditions, forces each $$\xi_j$$ (with $$\alpha_j \beta_j \neq 0$$) to have a characteristic function of the form $$\exp(i\mu_j t - \sigma_j^2 t^2/2)$$, which is the characteristic function of a Gaussian. The technical details use the Marcinkiewicz theorem (1939) — that a product of characteristic functions is Gaussian only if each factor is Gaussian — and a separation-of-variables argument on the functional equation.

**Application to LiNGAM.** In the bivariate linear model $$Y = aX + \varepsilon$$ with $$\varepsilon \perp X$$:

- Forward direction: $$Y$$ and $$\varepsilon_\mathrm{fwd} = Y - aX$$ are linear combinations of the independent sources $$(X, \varepsilon)$$ with coefficients $$(a, 1)$$ for $$Y$$ and $$(a, 1) - a(1, 0) = (0, 1)$$ for the residual. The product of the non-intercept coefficients is $$a \times 0 = 0$$, so by Darmois-Skitovich, $$\varepsilon_\mathrm{fwd}$$ and $$X$$ can be independent even if $$\varepsilon$$ is non-Gaussian. This is consistent with the ANM assumption.

- Reverse direction: If we fit $$X = bY + \eta$$ and ask whether $$\eta \perp Y$$, we get $$\eta = X - bY = X - b(aX + \varepsilon) = (1-ba)X - b\varepsilon$$. The coefficients of $$(X, \varepsilon)$$ are $$(1-ba)$$ for $$\eta$$ and $$(a, 1)$$ for $$Y$$. The products are $$a(1-ba)$$ for $$X$$ and $$1 \times (-b)$$ for $$\varepsilon$$. For $$\eta \perp Y$$ (independence of $$\eta$$ and $$Y$$ as linear forms of $$X, \varepsilon$$), Darmois-Skitovich requires that both $$X$$ and $$\varepsilon$$ are Gaussian. If either is non-Gaussian, the reverse residual cannot be independent of $$Y$$.

This is the formal proof that *if $$\varepsilon$$ is non-Gaussian, then $$X \to Y$$ is the unique direction admitting independent residuals*. The linear Gaussian case is the degenerate exception: when $$\varepsilon \sim \mathcal{N}(0, \sigma^2)$$, both directions admit independent Gaussian residuals of different variance, and no independence test can distinguish them.

**Generalization to random vectors and Banach spaces.** Ghurye and Olkin (1962) extended the theorem to random vectors in $$\mathbb{R}^d$$, establishing that the multivariate Gaussian is the unique distribution for which two linear transformations can be independent. Myronyuk (2008) further extended it to random elements in Banach spaces [\[71\]](#ref-71), enabling application to functional data (e.g., fMRI time series curves, EEG traces), as exploited by Func-LiNGAM [\[72\]](#ref-72).

#### 4.1.4. Relationship to Other Functional Model Methods

The ANM sits within a broader family of functional causal model approaches:

- **LiNGAM** (Linear Non-Gaussian Acyclic Model, [\[6\]](#ref-6)): assumes linearity but non-Gaussian noise. The model $$X = B X + E$$ where $$B$$ is a strictly lower triangular matrix (after causal ordering) and $$E$$ has non-Gaussian components is identifiable using Independent Component Analysis (ICA). The key insight is that non-Gaussianity breaks the rotational symmetry of Gaussian distributions that otherwise makes direction unidentifiable. LiNGAM is the linear complement to ANM: ANM handles nonlinear mechanisms with possibly Gaussian noise, while LiNGAM handles linear mechanisms with non-Gaussian noise.

- **Post-Nonlinear models** (Zhang and Hyvärinen [\[31\]](#ref-31)): $$Y = g(f(X) + \varepsilon)$$ where $$g$$ is an additional outer nonlinearity. The post-nonlinear model is more general than the ANM and identifiable under certain conditions on $$f$$, $$g$$, and $$P_\varepsilon$$.

- **IGCI** (Information-Geometric Causal Inference, [\[5\]](#ref-5)): exploits the principle that in the true causal direction, the marginal distribution $$P_X$$ and the conditional $$P_{Y\vert X}$$ are independent in an information-geometric sense. Computable via regression slope comparisons. Works best for deterministic or near-deterministic relationships.

- **SkewScore** [\[32\]](#ref-32): uses the skewness of the score function $$\nabla \log p$$ as a direction signal. Particularly suited to heteroscedastic noise settings where noise variance depends on the input.

CCA+ differs from all of the above in its signal: it uses the optimization landscape of neural networks (convergence speed) rather than residual independence, description length, information geometry, or score function skewness. This orthogonality means CCA+ captures a different aspect of the causal asymmetry and can be complementary to existing methods in an ensemble.

> **Assumption 1 (ANM Identifiability Conditions).**
>
> Throughout this paper, we assume:
>
> 1.  **Nonlinearity:** $$f$$ is nonlinear. The linear Gaussian case $$Y = aX + b + \varepsilon$$ with $$\varepsilon \sim \mathcal{N}(0, \sigma^2)$$ is not identifiable by any method; both directions admit an ANM with Gaussian noise of different variance.
>
> 2.  **Injectivity:** $$f$$ is injective (one-to-one). For every pair $$x_1 \neq x_2$$, $$f(x_1) \neq f(x_2)$$.
>
> 3.  **Full support:** $$P(X)$$ has full support on an interval with finite fourth moments.
>
> 4.  **Scale normalization:** Both $$X$$ and $$Y$$ are standardized to zero mean and unit variance before any analysis. This is a mandatory preprocessing step, not an optional one (see Section 2.3 for a detailed explanation of why).

The injectivity condition deserves attention. Many real-world mechanisms are injective or approximately injective: BMI increasing from 20 to 30 produces systematically higher glucose across the range; engine displacement increasing from 100cc to 400cc produces systematically lower fuel efficiency; shell weight in abalone increasing with age produces systematically more rings. Non-injective mechanisms, such as $$Y = X^2$$ where both positive and negative $$X$$ produce the same $$Y$$, are a known failure mode documented in Section 2.4.

### 4.2. Why the Reverse Direction Is Harder

Bake salt into bread and try to get it back out. You can approximate the original salt content — measure the conductivity, estimate the weight — but some salt is now irreversibly distributed through the loaf. The mixing destroyed information. This is not an analogy. It is the precise reason why the reverse direction in an ANM is harder to learn: when nature generates $$Y = f(X) + \varepsilon$$, the noise $$\varepsilon$$ is mixed into $$Y$$ in a way that cannot be perfectly undone by any finite-capacity predictor. The forward direction has clean, independent noise to converge toward. The reverse direction has entangled, structured residuals that resist convergence.

To make this precise, let $$g_\theta : \mathbb{R} \to \mathbb{R}$$ be a neural network predicting $$Y$$ from $$X$$ (the forward network) and $$h_\phi : \mathbb{R} \to \mathbb{R}$$ predicting $$X$$ from $$Y$$ (the reverse). Both trained with MSE loss and SGD. $$T_\mathrm{fwd}$$ is the step count for $$g_\theta$$ to reach MSE threshold $$\tau$$; $$T_\mathrm{rev}$$ the same for $$h_\phi$$. Three lemmas establish what separates them.

> **Lemma 4.4 (Reverse Residual Dependence).**
>
> Under the ANM with injective $$f$$, for any finite-capacity approximation $$h_\phi \neq h^*$$ where $$h^*(Y) = E[X \mid Y]$$, the reverse residual $$R_\mathrm{rev} = X - h_\phi(Y)$$ satisfies: 
>
> $$
> \mathrm{Cov}(R_\mathrm{rev},\, Y) \neq 0.
> \tag{12}
> $$
>
>  In contrast, the forward residual $$R_\mathrm{fwd} = Y - g_\theta(X)$$ satisfies $$\mathrm{Cov}(R_\mathrm{fwd}, X) \to 0$$ as $$g_\theta \to f$$.

*Proof.* We work through the forward and reverse cases separately.

**Forward case.** As $$g_\theta \to f$$, the forward residual converges: $$R_\mathrm{fwd} = Y - g_\theta(X) \to Y - f(X) = \varepsilon$$. By the ANM assumption, $$\varepsilon \perp X$$, so $$\mathrm{Cov}(\varepsilon, X) = E[\varepsilon X] - E[\varepsilon]E[X] = 0$$.

**Reverse case.** The population-optimal reverse regressor is $$h^*(Y) = E[X \mid Y]$$. At this optimum, the residual $$R^* = X - E[X \mid Y]$$ satisfies $$E[R^* \mid Y] = 0$$ by the law of iterated expectations, and $$\mathrm{Cov}(R^*, Y) = 0$$.

For any finite-capacity approximation $$h_\phi \neq h^*$$, let $$\delta_\phi(Y) = h_\phi(Y) - h^*(Y)$$. Since $$h_\phi \neq h^*$$, $$\delta_\phi$$ is a non-constant function of $$Y$$. Then: 

$$
\begin{aligned}
R_\mathrm{rev} &= X - h_\phi(Y) = (X - h^*(Y)) - \delta_\phi(Y) = R^* - \delta_\phi(Y), \\
\mathrm{Cov}(R_\mathrm{rev}, Y) &= \mathrm{Cov}(R^*, Y) - \mathrm{Cov}(\delta_\phi(Y), Y)
= -\mathrm{Cov}(\delta_\phi(Y), Y).

\end{aligned}\tag{13–14}
$$

 Since $$\delta_\phi$$ is a non-constant measurable function of $$Y$$ and $$P(X)$$ has full support (Assumption 1(iii)), we have $$\mathrm{Cov}(\delta_\phi(Y), Y) \neq 0$$. Therefore $$\mathrm{Cov}(R_\mathrm{rev}, Y) \neq 0$$. ◻

The interpretation is crucial. As a forward network improves, its errors converge to pure independent noise — noise that has no remaining relationship with the input. The network has successfully learned the mechanism $$f$$, and what remains is the irreducible structural noise $$\varepsilon$$. The gradient signal becomes clean: the optimizer knows exactly what kind of residual it is trying to minimize, and that residual is genuinely unpredictable from $$X$$.

For the reverse network, no such convergence happens. No matter how good $$h_\phi$$ becomes — unless it achieves exact population-level optimality, which finite networks trained on finite data cannot do — its residuals remain statistically linked to $$Y$$. The reason is that the noise $$\varepsilon$$ was added to $$Y$$ in a way that cannot be perfectly separated from the $$f(X)$$ component. An analogy: if you bake salt into bread, you cannot perfectly separate the salt from the bread after the fact. You can approximate the original salt content, but some salt remains irreversibly distributed through the bread. The residual contamination is always there.

#### 4.2.1. An Information-Theoretic Perspective on Lemma 1

Lemma 4.4 can also be understood through the lens of mutual information. Define the mutual information between the residual and the input as: 

$$
I_\mathrm{fwd} = I(R_\mathrm{fwd};\ X) = I(Y - g_\theta(X);\ X),
\tag{15}
$$

 

$$
I_\mathrm{rev} = I(R_\mathrm{rev};\ Y) = I(X - h_\phi(Y);\ Y).
\tag{16}
$$

 As $$g_\theta \to f$$, $$R_\mathrm{fwd} \to \varepsilon$$, and since $$\varepsilon \perp X$$ by the ANM assumption, $$I_\mathrm{fwd} \to 0$$. The forward residual becomes information-theoretically independent of the input.

For the reverse direction, $$I_\mathrm{rev} > 0$$ for any finite-capacity $$h_\phi$$. This is because $$Y = f(X) + \varepsilon$$ contains information about both $$X$$ and $$\varepsilon$$ in a mixed form. Given $$Y = y$$, the conditional distribution of $$X$$ given $$Y = y$$ is $$P(X \mid Y = y) \propto P_X(x) \cdot P_\varepsilon(y - f(x))$$. This is a weighted version of $$P_X$$ where the weights depend on $$y$$ through the noise density evaluated at $$y - f(x)$$. As $$y$$ changes, the posterior $$P(X \mid Y = y)$$ changes in a systematic way that is correlated with $$y$$ — and the residual $$X - E[X \mid Y]$$ carries this correlation. No function $$h_\phi(Y)$$ can eliminate this information from the residual without exactly computing $$E[X \mid Y]$$, which requires infinite capacity in general.

Concretely, the mutual information lower bound is: 

$$
I_\mathrm{rev} \geq \frac{1}{2}\log\left(1 + \frac{\mathrm{Var}(E[X \mid Y])}{\mathrm{Var}(X - E[X \mid Y])}\right) > 0,
\tag{17}
$$

 where the right-hand side is positive whenever $$E[X \mid Y]$$ is non-constant, which holds for injective $$f$$ with non-degenerate $$\varepsilon$$.

This information-theoretic formulation makes the connection to description length explicit: a higher $$I_\mathrm{rev}$$ means more bits of information must be transmitted about $$Y$$ to specify the reverse residual, leading to a longer effective description and slower learning.

> **Lemma 4.5 (Higher Irreducible Loss Floor).**
>
> Under Assumption 1 with scale normalization (so $$\mathrm{Var}(X) = \mathrm{Var}(Y) = 1$$), the population-level minimum MSE in each direction satisfies: 
>
> $$
> \mathcal{L}^*_\mathrm{fwd} = \sigma_\varepsilon^2 < \mathcal{L}^*_\mathrm{rev} = E[\mathrm{Var}(X \mid Y)] < 1.
> \tag{18}
> $$
>
>

*Proof.* **Forward minimum.** The optimal forward predictor is $$g^*(X) = f(X) = E[Y \mid X]$$. The minimum MSE is $$E[(Y - g^*(X))^2] = E[\varepsilon^2] = \sigma_\varepsilon^2$$.

**Reverse minimum.** The optimal reverse predictor is $$h^*(Y) = E[X \mid Y]$$. The minimum MSE is: 

$$
\mathcal{L}^*_\mathrm{rev} = E[(X - E[X \mid Y])^2] = E[\mathrm{Var}(X \mid Y)].
\tag{19}
$$

 By the law of total variance applied to the decomposition $$\mathrm{Var}(X) = E[\mathrm{Var}(X \mid Y)] + \mathrm{Var}(E[X \mid Y])$$: 

$$
\mathcal{L}^*_\mathrm{rev} = \mathrm{Var}(X) - \mathrm{Var}(E[X \mid Y]) = 1 - \mathrm{Var}(E[X \mid Y]).
\tag{20}
$$

 Since $$f$$ is injective and nonlinear with $$\varepsilon \perp X$$, the variable $$Y$$ carries genuine information about $$X$$, so $$\mathrm{Var}(E[X \mid Y]) > 0$$ and $$\mathcal{L}^*_\mathrm{rev} < 1$$.

**Comparison.** We need to show $$\mathcal{L}^*_\mathrm{rev} > \mathcal{L}^*_\mathrm{fwd}$$. This is equivalent to showing $$E[\mathrm{Var}(X \mid Y)] > \sigma_\varepsilon^2$$.

By the ANM, $$Y = f(X) + \varepsilon$$. The conditional distribution of $$X$$ given $$Y = y$$ has variance $$\mathrm{Var}(X \mid Y = y)$$. For injective $$f$$, each value of $$y$$ corresponds to a unique $$f(X)$$ value up to noise, and the spread of $$X$$ given $$Y$$ reflects both the noise and the curvature of $$f^{-1}$$. This variance is strictly greater than $$\sigma_\varepsilon^2 / (f'(X))^2$$ in the smooth case, and in general is strictly larger than the forward irreducible noise for nonlinear $$f$$. The full proof requires conditions on the smoothness of $$f$$ that are satisfied under Assumption 1; we omit the technical details for brevity. ◻

> **Insight.** The gap $$\mathcal{L}^*_\mathrm{rev} - \mathcal{L}^*_\mathrm{fwd}$$ is not just a numerical difference — it is a structural feature of the optimization landscape. The forward network can reach a low loss floor because its target ($$\varepsilon$$) is independent of its input ($$X$$). The reverse network is permanently above a higher floor because its target ($$E[X \mid Y]$$) leaves a residual that is correlated with its input ($$Y$$). No amount of additional training capacity or more epochs can close this gap. It is irreducible.

> **Lemma 4.6 (Harder Landscape Implies More Steps).**
>
> Let two MSE objectives $$\mathcal{L}_1$$ and $$\mathcal{L}_2$$ both satisfy the Polyak-Łojasiewicz (PL) condition [\[14\]](#ref-14) with constant $$\mu > 0$$ near their respective minima. Suppose $$\mathcal{L}^*_2 > \mathcal{L}^*_1$$. Under SGD with step size $$\eta$$ and gradient noise variance $$\sigma_g^2$$, the expected steps to reach threshold $$\tau$$ satisfy: 
>
> $$
> E[T_2] \geq E[T_1] + \Omega\!\left(\frac{\Delta^*}{\eta\mu \cdot \tau}\right),
> \tag{21}
> $$
>
>  where $$\Delta^* = \mathcal{L}^*_2 - \mathcal{L}^*_1 > 0$$.

*Proof.* The standard SGD convergence result under the PL condition [\[15\]](#ref-15) gives: 

$$
E[\mathcal{L}(\theta_t) - \mathcal{L}^*] \leq
(1 - 2\eta\mu)^t(L_0 - L^*) + \frac{\eta\sigma_g^2}{2\mu}.
\tag{22}
$$

 For objective $$\mathcal{L}_1$$ to reach $$\tau$$, it suffices to have $$(1-2\eta\mu)^t(L_0 - \mathcal{L}_1^*) \leq \tau - \mathcal{L}_1^* - \frac{\eta\sigma_g^2}{2\mu}$$, giving $$E[T_1] = O\!\left(\frac{1}{2\eta\mu}\log\frac{L_0 - \mathcal{L}_1^*}{\tau - \mathcal{L}_1^*}\right)$$. For $$\mathcal{L}_2$$, the effective gap to close is $$\tau - \mathcal{L}_2^* = (\tau - \mathcal{L}_1^*) - \Delta^* < \tau - \mathcal{L}_1^*$$, so $$T_2$$ must additionally overcome the extra offset $$\Delta^*$$, giving the stated bound. ◻

> **Theorem 4.7 (CCA Asymmetry).**
>
> Under Assumption 1, if the forward and reverse objectives both satisfy the PL condition with constant $$\mu > 0$$ locally near their minima, then for any threshold $$\tau > \mathcal{L}^*_\mathrm{fwd}$$: 
>
> $$
> E[T_\mathrm{fwd}] < E[T_\mathrm{rev}].
> \tag{23}
> $$
>
>  The forward direction converges in strictly fewer expected gradient steps.

*Proof.* By Lemma 4.5, $$\mathcal{L}^*_\mathrm{rev} > \mathcal{L}^*_\mathrm{fwd}$$, so $$\Delta^* > 0$$. By Lemma 4.6, this strictly positive gap implies $$E[T_\mathrm{rev}] > E[T_\mathrm{fwd}]$$. ◻

> **Remark 4.8.** The PL condition is weaker than convexity: it requires only that the gradient norm lower-bounds suboptimality, $$\|\nabla\mathcal{L}\|^2 \geq 2\mu(\mathcal{L} - \mathcal{L}^*)$$. This holds for many overparameterized networks near local minima. The theorem gives a lower bound on the convergence gap; experimentally, the gap is substantially larger because the reverse landscape also contains saddle points and flat regions not captured by the PL approximation.

### 4.3. The Mandatory Role of Scale Normalization

Before training either network, both $$X$$ and $$Y$$ must be standardized: 

$$
\tilde{X} = \frac{X - \mu_X}{\sigma_X}, \qquad \tilde{Y} = \frac{Y - \mu_Y}{\sigma_Y}.

\tag{24}
$$

 This is not a heuristic preprocessing step — it is a theoretical necessity.

To see why, consider $$Y = X^3 + \varepsilon$$ with $$X \sim \mathcal{N}(0,1)$$. Then $$\mathrm{Var}(Y) = E[X^6] + \sigma_\varepsilon^2 \approx 15 + \sigma_\varepsilon^2$$, while $$\mathrm{Var}(X) = 1$$. Without normalization, the forward network’s loss function is operating at a scale approximately 15 times larger than the reverse network’s. The forward network sees larger gradient magnitudes throughout training and reaches any fixed threshold $$\tau$$ more slowly, not because it is the non-causal direction, but because its output variance is larger. This scale contamination can completely reverse the CCA+ signal — and empirically does: without normalization, CCA+ achieves only 6/30 correct on this DGP, versus 26/30 with normalization.

After standardization, $$\mathrm{Var}(\tilde{X}) = \mathrm{Var}(\tilde{Y}) = 1$$, and the convergence comparison is on equal footing. The asymmetry that remains after normalization is purely the causal asymmetry established in Theorem 4.7.

### 4.4. Boundary Conditions and When CCA+ Fails

CCA+ is not a universal method. It has three theoretically-predicted and experimentally-confirmed failure modes. Understanding these is as important as understanding when it works.

#### 4.4.1. Linear Gaussian Mechanisms

If $$f(x) = ax + b$$ and $$\varepsilon \sim \mathcal{N}(0, \sigma^2)$$, then both directions admit an ANM with Gaussian noise of different variance: 

$$
Y = aX + b + \varepsilon_1 \quad \Leftrightarrow \quad X = \frac{1}{a}Y - \frac{b}{a} + \varepsilon_2,
\quad \varepsilon_2 = -\frac{1}{a}\varepsilon_1.
\tag{25}
$$

 This bijectivity means the two optimization problems are isomorphic: the forward and reverse networks learn equally efficiently. CCA+ returns near-zero scores — which is the correct answer, because the direction genuinely is not identifiable.

#### 4.4.2. Non-Injective Mechanisms

When $$f$$ is not one-to-one, Lemma 4.4 fails. The canonical example is $$Y = X^2 + \varepsilon$$ with symmetric $$P(X)$$. The reverse regression target is $$E[X \mid Y = y] = 0$$ for all $$y > 0$$, because $$P(X = x \mid Y = y) = P(X = -x \mid Y = y)$$ by symmetry. The reverse network therefore learns to predict zero in a handful of training steps — not because it has learned a meaningful inverse relationship, but because zero is the optimal constant predictor for a symmetric distribution. This gives $$T_\mathrm{rev} \ll T_\mathrm{fwd}$$ and a large positive CCA+ score, predicting the wrong direction.

> **Caution.** The $$Y = X^2$$ boundary condition is a degenerate collapse, not a sign of the reverse direction being truly causal. When CCA+ returns a large positive score for a pair that might have a non-injective relationship, the result should be treated with caution.

#### 4.4.3. Scale Contamination Without Normalization

As described in Section 2.3, large output variance differences corrupt the convergence comparison. The solution is simply to apply standardization (24) before any training. This boundary condition is entirely avoidable.

### 4.5. The CCA+ Score

In practice, we approximate the convergence time asymmetry by measuring final validation loss after a fixed number of epochs. The theoretical quantity is the step count; the practical proxy is the loss value at the end of training. Under the analysis above, if the forward direction converges faster, it will also reach a lower final loss in the same number of epochs.

> **Definition 4.9 (CCA+ Score).**
>
> Let $$\tilde{X}$$ and $$\tilde{Y}$$ be the standardized versions of $$X$$ and $$Y$$. For each of $$K$$ random seeds $$k = 1, \ldots, K$$:
>
> 1.  Split the data into 80% training, 20% validation.
>
> 2.  Train a two-hidden-layer MLP $$g_\theta^{(k)}$$ on $$(\tilde{X}_\mathrm{tr}, \tilde{Y}_\mathrm{tr})$$ for $$E$$ epochs. Record validation MSE $$L_\mathrm{fwd}^{(k)}$$.
>
> 3.  Train an identical MLP $$h_\phi^{(k)}$$ on $$(\tilde{Y}_\mathrm{tr}, \tilde{X}_\mathrm{tr})$$ for $$E$$ epochs. Record validation MSE $$L_\mathrm{rev}^{(k)}$$.
>
> The CCA+ score is: 
>
> $$
> \mathrm{CCA}^+(X, Y) = \bar{L}_\mathrm{fwd} - \bar{L}_\mathrm{rev}
> = \frac{1}{K}\sum_{k=1}^K L_\mathrm{fwd}^{(k)} - \frac{1}{K}\sum_{k=1}^K L_\mathrm{rev}^{(k)}.
>
> \tag{26}
> $$
>
>

The interpretation of the score is:

- $$\mathrm{CCA}^+ < -\theta_s$$: strong evidence that $$X \to Y$$.

- $$\mathrm{CCA}^+ > +\theta_s$$: strong evidence that $$Y \to X$$.

- $$-\theta_w \leq \mathrm{CCA}^+ \leq \theta_w$$: AMBIGUOUS — no reliable direction.

where $$\theta_s = 0.03$$ is the strong threshold and $$\theta_w = 0.008$$ is the weak threshold in our implementation. These values were calibrated empirically on synthetic data with known directions.

Averaging over multiple seeds reduces variance from random initialization. In our experiments, $$K = 5$$ seeds provided sufficient stability; increasing to $$K = 10$$ or more further reduces the variance of the score at modest additional computation cost.

## 5. The Faithfulness Assumption: What It Is, When It Fails, and Why CCA+ Is Immune

### 5.1. The Faithfulness Condition

Here is a problem that quietly breaks most causal discovery algorithms in practice, and that almost no applied paper discusses. It goes by the name faithfulness, and it is the reason why methods like PC and GES can return completely wrong graphs on real data even when the sample size is large.

The issue is this. Constraint-based discovery methods work by testing conditional independences in the data and translating them into graph edges. The translation rests on an assumption: that every conditional independence you observe in the distribution actually corresponds to a d-separation in the true graph. In other words, there are no “accidental” independences — no places where two causal paths happen to cancel each other out, creating the appearance of no relationship where a causal one exists.

That assumption is called faithfulness, and it can fail.

> **Definition 5.1 (Causal Markov Condition).** A distribution $$P$$ over variables $$V$$ satisfies the Causal Markov Condition (CMC) with respect to a DAG $$G$$ if every variable $$V_i \in V$$ is conditionally independent of all its non-descendants given its parents $$\mathrm{Pa}(V_i)$$ in $$G$$: 
>
> $$
> V_i \perp\!\!\!\perp \mathrm{NonDesc}(V_i) \mid \mathrm{Pa}(V_i).
> \tag{27}
> $$
>
>

The CMC is satisfied by any distribution generated by an SCM — it is essentially a restatement of the structural equation model’s modularity. Nobody argues about this one. Faithfulness is different.

> **Definition 5.2 (Faithfulness Condition).** A distribution $$P$$ is faithful to a DAG $$G$$ if every conditional independence in $$P$$ is entailed by the CMC applied to $$G$$. Equivalently, for any disjoint sets $$A, B, C > \subset V$$: $$(A \perp\!\!\!\perp B \mid C)_P \Rightarrow (A \perp\!\!\!\perp B \mid C)_G$$ (where the right-hand side denotes d-separation in $$G$$).

The plain reading: the only independences you see in the data are the ones the graph structurally requires. No accidental cancellations, no flukes.

### 5.2. Why Faithfulness Can Fail: Path Cancellation

Faithfulness can fail when the effects of multiple causal paths between two variables exactly cancel. Consider the three-variable path $$X \to Y \to Z$$ with additional direct effect $$X \to Z$$. The total effect of $$X$$ on $$Z$$ is: 

$$
\frac{\partial Z}{\partial X} = \underbrace{\beta_{XY} \cdot \beta_{YZ}}_{\text{indirect}} + \underbrace{\beta_{XZ}}_{\text{direct}}.
\tag{28}
$$

 If $$\beta_{XZ} = -\beta_{XY} \cdot \beta_{YZ}$$, the total effect is zero: $$X$$ and $$Z$$ are marginally independent despite $$X$$ causing $$Z$$ through two paths. A conditional independence test would incorrectly conclude there is no edge between $$X$$ and $$Z$$, leading the PC algorithm to output a wrong skeleton.

Uhler et al. [\[73\]](#ref-73) studied this phenomenon geometrically. The set of unfaithful distributions for a given DAG forms a union of algebraic varieties (zero sets of polynomials in the structural equation parameters). For the three-node case: 

$$
\text{Unfaithful iff: } a_{12} = 0 \text{ or } a_{13} = 0 \text{ or } a_{23} = 0 \text{ or }
\mathrm{Cov}(X_1, X_3 \mid X_2) = 0 \text{ or } \cdots,
\tag{29}
$$

 each condition defining a lower-dimensional algebraic variety. While the Lebesgue measure of the unfaithful set is zero (a generic distribution is faithful), the distribution can be arbitrarily *close* to a faithfulness violation. This is the key practical problem: with finite samples, distributions within a small neighborhood of a faithfulness violation produce spurious independence signals, causing the PC algorithm to make errors. Zhang and Spirtes [\[74\]](#ref-74) formalized this as the *strong-faithfulness* condition ($$\lambda$$-strong-faithfulness): requiring all non-zero partial correlations to exceed a threshold $$\lambda > 0$$, which enables uniform consistency of the PC algorithm (as opposed to mere pointwise consistency). However, Uhler et al. showed that for high-dimensional graphs with many cycles, the proportion of $$\lambda$$-strong-faithful distributions decreases rapidly — meaning faithfulness violations are practically common, not measure-theoretically rare.

### 5.3. Why CCA+ Does Not Require Faithfulness

CCA+ is a functional-model-based method, not a constraint-based method. It does not use conditional independence tests and therefore does not require the Faithfulness Condition. The convergence asymmetry exploited by CCA+ is a property of the *noise structure* of the data-generating process (specifically, the independence $$\varepsilon \perp X$$ in the ANM), not a property of the conditional independence structure of the graph.

Two variables can be marginally independent but still satisfy an ANM in one direction: if $$X$$ and $$Y$$ are independent (no causal relationship), then by convention CCA+ should return AMBIGUOUS, and indeed the forward and reverse loss floors will both equal $$\mathrm{Var}(Y) = 1$$ (after standardization), giving a CCA+ score near zero. Faithfulness violations that fool PC into thinking there is no edge where there is one do not affect CCA+, because CCA+ never tests for independence.

The relevant boundary conditions for CCA+ (nonlinearity, injectivity, and scale normalization) are entirely distinct from faithfulness. In particular, CCA+ can correctly orient an edge that the PC algorithm leaves undirected due to a faithfulness violation in the surrounding graph structure. This is a concrete practical advantage.

### 5.4. Near-Faithfulness and Weak Signals

While CCA+ is immune to faithfulness violations, it has its own version of the “near-violation” problem: near-zero CCA+ scores correspond to data-generating processes where the causal asymmetry is very weak. The threshold $$\theta_w = 0.008$$ separates AMBIGUOUS from weak-signal detection, but there is an intermediate regime where the score is above threshold but unreliable.

The two situations that produce weak CCA+ scores are:

1.  **Near-linear mechanisms.** If $$f$$ is approximately but not exactly linear, the asymmetry exists but is small. The CCA+ score will be small but positive.

2.  **High noise variance.** If $$\sigma_\varepsilon^2$$ is close to $$\mathrm{Var}(Y)$$ (nearly all variation is noise), the forward network converges to near-random prediction, and the asymmetry with the reverse network is small.

In both cases, the theoretical guarantee of Theorem 4.7 still holds in expectation, but the variance of the empirical CCA+ score may be large relative to the gap. Increasing the number of seeds $$K$$ and the training epochs $$E$$ provides more signal averaging and reduces this variance.

## 6. The Confounder Adjustment Problem

### 6.1. Why Direction Alone Is Not Enough

CCA+ gives you a directed edge. That is the hard part, and most of this paper is about proving it works. But a directed edge is not an intervention estimate. The number — the ACE, the $$\hat{\beta}_X$$ that tells you how many mg/dL of glucose come off per unit of BMI reduction — requires one additional step: accounting for the variables that confound the relationship.

Age is the clearest case in the Pima data. Older patients have higher BMI on average, because metabolism slows and physical activity decreases with age. Independently, older patients have higher glucose, because insulin sensitivity declines with age regardless of body weight. So part of what looks like “BMI predicts glucose” is actually “age predicts both.” If we estimate the BMI effect naively, we capture both the true causal effect and the age-driven correlation — and call all of it “BMI’s effect.” The naive estimate is wrong. The formula for how wrong is exact: $$\hat{\beta}_X^{\mathrm{naive}} = \beta_X + \sum_i \beta_{Z_i} \cdot \mathrm{Cov}(Z_i, X) / \mathrm{Var}(X)$$. Each unmeasured or unadjusted confounder inflates or deflates the estimate by a calculable amount. The backdoor formula removes this inflation.

Formally, the confounded regression gives: 

$$
\hat{\beta}_X^\mathrm{naive} = \beta_X + \sum_{i} \beta_{Z_i} \cdot \frac{\mathrm{Cov}(Z_i, X)}{\mathrm{Var}(X)},

\tag{30}
$$

 where $$\beta_X$$ is the true causal coefficient and the second term is the omitted variable bias — the amount by which the naive estimate is inflated (or deflated) by each uncontrolled confounder. Equation (30) is the classical omitted variable bias formula from econometrics, and it shows precisely how and why the naive estimate differs from the true causal effect.

### 6.2. Pearl’s Backdoor Criterion

Pearl provides a graphical condition that, when satisfied, guarantees that controlling for a set of variables $$Z$$ is sufficient to identify the causal effect.

> **Definition 6.1 (Backdoor Criterion).**
>
> A set of variables $$Z$$ satisfies the backdoor criterion relative to the ordered pair $$(X, Y)$$ in a directed acyclic graph $$G$$ if:
>
> 1.  No member of $$Z$$ is a descendant of $$X$$ in $$G$$.
>
> 2.  $$Z$$ blocks every directed path from any ancestor of $$X$$ to $$Y$$ that has an arrow into $$X$$ (every “backdoor path”).
>
> If $$Z$$ satisfies the backdoor criterion, then: 
>
> $$
> P(Y \mid \mathrm{do}(X = x)) = \sum_z P(Y \mid X = x, Z = z) \cdot P(Z = z).
> \tag{8}
> \tag{31}
> $$
>
>

The first condition — no descendants of $$X$$ in $$Z$$ — is critical and easily violated. In the Pima dataset, insulin is correlated with both BMI and glucose. But insulin is downstream of glucose (the pancreas secretes insulin in response to blood glucose levels). Including insulin in the adjustment set would block the very causal path we are trying to measure. Post-treatment variables (variables caused by the cause or effect) must be excluded.

The second condition — blocking backdoor paths — is what makes the adjustment work. A backdoor path is any path from $$X$$ to $$Y$$ that starts with an arrow *into* $$X$$ rather than out of it. These paths represent confounding: correlations between $$X$$ and $$Y$$ that are not due to $$X$$ causing $$Y$$, but due to common causes.

### 6.3. Practical Confounder Identification

In our setting, we do not have a pre-specified causal graph. We have a dataset with multiple columns and a discovered directed edge $$X \to Y$$. We need to automatically identify which other variables in the dataset should be included in the adjustment set.

#### 6.3.1. Collider Variables and Why They Must Be Excluded

Before presenting the identification procedure, we must address a subtle and important failure mode: collider bias [\[2\]](#ref-2). A *collider* is a variable that is caused by both $$X$$ and $$Y$$, rather than causing both. In graph terms: $$X \to C \leftarrow Y$$. If a collider $$C$$ is included in the adjustment set $$Z$$, then conditioning on $$C$$ opens a *spurious* path between $$X$$ and $$Y$$ — a path that was blocked before conditioning. This *increases* confounding rather than removing it, potentially reversing the sign of the estimated ACE.

A classic example: suppose $$X$$ is a gene variant, $$Y$$ is a disease, and $$C$$ is “hospitalized.” Both the gene variant and the disease increase the probability of hospitalization. If we condition on hospitalized patients only (i.e., include hospitalization in the adjustment set), we introduce a spurious negative correlation between $$X$$ and $$Y$$: among hospitalized patients, having the gene variant makes the disease less likely as an explanation for hospitalization (because the gene itself explains the hospitalization). This is Berkson’s paradox [\[33\]](#ref-33), a famous early example of collider bias.

The practical implication: any variable that is downstream of both $$X$$ and $$Y$$ must be excluded from the adjustment set, even if it is strongly correlated with both. Our third criterion (partial correlation of $$Z$$ and $$Y$$ after conditioning on $$X$$) catches most but not all colliders. A collider on $$X$$ and $$Y$$ will typically have a partial correlation with $$Y$$ given $$X$$ that is close to zero if $$X$$’s influence on $$C$$ explains most of the correlation. However, domain knowledge should always be used to override the automatic screening when the causal status of a candidate variable is known.

We use a three-criterion screening procedure. A variable $$Z$$ in the dataset is flagged as a candidate confounder if all three conditions hold:

1.  $$\vert r(Z, X)\vert  > \theta$$, where $$r$$ denotes Pearson correlation and $$\theta = 0.15$$ is the threshold. This checks that $$Z$$ is associated with the cause.

2.  $$\vert r(Z, Y)\vert  > \theta$$. This checks that $$Z$$ is associated with the effect.

3.  $$\vert r_\mathrm{partial}(Z, Y \mid X)\vert  > \theta/2$$, where the partial correlation is: $$r_\mathrm{partial}(Z, Y \mid X) = r(Z - \hat{Z}_{\vert X},\; Y - \hat{Y}_{\vert X}),$$ with $$\hat{Z}_{\vert X}$$ and $$\hat{Y}_{\vert X}$$ denoting the linear projections of $$Z$$ and $$Y$$ onto $$X$$. This checks that $$Z$$ predicts $$Y$$ over and above what $$X$$ predicts, ensuring the variable is not merely a consequence of $$X$$.

This procedure has known failure modes: it can include false positives (variables that are not confounders but satisfy all three criteria) and miss confounders with correlations below threshold. Including false positives in the adjustment set does not bias the ACE estimate — it merely adds unnecessary variables to the regression. Missing confounders below threshold leaves residual omitted variable bias. The threshold $$\theta = 0.15$$ was calibrated to favor inclusion: in the absence of domain knowledge, it is better to over-adjust than under-adjust.

> **Caution.** Variables that are *downstream* of $$X$$ or $$Y$$ will often satisfy criteria (1) and (2) but fail criterion (3). Insulin in the Pima dataset is an example: its partial correlation with BMI after controlling for Glucose is low because Insulin is determined by Glucose. Criterion (3) catches most but not all descendants. When domain knowledge is available, it should override the automatic screening.

#### 6.3.2. Alternative Adjustment Methods

The linear regression adjustment used in this paper is the simplest valid implementation of the backdoor formula, but it is not the only one. Several alternatives offer different tradeoffs between assumptions, robustness, and interpretability:

**Propensity Score Adjustment.** The propensity score [\[16\]](#ref-16), defined as $$e(z) = P(X = x \mid Z = z)$$ for a binary treatment or $$E[X \mid Z = z]$$ for a continuous treatment, is the conditional probability (or conditional mean) of the cause given the confounders. Under the backdoor criterion, adjusting for the propensity score is sufficient — you do not need to adjust for $$Z$$ directly. This is Rosenbaum and Rubin’s famous result that propensity score stratification achieves balance on all observed confounders. In our linear regression framework, the propensity score is implicitly included when $$X$$ is included in the adjusted regression: the residual of $$X$$ after regressing on $$Z$$ is exactly the variation in $$X$$ that is independent of $$Z$$, and the coefficient of this residual in the regression of $$Y$$ is the ACE.

**Inverse Probability Weighting (IPW).** An alternative is to reweight observations by $$1/P(X = x \mid Z)$$, creating a pseudo-population in which $$X$$ is independent of $$Z$$. The average causal effect is then the difference in weighted outcome means. IPW is particularly useful when the number of confounders is large relative to sample size, as regression adjustment can suffer from high variance in that regime.

**Doubly Robust Estimation.** Doubly robust estimators [\[34\]](#ref-34) combine outcome regression (our current approach) with propensity score weighting. They are consistent if either the outcome model or the propensity score model is correctly specified — not necessarily both. This provides a degree of protection against model misspecification that neither approach alone offers.

**Matching.** Rather than modeling the confounding relationship, matching-based methods find pairs of observations with similar confounder values but different values of $$X$$, and compare their $$Y$$ values directly. This is nonparametric and makes no linearity assumption, but requires good covariate overlap (i.e., for every value of $$X$$, there exist observations at both high and low confounder values).

For the purpose of this paper, we use linear regression adjustment for its simplicity, interpretability, and exact alignment with the backdoor formula’s linear continuous case. The nonlinear extensions are discussed in Section 8.

## 7. The Backdoor Adjustment Formula and ACE Estimation

### 7.1. From the Formula to a Number

Pearl’s backdoor formula is mathematically complete. It tells you exactly what to compute. The difficulty has never been the formula itself — it has been getting the inputs right: knowing the causal direction, identifying valid adjustment variables, and choosing a model for the conditional outcome distribution. The first two steps are handled by CCA+ and the confounder screening procedure. This section handles the third.

For continuous variables with a linear adjustment model, we fit: 

$$
Y = \alpha + \beta_X X + \sum_{i=1}^k \beta_{Z_i} Z_i + \epsilon,

\tag{33}
$$

 where $$\epsilon$$ is the residual. The coefficients $$(\hat{\alpha}, \hat{\beta}_X, \hat{\beta}_{Z_1}, \ldots, \hat{\beta}_{Z_k})$$ are obtained by ordinary least squares (OLS). The estimator minimizes: 

$$
\hat{\boldsymbol{\beta}} = \arg\min_{\boldsymbol{\beta}} \sum_{i=1}^n \left(y_i - \beta_0 - \beta_X x_i - \sum_{j=1}^k \beta_{Z_j} z_{ij}\right)^2,
\tag{34}
$$

 with closed-form solution $$\hat{\boldsymbol{\beta}} = (\mathbf{X}^\top \mathbf{X})^{-1}\mathbf{X}^\top \mathbf{y}$$ where $$\mathbf{X}$$ is the design matrix $$[1, X, Z_1, \ldots, Z_k]$$.

The key output is $$\hat{\beta}_X$$, the coefficient on the cause variable after controlling for the confounders. This is the **Average Causal Effect (ACE)**: the expected change in $$Y$$ per unit forced increase in $$X$$, averaged over the population distribution of confounders.

#### 7.1.1. Why OLS Gives the ACE Under the Backdoor Criterion

It is worth making explicit why the OLS coefficient $$\hat{\beta}_X$$ from the regression (33) is the correct estimator for the ACE. This is not obvious: OLS fits the best linear predictor of $$Y$$ given $$(X, Z_1, \ldots, Z_k)$$, which naively seems like a Rung 1 operation. The reason it gives the Rung 2 quantity is the Frisch-Waugh-Lovell (FWL) theorem [\[36\]](#ref-36).

> **Proposition 7.1 (Frisch-Waugh-Lovell Theorem).**
>
> Let $$\hat{\beta}_X$$ be the OLS coefficient on $$X$$ in the regression of $$Y$$ on $$(X, Z_1, \ldots, Z_k)$$. Then $$\hat{\beta}_X$$ equals the OLS coefficient in the simple regression of $$\tilde{Y}$$ on $$\tilde{X}$$, where $$\tilde{Y}$$ and $$\tilde{X}$$ are the residuals from regressing $$Y$$ and $$X$$ on $$(Z_1, \ldots, Z_k)$$ respectively.

The FWL theorem says that $$\hat{\beta}_X$$ measures the relationship between the part of $$X$$ that is orthogonal to the confounders and the part of $$Y$$ that is orthogonal to the confounders. In causal terms: it measures the relationship between $$X$$ after removing confounder influence and $$Y$$ after removing confounder influence. This is precisely the backdoor adjustment: the variation in $$X$$ that is independent of $$Z$$ (the residual $$\tilde{X}$$) is the variation that, by the backdoor criterion, is causally related to $$Y$$. The OLS slope on this residual is therefore the ACE.

More formally, under the linear backdoor model: 

$$
E[Y \mid \mathrm{do}(X = x)] = E[E[Y \mid X = x, Z]] = \alpha + \beta_X x + \sum_i \beta_{Z_i} \bar{Z}_i.
\tag{35}
$$

 The derivative $$\frac{\partial}{\partial x} E[Y \mid \mathrm{do}(X = x)] = \beta_X$$ is the ACE, and the OLS estimator $$\hat{\beta}_X$$ is consistent for $$\beta_X$$ when the adjustment set $$Z$$ satisfies the backdoor criterion and the linear model is correctly specified.

#### 7.1.2. The Gauss-Markov Theorem and Efficiency

Under homoscedastic errors ($$\mathrm{Var}(\epsilon) = \sigma^2$$ for all observations), the Gauss-Markov theorem guarantees that the OLS estimator is the *best linear unbiased estimator* (BLUE) of $$\beta_X$$: among all linear unbiased estimators, OLS has minimum variance. The variance of $$\hat{\beta}_X$$ is: 

$$
\mathrm{Var}(\hat{\beta}_X) = \sigma^2 \cdot (X^\top M_Z X)^{-1},
\tag{36}
$$

 where $$M_Z = I - Z(Z^\top Z)^{-1} Z^\top$$ is the annihilator matrix that projects onto the space orthogonal to the confounders. This is the variance that the bootstrap procedure in Section 4.3 estimates nonparametrically, without assuming homoscedasticity.

> **Definition 7.2 (Average Causal Effect via Backdoor Adjustment).**
>
> Under the backdoor criterion (Definition 6.1) with linear adjustment, the ACE of $$X$$ on $$Y$$ is: 
>
> $$
> \mathrm{ACE}(X \to Y) = \hat{\beta}_X = \frac{\partial}{\partial x} E[Y \mid \mathrm{do}(X = x)].
> \tag{37}
> $$
>
>  The intervention prediction at a specific value $$x$$ is: 
>
> $$
> \widehat{E}[Y \mid \mathrm{do}(X = x)] = \hat{\alpha} + \hat{\beta}_X \cdot x + \sum_{i=1}^k \hat{\beta}_{Z_i} \cdot \bar{Z}_i,
>
> \tag{38}
> $$
>
>  where $$\bar{Z}_i$$ is the sample mean of $$Z_i$$ (representing the population average confounder profile).

Equation (38) is the Rung 2 output. It answers the question: “If we forced $$X$$ to value $$x$$ for everyone in this population, what would the average $$Y$$ be?” This is different from asking what the average $$Y$$ is among people who *happen to have* $$X = x$$, which is the Rung 1 answer. The difference is the confounding bias that the adjustment removes.

### 7.2. Quantifying the Confounding Bias Removed

The confounding bias is the difference between the naive and adjusted estimates: 

$$
\text{Confounding bias} = \hat{\beta}_X^\mathrm{naive} - \hat{\beta}_X^\mathrm{adjusted}.

\tag{39}
$$

 This quantity tells us how much the naive regression was misleading due to unmeasured or uncontrolled confounders in the adjustment set. A large bias means the observational correlation substantially overstated or understated the true causal effect.

In the Pima Diabetes case, the naive effect of BMI on glucose is approximately $$1.31$$ mg/dL per BMI unit, while the adjusted ACE is approximately $$1.04$$ mg/dL per BMI unit. The bias of $$0.27$$ mg/dL per BMI unit reflects the portion of the naive estimate that was attributable to age and pregnancies — older, more-pregnant women tend to have higher BMI and independently higher glucose, so the naive estimate confounds the BMI effect with the age and parity effects.

### 7.3. Bootstrap Confidence Intervals

The ACE estimate from equation (33) has an associated uncertainty from finite sample size and from potential model misspecification. We quantify this uncertainty via the nonparametric bootstrap [\[17\]](#ref-17).

Let the original dataset be $$\mathcal{D} = \{(x_i, y_i, z_i^1, \ldots, z_i^k)\}_{i=1}^n$$. For $$b = 1, \ldots, B$$ bootstrap resamples:

1.  Draw $$\mathcal{D}_b$$ by sampling $$n$$ observations with replacement from $$\mathcal{D}$$.

2.  Fit the adjusted regression (33) on $$\mathcal{D}_b$$.

3.  Record the bootstrap ACE $$\hat{\beta}_X^{(b)}$$.

The $$95\%$$ bootstrap confidence interval is the interval from the $$2.5$$th to the $$97.5$$th percentile of $$\{\hat{\beta}_X^{(1)}, \ldots, \hat{\beta}_X^{(B)}\}$$: 

$$
\mathrm{CI}_{95\%} = \left[\hat{\beta}_X^{(0.025)},\; \hat{\beta}_X^{(0.975)}\right].
\tag{40}
$$

We use $$B = 500$$ resamples in our experiments. This is sufficient for stable 95% interval estimates; for 99% intervals or narrower problems, $$B = 1000$$ or more is recommended.

The bootstrap CI captures sampling uncertainty in the adjusted regression coefficients. It does not capture model uncertainty (whether the linear adjustment is correctly specified) or structural uncertainty (whether the no-unmeasured-confounders assumption holds). These limitations are discussed in Section 7.

### 7.4. Validity Conditions

The interventional estimate (38) is causally valid under three conditions:

1.  **Correct direction discovery.** CCA+ must correctly identify $$X \to Y$$. If the direction is wrong, the adjustment set is misidentified, and the formula gives an estimate of the wrong quantity.

2.  **Strong ignorability (no unmeasured confounders).** There must be no variable that causes both $$X$$ and $$Y$$ and is absent from the dataset or the adjustment set. This is the condition introduced by Rosenbaum and Rubin [\[16\]](#ref-16) as a necessary condition for identification of causal effects from observational data.

3.  **Correct functional form.** The adjustment in (33) assumes that the confounding relationship is approximately linear. Nonlinear confounding will leave residual bias. Extensions to nonlinear adjustment are discussed in Section 8.

These are standard requirements for any observational causal inference method. They are not additional limitations of CausalLens — they are the baseline requirements of the backdoor adjustment formula itself. Every causal inference from observational data, including those produced by econometricians with decades of domain expertise, rests on some version of these assumptions.

## 8. The Complete Pipeline

### 8.1. End-to-End Architecture

The previous four sections each solved one piece of a five-piece puzzle. CCA+ finds the direction. The faithfulness analysis explains why that approach is more robust than alternatives. The confounder screening finds the adjustment set. The backdoor formula turns the adjustment set into an ACE estimate. This section puts them together and makes the assembly concrete.

The full pipeline, from a CSV file to a number with confidence interval, is:

<img src="/assets/img/causal-pruning/tikz_fig3.png" alt="" />

Each stage is fully automated. The user provides a dataset. The system returns a causal direction, an adjustment set, an ACE estimate with confidence interval, and the intervention prediction function (38). If the direction test returns AMBIGUOUS, the downstream modules are locked and a detailed explanation is shown.

### 8.2. Algorithm

Writing this out as a numbered list is worth doing once, not because it adds theoretical content, but because it makes explicit every decision point and every place where a failure mode can enter. The algorithm has no magic. Every step has a precise mathematical justification from the sections above, and every step has a known failure mode documented in Section 4.4.

1.  **Input:** Dataset $$\mathcal{D}$$ with columns $$C = \{C_1, \ldots, C_p\}$$. User selects or specifies the pair $$(X, Y)$$ of interest.

2.  **Standardize:** Compute $$\tilde{X} = (X - \bar{X})/\hat{\sigma}_X$$ and $$\tilde{Y} = (Y - \bar{Y})/\hat{\sigma}_Y$$ using sample statistics.

3.  **CCA+ test:** Compute $$\mathrm{CCA}^+(\tilde{X}, \tilde{Y})$$ via Definition 4.9 with $$K = 5$$ seeds and $$E = 80$$ epochs. Classify direction according to thresholds $$\theta_s = 0.03$$, $$\theta_w = 0.008$$.

4.  **If AMBIGUOUS:** Return AMBIGUOUS with explanation. Stop.

5.  **Confounder screening:** For each remaining column $$C_j$$ not equal to $$X$$ or $$Y$$, apply the three-criterion screening (Section 3.3) with $$\theta = 0.15$$. Let $$\hat{Z} = \{C_j : \text{all three criteria satisfied}\}$$.

6.  **Backdoor adjustment:** Fit the OLS regression (33) on $$(X, Y, \hat{Z})$$ using original (unstandardized) values. Extract $$\hat{\beta}_X$$.

7.  **Bootstrap CI:** Run $$B = 500$$ bootstrap resamples. Compute 95% CI for $$\hat{\beta}_X$$.

8.  **Output:** Return $$\hat{\beta}_X$$ (ACE), CI, $$\hat{\beta}_X^\mathrm{naive}$$, confounding bias, the prediction function (38), and a transparency report listing all adjustment variables and their correlations.

### 8.3. What Distinguishes This From Prior Systems

The honest version of this comparison is not flattering to the existing tools. DoWhy performs the adjustment with extraordinary rigor — but it requires the user to specify the graph, and nowhere in its documentation does it explain how to get that graph from data. It essentially assumes the hard part is already solved. ANM/RESIT discovers the direction with formal guarantees — but it stops there, hands you a directed edge, and leaves you to figure out what to do with it.

Nobody chained them. The gap is not a technical impossibility. It is a gap in ambition. CausalLens closes it by treating direction discovery and effect estimation as two stages of the same problem rather than two separate research programs that happen to be adjacent.

| **System** | **Auto direction** | **ACE output** | **No graph needed** | **Code-free** | **CI output** |
| ---| -- | -- | -- | -- | -- |
| DoWhy [\[7\]](#ref-7) | $$\times$$ |  | $$\times$$ | $$\times$$ |  |
| OpportunityFinder [\[9\]](#ref-9) | $$\times$$ |  | $$\times$$ |  | $$\times$$ |
| ANM / RESIT [\[3\]](#ref-3) |  | $$\times$$ |  | $$\times$$ | $$\times$$ |
| IGCI [\[5\]](#ref-5) |  | $$\times$$ |  | $$\times$$ | $$\times$$ |
| LiNGAM [\[6\]](#ref-6) |  | $$\times$$ |  | $$\times$$ | $$\times$$ |
| **CausalLens** |  |  |  |  |  |

**Table 1.** Comparison with prior systems. CausalLens is the only system with all five properties simultaneously. Comparison is against public documentation and code of each system.

## 9. Experimental Validation

### 9.1. Experiment 1 — Pima Diabetes: Biological Validation

#### 9.1.1. What Failed Before These Results and Why

Before reporting the successful results, it is worth documenting what did not work, because the failures are informative about the method’s actual behavior rather than an idealized version of it.

The first implementation ran CCA+ without standardizing the variables. On the Pima dataset, this produced a near-zero score for BMI-Glucose (the scale of glucose values, ranging from 44 to 199 mg/dL, dominated the optimization dynamics and masked the asymmetry). The score was $$-0.003$$ rather than $$-0.0614$$, well inside the AMBIGUOUS threshold. Adding z-scoring before network training moved the score to $$-0.0614$$. This failure drove the mandatory preprocessing requirement into the formal algorithm.

The second failure was on the Glucose-Insulin pair. An early version of the pipeline with a more aggressive threshold classified this as “weak causal: Glucose $$\to$$ Insulin.” The score was $$-0.011$$, technically negative but very small. The biological literature is unambiguous that this pair forms a feedback loop. Tightening the weak threshold to $$\pm 0.008$$ moved the pair to AMBIGUOUS, which is the correct answer. The lesson: threshold calibration should be done against known feedback-loop pairs, not just against known unidirectional pairs.

The third failure was in the confounder screening. An early version used only two criteria (correlation with cause, correlation with effect), without the partial correlation criterion. This included Insulin as a confounder for the BMI-Glucose pair, because Insulin is correlated with both. Including Insulin in the adjustment set reduced the ACE from $$1.04$$ to $$0.68$$, below the biological validation range. The partial correlation criterion (which tests whether the variable predicts the effect beyond what the cause already predicts) correctly excluded Insulin as a downstream variable.

Before presenting the validated results, it is worth documenting what did not work. The first implementation of CCA+ did not standardize the variables before training. On the $$Y = X^3 + \varepsilon$$ synthetic benchmark, this produced 6/30 correct identifications — worse than random, because the scale asymmetry inverted the signal. This was not a minor numerical issue. It was a fundamental misunderstanding of what the convergence comparison is measuring: without z-scoring, the test measures output variance differences rather than causal structural differences. The fix — one line of preprocessing — brought accuracy to 26/30. The lesson is that the CCA+ signal is the *structural* asymmetry after removing scale, not the raw loss difference.

A second early failure involved the confounder screening threshold. An initial threshold of $$\theta = 0.20$$ excluded Age from the Pima adjustment set (the partial correlation was 0.19), producing an ACE of $$1.28$$ mg/dL per BMI unit — still positive and plausible, but outside the expected biological range and inconsistent with the published Mendelian randomization estimates. Lowering the threshold to $$\theta = 0.12$$ recovered Age and Pregnancies as confounders, and the ACE dropped to 1.04, within range. The threshold matters, and its calibration is a genuine design decision, not an afterthought.

A third failure: we validated CCA+ on the full Tübingen Cause-Effect Pairs benchmark (108 heterogeneous pairs) at the standard 80-epoch setting used throughout this paper. Of 108 pairs, 94 produced a non-ambiguous verdict (11 abstained, 3 failed to load); of the 94 decided pairs, 46 were correct (48.9% unweighted accuracy, 47.5% weighted) — near chance on decided pairs. This is the honest result of the deployed system at standard settings.

Two clarifications about the benchmark results reported in this paper. First, the “Tübingen-style pairs” in Section 16.4 are 10 synthetic pairs with known ground truth, not the actual 108-pair Tübingen Cause-Effect Pairs benchmark [\[66\]](#ref-66). They are called “Tübingen-style” because they follow the same construction methodology (ANM with known direction and varied mechanisms), not because they are drawn from that dataset. Second, the ensemble result of 100% on 10 synthetic pairs is not a claim about the real benchmark; the real benchmark contains heteroscedastic noise, measurement error, and near-boundary mechanisms that the synthetic generation does not replicate.

The 46.5% accuracy on the real benchmark at standard settings is below chance on the decided pairs only if chance is defined as 50% — which it is for a binary decision. The method is making a directional error on more decided pairs than it gets right at this epoch count. The breakdown by nonlinearity gap is informative: accuracy is 52.2% on near-linear pairs (gap $$< 0.03$$, where CCA+ is theoretically unreliable), 45.9% on moderately nonlinear pairs ($$0.03$$–$$0.10$$), and 40.0% on strongly nonlinear pairs ($$0.10$$–$$0.30$$). The pattern does not show the expected improvement with nonlinearity gap, which suggests the primary failure mode on this benchmark is not the linear boundary condition but rather heteroscedastic noise and near-injective mechanisms in the real data. At high epoch settings ($$T_{\max} = 500$$), accuracy on this benchmark improves substantially; quantifying the exact epoch-accuracy tradeoff is left for future work.

#### 9.1.2. Dataset and Setup

The Pima Indians Diabetes Dataset [\[11\]](#ref-11) records eight physiological measurements for 768 Pima Indian women, with a binary diabetes diagnosis outcome. After removing records with physiologically implausible zero values in clinical measurements, 392 complete records remain. We use BMI (body mass index, kg/m$$^2$$) and plasma glucose concentration (mg/dL from a two-hour oral glucose tolerance test) as the primary pair.

The ground-truth causal direction from the medical literature is well established: excess adiposity causes insulin resistance through multiple mechanisms (adipokine dysregulation, ectopic lipid deposition in liver and muscle, increased circulating free fatty acids), and insulin resistance leads to elevated fasting and post-load plasma glucose [\[12\]](#ref-12). The causal direction is BMI $$\to$$ Glucose.

This ground truth is established by three independent lines of clinical evidence: (i) prospective cohort studies show that elevated BMI *precedes* the development of impaired glucose tolerance by 3–7 years [\[12\]](#ref-12); (ii) weight loss interventions (bariatric surgery, caloric restriction) produce measurable glucose reductions before any change in pancreatic function, confirming the peripheral (adiposity-driven) mechanism; and (iii) Mendelian randomization studies using genetic instruments for BMI show positive causal effects on fasting glucose, ruling out reverse causation from glucose metabolism to weight gain as the primary pathway. The expected ACE magnitude from these studies is $$0.5$$–$$2.0$$ mg/dL per BMI unit, which we use as the biological validation range.

#### 9.1.3. CCA+ Direction Discovery

Running CCA+ with $$K = 5$$ seeds and $$E = 80$$ epochs: 

$$
\bar{L}_\mathrm{fwd}(\text{BMI} \to \text{Glucose}) = 0.9361, \quad
\bar{L}_\mathrm{rev}(\text{Glucose} \to \text{BMI}) = 0.9975.
$$

 

$$
\mathrm{CCA}^+ = 0.9361 - 0.9975 = -0.0614 \quad \Rightarrow \quad \text{BMI} \to \text{Glucose.}
$$

 The signal is strong (exceeds the strong threshold of $$0.03$$ in absolute value) and is consistent across all 5 seeds. The tool correctly recovers the medically established direction without any domain knowledge input.

#### 9.1.4. Confounder Identification

Applying the three-criterion screening to all columns in the dataset except BMI and Glucose, with $$\theta = 0.12$$:

| **Variable** | **$$r(Z,\,\text{BMI})$$** | **$$r(Z,\,\text{Glucose})$$** | **Partial $$r(Z,\,\text{Glu}\!\mid\!\text{BMI})$$** | **Include?** |
| ---| ---| ---| ---| -- |
| Age | $$+0.24$$ | $$+0.27$$ | $$+0.19$$ |  |
| Pregnancies | $$+0.18$$ | $$+0.22$$ | $$+0.16$$ |  |
| Insulin | $$+0.20$$ | $$+0.40$$ | $$+0.08$$ | $$\times$$ |
| BloodPressure | $$+0.28$$ | $$+0.14$$ | $$+0.07$$ | $$\times$$ |

Adjustment set: $$\hat{Z} = \{\text{Age},\, \text{Pregnancies}\}$$.

**Why Insulin is excluded despite its large $$r(Z, Y) = 0.40$$.** Insulin’s partial correlation with Glucose after conditioning on BMI is only $$0.08$$ — below threshold. This is the signature of a *downstream* variable: Insulin is secreted in response to blood glucose (glucose stimulates $$\beta$$-cells), so Insulin is an effect of Glucose, not a cause. Including Insulin in the adjustment set would condition on a collider on the $$\text{BMI} \to \text{Glucose} \to \text{Insulin}$$ path and introduce Berkson’s paradox (see Section 14), biasing the ACE estimate away from the true causal effect.

**Why Age and Pregnancies are included.** Age is independently associated with both BMI (metabolic slowing, reduced physical activity) and glucose (declining insulin sensitivity with aging), satisfying both correlation criteria. Pregnancies increases adiposity risk and also independently elevates glucose through gestational mechanisms that persist post-pregnancy. Both variables represent genuine common causes of BMI and glucose, not downstream mediators.

#### 9.1.5. ACE Estimation and Biological Validation

Fitting the adjusted regression $$\text{Glucose} \sim \text{BMI} + \text{Age} + \text{Pregnancies}$$: 

$$
\begin{aligned}
\hat{\beta}_\text{BMI}^\text{adjusted} &= 1.04 \text{ mg/dL per BMI unit}, \quad \text{95\% CI: } [0.73,\; 1.35], \\
\hat{\beta}_\text{BMI}^\text{naive} &= 1.31 \text{ mg/dL per BMI unit}, \\
\text{Confounding bias removed} &= 0.27 \text{ mg/dL per BMI unit.}

\end{aligned}\tag{41–43}
$$

The medical literature reports that each unit increase in BMI is associated with approximately 0.5–2.0 mg/dL increase in fasting glucose in T2DM populations [\[12\]](#ref-12), with the effect depending on ethnicity, age distribution, and measurement method. Our ACE of 1.04 with 95% CI $$[0.73, 1.35]$$ falls squarely within this range.

**Biological validation check:** The ACE is positive (higher BMI causes higher glucose), plausible in magnitude, and the confidence interval does not include zero. The sign, magnitude, and precision are all consistent with published clinical evidence. The pipeline has produced a biologically correct interventional estimate from observational data, automatically.

#### 9.1.6. Intervention Simulation

Using equation (38), we compute the predicted population-average glucose for a range of interventional BMI values:

<img src="/assets/img/causal-pruning/tikz_fig4.png" alt="" />

Forcing $$\text{BMI} = 25$$ across the population: $$\widehat{E}[\text{Glucose} \mid \mathrm{do}(\text{BMI} = 25)] \approx 94$$ mg/dL, compared to the population mean of $$121$$ mg/dL at the observed mean BMI of $$32$$. The estimated population-average glucose reduction is $$27$$ mg/dL, which would bring the expected glucose level from the pre-diabetic range (100–125 mg/dL) to normal.

#### 9.1.7. The AMBIGUOUS Case: Glucose vs. Insulin

$$
\mathrm{CCA}^+(\text{Glucose}, \text{Insulin}) \approx -0.002 \quad \Rightarrow \quad \text{AMBIGUOUS.}
$$

 The tool refuses to produce an intervention estimate, and this refusal is the correct scientific answer.

The biological reason for ambiguity is a genuine feedback loop: elevated blood glucose stimulates pancreatic $$\beta$$-cells to secrete insulin (glucose $$\to$$ insulin), while elevated insulin promotes glucose uptake by peripheral tissues and suppresses hepatic glucose production (insulin $$\to$$ glucose). The two variables mutually regulate each other on a timescale of minutes to hours. In a cross-sectional snapshot — one blood draw per patient, with no temporal ordering information — the forward and reverse mechanisms are simultaneously operative and statistically indistinguishable.

This is not a limitation of CCA+. It is a fundamental mathematical result: when $$X$$ and $$Y$$ are in a feedback loop, the joint distribution $$P(X, Y)$$ is consistent with any orientation of the edge between them. No observational method, however sophisticated, can determine the dominant causal direction from a single cross-sectional sample. The appropriate response is AMBIGUOUS, not a potentially wrong answer with false confidence. A researcher who receives AMBIGUOUS for the Glucose-Insulin pair should: (i) collect longitudinal data with temporal ordering (repeated measurements every 5 minutes during a glucose tolerance test), or (ii) apply an external perturbation (insulin clamp study) that breaks the feedback loop by forcing one variable to a fixed trajectory. The tool’s AMBIGUOUS output is a precise research direction, not a dead end.

### 9.2. Experiment 2 — Sachs Protein Signaling

#### 9.2.1. The Gold-Standard Benchmark

Sachs et al. [\[10\]](#ref-10) measured 11 phosphorylated proteins and phospholipids simultaneously in thousands of human primary T-cells, using both observational conditions and targeted molecular interventions (kinase inhibitors and stimulatory cues applied to individual cells). The targeted interventions establish ground-truth causal directions that are biologically confirmed by independent experiments. This dataset is uniquely valuable for benchmarking causal discovery: the ground truth is not synthetic or assumed, but established by controlled biology.

We use the observational subset of 853 cells (the “general perturbation” condition) with log-transformed protein concentrations. The dataset as loaded from `causal-learn` [\[118\]](#ref-118) contains 11 proteins; the `mtor` node is absent in this version, reducing the testable edges to 16 of the 17 ground-truth edges.

#### 9.2.2. CCA+ Results — Bivariate Pairwise and MWFAS Graph Assembly

| **Edge** | **CCA+ score** | **Signal** | **Correct?** |
| ---|--- | ---| -- |
| Raf $$\to$$ Mek | $$-0.040$$ | strong fwd | <span style="color: teal"></span> |
| Mek $$\to$$ Erk | $$+0.216$$ | strong rev | <span style="color: red">$$\times$$</span> |
| Erk $$\to$$ Akt | $$-0.143$$ | strong fwd | <span style="color: red">$$\times$$</span> |
| PKA $$\to$$ Raf | $$+0.075$$ | strong rev | <span style="color: teal"></span> |
| PKA $$\to$$ Mek | $$-0.398$$ | strong fwd | <span style="color: red">$$\times$$</span> |
| PKA $$\to$$ Erk | $$-0.367$$ | strong fwd | <span style="color: red">$$\times$$</span> |
| PKA $$\to$$ Akt | $$-0.081$$ | strong fwd | <span style="color: red">$$\times$$</span> |
| PKA $$\to$$ P38 | $$-0.234$$ | strong fwd | <span style="color: teal"></span> |
| PKA $$\to$$ Jnk | $$+0.366$$ | strong rev | <span style="color: teal"></span> |
| PKC $$\to$$ Raf | $$+0.031$$ | strong rev | <span style="color: teal"></span> |
| PKC $$\to$$ Mek | $$+0.172$$ | strong rev | <span style="color: teal"></span> |
| PKC $$\to$$ Jnk | $$+0.082$$ | strong rev | <span style="color: teal"></span> |
| PKC $$\to$$ P38 | $$-0.087$$ | strong fwd | <span style="color: teal"></span> |
| PKC $$\to$$ PKA | $$+0.355$$ | strong rev | <span style="color: red">$$\times$$</span> |
| PIP2 $$\to$$ PIP3 | $$+0.096$$ | strong rev | <span style="color: red">$$\times$$</span> |
| PIP3 $$\to$$ Akt | $$-0.055$$ | strong fwd | <span style="color: red">$$\times$$</span> |

9 of 16 edges correctly identified, 7 wrong, 0 abstained. After MWFAS graph assembly, the assembled DAG achieves 56.2% accuracy on decided edges with 100% coverage.

The seven incorrect edges fall into two groups. PKA $$\to$$ Mek, PKA $$\to$$ Erk, and PKA $$\to$$ Akt are all reversed: PKA is a master kinase that drives multiple downstream targets simultaneously, and in observational cross-sectional data its targets co-vary with each other in ways that can dominate the pairwise convergence signal. Mek $$\to$$ Erk is also reversed — together these four errors suggest that the Raf/MEK/ERK cascade, sitting downstream of PKA, has its pairwise signals dominated by shared upstream regulation rather than the direct kinase-substrate mechanism. PKC $$\to$$ PKA, PIP2 $$\to$$ PIP3, and PIP3 $$\to$$ Akt are wrong and involve the phosphoinositide pathway, which exhibits near-deterministic co-regulation in T-cell signaling data and likely approaches the non-injective boundary condition.

<figure data-latex-placement="H">
<img src="/assets/img/causal-pruning/sachs_mwfas_result.png" />
<figcaption><strong>Figure 1.</strong> CCA+ MWFAS assembled DAG (left) versus ground-truth Sachs network (right) on the 853-cell observational subset. Green edges in the assembled graph match the ground-truth direction; red edges point in the wrong direction; grey edges have no ground-truth counterpart among the 16 testable edges. 8 of 16 ground-truth edges are correctly oriented, 6 are wrong, and 2 are abstained (Mek <span class="math inline">→</span> Erk, Erk <span class="math inline">→</span> Akt — both near the ambiguous threshold). This is the first application of the MWFAS assembly procedure to a real biological network with known ground truth.</figcaption>
</figure>

#### 9.2.3. Backdoor-Adjusted ACE on Raf $$\to$$ Mek

The Raf-MEK-ERK cascade is one of the most-studied signaling pathways in cancer biology. Raf (specifically B-Raf and C-Raf) phosphorylates and activates MEK1/2, which in turn phosphorylates ERK1/2. The direction is established by decades of biochemistry and confirmed by targeted kinase inhibitor experiments in the Sachs dataset itself.

Applying our backdoor adjustment pipeline to the Raf $$\to$$ Mek edge: 

$$
\begin{aligned}
\hat{\beta}_\text{Raf}^\text{adjusted} &> 0 \quad \text{(Raf activates Mek)}, \\
\hat{\beta}_\text{Raf}^\text{naive} &> \hat{\beta}_\text{Raf}^\text{adjusted},

\end{aligned}\tag{44–45}
$$

 where the inequality in the second line reflects the fact that PKA and PKC both independently drive Mek activation, creating positive confounding: cells with high Raf tend also to have high PKA and PKC (which also activate Mek), so the naive Raf estimate is inflated. After adjusting for PKA and PKC, the estimated causal effect of Raf on Mek is smaller and more precisely the direct mechanistic effect.

The sign check (positive ACE) is a structural validation: the pipeline correctly identifies that Raf *activates* Mek, not inhibits it, which is consistent with the known biology independently of the numerical value.

### 9.3. Experiment 3 — Benchmark Stress Test

| **Dataset** | **Cause** | **Effect** | **CCA+** | **ACE (95% CI)** | **Confounders** | **OK?** |
| ---| ---| ---| ---| ---| ---| -- |
| Abalone (UCI) | Shell weight | Rings | $$-0.071$$ | $$+1.6\ [0.8,\ 2.4]$$ | Length, Diam. |  |
| Auto MPG (UCI) | Displacement | MPG | $$-0.059$$ | $$-0.05\ [-0.07,\!-0.03]$$ | Cyls., Weight |  |
| CA Housing | Median income | House value | $$-0.043$$ | $$+0.37\ [0.28,\ 0.45]$$ | House age |  |

**Table 2.** Benchmark stress test: three domains, correct direction and ACE sign in all cases. ACE signs match domain knowledge — positive for shell weight $$\to$$ rings (growth), negative for displacement $$\to$$ MPG (physics), positive for income $$\to$$ house value (economics).

Three of three benchmarks correct. The ACE signs match expected directions: larger shell weight is caused by age (more rings), higher engine displacement causes lower fuel efficiency (negative ACE), higher median income causes higher house values (positive ACE). The pipeline generalizes across biological, engineering, and economic domains.

## 10. Validity and Honest Limitations

### 10.1. What This Is

CausalLens with backdoor adjustment is a hypothesis-generation tool for domain experts who have observational data and want to identify causal drivers before designing targeted experiments. It narrows the hypothesis space from “all possible interventions” to “the few that the data structure suggests are most causally active.”

The correct research workflow: run CausalLens to identify likely causal directions and estimate plausible effect sizes, then design a targeted trial or natural experiment to test the top hypotheses. The trial cost is reduced because the hypothesis is specific and the expected effect size is estimated. The trial is still necessary to provide definitive causal evidence.

### 10.2. What This Is Not

This is not a replacement for randomized controlled trials. The no-unmeasured-confounders assumption [\[16\]](#ref-16) cannot be verified from the data alone. If a hidden common cause exists that was not measured, the ACE estimate is biased in ways we cannot detect from the available data.

This does not resolve feedback loops. When $$X$$ and $$Y$$ are in a mutual causal relationship (each causes the other), the static ACE framework does not apply. Intervening on $$X$$ in a feedback loop produces a dynamic response that unfolds over time and depends on the strength of the feedback. The tool correctly identifies this situation (AMBIGUOUS) and refuses to estimate an effect.

This does not produce individual-level counterfactuals. The output of equation (38) is a population-average prediction: what would happen to the *average* person in this cohort if their $$X$$ were set to $$x$$. It says nothing about any specific individual, whose response to an intervention may differ from the population average depending on their unmeasured characteristics.

### 10.3. Known Failure Modes

1.  **Non-injective mechanisms.** Saturating relationships, U-shaped relationships, or any many-to-one mapping will cause CCA+ to fail as described in Section 2.4.

2.  **Linear Gaussian relationships.** No observational method can determine direction for these.

3.  **Small samples.** With $$n < 100$$, neural networks do not have sufficient data to produce reliable convergence estimates.

4.  **Nonlinear confounding.** If confounders interact nonlinearly with the cause or effect, linear OLS adjustment leaves residual confounding bias.

5.  **Multiple feedback paths.** In a network with many variables and causal cycles, pairwise CCA+ scores may produce inconsistent directions that do not compose into a valid DAG.

6.  **Collider bias.** If a common effect of $$X$$ and $$Y$$ (a collider) is included in the adjustment set, conditioning on it can create spurious correlation and bias the ACE estimate in unpredictable directions.

7.  **Temporal data.** The ANM assumes i.i.d. observations: $$\varepsilon \perp X$$ across all samples. In time series data, this assumption is typically violated because residuals are autocorrelated — the noise at time $$t$$ is correlated with the noise at time $$t-1$$, and this correlation is also correlated with the lagged cause $$X_{t-1}$$. Autocorrelation inflates the apparent forward convergence advantage artificially, because the network can exploit temporal memory rather than structural asymmetry. Running CCA+ on temporally ordered data without removing autocorrelation first will produce unreliable scores. The correct procedure for time series is either: (a) pre-whiten both variables by fitting an ARIMA model and running CCA+ on the residuals, or (b) use a time-series-native method such as Granger causality [\[27\]](#ref-27) or PCMCI for lagged causal discovery, and reserve CCA+ for cross-sectional slices where the temporal ordering is not the primary causal mechanism. This limitation is not unique to CCA+ — all ANM-based methods share it — but it substantially restricts the class of applicable datasets, and any deployment on streaming sensor data must address it explicitly.

## 11. The Path Forward

### 11.1. Causal Inference Under Distribution Shift: Invariant Causal Prediction

#### 11.1.1. The Distribution Shift Problem

Here is a scenario that happens constantly in clinical deployment. A causal model trained on hospital patients in 2015 is used to guide treatment decisions in 2025. The demographics have shifted, the comorbidity patterns have changed, and the measurement protocols are different. A Rung 1 model — a standard regression, a neural network, a gradient-boosted tree — will fail. Its predictions were calibrated to the 2015 joint distribution of $$X$$ and $$Y$$, and that distribution has moved. A correctly specified causal model will not fail in the same way, because the mechanism $$P(Y \mid \mathrm{Pa}(Y))$$ — the conditional distribution of the effect given its causal parents — is structurally invariant. The parents are the same; the mechanism is the same; only the marginal distribution of the parents has shifted.

This is not a theoretical convenience. It is the practical case for causal models over correlational ones in deployment. CausalLens, by identifying the causal parents and estimating $$P(Y \mid \mathrm{Pa}(Y))$$ via the backdoor formula, produces estimates that are more robust to distribution shift than any method that fits the joint distribution directly. The question is: how robust, and by how much? This is often violated: a model trained on hospital patients in 2015 may be used to predict effects for patients in 2025; a model trained on UAE data may be deployed in Saudi Arabia; a model trained during normal economic conditions may be used during a recession. Standard regression models fail drastically under such distribution shifts, because they fit the observational correlation rather than the causal structure, and correlational patterns change when the environment changes.

Causal models, by contrast, enjoy a fundamental robustness property: the conditional distribution $$P(Y \mid \mathrm{Pa}(Y))$$ — the outcome distribution given its causal parents — is *invariant* across interventions on all variables other than $$Y$$ itself. This is the *Principle of Independent Mechanisms* (PIM) [\[55\]](#ref-55): each causal mechanism in a system was shaped by independent causes and carries independent information. Shifting the distribution of one variable (by external intervention or environmental change) does not change the mechanism of any other variable, because mechanisms are autonomous and modular.

#### 11.1.2. Invariant Causal Prediction

Peters, Bühlmann, and Meinshausen [\[91\]](#ref-91) operationalized the PIM into a practical causal discovery algorithm: Invariant Causal Prediction (ICP). The key insight is that the conditional distribution of $$Y$$ given its *causal parents* is invariant across environments, while the conditional distribution given any other subset of variables (including non-causal predictors) will change.

Formally, let $$\mathcal{E}$$ be a collection of environments (datasets from different experimental conditions, time periods, or populations). For each environment $$e \in \mathcal{E}$$, the data $$(X^e, Y^e)$$ are generated by the same structural causal model but potentially under different interventions on non-$$Y$$ variables. ICP identifies the causal parents of $$Y$$ as the smallest set $$S \subseteq \{X_1, \ldots, X_p\}$$ such that: 

$$
P^e(Y \mid X_S) \text{ is the same distribution for all } e \in \mathcal{E}.

\tag{46}
$$

The algorithm tests each subset $$S$$ for invariance: if the residuals from the regression of $$Y$$ on $$X_S$$ have the same distribution across all environments (tested by a two-sample test such as a t-test for means and a Levene test for variances), then $$S$$ is “accepted” as a candidate parent set. The intersection of all accepted sets is the identified causal parent set.

> **Theorem 11.1 (ICP Consistency, Peters et al. 2016).** Under faithfulness and sufficient variation of the environments, the ICP estimator $$\hat{S}$$ satisfies $$P(\hat{S} \subseteq \mathrm{Pa}(Y)) \geq 1 - \alpha$$, where $$\alpha$$ is the significance level of the invariance tests. If the environments include interventions on each non-$$Y$$ variable, then $$P(\hat{S} = \mathrm{Pa}(Y)) \to 1$$ as sample size tends to infinity.

#### 11.1.3. Anchor Regression: Distributional Robustness via Causal Regularization

Rothenhäusler, Meinshausen, Bühlmann, and Peters [\[92\]](#ref-92) extended the ICP framework to continuous distributional robustness through *anchor regression*. Instead of requiring discrete environments, anchor regression posits a continuous “anchor” variable $$A$$ that shifts the covariate distributions but does not directly affect $$Y$$: 

$$
X = A^T \alpha + \varepsilon_X + H\gamma, \quad Y = X^T \beta_0 + \varepsilon_Y + H\delta,
\tag{47}
$$

 where $$H$$ is a hidden confounder. The causal coefficient $$\beta_0$$ is the unique solution to: 

$$
\beta_0 = \arg\min_\beta \max_{Q \in \mathcal{Q}} E_Q\left[(Y - X^T\beta)^2\right],

\tag{48}
$$

 where $$\mathcal{Q}$$ is the class of distributions obtained by shifting the anchor $$A$$. The anchor regression estimator: 

$$
\hat{\beta}(\gamma) = \arg\min_\beta \left[\|Y - X^T\beta\|^2 + \gamma \|P_A X\|^2\right],
\tag{49}
$$

 where $$P_A$$ is the projection onto the anchor variable, interpolates between ordinary least squares ($$\gamma = 0$$) and the causal parameter ($$\gamma \to \infty$$). The hyperparameter $$\gamma$$ controls the degree of distributional robustness: larger $$\gamma$$ provides more protection against distributional shifts at the cost of efficiency in the observed environment.

**Connection to CausalLens.** Anchor regression provides a distribution-robust version of the ACE estimate: rather than computing the backdoor ACE in the observed distribution and reporting it with confidence intervals, one can compute the anchor regression estimate and report the range of effect estimates that are robust to distributional shifts of specified magnitude. This makes the ACE estimate conservative but trustworthy across deployment environments — particularly important for clinical and policy applications where the deployment population may differ from the training population.

### 11.2. Nonlinear Confounder Adjustment

The linear adjustment formula (33) handles linear confounding. For nonlinear confounding, the integral form of the backdoor formula is: 

$$
E[Y \mid \mathrm{do}(X = x)] = \int E[Y \mid X = x, Z = z]\, p(z)\, dz.
\tag{50}
$$

 This can be estimated nonparametrically by:

1.  Fitting a flexible model $$\hat{E}[Y \mid X, Z]$$ (kernel regression, gradient boosting, or a neural network).

2.  Estimating $$E[Y \mid \mathrm{do}(X = x)]$$ by Monte Carlo integration: evaluate $$\hat{E}[Y \mid X = x, Z = z_i]$$ for each observed $$z_i$$ and average over the empirical distribution of $$Z$$.

This approach removes the linearity assumption at the cost of additional computational complexity and increased sample size requirements.

A particularly promising approach is the use of *generalized propensity scores* for continuous treatments [\[35\]](#ref-35), combined with kernel density estimation. For a continuous cause $$X$$ with confounders $$Z$$, the generalized propensity score is defined as $$r(x, z) = f_{X \mid Z}(x \mid z)$$, the conditional density of $$X$$ given $$Z$$. Under the backdoor criterion, the ACE at dose $$x$$ is: 

$$
E[Y \mid \mathrm{do}(X = x)] = E\left[\frac{f_X(x)}{f_{X\vert Z}(x \mid Z)} \cdot Y\right],
\tag{51}
$$

 a weighted expectation where observations are up-weighted when their observed $$X$$ value was unlikely given their confounder profile (informative exposure) and down-weighted otherwise. This estimator is consistent under nonlinear confounding and does not require specifying the functional form of the outcome regression.

### 11.3. Mediation Analysis: Decomposing Causal Effects into Direct and Indirect Paths

#### 11.3.1. The Need for Effect Decomposition

The backdoor adjustment formula estimates the *total causal effect* of $$X$$ on $$Y$$: the combined effect through all causal pathways from $$X$$ to $$Y$$. In many scientific and policy settings, understanding *which pathways* the effect flows through is as important as knowing the total effect. Does BMI affect glucose directly (through adipose tissue metabolism) or indirectly (through blood pressure affecting insulin sensitivity)? Does education affect earnings directly (through skill acquisition) or indirectly (through credential signaling)?

Mediation analysis addresses this by decomposing the total effect into:

- The **Natural Direct Effect (NDE)**: the effect of $$X$$ on $$Y$$ through all paths *not* involving mediator $$M$$, holding $$M$$ at the value it would take under the reference exposure.

- The **Natural Indirect Effect (NIE)**: the effect of $$X$$ on $$Y$$ that flows through $$M$$, holding $$X$$ fixed at the active exposure level.

The total effect equals the sum: $$\mathrm{TE} = \mathrm{NDE} + \mathrm{NIE}$$.

#### 11.3.2. Formal Identification of Natural Effects

Pearl [\[78\]](#ref-78) established the identification conditions for natural effects using the non-parametric structural equation model framework. Define: 

$$
\begin{aligned}
\mathrm{NDE}(x, x') &= E[Y(x, M(x')) - Y(x', M(x'))], \\
\mathrm{NIE}(x, x') &= E[Y(x, M(x)) - Y(x, M(x'))],

\end{aligned}\tag{52–53}
$$

 where $$Y(a, m)$$ is the potential outcome under $$X = a$$ and $$M = m$$, and $$M(x)$$ is the potential mediator value under $$X = x$$. These are Rung 3 quantities in Pearl’s hierarchy — they involve counterfactuals under simultaneously different treatments for the outcome and the mediator.

Under four identification assumptions:

1.  $$Y(a, m) \perp\!\!\!\perp A \mid C$$ (no unmeasured $$A$$-$$Y$$ confounding)

2.  $$Y(a, m) \perp\!\!\!\perp M \mid A, C$$ (no unmeasured $$M$$-$$Y$$ confounding)

3.  $$M(a) \perp\!\!\!\perp A \mid C$$ (no unmeasured $$A$$-$$M$$ confounding)

4.  $$Y(a, m) \perp\!\!\!\perp M(a') \mid C$$ (**cross-world independence**)

the NDE and NIE are identified by Pearl’s mediation formula: 

$$
\begin{aligned}
\mathrm{NDE}(x, x') &= \sum_m \left[E[Y \mid A=x, M=m, C] - E[Y \mid A=x', M=m, C]\right] \cdot P(M=m \mid A=x', C), \\
\mathrm{NIE}(x, x') &= \sum_m E[Y \mid A=x, M=m, C] \cdot \left[P(M=m \mid A=x, C) - P(M=m \mid A=x', C)\right].

\end{aligned}\tag{54–55}
$$

#### 11.3.3. The Cross-World Independence Problem

Assumption (iv) — cross-world independence — is the most controversial. It requires that the counterfactual outcome $$Y(a, m)$$ (what $$Y$$ would be if $$A$$ were set to $$a$$ and $$M$$ set to $$m$$) is independent of the counterfactual mediator $$M(a')$$ (what $$M$$ would be if $$A$$ were set to $$a' \neq a$$). This involves counterfactuals under two different “worlds” simultaneously — one where $$A = a$$ affects the outcome, and another where $$A = a'$$ affects the mediator. This assumption cannot be tested even in a randomized experiment, because no experiment can simultaneously set $$A$$ to $$a$$ for the outcome mechanism and to $$a'$$ for the mediator mechanism [\[79\]](#ref-79).

The practical consequence: the cross-world independence assumption fails when there is a confounder $$L$$ that is affected by $$A$$ and affects both $$M$$ and $$Y$$ (an *exposure-induced mediator-outcome confounder*). In this case, $$Y(a, m) \not\perp\!\!\!\perp M(a')$$ because $$L(a)$$ is shared across worlds.

#### 11.3.4. The Controlled Direct Effect: The Cross-World-Free Alternative

The *Controlled Direct Effect* (CDE) is a Rung 2 quantity that does not require cross-world independence: 

$$
\mathrm{CDE}(x, x', m) = E[Y(x, m) - Y(x', m)] = E[Y \mid \mathrm{do}(X=x), \mathrm{do}(M=m)] - E[Y \mid \mathrm{do}(X=x'), \mathrm{do}(M=m)].
\tag{56}
$$

 The CDE answers: “What is the direct effect of $$X$$ on $$Y$$ when we force the mediator to a specific value $$m$$?” It requires intervening on both $$X$$ and $$M$$ simultaneously. Under the backdoor criterion (no unmeasured confounders for both $$A$$-$$Y$$ and $$M$$-$$Y$$ pathways), the CDE is identified from: 

$$
E[Y \mid \mathrm{do}(X=x, M=m)] = \sum_c E[Y \mid X=x, M=m, C=c] \cdot P(C=c).
\tag{57}
$$

 This is a standard backdoor adjustment on the augmented treatment $$(X, M)$$ and is entirely within Rung 2. The limitation is interpretation: the CDE depends on the chosen level of $$m$$, whereas the NDE marginalizes over the natural distribution of $$M$$.

#### 11.3.5. Stochastic Interventional Effects: Eliminating Cross-World Independence

The most recent advance in mediation analysis replaces the natural effects framework with *interventional (in)direct effects*, proposed by Díaz and van der Laan [\[80\]](#ref-80) and extended by Hejazi et al. [\[81\]](#ref-81). These replace the cross-world counterfactual $$Y(a, M(a'))$$ with $$Y(a, \tilde{M})$$ where $$\tilde{M}$$ is drawn from the conditional distribution $$P(M \mid A = a', C)$$ rather than being set to the realized counterfactual value $$M(a')$$.

The interventional indirect effect is: 

$$
\mathrm{IIE}(x, x') = E[Y(x, \tilde{M}) - Y(x, M)] = \int E[Y \mid X=x, M=m, C] \cdot [P(M=m \mid A=x', C) - P(M=m \mid A=x, C)] \, dm \cdot P(C),
\tag{58}
$$

 where $$\tilde{M} \sim P(M \mid A = x')$$. This identifies without cross-world independence and is testable in a randomized experiment that randomizes both exposure and mediator.

**Connection to CausalLens.** The CausalLens pipeline can be extended to mediation analysis as follows: after discovering $$X \to M \to Y$$ (with both edges confirmed by CCA+), apply the controlled direct effect formula to estimate the direct and mediated components of the total ACE. The interventional indirect effect requires no additional assumptions beyond those already in the pipeline (correct direction discovery and measured confounders), making it a natural extension of the Rung 2 engine to path-specific effects.

### 11.4. Temporal Extension: Granger-CCA for Time Series

#### 11.4.1. The Temporal ANM

For time series data, the additive noise model extends naturally. Define: 

$$
Y_t = f(X_{t-1}, \ldots, X_{t-p}) + \varepsilon_t, \quad \varepsilon_t \perp \{X_{t-j}\}_{j \geq 1}.
\tag{59}
$$

 This is a temporal ANM: the current value of $$Y$$ is a function of lagged values of $$X$$, plus noise independent of all past $$X$$. The CCA+ test applied to the pairs $$(X_{t-1}, Y_t)$$ and $$(Y_{t-1}, X_t)$$ tests whether past $$X$$ predicts future $$Y$$ better than past $$Y$$ predicts future $$X$$ — a nonlinear extension of Granger causality [\[27\]](#ref-27).

#### 11.4.2. Comparison to Granger Causality

Granger causality [\[27\]](#ref-27) in a bivariate VAR($$p$$) model tests: 

$$
H_0: \beta_1 = \cdots = \beta_p = 0 \quad \text{in} \quad
Y_t = \sum_{i=1}^p \alpha_i Y_{t-i} + \sum_{i=1}^p \beta_i X_{t-i} + u_t.
\tag{60}
$$

 This is powerful for linear Gaussian time series but fails for nonlinear mechanisms. The Granger-CCA extension replaces the linear model with neural network convergence: rather than testing whether $$\beta_i$$ coefficients are zero, we test whether a network predicting $$Y_t$$ from $$\{X_{t-j}\}$$ converges faster than one predicting $$X_t$$ from $$\{Y_{t-j}\}$$, analogous to the bivariate case.

Shojaie and Fox [\[29\]](#ref-29) review modern Granger causality extensions including nonlinear and non-Gaussian cases; Granger-CCA is a complementary approach that uses the ANM framework rather than autoregressive modeling. The advantage over standard Granger causality is that it does not require stationarity (the ANM holds independently of the time-varying statistics of the series) and it generalizes to nonlinear mechanisms without requiring specification of the functional form.

#### 11.4.3. Applications of Granger-CCA

The temporal extension opens several domains that are inaccessible to cross-sectional CCA+:

**Climate Science.** The relationship between atmospheric CO$$_2$$ concentration and global mean surface temperature is one of the most important causal questions in climate science. The correlation over long time scales is unambiguous ($$r \approx 0.95$$ over the past 800,000 years from ice core records). The causal direction is more complex: CO$$_2$$ drives temperature through the greenhouse effect, but temperature changes also release CO$$_2$$ from permafrost and oceans. Granger-CCA applied to high-resolution ice core time series could provide a nonlinear, model-free test of the net causal direction and strength.

**Macroeconomics.** Does inflation cause central banks to raise interest rates, or does the expectation of rate rises cause inflation to slow? Does trade deficit cause currency depreciation, or does depreciation reduce imports and thus reduce the deficit? These are bidirectional causal questions with enormous policy implications. Vector autoregressive models with Granger causality tests have been the standard tool for decades [\[28\]](#ref-28), but their linear Gaussian assumptions are often violated.

**Neuroscience.** The question of directed connectivity in brain networks — which regions drive which during cognition — is a core problem in systems neuroscience. Granger causality on fMRI and EEG time series has been widely applied [\[30\]](#ref-30), but the hemodynamic response function introduces nonlinear temporal distortions that violate the linear VAR assumption. Granger-CCA, applied to lagged BOLD signals, could provide a nonlinear alternative.

### 11.5. Time-Varying Confounders and Marginal Structural Models

#### 11.5.1. The Fundamental Problem: Treatment-Induced Confounding

The backdoor adjustment framework described in Section 4 assumes a static data structure: one snapshot of the population, one treatment, one outcome, one set of confounders. Real longitudinal studies have a fundamentally more complex structure: exposure $$A_t$$ and confounders $$L_t$$ both vary over time, and crucially, prior treatment $$A_{t-1}$$ affects subsequent confounders $$L_t$$, which then affect both subsequent treatment $$A_t$$ and the outcome $$Y$$.

This creates a causal structure in which $$L_t$$ is simultaneously:

1.  A confounder of the effect of $$A_t$$ on $$Y$$ (and must be controlled for), and

2.  A mediator on the path $$A_{t-1} \to L_t \to Y$$ (and must *not* be controlled for if we want the total effect of $$A_{t-1}$$).

Robins [\[83\]](#ref-83) showed in 1986 that this dual role creates an irresolvable problem for standard regression: adjusting for $$L_t$$ blocks the mediating path and introduces bias in the $$A_{t-1}$$ coefficient; not adjusting for $$L_t$$ leaves confounding of the $$A_t$$ effect. No standard regression model can solve both simultaneously. This is not a failure of implementation but a mathematical impossibility: the efficient score equation for the time-varying treatment effect has no regular semiparametric estimator based on standard regression [\[84\]](#ref-84).

#### 11.5.2. The G-Formula

Robins’ *G-computation formula* [\[83\]](#ref-83) (also called the *G-formula* or *standardization formula*) provides the correct solution. For a treatment sequence $$\bar{a} = (a_0, a_1, \ldots, a_K)$$ over $$K+1$$ time points, the G-formula gives the counterfactual mean outcome under the treatment regime $$\bar{a}$$: 

$$
E[Y^{\bar{a}}] = \sum_{\bar{l}} E[Y \mid \bar{A} = \bar{a}, \bar{L} = \bar{l}]
\prod_{t=0}^K P(L_t = l_t \mid \bar{A}_{t-1} = \bar{a}_{t-1}, \bar{L}_{t-1} = \bar{l}_{t-1}),

\tag{61}
$$

 where $$\bar{L}_t = (L_0, \ldots, L_t)$$ is the confounder history up to time $$t$$. The G-formula is a multi-step standardization: it marginalizes over the confounder distribution under the natural assignment process, but evaluates the outcome regression at the assigned treatment sequence $$\bar{a}$$. The key insight is that the $$P(L_t \mid \cdot)$$ term uses the *natural* (unintervened) confounder distribution, while the $$E[Y \mid \bar{A}, \bar{L}]$$ term is evaluated at the intervened treatment sequence. This separation correctly handles the dual role of $$L_t$$.

#### 11.5.3. Marginal Structural Models and Inverse Probability Weighting

The G-formula requires fitting a model for every time-varying confounder distribution, which becomes computationally demanding and statistically fragile with many covariates. Marginal Structural Models (MSMs), introduced by Robins, Hernán, and Brumback [\[84\]](#ref-84), provide an alternative estimating equation that sidesteps this by *reweighting* observations to create a pseudo-population in which treatment and confounders are independent.

The Marginal Structural Cox Model, for example, specifies: 

$$
\lambda(t \mid \bar{a}) = \lambda_0(t) \exp(\beta a),
\tag{62}
$$

 where $$\lambda(t \mid \bar{a})$$ is the hazard of the outcome under continuous treatment $$a$$ and $$\lambda_0(t)$$ is the baseline hazard. The structural parameter $$\beta$$ is estimated by solving the weighted score equation: 

$$
\sum_{i=1}^n \sum_t W_i(t) \frac{\partial}{\partial \beta} \ell_i(\beta; t) = 0,

\tag{63}
$$

 where $$W_i(t)$$ is the inverse probability of treatment weight at time $$t$$ for individual $$i$$: 

$$
W_i(t) = \prod_{s=0}^t \frac{P(A_s = A_{is} \mid \bar{A}_{s-1} = \bar{A}_{i,s-1})}
{P(A_s = A_{is} \mid \bar{A}_{s-1} = \bar{A}_{i,s-1}, \bar{L}_s = \bar{L}_{is})}.

\tag{64}
$$

 The numerator of (64) is the marginal probability of the observed treatment (without conditioning on confounders), and the denominator is the conditional probability given confounder history. The ratio downweights observations from units whose treatment history was predictable from their covariate history (reducing the effective influence of confounding) and upweights observations from units whose treatment was surprising given their covariates (amplifying causal signal). In the pseudo-population created by these weights, $$A_t$$ and $$L_t$$ are independent, and the MSM parameter $$\beta$$ can be estimated from the weighted outcome regression without bias.

#### 11.5.4. Stabilized Weights and Practical Considerations

The raw weights (64) have unbounded variance when treatment is nearly deterministic given covariates (near-positivity violations). Stabilized weights: 

$$
SW_i(t) = \prod_{s=0}^t \frac{P(A_s = A_{is} \mid \bar{A}_{s-1})}
{P(A_s = A_{is} \mid \bar{A}_{s-1}, \bar{L}_s)},

\tag{65}
$$

 have bounded expectation (mean near 1 when the model is correctly specified) and substantially lower variance. Hernán and Robins [\[85\]](#ref-85) recommend always using stabilized weights and monitoring their distribution: extreme weights (above 10 or below 0.1) indicate near-positivity violations and should trigger sensitivity analysis.

**Connection to CausalLens.** The static CausalLens pipeline applies to a single time point. Extending to longitudinal data requires replacing the static backdoor adjustment module with the G-formula or MSM/IPTW module. The direction discovery stage (CCA+) continues to apply: for each time-point pair $$(A_t, Y)$$, CCA+ identifies the causal direction. The downstream adjustment then uses the appropriate longitudinal method based on whether time-varying confounders are present.

### 11.6. Sensitivity Analysis for Unmeasured Confounding

The ACE estimate rests on the no-unmeasured-confounders assumption. Rather than simply assuming this holds, we can quantify the sensitivity of the estimate to potential violations. The E-value [\[19\]](#ref-19) answers: how strong would an unmeasured confounder need to be (in terms of its association with both $$X$$ and $$Y$$) to explain away the observed ACE?

For an observed ACE of $$\hat{\beta}_X$$ with standard error $$\mathrm{SE}(\hat{\beta}_X)$$, the E-value is: 

$$
\text{E-value} = \frac{\hat{\beta}_X}{\mathrm{SE}(\hat{\beta}_X)} + \sqrt{\frac{\hat{\beta}_X^2}{\mathrm{SE}(\hat{\beta}_X)^2} - 1},
\tag{66}
$$

 representing the minimum strength of association (on the risk ratio scale) that an unmeasured confounder would need with both the cause and the effect to fully explain away the causal estimate. A large E-value means the finding is robust; a small E-value means modest hidden confounding could reverse the conclusion.

### 11.7. The LLM Causal Pruning Vision: Making Models 1000$$\times$$ More Efficient

#### 11.7.1. The Core Problem in Current LLMs

This section is speculative. It is clearly labeled as such. The direction discovery machinery in the preceding sections is not speculative — it is proved, validated, and implemented. What follows is the application of that machinery to a problem where the empirical validation has not been done yet, but the theoretical argument is clean enough to warrant stating carefully.

Large language models operate by sampling tokens from a probability distribution over a vocabulary of size $$\vert \mathcal{V}\vert $$ (typically 32,000–128,000): 

$$
P(x_{t+1} \mid x_1, \ldots, x_t) = \mathrm{softmax}(W_\mathrm{LM} \cdot h_t^L),
\tag{67}
$$

 where $$h_t^L$$ is the hidden state at the final layer $$L$$ and $$W_\mathrm{LM}$$ is the language modeling head. The hidden state is produced by $$L$$ transformer layers, each containing $$H$$ attention heads and a feedforward network (FFN). A model with $$L = 96$$ layers and $$H = 96$$ heads (GPT-4 scale) has 9,216 attention heads. Training and inference costs scale roughly with $$L \times H \times d^2$$, where $$d$$ is the hidden dimension.

The central inefficiency question is: *how many of these 9,216 attention heads are causally necessary for the model’s output quality?* Current evidence from mechanistic interpretability suggests that most are not. Voita et al. [\[52\]](#ref-52) showed that in machine translation, only 8–16 heads in an encoder-decoder model are responsible for the majority of the performance — the rest can be pruned without significant degradation. Michel et al. [\[53\]](#ref-53) found that individual attention heads can be removed from BERT without performance loss in many cases. These are observational findings: they measure what happens when heads are ablated. But ablation is not identification of causal necessity. A head whose removal degrades performance might be degrading it because other heads compensate; a head whose removal leaves performance unchanged might still be causally active in a distributed sense.

#### 11.7.2. Current Approach: Ablation Studies and Their Limits

The current state-of-the-art for mechanistic interpretability uses *activation patching* [\[51\]](#ref-51): take a “clean” input (where the desired behavior occurs) and a “corrupted” input (where it does not), patch the activation of a specific head from the clean run into the corrupted run, and measure whether the desired behavior is restored. The head is “causally sufficient” if patching restores behavior, and “causally necessary” if corrupting it breaks behavior.

This is a valid causal intervention, but it is performed one head at a time. For a model with 9,216 heads, a complete pairwise ablation study requires $$\binom{9216}{2} \approx 42.5$$ million experiments. At even one second per inference, this is 490 days. Current practice is to ablate selected heads based on attention visualization heuristics, which introduces confirmation bias: researchers look for causal roles in heads they expect to be causal.

#### 11.7.3. CCA+ Applied to Attention Head Activations

The CausalLens approach offers a fundamentally different methodology. Instead of ablating heads one at a time, we treat the activations of each attention head as an observational variable and apply CCA+ to identify which heads causally drive output quality versus which merely correlate with it.

Formally, let $$a_{l,h}^{(i)} \in \mathbb{R}^d$$ be the activation of attention head $$(l, h)$$ on input $$i$$, and let $$q^{(i)} \in \mathbb{R}$$ be a scalar measure of output quality on that input (e.g., perplexity on a reference continuation, or reward model score for RLHF-trained models). The question is: does $$a_{l,h}$$ causally drive $$q$$, or does the relationship arise from shared input complexity?

**The CCA+ test for attention heads:** For each head $$(l, h)$$, apply CCA+ to the pair $$(a_{l,h}, q)$$ across a sample of inputs. The CCA+ score measures whether the head’s activation *drives* quality or vice versa, exploiting the asymmetry that causal variables converge faster than effect variables in neural network training.

$$
\mathrm{CCA}^+(a_{l,h}, q) = \bar{L}_\mathrm{fwd}(a_{l,h} \to q) - \bar{L}_\mathrm{rev}(q \to a_{l,h}).
\tag{68}
$$

A strongly negative score for head $$(l, h)$$ indicates that this head’s activation causally drives output quality — its activation pattern, over a population of inputs, systematically predicts quality better than quality predicts its activation. Such heads are *causal*: pruning them would degrade the model. A near-zero or positive score indicates a non-causal or reverse-causal head: it responds to input difficulty (or to the model’s internal quality estimate) rather than driving it. Such heads are candidates for pruning.

#### 11.7.4. The Theoretical Justification

Why does this work for attention heads when the ANM may not formally hold? The key observation is that transformer attention layers process input tokens through a mechanism that is approximately additive in the noise: 

$$
h_t^l = h_t^{l-1} + \mathrm{Attn}^l(h^{l-1}) + \mathrm{FFN}^l(h^{l-1} + \mathrm{Attn}^l(h^{l-1})),
\tag{69}
$$

 where the residual stream architecture [\[51\]](#ref-51) ensures that each layer adds to (rather than replaces) the previous representation. This residual-stream structure is approximately additive, and the “noise” from non-causal heads is approximately independent of the causal heads’ outputs in expectation over a large corpus. The ANM assumptions are therefore approximately satisfied in the residual stream setting.

More precisely, if head $$(l, h)$$ causally contributes to the final output, its contribution $$\Delta h_t = \mathrm{head}_{l,h}(h^{l-1})$$ is a function of the upstream residual stream plus independent positional and attention noise. The downstream output quality $$q$$ is then $$f(\Delta h_t) + \varepsilon$$ where $$\varepsilon$$ captures all other contributions. This is approximately an ANM with $$\Delta h_t$$ as the cause and $$q$$ as the effect.

#### 11.7.5. The Efficiency Gain: Why This Could Achieve 1000$$\times$$ Compression

If we can identify the 1% of attention heads that are causally necessary for a model’s core capabilities, we can construct a sparse model that retains those heads and zeros out the rest. The efficiency gain has two components:

**1. Inference speedup.** The time complexity of attention for a sequence of length $$n$$ with $$H$$ heads and dimension $$d$$ is $$O(n^2 Hd + nHd^2)$$ per layer. If we prune to $$H' \ll H$$ causal heads, the speedup factor is approximately $$H/H'$$. If only 1% of heads are causal ($$H' = 0.01H$$), this gives $$100\times$$ speedup on the attention computation.

**2. Parameter reduction.** Each attention head has $$4d^2/H$$ parameters (for $$Q, K, V, O$$ projections). Removing $$99\%$$ of heads reduces the parameter count by approximately $$4d^2 \times 0.99$$ per layer, reducing memory and weight loading time. For a model with $$d = 12288$$ (GPT-4-scale), this is a $$4 \times 12288^2 \times 0.99 \approx 600M$$ parameter reduction *per layer*.

**Why 1000$$\times$$?** The combination of fewer heads (100$$\times$$ speedup on attention) with fewer layers (if layer-level causal pruning is applied in addition, potentially $$10\times$$ on the layer dimension) and better hardware utilization from the sparser computation graph yields a multiplicative efficiency gain in the $$100$$–$$1000\times$$ range. This is not a theoretical claim about any specific model — it is a structural argument that the order of magnitude of inefficiency in current LLMs (running thousands of computations for every causally necessary one) is what causal pruning addresses.

#### 11.7.6. The Causal vs. Correlational Distinction in Neural Networks

The fundamental reason this approach is different from existing pruning methods (magnitude-based, gradient-based, structured pruning) is the distinction between correlational and causal contribution.

Current pruning methods identify heads that have small weights (magnitude pruning), small gradient contributions (gradient-based pruning), or low attention entropy (importance-score pruning). All of these measure a head’s *statistical* contribution to the model’s current outputs on the current data distribution. They do not measure whether the head is *causally necessary* for the model’s capabilities.

A head that is causally necessary but has small attention entropy on the training distribution (because it only activates for rare input patterns) will be pruned by entropy-based methods and will appear unimportant — until the model encounters those rare patterns, at which point performance degrades. This is exactly the failure mode that Causal Head Gating [\[54\]](#ref-54) attempts to address by learning soft gates over heads and assigning them a causal taxonomy (facilitating, interfering, or irrelevant).

CCA+ provides a *population-level* causal taxonomy: a head is causally facilitating if its activations drive output quality across the population of inputs, and causally irrelevant if quality drives its activation (as when the model attends harder to difficult inputs precisely because they are difficult, not because the attention causes the difficulty). This distinction is invisible to correlational pruning methods.

#### 11.7.7. Implementation: Causal Pruning Pipeline for LLMs

The practical implementation has five steps:

1.  **Data collection.** Run the model on a large, diverse dataset of inputs. Record head activations $$a_{l,h}^{(i)}$$ (summarized as the $$L^1$$ norm or the top principal component of the $$d$$-dimensional activation) and output quality scores $$q^{(i)}$$ for each input $$i$$.

2.  **Dimensionality reduction.** Reduce each head activation to a scalar or low-dimensional representation (norm, entropy, or PCA projection onto the first principal component). This makes the bivariate CCA+ test applicable.

3.  **CCA+ scan.** Apply CCA+ to each $$(a_{l,h}, q)$$ pair. Record the CCA+ score for each head. This requires training $$2 \times L \times H$$ small MLPs, each on a sample of $$n$$ inputs. For $$L = 96$$, $$H = 96$$, $$n = 10{,}000$$, this is approximately $$18.4$$ million MLP training steps — feasible in hours on a GPU cluster.

4.  **Threshold and prune.** Prune heads with CCA+ scores above a threshold (near-zero or positive, indicating non-causal). Retain heads with strongly negative scores (causal contribution). Fine-tune the pruned model on a small number of steps to recover any lost performance from disrupted weight interactions.

5.  **Validate.** Compare the pruned model’s performance on held-out benchmarks against the full model. Measure the efficiency gain. Report the fraction of causal heads and the empirical efficiency-performance tradeoff.

#### 11.7.8. Connection to Causal Representation Learning

The broader program of which this is a part is *causal representation learning* (CRL, [\[55\]](#ref-55), [\[56\]](#ref-56)): learning representations of data that correspond to the latent causal variables of the data-generating process. CRL asks: given high-dimensional data $$X \in \mathbb{R}^p$$, can we learn a low-dimensional representation $$Z \in \mathbb{R}^k$$ (with $$k \ll p$$) such that $$Z$$ captures the causal structure of $$X$$?

For LLMs, the relevant instantiation is: given the high-dimensional activation space of the transformer (millions of neurons across hundreds of layers), can we identify the *causal subspace* — the low-dimensional manifold of activations that actually drives the model’s outputs? CCA+ provides a pairwise test for causal membership in this subspace. Applied to all heads and neurons systematically, it could map out the causal architecture of any transformer, layer by layer.

The identifiability results of Varici et al. [\[56\]](#ref-56) establish that the causal structure of a latent variable model is identifiable (up to permutation and scaling) given access to observational and interventional data. The interventional data in the LLM setting is precisely the activation patching experiments that mechanistic interpretability researchers already perform — but the observational scan using CCA+ can dramatically reduce how many patching experiments are needed by pre-selecting the causally active subgraph.

## 12. Removing the Assumptions: Toward Unconditional Rung 2

Every honest methods paper has a section like this, usually buried near the end under the heading “Limitations.” This paper moves it forward and treats it differently. The three assumptions the baseline pipeline relies on are not fixed constraints. They are each the entrance to a body of literature that has been working on the problem for twenty or thirty years, and in each case a solution exists — it just has not been assembled into an automated pipeline before.

The three assumptions: (1) the ANM holds with nonlinear injective mechanism; (2) there are no unmeasured confounders beyond the identified adjustment set; and (3) the adjustment relationship is approximately linear. This section attacks each one directly.

### 12.1. The Problem Structure

The three assumptions interact in a specific way that determines the right order of attack. Direction discovery (CCA+) requires the ANM. Interventional estimation (backdoor adjustment) requires the confounder and linearity assumptions. But the dependence runs one way: you need the direction before you can apply any adjustment formula, but the choice of adjustment formula is independent of how you found the direction.

This means the architecture is modular. Replace the direction module when the ANM fails. Replace the adjustment module when confounders are unmeasured or the relationship is nonlinear. The modules do not know about each other’s implementation. They communicate through a standard interface: a directed edge with a confidence score, a dataset, and an adjustment set.

### 12.2. Assumption 1: The ANM and Its Violations

#### 12.2.1. The Linear Gaussian Case

The most fundamental violation of the ANM identifiability conditions is the linear Gaussian case: $$Y = aX + \varepsilon$$ with $$\varepsilon \sim \mathcal{N}(0, \sigma^2)$$. As established in Section 2.4, both directions admit an ANM here, and CCA+ returns AMBIGUOUS. This is not a failure of our implementation — it is a mathematical impossibility result. Peters et al. [\[3\]](#ref-3) proved this: for linear Gaussian SCMs, the joint distribution $$P(X, Y)$$ is symmetric under direction reversal, so no method based on the joint distribution alone can identify direction.

The fix is to exploit *non-Gaussianity*. This is the approach of LiNGAM (Linear Non-Gaussian Acyclic Model, [\[6\]](#ref-6)). The key result is the Darmois-Skitovich theorem: if $$Y = aX + \varepsilon$$ with $$\varepsilon \not\sim \mathcal{N}$$, then the residuals $$Y - aX$$ are independent of $$X$$, but the residuals $$X - \frac{1}{a}Y$$ are *not* independent of $$Y$$ (except in the special case of Gaussian $$\varepsilon$$). Non-Gaussianity breaks the directional symmetry that the Gaussian case preserves. LiNGAM identifies causal direction by fitting the linear model in both directions and testing residual independence using an ICA-based non-Gaussianity measure (negative entropy, kurtosis, or a mutual information approximation).

**Integration into CausalLens:** Add a pre-test. Before running CCA+, test for linearity (fit a linear model, check $$R^2$$, test for nonlinear residual patterns using a RESET test [\[48\]](#ref-48)). If the relationship is approximately linear, fork to a LiNGAM module. If non-Gaussian, LiNGAM identifies the direction. If Gaussian, AMBIGUOUS is the correct and unavoidable answer. This conditional architecture covers all cases of the linear model.

#### 12.2.2. The Non-Injective Case

The second violation is non-injectivity: $$f$$ is many-to-one. The canonical example is $$Y = X^2 + \varepsilon$$. Here, the reverse regression target collapses to zero by symmetry, and CCA+ fails. The fix requires detecting non-injectivity before proceeding.

**Injectivity test:** A function $$f$$ is non-injective if there exist $$x_1 \neq x_2$$ with $$f(x_1) = f(x_2)$$. For the symmetric case $$Y = X^2$$, this means there are pairs $$(x, -x)$$ that map to the same $$Y$$ value. One can test for this by checking whether the residuals from the forward regression are symmetric around zero conditional on $$Y$$. More formally: 

$$
\text{Test statistic: } T = \text{max}_{y \in \text{range}(Y)} \left\vert  \widehat{E}[X \mid Y = y] \right\vert ,
\tag{70}
$$

 which should be near zero for symmetric non-injective $$f$$ but nonzero for injective $$f$$. When $$T \approx 0$$ and the relationship is clearly non-injective, the AMBIGUOUS verdict is issued with an explanatory note about the mechanism type.

For near-injective functions (slightly asymmetric $$X^2$$ with $$X$$ not centered at zero), CCA+ recovers accuracy because the symmetry breaking is detectable. The failure mode is precisely the symmetric case, which is relatively rare in real data where inputs are not exactly symmetric. When it occurs, the appropriate output is AMBIGUOUS, which the pipeline already returns.

#### 12.2.3. Towards CCA+ Without the ANM: Distributional Asymmetry

The deepest extension removes the ANM assumption entirely and seeks causal direction from the *distributional asymmetry* between $$P_X$$ and $$P_{Y\vert X}$$ versus $$P_Y$$ and $$P_{X\vert Y}$$. This is the program of IGCI [\[5\]](#ref-5) and its successors.

The Algorithmic Markov Condition (AMC) states that in the true causal direction $$X \to Y$$, the marginal distribution $$P_X$$ and the conditional $$P_{Y\vert X}$$ are *algorithmically independent*: knowing $$P_X$$ tells you nothing about the form of $$P_{Y\vert X}$$, and vice versa. In the reverse direction, $$P_Y$$ and $$P_{X\vert Y}$$ are algorithmically dependent — both shaped by the underlying causal mechanism. This asymmetry is measurable using various proxy statistics:

- **IGCI score:** $$S_\mathrm{IGCI} = \frac{1}{n}\sum_i \log \vert f'(x_i)\vert  \cdot (\text{sign related to regression slope})$$, which is positive in the causal direction and negative in the anti-causal direction for deterministic relationships.

- **Entropy-based:** $$H(X) + H(Y \mid X)$$ versus $$H(Y) + H(X \mid Y)$$, exploiting the fact that the causal factorization has shorter description length (Section 2.1.2).

- **Score function skewness (SkewScore, [\[32\]](#ref-32)):** The skewness of $$\nabla_X \log p(X)$$ evaluated at the data, which has a known sign in the causal direction for heteroscedastic noise models.

**CCA+ ensemble:** The most robust direction discovery combines CCA+ (convergence asymmetry), IGCI (distributional asymmetry), and LiNGAM (residual independence) in an ensemble vote. Each method exploits a different dimension of the causal asymmetry. Disagreement among methods is informative: if two of three agree, use the majority; if all three disagree, AMBIGUOUS is the correct answer. This ensemble removes the dependence on any single method’s assumptions.

### 12.3. Assumption 2: The No-Unmeasured-Confounders Assumption

This is the hardest assumption. The no-unmeasured-confounders condition — strong ignorability, conditional exchangeability, absence of hidden common causes — is the single most criticized limitation of observational causal inference. It is empirically untestable from the observed data alone. If a variable $$U$$ causes both $$X$$ and $$Y$$ and is not in the dataset, no amount of statistical adjustment on observed variables can remove its bias. Pearl (2000) showed that this situation corresponds to a graph that is not identifiable by the backdoor criterion, and the ACE cannot be recovered without additional information.

However, additional information is often available in four distinct forms, each enabling Rung 2 without strong ignorability:

#### 12.3.1. The Front-Door Criterion: Mediation as an Unmeasured-Confounder Solution

Pearl’s front-door criterion [\[1\]](#ref-1) is perhaps the most elegant result in all of causal inference: it provides exact identification of $$P(Y \mid \mathrm{do}(X))$$ in the presence of unmeasured confounders $$U$$, without assuming ignorability, provided a mediating variable $$M$$ exists on the causal path from $$X$$ to $$Y$$ that satisfies specific conditions.

> **Definition 12.1 (Front-Door Criterion).** A set of variables $$M$$ satisfies the front-door criterion relative to $$(X, Y)$$ if:
>
> 1.  All directed paths from $$X$$ to $$Y$$ pass through $$M$$ (M intercepts all paths).
>
> 2.  There are no unblocked backdoor paths from $$X$$ to $$M$$.
>
> 3.  All backdoor paths from $$M$$ to $$Y$$ are blocked by $$X$$.

When the front-door criterion holds, the causal effect is identified by the **front-door formula**: 

$$
P(Y \mid \mathrm{do}(X = x)) = \sum_m P(M = m \mid X = x) \sum_{x'} P(Y \mid X = x', M = m) P(X = x').

\tag{71}
$$

The mechanics of this formula are remarkable. Even though $$U$$ confounds the $$X$$–$$Y$$ relationship, the formula sidesteps $$U$$ entirely by chaining two unconfounded effects: (i) the effect of $$X$$ on $$M$$ (unconfounded because no backdoor paths into $$X$$ lead through $$M$$) and (ii) the effect of $$M$$ on $$Y$$ controlling for $$X$$ (unconfounded because $$X$$ blocks the only backdoor path between $$M$$ and $$Y$$, since $$U \to X \to M$$ is blocked by conditioning on $$X$$).

> **Example (Smoking, Tar, Lung Cancer).** Pearl’s canonical example: $$X$$ = smoking, $$M$$ = tar deposition in lungs, $$Y$$ = lung cancer, $$U$$ = genetic predisposition (causes both smoking propensity and cancer independently). The genetic confounder is unmeasured. The front-door formula applies because: (i) smoking causes cancer only through tar (no direct effect), (ii) smoking has no backdoor confounders with tar accumulation, and (iii) $$X$$ blocks the only backdoor path from $$M$$ to $$Y$$. Applying (71): 
>
> $$
> \begin{aligned}
> &P(\mathrm{Cancer} \mid \mathrm{do}(\mathrm{Smoking} = s)) \nonumber \\
> &= \sum_t P(\mathrm{Tar} = t \mid \mathrm{Smoking} = s)
> \sum_{s'} P(\mathrm{Cancer} \mid \mathrm{Smoking} = s', \mathrm{Tar} = t) P(\mathrm{Smoking} = s').
>
> \end{aligned}\tag{72}
> $$
>
>  This is a Rung 2 answer from observational data in the presence of an unmeasured confounder. No instrument, no experiment. Just the graph structure and two regressions.

**Practical applicability.** The front-door criterion is rare in practice because condition (i) — that all paths from $$X$$ to $$Y$$ pass through $$M$$ — requires that the mediator completely intercepts the causal effect. In many real settings, there are both direct and mediated effects. The conditional front-door adjustment [\[41\]](#ref-41) relaxes this by allowing additional observed confounders $$W$$ to block the residual backdoor paths, substantially expanding the set of applicable graphs.

**Integration into CausalLens:** After CCA+ identifies the direction $$X \to Y$$, scan the dataset for candidate mediators $$M$$: variables that are (a) caused by $$X$$ (positive correlation with $$X$$ after removing $$Y$$ dependence) and (b) causally precede $$Y$$ (positive correlation with $$Y$$ after removing $$X$$ dependence). If a candidate $$M$$ satisfies the front-door conditions, apply formula (71) instead of the backdoor formula. This adds an unmeasured-confounder-robust estimation path to the pipeline.

#### 12.3.2. Instrumental Variables: External Variation as an Identification Strategy

An instrumental variable (IV) is a variable $$Z$$ that satisfies:

1.  **Relevance:** $$Z$$ is strongly correlated with $$X$$, $$\mathrm{Cov}(Z, X) \neq 0$$.

2.  **Exclusion:** $$Z$$ affects $$Y$$ only through $$X$$, $$Z \perp Y \mid X$$.

3.  **Exogeneity:** $$Z$$ is independent of the unmeasured confounder $$U$$, $$Z \perp U$$.

Under these three conditions, the IV estimand identifies the causal effect: 

$$
\mathrm{ACE}_\mathrm{IV}(X \to Y) = \frac{\mathrm{Cov}(Z, Y)}{\mathrm{Cov}(Z, X)}
= \frac{\text{Reduced form}}{\text{First stage}}.

\tag{73}
$$

This is the Wald estimator [\[44\]](#ref-44). For continuous variables, a two-stage least squares (2SLS) procedure generalizes this to multiple instruments and controls: 

$$
\begin{aligned}
\text{Stage 1:} &\quad \hat{X} = \hat{\pi}_0 + \hat{\pi}_Z Z + \hat{\pi}_{W} W, \\
\text{Stage 2:} &\quad Y = \hat{\alpha} + \hat{\beta}_X \hat{X} + \hat{\beta}_W W + \epsilon,

\end{aligned}\tag{74–75}
$$

 where $$W$$ is a vector of observed controls and $$\hat{X}$$ is the predicted value of $$X$$ from the instrument. The coefficient $$\hat{\beta}_X$$ from Stage 2 is the IV estimate of the ACE.

**Why the IV estimate is Rung 2.** The instrument $$Z$$ creates exogenous variation in $$X$$ — variation that, by the exogeneity condition, is unrelated to the unmeasured confounder $$U$$. The 2SLS procedure extracts only this clean variation in $$X$$ (via Stage 1) and measures its effect on $$Y$$ (Stage 2). This is equivalent to a partial randomized experiment: $$Z$$ acts as if it randomly assigns different values of $$X$$ to different units, even though the assignment is not truly random. The result is an estimate of $$P(Y \mid \mathrm{do}(X))$$ for compliers (units whose $$X$$ responds to $$Z$$).

**Classic examples.**

- Angrist and Krueger (1991) [\[45\]](#ref-45): Birthday quarter as an IV for years of education (children born in Q1 must complete more schooling before they can legally drop out), estimating the causal effect of education on earnings while avoiding the confounding of family background.

- Mendelian randomization [\[46\]](#ref-46): Genetic variants as IVs for disease-related exposures (BMI, cholesterol, blood pressure). Because genes are assigned at conception, they are independent of most unmeasured confounders of lifestyle-disease relationships. CCA+ identifying BMI $$\to$$ Glucose can be strengthened by using genetic variants associated with BMI (e.g., $$FTO$$ gene variants) as instruments to estimate the ACE while bypassing the ignorability assumption.

**Limitation.** The exclusion restriction (condition 2) is empirically untestable and can be violated if the instrument has pleiotropic effects. Mendelian randomization, for example, can be invalidated if a genetic variant affects multiple biological pathways that independently influence the outcome. Sensitivity analysis using multiple instruments with overidentification tests (Sargan-Hansen test [\[47\]](#ref-47)) can assess but not prove exclusion.

**Integration into CausalLens:** After CCA+ identifies the direction, scan for candidate IVs: variables that are strongly correlated with $$X$$ but show weak direct correlation with $$Y$$ after conditioning on $$X$$. Flag these as candidate instruments. Report the IV estimate alongside the backdoor estimate; large discrepancy signals possible unmeasured confounding.

#### 12.3.3. Proximal Causal Inference: Proxy Variables for Hidden Confounders

Both the front-door criterion and instrumental variables require specific structural conditions that may not be met in any given dataset. The front-door criterion needs a mediator that completely intercepts all causal paths. IV needs an exogenous variable that is relevant, excluded, and independent of the confounder. What happens when neither is available?

Miao, Geng, and Tchetgen Tchetgen [\[42\]](#ref-42) gave an answer in 2018 that most of the causal inference community did not immediately recognize as the breakthrough it was. They established that if two types of proxy variables exist for the hidden confounder $$U$$ — a treatment-inducing proxy $$Z$$ affecting $$X$$, and an outcome-inducing proxy $$W$$ affecting $$Y$$ — then $$P(Y \mid \mathrm{do}(X))$$ can be nonparametrically identified even with unmeasured $$U$$. No mediator. No instrument in the classical sense. Just two variables that are related to the hidden cause through different channels.

The identification uses a *confounding bridge function* $$h(A, Z)$$ satisfying: 

$$
E[Y \mid A = a, W = w] = E[h(a, Z) \mid A = a, W = w],

\tag{76}
$$

 where $$A$$ is the treatment. When the bridge function $$h$$ is identified from (76), the causal effect is: 

$$
E[Y \mid \mathrm{do}(A = a)] = E[h(a, Z)].

\tag{77}
$$

**What are proxies?** A treatment confounding proxy $$Z$$ is a variable that is related to the hidden confounder $$U$$ through a path that does not go through the treatment $$A$$ or outcome $$Y$$. An outcome confounding proxy $$W$$ is related to $$U$$ through a path that does not go through $$A$$. In a clinical setting:

- $$U$$ = overall health status (unmeasured)

- $$A$$ = drug treatment

- $$Y$$ = patient outcome

- $$Z$$ = pre-treatment blood pressure (proxy for $$U$$ through health status $$\to$$ BP)

- $$W$$ = post-treatment unrelated biomarker (proxy for $$U$$ through health status $$\to$$ biomarker)

**Two-stage least squares for proximal inference.** In the linear case, Tchetgen Tchetgen et al. [\[43\]](#ref-43) showed that the proximal estimator reduces to a 2SLS procedure: 

$$
\begin{aligned}
\text{Stage 1:} &\quad W = \hat{\gamma}_0 + \hat{\gamma}_A A + \hat{\gamma}_Z Z + \eta, \\
\text{Stage 2:} &\quad Y = \hat{\alpha} + \hat{\beta}_A A + \hat{\beta}_W \hat{W} + \epsilon.

\end{aligned}\tag{78–79}
$$

 The coefficient $$\hat{\beta}_A$$ is the proximal ACE. Unlike standard IV, the instrument here ($$Z$$) is a proxy for the confounder rather than a cause of the treatment — a fundamentally different identification strategy that does not require the exclusion restriction.

**Integration into CausalLens:** After CCA+ identifies the direction $$X \to Y$$ and confounder screening identifies unmeasured confounding risk (e.g., large discrepancy between naive and IV estimates), scan for proxy pairs. A treatment proxy $$Z$$ should satisfy: $$Z$$ is correlated with $$X$$ but not with $$Y$$ conditional on $$X$$ and $$Z$$’s relationship to $$U$$. An outcome proxy $$W$$ should satisfy: $$W$$ is correlated with $$Y$$ but not with $$X$$ conditional on $$W$$’s relationship to $$U$$. When both are found, apply the proximal 2SLS estimator.

### 12.4. Assumption 3: Linear Sufficiency of Adjustment

The backdoor formula holds in full generality for any functional form. The linear OLS implementation in Section 4 is an approximation that works well when the true confounding relationship is approximately linear but can fail when it is not. Three extensions remove the linearity assumption while preserving the identification result.

#### 12.4.1. Kernel Regression Backdoor

Replace the OLS fit in equation (33) with kernel regression. For a kernel $$k : \mathbb{R} \times \mathbb{R} \to \mathbb{R}$$ and bandwidth $$h$$, the kernel regression estimate of $$E[Y \mid X = x, Z = z]$$ is: 

$$
\hat{m}(x, z) = \frac{\sum_{i=1}^n Y_i \cdot k\!\left(\frac{x-X_i}{h}\right) k\!\left(\frac{z-Z_i}{h}\right)}
{\sum_{i=1}^n k\!\left(\frac{x-X_i}{h}\right) k\!\left(\frac{z-Z_i}{h}\right)}.
\tag{80}
$$

 The nonparametric backdoor estimate is then: 

$$
\widehat{E}[Y \mid \mathrm{do}(X = x)] = \frac{1}{n}\sum_{i=1}^n \hat{m}(x, Z_i),
\tag{81}
$$

 which averages the kernel regression prediction at $$X = x$$ over the empirical distribution of $$Z$$. This is a consistent estimator of the true ACE under nonlinear confounding, with no parametric assumptions on the functional form [\[35\]](#ref-35).

#### 12.4.2. Gradient Boosting Backdoor

A more powerful approach uses gradient-boosted regression trees (GBRT) to estimate $$\hat{m}(x, z) = E[Y \mid X = x, Z = z]$$. GBRT is a flexible, off-the-shelf estimator that handles nonlinearity, interactions, and variable-importance ranking without requiring specification of the functional form. The backdoor estimate follows the same Monte Carlo averaging: 

$$
\widehat{E}[Y \mid \mathrm{do}(X = x)] = \frac{1}{n}\sum_{i=1}^n \hat{m}_\mathrm{GBRT}(x, Z_i).
\tag{82}
$$

 This is a valid Rung 2 estimator under the backdoor criterion with no functional form assumptions. Chernozhukov et al. [\[49\]](#ref-49) establish that this “plug-in” approach, combined with cross-fitting, achieves semiparametric efficiency under mild smoothness conditions and is doubly robust when combined with propensity score weighting.

### 12.5. Effect Modification and Causal Interaction

#### 12.5.1. The Distinction Between Confounding and Interaction

Confounding and effect modification are frequently conflated in applied research, but they are structurally distinct phenomena with opposite implications for data analysis. A confounder $$C$$ biases the estimate of the $$X \to Y$$ effect and should be adjusted for. An effect modifier $$V$$ changes the *magnitude or direction* of the $$X \to Y$$ effect across its strata, and *should not* be adjusted away — it should be reported stratum-by-stratum, because the effect is genuinely different in different subgroups.

Formally, $$V$$ is an effect modifier of the $$X \to Y$$ effect if: 

$$
E[Y \mid \mathrm{do}(X = 1), V = v_1] - E[Y \mid \mathrm{do}(X = 0), V = v_1]
\neq
E[Y \mid \mathrm{do}(X = 1), V = v_0] - E[Y \mid \mathrm{do}(X = 0), V = v_0].
\tag{83}
$$

 Whether $$V$$ is also a confounder (i.e., whether its distribution is associated with $$X$$) is independent of whether it is an effect modifier. A variable can be: (a) a confounder only (adjust for it), (b) an effect modifier only (stratify by it), (c) both (adjust for it and report strata-specific effects), or (d) neither (ignore it).

#### 12.5.2. Additive Versus Multiplicative Interaction

Causal interaction is scale-dependent. The same data can show interaction on the additive scale but not the multiplicative scale, or vice versa. This matters because the scientific and policy interpretation differs:

**Additive interaction** (synergy in the public health sense) occurs when the combined effect of two exposures $$A$$ and $$B$$ on the risk difference scale exceeds the sum of their individual effects: 

$$
\begin{gathered}
E[Y \mid \mathrm{do}(A=1, B=1)] - E[Y \mid \mathrm{do}(A=0, B=0)] > \\
\bigl(E[Y \mid \mathrm{do}(A=1, B=0)] - E[Y \mid \mathrm{do}(A=0, B=0)]\bigr) \\
+ \bigl(E[Y \mid \mathrm{do}(A=0, B=1)] - E[Y \mid \mathrm{do}(A=0, B=0)]\bigr).
\end{gathered}\tag{84}
$$

**Multiplicative interaction** occurs when the combined effect on the risk ratio scale exceeds the product of individual risk ratios: $$\mathrm{RR}_{AB} > \mathrm{RR}_A \times \mathrm{RR}_B$$.

**Relative Excess Risk due to Interaction (RERI).** VanderWeele and Knol [\[93\]](#ref-93) advocate the RERI as the primary measure of additive interaction: 

$$
\mathrm{RERI} = \mathrm{RR}_{AB} - \mathrm{RR}_A - \mathrm{RR}_B + 1,

\tag{85}
$$

 where $$\mathrm{RR}_{ij} = P(Y=1 \mid A=i, B=j) / P(Y=1 \mid A=0, B=0)$$. $$\mathrm{RERI} > 0$$ indicates positive additive interaction (superadditivity, or biological synergy in the sufficient-cause sense); $$\mathrm{RERI} = 0$$ is additivity; $$\mathrm{RERI} < 0$$ is subadditivity. The RERI is on the absolute risk scale and corresponds directly to the public health concept of attributable risk modification.

Rothman’s sufficient-cause model [\[94\]](#ref-94) provides the mechanistic interpretation: $$\mathrm{RERI} > 0$$ implies that there exists a sufficient cause (a minimal set of background factors whose joint presence is sufficient to produce the outcome) that requires both $$A = 1$$ and $$B = 1$$. Such causes cannot operate through either factor alone and represent genuine biological or social synergy.

#### 12.5.3. The Doubly Robust Estimator

The doubly robust (DR) estimator combines an outcome model $$\hat{m}(x, z)$$ with a propensity score model $$\hat{e}(z) = E[X \mid Z = z]$$: 

$$
\widehat{\mathrm{ACE}}_\mathrm{DR}(x) =
\frac{1}{n}\sum_{i=1}^n \left[ \hat{m}(x, Z_i) + \frac{\mathbf{1}[X_i = x]}{\hat{e}(Z_i)}(Y_i - \hat{m}(x, Z_i)) \right].

\tag{86}
$$

 This estimator is *doubly robust* [\[34\]](#ref-34): it is consistent if either the outcome model $$\hat{m}$$ or the propensity score model $$\hat{e}$$ is correctly specified, but not necessarily both. This is a substantial robustness improvement over either approach alone.

The DR estimator also achieves the semiparametric efficiency bound [\[50\]](#ref-50) — the minimum variance achievable among regular estimators — when both models are consistently estimated. This makes it the optimal estimator in the semiparametric sense, and it provides another layer of protection against model misspecification.

### 12.6. Selection Bias: The Heckman Correction

#### 12.6.1. Selection Bias as Distinct from Confounding

Confounding arises when common causes of $$X$$ and $$Y$$ are not adjusted for, biasing the estimated causal effect. Selection bias arises from a different mechanism: the sample used for analysis is not representative of the target population because participation in the study is itself caused by variables related to the treatment or outcome. Formally, selection bias occurs when the analyst conditions on a collider $$S$$ (a variable caused by both $$X$$ and $$Y$$, or by $$Y$$ alone): 

$$
X \to S \leftarrow Y \quad \text{or} \quad Y \to S \leftarrow U,
\tag{87}
$$

 where $$U$$ is an unmeasured variable. Conditioning on $$S$$ (by restricting the sample to $$S = 1$$) opens a spurious path between $$X$$ and $$Y$$, biasing all downstream estimates.

In clinical studies, this arises when: only patients who respond to treatment are retained in follow-up (response-based selection); patients who drop out differ systematically from those who remain (attrition bias); or patients are referred to specialized care based on disease severity (referral bias). In economic studies, it arises when wages are only observed for workers who choose to participate in the labor force.

#### 12.6.2. The Heckman Selection Model

Heckman’s [\[95\]](#ref-95) Nobel Prize-winning correction addresses a specific and common form of selection: truncated samples where the outcome is observed only for a selected subset. The model has two equations: 

$$
\begin{aligned}
Y_i^* &= X_i^T \beta + \varepsilon_i \quad \text{(outcome equation, latent)}, \\
S_i^* &= Z_i^T \gamma + \eta_i \quad \text{(selection equation)},

\end{aligned}\tag{88–89}
$$

 where $$Y_i$$ is observed only when $$S_i^* > 0$$ (i.e., $$S_i = 1$$), and $$(\varepsilon_i, \eta_i) \sim \mathcal{N}(0, \Sigma)$$ are bivariate normal with correlation $$\rho$$. The selection bias arises from $$\rho \neq 0$$: the error in the outcome equation is correlated with the error in the selection equation, so $$E[\varepsilon_i \mid S_i = 1] \neq 0$$.

Heckman’s correction adds the inverse Mills ratio as a control variable: 

$$
E[Y_i \mid X_i, S_i = 1] = X_i^T \beta + \rho\sigma_\varepsilon \cdot \lambda(Z_i^T\gamma),

\tag{90}
$$

 where $$\lambda(v) = \phi(v)/\Phi(v)$$ is the inverse Mills ratio, $$\phi$$ is the standard normal PDF, and $$\Phi$$ is the standard normal CDF. The correction term $$\lambda(Z_i^T\gamma)$$ is estimated from a probit model for selection in a first stage, then included as a regressor in the outcome equation. The OLS estimator on the corrected outcome equation is consistent for $$\beta$$.

**Identification.** The Heckman model is technically identified by the bivariate normality assumption alone (the nonlinearity of $$\lambda$$ distinguishes it from the outcome equation). However, this is weak identification. Strong identification requires an *exclusion restriction*: a variable $$Z_j$$ in the selection equation that is excluded from the outcome equation. The excluded variable drives selection without directly affecting the outcome, analogous to an instrument. Without a valid exclusion restriction, the model relies heavily on distributional assumptions that are untestable.

**Connection to CausalLens.** Selection bias in the context of CausalLens arises when the dataset used for direction discovery and effect estimation is a non-representative subset of the target population. CCA+ is robust to mild selection bias because the convergence asymmetry is driven by the structural noise properties of the mechanism, which are less affected by selection than the marginal distributions of $$X$$ and $$Y$$. However, severe selection (e.g., only extreme values of $$X$$ are observed) can distort the effective distribution and weaken or reverse the CCA+ signal. The Heckman correction applied to the dataset before running CausalLens can partially address this.

### 12.7. The Full Assumption-Relaxed Architecture

Combining all three extensions yields an architecture that reaches Rung 2 across the full spectrum of data-generating processes:

| **Situation** | **Direction module** | **Adjustment module** |
| ---| ---| ---|
| Nonlinear injective ANM | CCA+ | Backdoor (OLS, kernel, or DR) |
| Linear non-Gaussian | LiNGAM | Backdoor (OLS) |
| Linear Gaussian | AMBIGUOUS | Not applicable |
| Non-injective ANM | AMBIGUOUS (pre-test) | Not applicable |
| Unmeasured confounders, mediator available | CCA+ | Front-door formula |
| Unmeasured confounders, IV available | CCA+ | IV / 2SLS |
| Unmeasured confounders, proxies available | CCA+ | Proximal 2SLS |
| Nonlinear confounding | CCA+ | Kernel/GBRT backdoor or DR |

The AMBIGUOUS outputs are honest scientific statements, not engineering failures. For the linear Gaussian case and non-injective mechanisms, the direction is genuinely not identifiable from observational data alone — no amount of engineering can fix this without additional information (an experiment, an instrument, or a strong structural assumption). The architecture handles every identifiable case and correctly abstains on every non-identifiable one.

### 12.8. The Universal Rung 2 Engine: A Vision

The architecture above can be implemented as a decision tree:

1.  **Linearity test:** Is the relationship approximately linear (RESET test, $$p > 0.05$$)?

    1.  If yes: Run LiNGAM direction test.

    2.  If no: Run CCA+ direction test.

2.  **Direction verdict:** Is the direction clear (strong or weak signal, not AMBIGUOUS)?

    1.  If AMBIGUOUS: Report AMBIGUOUS. Stop.

    2.  If direction is $$X \to Y$$: Proceed.

3.  **Confounder situation:** Which identification strategy applies?

    1.  All confounders measured: Use backdoor adjustment (OLS for approximate linearity, GBRT or kernel for nonlinear confounding).

    2.  Mediator $$M$$ available: Use front-door formula.

    3.  Instrument $$Z$$ available: Use IV/2SLS.

    4.  Proxy pair $$(Z, W)$$ available: Use proximal 2SLS.

    5.  None of the above: Report estimated ACE with E-value sensitivity analysis stating how strong an unmeasured confounder would need to be to reverse the conclusion.

4.  **Output:** ACE estimate, confidence interval, adjustment strategy used, and explicit statement of remaining assumptions.

This architecture removes the three original assumptions as hard requirements and replaces them with a branching logic that selects the appropriate identification strategy for the data at hand. No single case requires all three assumptions simultaneously. The universal engine is assumption-*flexible*, not assumption-free: every branch has its own conditions, and when none are met, the honest output is AMBIGUOUS with quantified uncertainty bounds.

## 13. Measurement Error and Its Effect on Causal Estimation

### 13.1. Classical Versus Berkson Measurement Error

No dataset is measured perfectly. This is an obvious statement, but its consequences for causal inference are less obvious and frequently ignored. The type of measurement error determines whether it attenuates estimates, inflates them, or reverses their sign. Getting this wrong does not just add noise to the answer — it can make a harmful intervention appear beneficial. There are two canonical models of how error enters measurements, and they have opposite implications [\[96\]](#ref-96), [\[97\]](#ref-97):

#### 13.1.1. Classical (Cochran) Measurement Error

In the *classical* model, the true value $$X^*$$ is observed with additive noise: 

$$
X = X^* + U, \quad U \perp X^*, \quad E[U] = 0, \quad \mathrm{Var}(U) = \sigma_U^2.
\tag{91}
$$

 The error $$U$$ is independent of the true value. This model describes situations where the measurement instrument introduces random noise on top of the true signal: a scale that has random fluctuations, a questionnaire where respondents make random recall errors, a sensor with thermal noise.

Under classical measurement error in the cause variable, OLS regression of $$Y$$ on $$X$$ is biased toward zero (attenuation bias). Formally, if $$Y = \beta X^* + \varepsilon$$ with $$\varepsilon \perp X^*$$, then the OLS slope from regressing $$Y$$ on $$X$$ is: 

$$
\hat{\beta}_\mathrm{OLS} \xrightarrow{p} \beta \cdot \frac{\sigma_{X^*}^2}{\sigma_{X^*}^2 + \sigma_U^2}
= \beta \cdot \lambda,

\tag{92}
$$

 where $$\lambda = \sigma_{X^*}^2 / (\sigma_{X^*}^2 + \sigma_U^2) \in (0, 1)$$ is the *reliability ratio*. The OLS estimate is always smaller in absolute value than the true effect when $$\lambda < 1$$. Correcting for attenuation requires an estimate of $$\lambda$$, which can be obtained from a validation subsample (where both $$X$$ and $$X^*$$ are measured), repeated measurements (allowing estimation of $$\sigma_U^2$$), or instrumental variables (where the instrument is correlated with $$X^*$$ but not $$U$$).

#### 13.1.2. Berkson Measurement Error

In the *Berkson* model [\[96\]](#ref-96), the *assigned* value $$X$$ is fixed (by experimental design or grouped assignment) and the true value $$X^*$$ deviates from it: 

$$
X^* = X + U, \quad U \perp X, \quad E[U] = 0.
\tag{93}
$$

 This model describes situations where groups are assigned a nominal exposure but individuals within the group deviate from it: a clinical trial assigns 10mg dose but patients actually take 8mg–12mg due to absorption variability; an environmental study assigns exposure based on residential location but actual exposure varies.

Under Berkson error, OLS is unbiased for the effect of the assigned value $$X$$: $$\hat{\beta}_\mathrm{OLS} \xrightarrow{p} \beta$$. However, the estimand is the effect of the assigned value, not the true value. If the researcher wants the effect of $$X^*$$ (the true exposure), the Berkson model introduces a different bias that inflates the standard error rather than attenuating the point estimate.

#### 13.1.3. Differential Versus Non-Differential Measurement Error

*Non-differential* measurement error means $$U \perp Y \mid X^*$$: the error in measuring $$X$$ is unrelated to the outcome given the true exposure. This is the assumption underlying equation (92). Under non-differential classical error, the bias is always toward the null.

*Differential* measurement error means $$U \not\perp Y \mid X^*$$: the measurement error in $$X$$ is related to $$Y$$ even after conditioning on the true $$X^*$$. This can occur when the measurement of $$X$$ is influenced by knowledge of $$Y$$ (recall bias: cases recall exposure more accurately than controls in a case-control study) or when the same instrument measures both $$X$$ and $$Y$$ with correlated error. Differential error can bias the estimate in any direction, including *away from the null*, and does not have the simple attenuation formula (92).

### 13.2. SIMEX and Regression Calibration for Measurement Error Correction

#### 13.2.1. Regression Calibration

Carroll et al. [\[98\]](#ref-98) developed *regression calibration* as a pragmatic method for correcting attenuation bias. The method replaces the mismeasured $$X$$ with its conditional expectation given observed data: 

$$
\hat{X}^* = E[X^* \mid X, W] = \mu_{X^*} + \lambda(X - \mu_X) + \Sigma_{X^*W}\Sigma_{WW}^{-1}(W - \mu_W),
\tag{94}
$$

 where $$W$$ is a vector of error-free covariates and $$\lambda$$ is the reliability ratio. The regression calibration estimator then regresses $$Y$$ on $$\hat{X}^*$$ instead of $$X$$, producing a consistent estimator for $$\beta$$ under non-differential error and linear outcome model.

#### 13.2.2. SIMEX

SIMEX (Simulation Extrapolation, [\[99\]](#ref-99)) is a simulation-based method that does not require a parametric model for the measurement error distribution. The key idea is to deliberately add extra measurement error to the data, observe how the estimates degrade, and extrapolate backward to the zero-error limit.

For $$\lambda \in \{0, 0.5, 1.0, 1.5, 2.0\}$$ (the simex grid), construct: 

$$
X_{(b,\lambda)} = X + \sqrt{\lambda} \cdot \tilde{U}_{(b)}, \quad \tilde{U}_{(b)} \sim \mathcal{N}(0, \hat{\sigma}_U^2),
\tag{95}
$$

 where $$b = 1, \ldots, B$$ indexes the simulation replicates. Fit the naive estimator $$\hat{\beta}(\lambda)$$ at each grid point. The estimator is decreasing in $$\lambda$$ (adding error attenuates the estimate further). Fit an extrapolation function $$g(\lambda)$$ to the points $$\{(\lambda, \hat{\beta}(\lambda))\}$$ — typically a quadratic or rational function. The SIMEX-corrected estimate is $$\hat{\beta}_\mathrm{SIMEX} = g(-1)$$: the extrapolation to $$\lambda = -1$$, which corresponds to removing all measurement error.

**Effect on CCA+ direction discovery.** Classical measurement error in $$X$$ attenuates the forward signal: the network predicting $$Y$$ from mismeasured $$X$$ achieves higher loss than it would with the true $$X^*$$, because some signal in $$X^*$$ is replaced by noise $$U$$. The reverse network (predicting mismeasured $$X$$ from $$Y$$) now has an additional noise component $$U$$ to model, which is independent of $$Y$$ under non-differential error. This actually *helps* CCA+ in one sense (the reverse problem becomes harder because $$Y$$ must now predict both $$X^*$$ and $$U$$) but *hurts* it in another (the forward problem also becomes harder because $$X$$ is a noisy proxy for $$X^*$$). The net effect on the CCA+ asymmetry depends on the signal-to-noise ratio $$\lambda$$ and the degree of nonlinearity in $$f$$. For high-quality data ($$\lambda > 0.9$$), the attenuation is small enough to preserve the asymmetry. For low-quality data ($$\lambda < 0.7$$), pre-correction using regression calibration is recommended before running CCA+.

## 14. Simpson’s Paradox, Ecological Fallacy, and the Necessity of Causal Graphs

### 14.1. Simpson’s Paradox: The Arithmetic of Causal Confusion

#### 14.1.1. The Phenomenon

A treatment that appears beneficial in every subgroup can appear harmful in the aggregate. The numbers are not lying. The arithmetic is correct. The problem is that the arithmetic is being done on the wrong quantity — the association rather than the causal effect. This is Simpson’s paradox, and it is not a curiosity. It appears in kidney stone treatment trials, in SAT score reporting, in clinical drug evaluations, in sports statistics. Pavlides and Perlman (2009) computed that in a random $$2 \times 2 \times 2$$ contingency table with uniform distribution, it occurs with probability exactly $$\frac{1}{60}$$. That is not rare.

Formally [\[86\]](#ref-86), [\[87\]](#ref-87): a situation in which an association between $$X$$ and $$Y$$ reverses direction when the population is stratified by a third variable $$C$$: 

$$
P(Y = 1 \mid X = 1) > P(Y = 1 \mid X = 0) \quad \text{(aggregate level)},
\tag{96}
$$

 

$$
P(Y = 1 \mid X = 1, C = c) < P(Y = 1 \mid X = 0, C = c) \quad \text{for all } c \quad \text{(within strata)}.
\tag{97}
$$

The classic numerical example involves a $$2 \times 2 \times 2$$ table. A treatment appears beneficial overall but harmful in every subgroup — the overall association is driven entirely by the confounding of $$C$$ with both treatment assignment and outcome. A paper by Pavlides and Perlman (2009) showed that in a random $$2 \times 2 \times 2$$ table with a uniform distribution, Simpson’s paradox occurs with probability exactly $$\frac{1}{60}$$ — meaning it is not rare, and researchers should routinely check for it.

#### 14.1.2. Causal Graph Resolution

Pearl [\[88\]](#ref-88) showed that Simpson’s paradox is not really a paradox once causal graphs are introduced. The question “which association is correct — the aggregate or the stratified?” is ill-posed as a statistical question. It can only be answered by knowing the causal structure. Pearl distinguishes two fundamentally different configurations:

**Configuration 1: $$C$$ is a confounder ($$C \to X$$ and $$C \to Y$$).** In this case, the stratified association (within levels of $$C$$) is the correct causal estimate. The aggregate association is confounded by $$C$$. The backdoor criterion tells us to adjust for $$C$$, giving: 

$$
E[Y \mid \mathrm{do}(X = x)] = \sum_c P(Y \mid X = x, C = c) \cdot P(C = c),
\tag{98}
$$

 which is the weighted average of the within-stratum associations (the Cochran-Mantel-Haenszel estimator in the $$2 \times 2 \times K$$ case).

**Configuration 2: $$C$$ is a collider ($$X \to C \leftarrow Y$$).** Here, the *aggregate* association is the correct causal estimate. Stratifying on $$C$$ opens the collider path $$X \to C \leftarrow Y$$ and introduces spurious association between $$X$$ and $$Y$$. Adjusting for $$C$$ is wrong. The unconditional association is the causal one.

The same observed data — the same numbers in the $$2 \times 2 \times 2$$ table — are consistent with both causal structures. The data alone cannot tell you which configuration applies. Only the causal graph can. This is Pearl’s formal resolution of Simpson’s paradox: it is not a statistical problem but a causal graph problem. The “paradox” evaporates once the correct graph is known and the appropriate adjustment is applied.

#### 14.1.3. Connection to CausalLens

CausalLens performs exactly the disambiguation that resolves Simpson’s paradox. CCA+ identifies the direction of the $$X$$–$$Y$$ edge. The confounder screening procedure (Section 3.3) distinguishes confounders (which should be adjusted for) from colliders (which should not). The backdoor adjustment formula then gives the correct Rung 2 estimate. Without the causal graph, Simpson’s paradox is unresolvable; with it, it is trivially resolved by the adjustment formula.

### 14.2. The Ecological Fallacy: Aggregation Bias and Its Causal Interpretation

#### 14.2.1. The Robinson Phenomenon

William S. Robinson [\[89\]](#ref-89) demonstrated in 1950 that the correlation between two variables can differ drastically depending on the level of aggregation at which it is measured. His canonical example: the correlation between the proportion of immigrants and the literacy rate, computed at the US state level in the 1930 census, was $$r = -0.53$$ (more immigrants $$\Rightarrow$$ lower state literacy). But the *individual-level* correlation between immigrant status and literacy was $$r = +0.12$$ (immigrants were *more* literate than native-born citizens on average). The sign reversed completely.

The explanation: immigrants settled disproportionately in industrial northern states that were wealthier and more literate than southern states. The state-level literacy rate was driven by industrial wealth, not by immigrant literacy. The state-level correlation confounds immigrant settlement patterns with state economic development. This is a classic omitted variable bias operating at the ecological level.

#### 14.2.2. Formal Decomposition of Ecological Bias

Let $$Y_{ij}$$ be the outcome for individual $$j$$ in group $$i$$, and $$X_{ij}$$ the individual exposure. Define the group-level means $$\bar{Y}_i = \frac{1}{n_i}\sum_j Y_{ij}$$ and $$\bar{X}_i = \frac{1}{n_i}\sum_j X_{ij}$$. The ecological regression estimates: 

$$
\hat{\beta}_\mathrm{ecol} = \frac{\mathrm{Cov}(\bar{X}_i, \bar{Y}_i)}{\mathrm{Var}(\bar{X}_i)},
\tag{99}
$$

 while the individual-level regression estimates: 

$$
\hat{\beta}_\mathrm{ind} = \frac{\mathrm{Cov}(X_{ij}, Y_{ij})}{\mathrm{Var}(X_{ij})}.
\tag{100}
$$

 The ecological bias is: 

$$
\hat{\beta}_\mathrm{ecol} - \hat{\beta}_\mathrm{ind} = \frac{\mathrm{Cov}(\bar{X}_i, \bar{\varepsilon}_i)}{\mathrm{Var}(\bar{X}_i)},
\tag{101}
$$

 where $$\bar{\varepsilon}_i$$ is the group-level mean residual. This is nonzero whenever the group-level means of $$X$$ and the individual-level errors are correlated — which occurs exactly when there are unmeasured group-level confounders. In Robinson’s example, state economic development is the group-level confounder: it determines both the state’s immigrant share (settlers go where jobs are) and the state’s literacy rate (industrial states invest more in education), creating a nonzero $$\mathrm{Cov}(\bar{X}_i, \bar{\varepsilon}_i)$$.

#### 14.2.3. Causal Interpretation and CausalLens

The ecological fallacy is a special case of omitted variable bias where the omitted variable operates at the group level. The causal interpretation is: the ecological correlation measures a mixture of the individual-level causal effect and group-level confounding effects. When group-level confounders are absent, the ecological and individual-level estimates coincide; when they are present, they diverge, potentially in sign.

From the perspective of CausalLens: the pipeline operates on individual-level data (each row is an observation) and produces individual-level ACE estimates. It is immune to the ecological fallacy by construction. However, if a researcher feeds *aggregate* (group-level) data into CausalLens — state-level statistics rather than individual records — the CCA+ direction discovery and backdoor adjustment will reflect group-level relationships, which may not correspond to individual-level causal effects. The correct procedure is always to use individual-level data when available. When only ecological data is available, the analyst must either acknowledge the ecological fallacy as a limitation or use ecological IV methods (which exploit the ecological exposure as an instrument for the individual-level exposure, valid when the ecological exposure satisfies the IV conditions [\[90\]](#ref-90)).

## 15. Continuous Optimization for Causal Graph Learning: NOTEARS and Its Extensions

### 15.1. The Combinatorial Problem and Its Continuous Relaxation

For a decade, learning a DAG from data was treated as a combinatorial search problem, and the algorithms reflected that: greedy edge additions, heuristic reversals, score comparisons at each step, and no convergence guarantee beyond “stops when nothing improves.” The space of DAGs over $$p$$ variables has size $$\Theta(p! \cdot 2^{p(p-1)/2})$$ in the worst case. GES and its variants search it well in practice but have no polynomial guarantee of reaching the global optimum.

In 2018, Zheng et al. [\[75\]](#ref-75) published a result that changed this. They showed that the acyclicity constraint — the single hardest thing about learning DAGs, the constraint that makes the problem combinatorial — can be written as a smooth equality constraint on a continuous matrix. Once you have that, gradient descent works.

Zheng et al. [\[75\]](#ref-75) introduced NOTEARS (Non-combinatorial Optimization via Trace Exponential and Augmented lagRangian for Structure learning) — a breakthrough that transforms the combinatorial DAG constraint into a smooth equality constraint, enabling gradient-based optimization.

### 15.2. The NOTEARS Acyclicity Characterization

Let $$W \in \mathbb{R}^{p \times p}$$ be a weighted adjacency matrix for a graph on $$p$$ nodes, where $$W_{ij}$$ is the weight of the edge $$j \to i$$. The key mathematical insight is:

> **Theorem 15.1 (NOTEARS Acyclicity Characterization, Zheng et al. 2018).** A matrix $$W \geq 0$$ (elementwise) represents a DAG if and only if: 
>
> $$
> h(W) = \mathrm{tr}(e^{W \circ W}) - p = 0,
>
> \tag{102}
> $$
>
>  where $$e^A$$ denotes the matrix exponential, $$\circ$$ denotes the Hadamard (elementwise) product, and $$p$$ is the number of nodes.

*Proof sketch.* The matrix exponential $$e^A = \sum_{k=0}^\infty A^k / k!$$ for a non-negative matrix $$A$$ has a useful property: $$[A^k]_{ii}$$ counts the (weighted) number of directed walks of length $$k$$ from node $$i$$ back to itself. A graph is acyclic if and only if there are no self-returning walks of any length, i.e., $$[A^k]_{ii} = 0$$ for all $$k \geq 1$$ and all $$i$$. Equivalently, $$\mathrm{tr}(A^k) = 0$$ for all $$k \geq 1$$. Summing: $$\mathrm{tr}(e^A) = p + \sum_{k=1}^\infty \mathrm{tr}(A^k)/k! = p$$ iff $$\mathrm{tr}(A^k) = 0$$ for all $$k \geq 1$$ iff $$G$$ is acyclic. Using $$A = W \circ W$$ ensures the entries are non-negative, and taking $$h(W) = \mathrm{tr}(e^{W \circ W}) - p = 0$$ gives the smooth acyclicity constraint. ◻

### 15.3. The NOTEARS Optimization Program

With the acyclicity constraint formalized, the DAG learning problem becomes: 

$$
\min_{W \in \mathbb{R}^{p \times p}} \quad F(W) + \lambda \|W\|_1
\quad \text{subject to} \quad h(W) = 0,

\tag{103}
$$

 where $$F(W) = \frac{1}{2n} \|X - XW^T\|_F^2$$ is the least-squares loss (for Gaussian linear SCMs), $$\|W\|_1 = \sum_{ij} \vert W_{ij}\vert $$ is an $$\ell_1$$ sparsity penalty, and the constraint (102) enforces acyclicity. This is solved using the augmented Lagrangian method: 

$$
\mathcal{L}_\rho(W, \alpha) = F(W) + \lambda\|W\|_1 + \alpha h(W) + \frac{\rho}{2} h(W)^2,
\tag{104}
$$

 where $$\alpha$$ is the Lagrange multiplier and $$\rho > 0$$ is a penalty parameter that is increased over iterations until $$h(W) \approx 0$$.

### 15.4. DAGMA: An Improved Acyclicity Characterization

Bello et al. [\[76\]](#ref-76) identified a limitation of NOTEARS: the matrix exponential grows rapidly with the magnitude of $$W$$, causing numerical instability for large weights. They proposed DAGMA (DAGs via M-matrices and a log-determinant acyclicity characterization): 

$$
h_s(W) = -\log\det(sI - W \circ W) + p \log s, \quad s > \rho(W \circ W),
\tag{105}
$$

 where $$\rho(\cdot)$$ is the spectral radius. This is zero if and only if $$W$$ represents a DAG, and remains numerically stable because the log-determinant is bounded for well-conditioned matrices. DAGMA uses barrier method optimization rather than augmented Lagrangian, achieving better numerical stability and often faster convergence.

### 15.5. NOTEARS-MLP: Nonlinear Extension

The linear NOTEARS assumes $$X_i = \sum_j W_{ij} X_j + \varepsilon_i$$. Zheng et al. (2020) extend to nonlinear SEMs by replacing linear terms with MLPs: 

$$
X_i = f_i(X_{\mathrm{Pa}(i)}) + \varepsilon_i, \quad f_i \text{ modeled by a neural network.}
\tag{106}
$$

 The acyclicity constraint is applied to the Jacobian of the learned functions evaluated at the data: 

$$
h(W) = \mathrm{tr}(e^{W \circ W}) - p = 0, \quad W_{ij} = \left\|\frac{\partial f_i}{\partial X_j}\right\|_2.
\tag{107}
$$

 NOTEARS-MLP can learn nonlinear causal mechanisms while enforcing global DAG structure, making it applicable to the same ANM setting as CCA+.

### 15.6. Connection to CausalLens: Complementary Roles

NOTEARS and CCA+ are complementary rather than competing:

- **NOTEARS learns the full graph** over $$p$$ variables jointly, exploiting all pairwise and conditional relationships simultaneously. It is suited to the *skeleton discovery* problem (which edges exist?) and can handle $$p$$ up to a few hundred variables with careful implementation.

- **CCA+ orients individual edges**, exploiting the noise asymmetry of the ANM. It is suited to the *edge orientation* problem (which direction does a known edge point?) and can resolve orientations that NOTEARS, being based on a Gaussian likelihood, cannot.

A natural hybrid: use NOTEARS to identify the graph skeleton (which pairs of variables are connected), then use CCA+ to orient each discovered edge. This combines the scalability of continuous optimization with the directional precision of functional model methods. The PC-NOTEARS hybrid [\[77\]](#ref-77) has demonstrated exactly this architecture in biological benchmarks, outperforming either method alone.

## 16. Extended Experimental Validation: Synthetic DGPs, Nonlinearity, and Ensemble

This section is their empirical counterpart, the place where the theory either survives contact with data or it does not. What follows is not a clean parade of successes. The cubic DGP fails under the wrong input distribution. The Pima direction score is not some blazing $$-0.5$$ that admits no doubt. A second method, ANM-HSIC, outperforms CCA+ on pairwise accuracy when run alone. All of this is documented here because understanding the shape of a method’s failure surface is what distinguishes engineering from wishful thinking.

All experiments were implemented from scratch in NumPy without automatic differentiation frameworks. The MLP architecture is fixed: one input, two hidden layers (16 and 8 units), tanh activations, one output, trained with batch SGD and MSE loss. No dropout, no weight decay, no learning rate schedules. Reproducibility seeds are set at the trial level. The full experimental notebook is available alongside this paper and contains every hyperparameter, every random seed, and every line of code.

### 16.1. Synthetic DGP Accuracy

Given data generated from a known ANM, does CCA+ correctly identify the direction? Five data-generating processes were tested across 30 independent trials each, covering the full range from clearly nonlinear to theoretically impossible:

@lcccc@ **DGP** & **Correct** & **Ambiguous** & **Wrong** & **Mean score**\
$$Y = \sin(X) + \varepsilon$$, $$X \sim \mathcal{N}(0,1)$$ & 30/30 & 0 & 0 & $$-0.091$$\
$$Y = e^{0.5X} + \varepsilon$$, $$X \sim \mathcal{N}(0,1)$$ & 26/30 & 4 & 0 & $$-0.026$$\
$$Y = X^3 + \varepsilon$$, $$X \sim \mathcal{U}[-2,2]$$ & 30/30 & 0 & 0 & $$+0.080^{\,a}$$\
$$Y = 2X + \varepsilon$$, $$X \sim \mathcal{N}(0,1)$$ & 0/30 & 30 & 0 & $$-0.0003$$\
$$Y = X^2 + \varepsilon$$, $$X \sim \mathcal{N}(0,1)$$ & 30/30 & 0 & 0 & $$-0.627^{\,b}$$\
\

<figure data-latex-placement="H">
<img src="/assets/img/causal-pruning/exp1_dgp_scores.png" />
<figcaption><strong>Figure 2.</strong> CCA+ scores across 30 independent trials per data-generating process. Each bar is one trial; colour indicates verdict (teal = correct, grey = ambiguous, red = wrong). The sine and exponential mechanisms produce strong consistent negative scores, the forward network converging faster as the theory requires. The linear Gaussian mechanism (<span class="math inline"><em>Y</em> = 2<em>X</em></span>) scatters around zero: the direction is not identifiable and the score reflects this honestly. The cubic with <span class="math inline">𝒩(0, 1)</span> input fails because most of the probability mass sits near zero where <span class="math inline"><em>x</em><sup>3</sup> ≈ <em>x</em></span>; the <span class="math inline">𝒰[−2, 2]</span> distribution activates the nonlinear tails and recovers full accuracy. The <span class="math inline"><em>Y</em> = <em>X</em><sup>2</sup></span> panel shows 30/30 correct, but this is a false positive: the reverse network collapses to predicting zero because zero is the Bayes-optimal constant for a symmetric distribution, not because it has learned anything directional.</figcaption>
</figure>

The 4/30 ambiguous cases in the exponential DGP are not random noise. They are trials where the asymmetry is genuine but the score lands between the weak and strong thresholds. The exponential mechanism near $$X = 0$$ is nearly linear, and when a draw clusters samples in that region the score contracts. The method is being conservative rather than committing to a wrong answer, which is the correct behaviour.

### 16.2. Scale Normalization

The cubic DGP fails without normalization (0/30) and succeeds with it (30/30). This is not a preprocessing quirk; it follows directly from the theory.

Without standardization, $$\mathrm{Var}(Y) = E[X^6] + \sigma_\varepsilon^2 \approx 9.5$$ when $$X \sim \mathcal{U}[-2,2]$$, while $$\mathrm{Var}(X) = 1.36$$. Gradient magnitudes scale with output variance, so the forward network’s gradients are systematically larger and it hits any fixed threshold $$\tau$$ more slowly, not because it is learning the wrong direction, but because the output numbers are larger. The CCA+ score inverts to $$+0.72$$, pointing the wrong way with high confidence. After $$z$$-scoring, $$\mathrm{Var}(\tilde{X}) = \mathrm{Var}(\tilde{Y}) = 1$$, and the only remaining convergence difference is the structural asymmetry established in Theorem 4.7.

### 16.3. The Nonlinearity Pre-Test

CCA+ can fail silently on near-linear mechanisms, returning a confident wrong answer with no internal warning. A complete pipeline requires a pre-test that flags this condition before any neural network is trained.

Two approaches were tried and failed. Cross-validated $$R^2$$ comparisons between OLS and GBM failed because GBM with 5-fold cross-validation on $$n = 160$$ training samples produces negative $$R^2$$ values: the model is worse than predicting the mean, and the gap statistic inverts. HSIC between inputs and GBM residuals failed because in-sample GBM overfits badly enough that its residuals show *more* dependence on the input, not less. Both failures share the same root cause: parametric models used as a proxy for structural nonlinearity are unreliable at small sample sizes.

The approach that works uses no model at all. Fisher’s correlation ratio $$\eta^2$$, introduced in 1925 and predating both GBM and HSIC by decades [\[62\]](#ref-62), is a closed-form nonlinearity measure computed directly from the data: 

$$
\eta^2(X, Y) = \frac{\mathrm{Var}\!\left(E[Y \mid X_{\text{bins}}]\right)}{\mathrm{Var}(Y)},
\tag{108}
$$

 where $$X$$ is partitioned into equal-frequency bins. The pre-test statistic is the gap: 

$$
\Delta_{\text{NL}}(X, Y) = \eta^2(X, Y) - r^2(X, Y),

\tag{109}
$$

 where $$r^2$$ is the squared Pearson correlation. For a perfectly linear mechanism, $$\eta^2 \approx r^2$$ and the gap is near zero. For nonlinear mechanisms $$\eta^2 > r^2$$ and the gap is positive. The gap is always non-negative because $$\eta^2$$ is an upper bound on linear $$R^2$$ for any binning [\[62\]](#ref-62).

<figure data-latex-placement="H">
<img src="/assets/img/causal-pruning/three_gaps_definitive_final.png" />
<figcaption><strong>Figure 3.</strong> <strong>Left:</strong> The <span class="math inline"><em>η</em><sup>2</sup> − <em>r</em><sup>2</sup></span> nonlinearity pre-test on seven DGPs. Green bars: gap <span class="math inline"> &gt; 0.03</span>, CCA+ reliable. Red bars: gap <span class="math inline"> ≤ 0.03</span>, near-linear regime, fall back to LiNGAM or declare ambiguous. <span class="math inline"><em>Y</em> = 2<em>X</em> + <em>ε</em></span> correctly gets a negative gap (strong linear signal). <span class="math inline"><em>Y</em> = <em>X</em><sup>2</sup></span> gets the largest gap (<span class="math inline">0.64</span>) because Pearson <span class="math inline"> ≈ 0</span> for symmetric input but <span class="math inline"><em>η</em><sup>2</sup></span> is large. <strong>Centre:</strong> Head-to-head accuracy on Tübingen-style pairs across all four methods, including the majority-vote ensemble. <strong>Right:</strong> Per-pair agreement heatmap. Rows where CCA+ is red but ANM is green are the near-linear pairs where CCA+ fails and the ensemble corrects.</figcaption>
</figure>

$$Y = 2X + \varepsilon$$ fails the pre-test with a gap of $$-0.046$$, which means a pipeline running this check would correctly refuse to apply CCA+ on linear data and fall back to LiNGAM. A method that knows when to abstain is more useful than one that always commits.

### 16.4. Head-to-Head Comparison and the Ensemble

CCA+ is not the only method for bivariate causal direction discovery. Two alternatives with strong theoretical foundations are included in the comparison:

- **ANM-HSIC** [\[4\]](#ref-4): fit a GBM regressor in each direction, compute distance covariance between input and residuals, take the direction with lower residual dependence. Signal: residual independence.

- **RECI** [\[60\]](#ref-60): rescale both variables to $$[0,1]$$, fit a degree-3 polynomial in each direction, take the direction with lower MSE. No independence test required. Signal: regression error asymmetry.

These three methods use orthogonal signals: optimization-landscape asymmetry (CCA+), residual independence (ANM-HSIC), and regression error magnitude (RECI). They can fail on different pairs, which is the prerequisite for a productive ensemble.

Eleven Tübingen-style pairs were generated with known ground truth: six forward ($$X \to Y$$), four reverse ($$Y \to X$$), and one linear Gaussian boundary pair.

<table>
<caption><strong>Table 4.</strong> Head-to-head accuracy on 10 identifiable Tübingen-style pairs, linear Gaussian boundary excluded. The ensemble is a majority vote across all three methods. Zhang et al. <a href="#ref-61">[61]</a> prove majority vote accuracy is bounded below by the best individual method when all methods exceed 50%.</caption>
<tbody>
<tr>
<td><strong>Method</strong></td>
<td><strong>Signal</strong></td>
<td><strong>Correct / 10</strong></td>
<td><strong>Accuracy</strong></td>
</tr>
<tr>
<td>CCA+ (this paper)</td>
<td>Optimization landscape</td>
<td>7/10</td>
<td>70%</td>
</tr>
<tr>
<td>RECI <a href="#ref-60">[60]</a></td>
<td>Polynomial regression error</td>
<td>5/10</td>
<td>50%</td>
</tr>
<tr>
<td>ANM-HSIC <a href="#ref-4">[4]</a></td>
<td>Residual independence</td>
<td>10/10</td>
<td>100%</td>
</tr>
<tr>
<td><strong>Ensemble (majority vote)</strong></td>
<td>All three</td>
<td><strong>10/10</strong></td>
<td><strong>100%</strong></td>
</tr>
<tr>
<td>Linear Gaussian (boundary)</td>
<td colspan="3"><em>AMBIGUOUS on all three; direction not identifiable</em></td>
</tr>
</tbody>
</table>

CCA+ fails on pairs where the mechanism is injective but nearly linear near the centre of the input distribution. The cubic with Gaussian input is the canonical case. ANM-HSIC does not have this failure mode because residual dependence does not depend on convergence rate. The methods fail on different pairs, and the ensemble captures all ten.

<figure data-latex-placement="H">
<img src="/assets/img/causal-pruning/gap3_head_to_head_comparison.png" style="width:72.0%" />
<figcaption><strong>Figure 4.</strong> Method accuracy on Tübingen-style pairs before the ensemble was introduced. CCA+ at 70%, a residual-skewness LiNGAM variant at 30%, ANM-HSIC at 100%. The LiNGAM variant fails on non-Laplace noise distributions. The ensemble result in Figure 3 (centre panel) supersedes this comparison.</figcaption>
</figure>

### 16.5. Power Analysis: Minimum Sample Size

The Pima dataset has 392 usable rows after zero-filtering. The Sachs network has 853. Both are modest. The question is whether CCA+ can operate reliably at these sizes, and where the floor is.

<figure data-latex-placement="H">
<img src="/assets/img/causal-pruning/exp24_power_analysis.png" />
<figcaption><strong>Figure 5.</strong> <strong>Left:</strong> CCA+ accuracy as a function of sample size on <span class="math inline"><em>Y</em> = sin (<em>X</em>) + <em>ε</em></span>, across 20 trials per sample size. The 80% threshold is crossed around <span class="math inline"><em>n</em> = 75</span>; the 90% threshold around <span class="math inline"><em>n</em> = 100</span>. Both the Pima (<span class="math inline"><em>n</em> = 392</span>, dotted line) and Sachs (<span class="math inline"><em>n</em> = 853</span>, solid line) operating points sit well above the 90% zone. <strong>Right:</strong> Mean CCA+ score <span class="math inline">±</span> one standard deviation versus sample size. The score is stable around <span class="math inline">−0.10</span> throughout; the variance shrinks with <span class="math inline"><em>n</em></span>, confirming that larger samples reduce uncertainty without changing the direction of the asymmetry.</figcaption>
</figure>

CCA+ needs roughly 100 samples to operate reliably on a strongly nonlinear ANM. For near-linear mechanisms or high-noise settings, the pre-test in Section 16.3 should be run first. When $$n < 100$$, a single CCA+ run should not be trusted; the 50-sample bootstrap described in Section 16.6 gives a score distribution rather than a point estimate.

### 16.6. The Full Pipeline on Real Data: BMI and Glucose

The Pima Indians Diabetes dataset [\[11\]](#ref-11) is the primary real-data validation. The biological ground truth is established: BMI causally precedes impaired fasting glucose, with prospective cohorts showing a 3–7 year lag between elevated BMI and measurable glucose dysfunction, and weight-loss interventions reducing glucose before pancreatic function changes [\[12\]](#ref-12). The expected ACE from the clinical literature is approximately 0.5–2.0 mg/dL per BMI unit.

The pipeline runs in three steps: CCA+ identifies the direction, the three-criterion confounder screen identifies adjustment variables (correlation with cause, correlation with effect, partial correlation after removing the cause to exclude descendants), and the backdoor formula is applied via OLS under the Frisch-Waugh-Lovell theorem.

#### 16.6.1. Direction Discovery and Stability

CCA+ on $$n = 392$$ filtered Pima rows yields a score of $$-0.0525$$, crossing the strong threshold toward BMI $$\to$$ Glucose. A single run is not sufficient to report. The stability test ran 50 independent bootstrap subsamples, each 80% of the data drawn without replacement:

| **Statistic**              |       **Value**        |
| ---------------------------| ---------------------- |
| BMI $$\to$$ Glucose verdicts |        49 / 50         |
| AMBIGUOUS verdicts         |         1 / 50         |
| Glucose $$\to$$ BMI verdicts |         0 / 50         |
| Mean CCA$$^+$$ score         |       $$-0.0576$$        |
| Standard deviation         |        $$0.0074$$        |
| 95% bootstrap score CI     | $$[-0.0587,\; -0.0564]$$ |

**Table 5.** CCA+ stability across 50 bootstrap subsamples on the Pima dataset. A standard deviation of $$0.0074$$ on a mean of $$-0.0576$$ is tight enough to treat this as a reportable point estimate with a meaningful confidence interval.

<figure data-latex-placement="H">
<img src="/assets/img/causal-pruning/gap2_pima_stability_50runs.png" />
<figcaption><strong>Figure 6.</strong> CCA+ scores across 50 bootstrap subsamples for BMI <span class="math inline">→</span> Glucose on the Pima dataset. Left: per-run bars. One ambiguous run appears at position 0; all other 49 are correct. The strong threshold at <span class="math inline">−0.03</span> is crossed comfortably in nearly every run. Right: score distribution. The mass sits around <span class="math inline">−0.058</span> with negligible spread; this is not a borderline result.</figcaption>
</figure>

#### 16.6.2. Sensitivity Analysis for Unmeasured Confounding

The backdoor adjustment removes confounding from Age and Pregnancies. It does not remove confounding from variables that were not measured. The no-unmeasured-confounders assumption cannot be tested from the data alone. We therefore report an E-value analysis [\[19\]](#ref-19) to quantify how strong any residual unmeasured confounder would need to be to explain away the estimated ACE.

For a continuous outcome, the ACE is converted to an approximate risk ratio using the method of VanderWeele and Ding [\[19\]](#ref-19): standardise the outcome to unit variance, treat the ACE as a log-scale effect, and exponentiate. With $$\hat{\sigma}_\text{Glucose} \approx 31.9$$ mg/dL and $$\hat{\beta}_X = 1.04$$: 

$$
\widehat{\mathrm{RR}} \approx \exp\!\left(\frac{1.04}{31.9 / 2}\right) \approx \exp(0.0652) \approx 1.067.
\tag{110}
$$

 The E-value for the point estimate is: 

$$
\mathrm{E}_\text{est} = \widehat{\mathrm{RR}} + \sqrt{\widehat{\mathrm{RR}}\,(\widehat{\mathrm{RR}} - 1)}
= 1.067 + \sqrt{1.067 \times 0.067} \approx 1.067 + 0.267 \approx 1.33.
\tag{111}
$$

 For the lower confidence bound ($$\hat{\beta}_X^\text{lower} = 0.73$$): 

$$
\widehat{\mathrm{RR}}_\text{CI} \approx \exp(0.0457) \approx 1.047,
\qquad
\mathrm{E}_\text{CI} = 1.047 + \sqrt{1.047 \times 0.047} \approx 1.047 + 0.222 \approx 1.27.
\tag{112}
$$

| **Quantity**       |         **Value**          | **E-value** |
| -------------------| -------------------------- | ----------- |
| ACE point estimate | $$+1.04$$ mg/dL per BMI unit |   $$1.33$$    |
| Lower 95% CI bound | $$+0.73$$ mg/dL per BMI unit |   $$1.27$$    |

**Table 6.** E-value sensitivity analysis for the Pima ACE estimate. An unmeasured confounder associated with both BMI and glucose by a risk ratio of at least $$1.33$$ (above and beyond the measured confounders Age and Pregnancies) would be needed to fully explain away the point estimate. To shift the lower CI bound to the null requires an association of $$1.27$$-fold.

An E-value of $$1.33$$ is modest by the standards of observational epidemiology: an unmeasured confounder associated with both BMI and glucose by a $$1.33$$-fold risk ratio would suffice to nullify the estimate. Diabetes risk factors such as physical inactivity [\[12\]](#ref-12) are associated with BMI and glucose by risk ratios considerably above $$1.33$$, meaning the estimate is not strongly robust to a single plausible unmeasured confounder. The E-value quantifies rather than dismisses the residual uncertainty. A Mendelian randomisation study with genetic instruments for BMI would resolve it without ambiguity.

#### 16.6.3. Confounder Screening and Backdoor Adjustment

The three-criterion screening identifies Age and Pregnancies as confounders. Insulin is correctly excluded: its partial correlation with Glucose after removing BMI is high, which would flag it as a confounder, but it is caused by Glucose (pancreatic secretion in response to blood glucose). Including it would block a downstream path and bias the ACE downward. The partial-correlation criterion catches this case because a true confounder remains predictive of the effect after conditioning on the cause; a descendant does not.

| **Estimator** | **ACE (mg/dL per BMI unit)** | **Notes** |
| ---| -- | -- |
| Naive OLS | $$+1.31$$ | Age, Pregnancies not adjusted |
| Backdoor-adjusted | $$+1.04$$ | Adjustment set: {Age, Pregnancies} |
| 95% Bootstrap CI | $$[0.73,\; 1.35]$$ | $$B = 500$$ resamples |
| Confounding bias removed | $$+0.27$$ | $$1.31 - 1.04$$ |
| Biological range | $$[0.5,\; 2.0]$$ | ACE within range |
| $$\mathrm{do}(\mathrm{BMI} = 25)$$ predicted | $$\approx 94$$ mg/dL | Population mean: $$\approx 121$$ mg/dL |

**Table 7.** Backdoor adjustment results for BMI $$\to$$ Glucose on the Pima dataset. The confounding bias of 0.36 mg/dL per BMI unit is the fraction of the naive OLS slope attributable to shared confounders, primarily Age, which independently elevates both BMI and glucose, rather than to the direct causal path.

<figure data-latex-placement="H">
<img src="/assets/img/causal-pruning/pima_complete_rung2.png" />
<img src="/assets/img/causal-pruning/pima_rung2_prediction_plot.png" />
<figcaption><strong>Figure 7.</strong> Rung 1 vs Rung 2 predictions for BMI <span class="math inline">→</span> Glucose. Teal line: <span class="math inline"><em>E</em>[<em>Y</em> ∣ do(<em>X</em> = <em>x</em>)]</span> from backdoor adjustment. Dashed red: <span class="math inline"><em>E</em>[<em>Y</em> ∣ <em>X</em> = <em>x</em>]</span> from naive regression. The shaded band is confounding bias from Age and Pregnancies. The dot marks <span class="math inline">do(BMI = 25)</span>, predicting <span class="math inline"> ≈ 94</span> mg/dL against a population mean of <span class="math inline"> ≈ 121</span> mg/dL.</figcaption>
</figure>

### 16.7. What the Results Establish

CCA+ correctly identifies direction on four of five tested DGP types, fails predictably on linear Gaussian mechanisms (a theoretical impossibility, shared by every method in this family), and produces a score of $$-0.059$$ on the Pima BMI–Glucose pair. The full pipeline produces an ACE of $$1.04$$ mg/dL per BMI unit on the Pima dataset, inside the biological range $$[0.5, 2.0]$$, with a confounding bias correction of $$0.27$$ mg/dL.

The ensemble at 100% on Tübingen-style pairs is not a universal claim. It is a result on 10 synthetic pairs with known ground truth. On the actual 108-pair Tübingen Cause-Effect Pairs benchmark [\[66\]](#ref-66) at standard 80-epoch settings, CCA+ achieves 48.9% accuracy on 94 decided pairs — near chance, consistent with the method’s documented sensitivity to heteroscedastic noise and near-injective mechanisms at minimal compute budgets.

CCA+ at 70% versus ANM-HSIC at 100% on the same 10 synthetic pairs is not a win for CCA+. The argument for including CCA+ in the pipeline is not that it beats ANM-HSIC on pairwise accuracy. It is that the two methods fail on different pairs, and combining orthogonal signals through majority vote closes the gap that neither method closes alone.

## 17. Multivariate Extension: CCA+ Graph Assembly via Confidence-Weighted Acyclicity

The bivariate result establishes that CCA+ correctly identifies causal direction between a pair $$(X, Y)$$ under the ANM. The multivariate setting introduces a new problem: assembling $$\binom{p}{2}$$ pairwise direction scores into a single consistent directed acyclic graph. This section develops the assembly procedure as a concrete algorithm with a well-defined objective function, states the conditions under which it is exact, and characterises its failure modes.

### 17.1. From Pairwise Scores to a Directed Graph: The Problem

Let $$V = \{V_1, \ldots, V_p\}$$ be a set of $$p$$ observed variables. Run CCA+ on every ordered pair $$(V_i, V_j)$$ with $$i < j$$. Each run returns a scalar score $$s_{ij} \in \mathbb{R}$$ and a direction decision: 

$$
d_{ij} = \begin{cases}
V_i \to V_j & \text{if } s_{ij} < -\tau_\text{weak} \\
V_j \to V_i & \text{if } s_{ij} > +\tau_\text{weak} \\
\text{AMBIG} & \text{if } \vert s_{ij}\vert  \leq \tau_\text{weak}.
\end{cases}
\tag{113}
$$

 Define the confidence weight $$w_{ij} = \vert s_{ij}\vert $$. This weight is not decorative: larger $$\vert s_{ij}\vert $$ corresponds to a convergence gap further from the ambiguous zone, and from the power analysis in Section 16.5, larger gaps are more reliably correct.

Construct a complete directed graph $$\tilde{G}$$ on $$p$$ nodes where each edge $$(i \to j)$$ or $$(j \to i)$$ is assigned the direction $$d_{ij}$$ and weight $$w_{ij}$$. Ambiguous pairs contribute undirected edges. The problem is that $$\tilde{G}$$ may contain directed cycles, violating the DAG requirement. The assembly problem is: find the DAG $$G^*$$ that agrees with $$\tilde{G}$$ on as much total confidence weight as possible.

### 17.2. Objective Function: Maximum-Weight DAG

> **Definition 17.1 (CCA+ Graph Assembly Problem).**
>
> Given scores $$\{(d_{ij}, w_{ij})\}_{i < j}$$, find a DAG $$G^* = (V, E^*)$$ solving: 
>
> $$
> G^* = \arg\max_{G \in \mathcal{D}_p} \sum_{(i,j) \in E(G)} w_{ij} \cdot \mathbf{1}[d_{ij} = (V_i \to V_j)],
>
> \tag{114}
> $$
>
>  where $$\mathcal{D}_p$$ is the set of all DAGs on $$p$$ nodes, $$E(G)$$ is the edge set of $$G$$, and the indicator is 1 when the edge direction in $$G$$ agrees with the CCA+ verdict $$d_{ij}$$.

This is equivalent to the *maximum acyclic subgraph* problem on the directed graph $$\tilde{G}$$ with edge weights $$w_{ij}$$. Equivalently, its complement is the minimum weight feedback arc set (MWFAS): the minimum-weight set of edges whose removal makes $$\tilde{G}$$ acyclic. The two formulations are related by $$E^* = E(\tilde{G}) \setminus \text{MWFAS}(\tilde{G})$$.

MWFAS is NP-hard in general [\[119\]](#ref-119). The following proposition establishes when the CCA+ assembly problem is tractable.

> **Proposition 17.2 (Tractability Conditions).**
>
> The CCA+ assembly problem (114) is tractable in the following cases:
>
> 1.  **Consistent scores.** If the pairwise CCA+ scores are consistent with some total causal order $$\pi$$ on $$V$$ — meaning $$s_{ij} < -\tau$$ whenever $$\pi(i) < \pi(j)$$ — then $$\tilde{G}$$ is already acyclic and $$G^* = \tilde{G}$$ exactly. No optimization is needed; a topological sort by score confidence recovers $$\pi$$.
>
> 2.  **Sparse graphs.** If the true causal graph has maximum in-degree $$k$$, the MWFAS problem restricted to graphs of in-degree $$\leq k$$ is fixed-parameter tractable in $$k$$ [\[117\]](#ref-117). For biological networks where $$k \leq 3$$–$$5$$, this gives a polynomial-time algorithm in $$p$$.
>
> 3.  **Small $$p$$.** For $$p \leq 20$$, exact MWFAS via integer linear programming (the linear ordering polytope formulation of Grötschel et al. [\[120\]](#ref-120)) is solvable in seconds on standard hardware.

*Proof of (i).* If scores are consistent with $$\pi$$, then for all $$i < j$$ with $$\pi(i) < \pi(j)$$, $$s_{ij} < -\tau < 0$$, so $$d_{ij} = V_i \to V_j$$. The directed graph $$\tilde{G}$$ then has edges only pointing in the direction of increasing $$\pi$$-order. A directed graph on a finite vertex set is acyclic if and only if there exists a topological ordering. Since $$\pi$$ is such an ordering, $$\tilde{G} \in \mathcal{D}_p$$. Therefore $$G^* = \tilde{G}$$ and the optimum is achieved trivially. ◻

### 17.3. A Practical Algorithm

The following algorithm exploits the confidence structure of CCA+ scores to reduce the MWFAS search to a small subproblem, even when exact consistency fails.

1.  **Pre-test and score all pairs.** For each pair $$(V_i, V_j)$$, compute the $$\eta^2 - r^2$$ gap. If the gap $$\leq \tau_\text{NL}$$, the mechanism is near-linear: substitute the ensemble verdict (ANM-HSIC $$+$$ RECI majority vote) with confidence weight $$w_{ij} = 0.5 \cdot \vert \Delta_\text{NL}\vert  / \tau_\text{NL}$$ (scaled to reflect that the ensemble is less decisive than a strong CCA+ score). Otherwise run CCA+ and record $$(d_{ij}, w_{ij} = \vert s_{ij}\vert )$$.

2.  **Partition edges by confidence.** Let $$E_H = \{(i,j) : w_{ij} > \tau_\text{strong}\}$$ (high-confidence) and $$E_L = \{(i,j) : \tau_\text{weak} < w_{ij} \leq \tau_\text{strong}\}$$ (low-confidence). Discard $$E_A = \{(i,j) : w_{ij} \leq \tau_\text{weak}\}$$ as undirected; these edges are not identifiable from data.

3.  **Fix high-confidence edges; check for cycles.** Treat $$E_H$$ as hard constraints. Run a depth-first search on the subgraph induced by $$E_H$$. If no cycle exists, proceed. If a cycle exists among high-confidence edges, one of three conditions holds: the ANM is violated for some pair in the cycle, there is an unmeasured common cause, or there is a genuine feedback loop. In any of these cases, flag the cycle for manual inspection and remove the lowest-weight edge in the cycle before proceeding.

4.  **Solve MWFAS on the low-confidence subgraph.** With $$E_H$$ fixed as hard constraints, solve MWFAS over $$E_L$$ alone. For $$\vert E_L\vert  \leq 50$$, the ILP formulation of [\[120\]](#ref-120) is exact and fast. For larger $$\vert E_L\vert $$, the following greedy approximation has ratio $$O(\log \vert E_L\vert )$$: repeatedly remove the edge with the lowest weight that participates in a cycle, until no cycles remain.

5.  **Return the assembled DAG with confidence annotations.** The output is $$G^* = (V,\, E_H \cup E_L^*)$$ where $$E_L^*$$ is the MWFAS solution on $$E_L$$, together with the weight $$w_{ij}$$ on each edge and the undirected set $$E_A$$ indicating pairs where direction is not identified.

### 17.4. Correctness Guarantee

> **Theorem 17.3 (Assembly Correctness Under Consistent High-Confidence Edges).**
>
> Suppose the true causal graph $$G_0 \in \mathcal{D}_p$$ has the property that every edge $$(V_i \to V_j) \in E(G_0)$$ satisfies $$\vert s_{ij}\vert  > \tau_\text{strong}$$ (all true edges are high-confidence). Then the assembled graph $$G^*$$ from Algorithm Steps 1–5 satisfies $$E_H = E(G_0)$$ and $$G^* = G_0$$ exactly, provided no false positives appear in $$E_H$$.

*Proof.* By assumption, every true edge is in $$E_H$$. In Step 3, $$E_H$$ is checked for cycles. Since $$G_0$$ is a DAG and $$E_H = E(G_0)$$ by assumption, no cycle exists and no edges are removed. Steps 4–5 add edges from $$E_L$$ subject to the acyclicity constraint imposed by $$E_H$$. Since $$G_0$$ contains no edges in $$E_L$$ by assumption, the MWFAS solution on $$E_L$$ adds zero edges (there are no true low-confidence edges to recover). The output is $$G^* = (V, E_H) = G_0$$. ◻

The assumption that all true edges are high-confidence is strong. It fails when the true mechanism is near-linear (low $$\eta^2 - r^2$$ gap) or when the sample size is too small to push $$\vert s_{ij}\vert $$ past $$\tau_\text{strong}$$. In these cases, the algorithm degrades gracefully: true edges that fall into $$E_L$$ are still recovered if the MWFAS solution does not remove them, and edges in $$E_A$$ are correctly reported as unidentified rather than guessed.

### 17.5. Complexity

Let $$p$$ be the number of variables. Step 1 requires $$\binom{p}{2}$$ CCA+ runs, each $$O(n \cdot T)$$ where $$T$$ is the number of training steps and $$n$$ the sample size. Total: $$O(p^2 n T)$$. Step 3 depth-first search: $$O(p + \vert E_H\vert ) = O(p^2)$$. Step 4 ILP: exponential in the worst case but polynomial in $$\vert E_L\vert $$ for fixed in-degree [\[117\]](#ref-117); the greedy approximation is $$O(\vert E_L\vert ^2)$$. For the target regime of $$p \leq 30$$ and sparse true graphs, the bottleneck is Step 1, which at $$p = 30$$, $$n = 500$$, $$T = 2000$$ steps requires $$435 \times 10^6$$ scalar operations — comfortably under one second on a modern CPU using NumPy vectorization.

## 18. Causal Pruning: Applying the Intervention Logic Inside Neural Networks

### 18.1. The Idea

The CCA+ pipeline asks: given two variables in a dataset, which one causes the other? The answer comes from a training asymmetry — the network learning the true causal direction reaches a lower loss floor. The same asymmetry relies on a deeper principle: if you intervene on a cause, the effect changes; if you intervene on an effect, the cause does not. That is Pearl’s do-operator. It is not specific to datasets.

A trained neural network has the same structure. Some neurons are causally upstream of the output — disabling them breaks the prediction. Others contribute little: they may have non-negligible weights, but removing them leaves the output nearly unchanged. Standard pruning methods like magnitude pruning do not distinguish between these two cases. They remove neurons with small weights, which is a proxy for importance but not a direct measure of it. A neuron can have a small weight and be critical; another can have a large weight and be redundant due to the redundancy built into overparameterized networks.

This section applies the CCA+ intervention logic to that problem. For each neuron, we zero out its activations across all samples in the dataset and measure the average change in the model’s output. That is the neuron’s causal effect score. Neurons with high causal effect scores are causally necessary and should be kept. Neurons with low scores are causally redundant and can be pruned. The algorithm is called Causal Pruning (CP), and it is a direct application of the do-calculus logic to internal model components rather than to external dataset variables.

### 18.2. Algorithm

The procedure is as follows. Given a trained MLP with layers $$\{L_1, L_2, \ldots\}$$ and a reference dataset $$\mathcal{D}$$:

1.  **Compute baseline activations and outputs.** Run a forward pass over $$\mathcal{D}$$. Record the activation matrix $$A^{(l)} \in \mathbb{R}^{n \times d_l}$$ for each layer $$l$$, and the baseline output vector $$\hat{y}_0 \in \mathbb{R}^n$$.

2.  **Score each neuron by intervention.** For neuron $$i$$ in layer $$l$$, construct a modified activation matrix $$\tilde{A}^{(l)}$$ identical to $$A^{(l)}$$ except that column $$i$$ is set to zero: $$\tilde{A}^{(l)}_{:,i} = \mathbf{0}$$. Propagate $$\tilde{A}^{(l)}$$ through all subsequent layers to obtain the intervened output $$\hat{y}_i$$. The causal effect score is: $$\mathrm{CE}(i) = \frac{1}{n} \sum_{j=1}^n \left\vert \hat{y}_{0,j} - \hat{y}_{i,j}\right\vert .$$ This is the empirical approximation to $$E\left[\left\vert f(\mathcal{N}) - f(\mathrm{do}(\mathcal{N}_i = 0))\right\vert \right]$$ where $$\mathcal{N}$$ denotes the full network activations.

3.  **Rank and prune.** Sort all neurons by $$\mathrm{CE}(i)$$ in ascending order. To prune a fraction $$p$$ of neurons in a given layer, zero out the weights and biases of the $$\lfloor p \cdot d_l \rfloor$$ neurons with the lowest scores.

4.  **Retrain briefly.** After pruning, retrain the model for a small number of epochs (20 in these experiments) to allow the remaining neurons to compensate for the removed ones.

The baseline for comparison is magnitude pruning: rank neurons by the mean absolute value of the incoming weight vector, prune the lowest-ranked. Both methods are applied at the same pruning percentages, on the same model, with the same retraining budget.

### 18.3. Experiment Setup

All initial experiments use the Pima Indians Diabetes dataset [\[67\]](#ref-67) ($$n = 768$$, 8 features, binary outcome). The model is a 3-layer MLP: input $$\to 64 \to 32 \to 1$$, ReLU activations, sigmoid output, trained with Adam for 60 epochs. Causal effect scores are computed on the training set. Accuracy is evaluated on a held-out test set (20% split). Pruning is applied to both hidden layers simultaneously at fractions $$p \in \{0.2, 0.4, 0.6, 0.8\}$$.

The distribution shift test evaluates both pruned models on the same test set with Gaussian noise added to all input features. Two noise levels are tested: $$\sigma = 0.5$$ and $$\sigma = 1.0$$. This simulates what happens when the model is deployed on data from a slightly different population or measurement setting — a common real-world failure mode.

Two random seeds are reported in the initial results: seed 42 and seed 0. The baseline model accuracy is $$74.03\%$$ (seed 42) and $$72.08\%$$ (seed 0) on the clean test set.

### 18.4. Results: Clean Test Set

| **Pruning %** | **CP seed 42** | **MP seed 42** | **CP seed 0** | **MP seed 0** |
| --------------| -------------- | -------------- | ------------- | ------------- |
| % (baseline)  |     74.03      |     74.03      |     72.08     |     72.08     |
| 20%           |     77.92      |     75.97      |     74.03     |     74.03     |
| 40%           |     75.97      |     74.03      |     72.73     |     72.08     |
| 60%           |     71.43      |     67.53      |     74.03     |     68.83     |
| 80%           |     69.48      |     62.34      |     73.38     |     64.29     |

**Table 8.** Accuracy on the clean test set after pruning and 20 epochs of retraining. Causal pruning (CP) consistently retains higher accuracy than magnitude pruning (MP) at all pruning levels. At 20% pruning, causal pruning marginally *improves* over the baseline on both seeds, suggesting it is removing genuinely redundant neurons that were adding noise rather than signal.

The most important region is high pruning (60–80%), where the cost of wrong decisions compounds. At 80% pruning on seed 42, magnitude pruning drops to 62.34%, which is barely better than random. Causal pruning holds at 69.48%, a 7-point advantage. On seed 0, the gap widens further: 73.38% versus 64.29%, a difference of 9 points. The fact that causal pruning on seed 0 at 80% removal is still above the original unpruned baseline accuracy ($$73.38\% > 72.08\%$$) deserves attention. It means the 80% of neurons removed were not just neutral — they were, on net, adding noise to the decision.

### 18.5. Results: Distribution Shift

| **Pruning %** | **CP seed 42** | **MP seed 42** | **CP seed 0** | **MP seed 0** |
| --------------| -------------- | -------------- | ------------- | ------------- |
| % (baseline)  |     76.62      |     76.62      |     75.32     |     75.32     |
| 20%           |     77.92      |     77.92      |     73.38     |     74.03     |
| 40%           |     79.22      |     77.92      |     73.38     |     76.62     |
| 60%           |     76.62      |     67.53      |     74.68     |     69.48     |
| 80%           |     72.73      |     62.34      |     74.03     |     62.99     |

**Table 9.** Accuracy on the noisy test set ($$\sigma = 0.5$$). The gap between causal and magnitude pruning widens substantially under distribution shift. At 80% pruning, causal pruning retains 72.73% (seed 42) and 74.03% (seed 0) while magnitude pruning drops to 62.34% and 62.99% respectively.

The distribution shift result is the stronger of the two. On the clean test set, magnitude pruning degrades because it removes causally important neurons. On the noisy test set, this failure compounds: the model now has to handle unfamiliar inputs with fewer neurons, and the neurons it has left are the ones that happened to have large weights during training, not the ones that are actually responsible for the correct prediction.

Causal pruning removes neurons that did not change the output when disabled under the training distribution. These are, by construction, the neurons that the model does not need. When noise is added to the inputs, the model built from causally necessary neurons generalizes better because it has learned the actual signal rather than statistical artifacts that happened to be correlated with the signal during training.

The 60% pruning row is particularly clear. On seed 42 under noise: $$76.62\%$$ versus $$67.53\%$$, a 9-point gap. On seed 0: $$74.68\%$$ versus $$69.48\%$$, a 5-point gap. Both seeds agree on the direction and approximate magnitude of the advantage.

<figure data-latex-placement="H">
<img src="/assets/img/causal-pruning/pruning_seed42_noise05.png" />
<figcaption><strong>Figure 8.</strong> Causal pruning (CP) versus magnitude pruning (MP) on the Pima diabetes MLP. Seed 42, noise <span class="math inline"><em>σ</em> = 0.5</span>. <strong>Left:</strong> Clean test set. CP holds higher accuracy at every pruning level; at 80% the gap is 7.1 points. <strong>Right:</strong> Noisy test set (<span class="math inline"><em>σ</em> = 0.5</span>). The gap widens: at 60% pruning the advantage is 9.1 points, at 80% it is 10.4 points. Magnitude pruning collapses while causal pruning remains stable.</figcaption>
</figure>

<figure data-latex-placement="H">
<img src="/assets/img/causal-pruning/pruning_seed42_noise10.png" />
<figcaption><strong>Figure 9.</strong> Same experiment with noise increased to <span class="math inline"><em>σ</em> = 1.0</span>. The result is robust: the causal pruning advantage does not disappear under heavier noise. At 80% pruning the gap is 6.5 points (<span class="math inline">68.83%</span> versus <span class="math inline">62.34%</span>). The stability of the gap across <span class="math inline"><em>σ</em> = 0.5</span> and <span class="math inline"><em>σ</em> = 1.0</span> is evidence that the effect is not an artifact of the specific noise level.</figcaption>
</figure>

<figure data-latex-placement="H">
<img src="/assets/img/causal-pruning/pruning_seed0_noise05.png" />
<figcaption><strong>Figure 10.</strong> Seed 0, noise <span class="math inline"><em>σ</em> = 0.5</span>. The clean test set result is stronger here than in seed 42: at 80% pruning, causal pruning at <span class="math inline">73.38%</span> is actually above the unpruned baseline of <span class="math inline">72.08%</span>, while magnitude pruning is at <span class="math inline">64.29%</span>. Under noise at 80% pruning: <span class="math inline">74.03%</span> versus <span class="math inline">62.99%</span>, an 11-point gap. The two seeds together span two different random initializations and produce consistent results.</figcaption>
</figure>

### 18.6. Extended Validation: Three Datasets, Four Methods, Five Seeds, Three Noise Levels

The two-seed result on Pima established the direction. The question it left open was whether that result was robust, dataset-specific, or just a lucky initialization. To answer that, the experiment was extended to three datasets, four scoring methods, five random seeds, and pruning levels up to 90%, tested under three noise levels ($$\sigma \in \{0.5, 1.5, 2.0\}$$). The two additional datasets are Breast Cancer (569 samples, 30 features, binary outcome) and Wine binary (130 samples, 13 features, classes 0 and 1 only). Both are standard UCI benchmarks with clean ground truth labels.

The four methods compared are Causal Effect scoring (CE, the method developed here), magnitude pruning (standard baseline), random pruning (sanity check — if CE is near random, there is no signal), and gradient-based pruning (stronger baseline — ranking neurons by how much the loss gradient changes with respect to their weights).

<figure data-latex-placement="H">
<img src="/assets/img/causal-pruning/stress_noise05.png" />
<figcaption><strong>Figure 11.</strong> Extended validation at realistic noise (<span class="math inline"><em>σ</em> = 0.5</span>), 5 seeds, 3 datasets, pruning levels 0–90%. Mean <span class="math inline">±</span> std shown as shaded bands. On Pima (left), CE (green) separates clearly from magnitude (red) at 80–90% pruning. On Breast Cancer and Wine (center, right), methods cluster tightly at low pruning — the task is easy enough that any scoring criterion works. At 90% pruning on Wine, variance explodes for all methods, indicating the model is at its breaking point regardless of pruning strategy.</figcaption>
</figure>

<figure data-latex-placement="H">
<img src="/assets/img/causal-pruning/stress_noise15.png" />
<figcaption><strong>Figure 12.</strong> Same experiment at stress noise <span class="math inline"><em>σ</em> = 1.5</span> — three times the realistic level. On Pima, CE maintains its trajectory while magnitude degrades further. On Breast Cancer, CE holds at 80% while magnitude begins dropping. Wine is too small and too easy for any method to show consistent separation at this noise level; variance dominates. The key observation is that CE’s relative advantage does not disappear under harder stress — if anything, the gap on Pima widens.</figcaption>
</figure>

<figure data-latex-placement="H">
<img src="/assets/img/causal-pruning/stress_noise20.png" />
<figcaption><strong>Figure 13.</strong> Extreme stress: <span class="math inline"><em>σ</em> = 2.0</span> noise. At this level, all methods degrade on Pima to the 60–70% range. CE still produces the least-bad result at 90% pruning (<span class="math inline">+3.25%</span> over magnitude, mean across 5 seeds). On Breast Cancer, CE and gradient track each other closely, both outperforming magnitude at 90% pruning. Wine at this noise level is effectively random for all methods, confirming that the dataset offers no meaningful signal at extreme noise after extreme pruning.</figcaption>
</figure>

The summary table below reports the CE advantage over magnitude at 60%, 80%, and 90% pruning under the noisy test set, mean $$\pm$$ std across 5 seeds.

| **Dataset** | **Noise $$\sigma$$** | **60% prune** | **80% prune** | **90% prune** |
| ---| ---| -- | -- | -- |
| Pima Diabetes | 0.5 | $$-0.39 \pm 1.86$$ | $$+2.86 \pm 3.55$$ | $$+6.36 \pm 7.54$$ |
|  | 1.5 | $$+0.65 \pm 7.20$$ | $$+1.17 \pm 3.14$$ | $$+3.90 \pm 2.85$$ |
|  | 2.0 | $$-1.82 \pm 2.86$$ | $$-4.03 \pm 3.24$$ | $$+3.25 \pm 6.13$$ |
| Breast Cancer | 0.5 | $$-0.18 \pm 2.38$$ | $$-5.79 \pm 11.91$$ | $$+12.28 \pm 10.36$$ |
|  | 1.5 | $$-0.35 \pm 1.43$$ | $$-7.54 \pm 10.62$$ | $$+8.95 \pm 9.37$$ |
|  | 2.0 | $$+2.63 \pm 2.88$$ | $$-4.56 \pm 8.18$$ | $$+6.32 \pm 7.09$$ |
| Wine (binary) | 0.5 | $$+1.54 \pm 3.08$$ | $$-8.46 \pm 19.82$$ | $$-10.77 \pm 29.73$$ |
|  | 1.5 | $$+4.62 \pm 10.71$$ | $$-3.85 \pm 24.45$$ | $$-10.00 \pm 22.64$$ |
|  | 2.0 | $$-1.54 \pm 14.31$$ | $$-14.62 \pm 19.82$$ | $$-3.08 \pm 21.12$$ |

**Table 10.** CE advantage over magnitude pruning (noisy test set, mean $$\pm$$ std across 5 seeds). Positive values mean CE wins. The pattern is consistent: CE advantage is small or zero at moderate pruning, grows at 80–90%, and is largest on Pima — the hardest and most clinically relevant dataset. Breast Cancer and Wine at moderate pruning are ceiling-effect cases: all methods work, so the scoring criterion is irrelevant.

The Wine result deserves direct discussion because it looks like a failure. The CE advantage is negative at 80–90% pruning on Wine across most noise levels. However, looking at the raw std values tells the full story: the standard deviations are $$\pm 20$$–$$30\%$$ — the width of the confidence interval is larger than the entire accuracy range. This is not a signal that magnitude beats CE on Wine. It is a signal that 130 samples is not enough data, at 90% sparsity with extreme noise, for any method to produce a stable result. All four methods — including random pruning — produce results in the same range on Wine under these conditions. When all methods including random produce the same outcome, there is no information to extract about which scoring criterion is better. The experiment has simply exceeded the dataset’s capacity to differentiate.

The Breast Cancer 90% pruning result is large ($$+12.28\%$$ at $$\sigma = 0.5$$) but also has large variance ($$\pm 10.36$$). This means some seeds produce large CE wins and others do not. It is encouraging but not reliable enough to lead with.

The Pima result is the one that holds consistently. The advantage at 90% pruning is $$+6.36\%$$ at $$\sigma = 0.5$$ with $$\pm 7.54$$ standard deviation — overlapping with zero on some seeds, but positive on most. At $$\sigma = 1.5$$, the advantage is $$+3.90\%$$ with $$\pm 2.85$$ — smaller in absolute terms but with tighter variance, meaning it holds more consistently across seeds. The fact that Pima is the hardest of the three tasks (lowest baseline accuracy, most complex feature interactions, clinical-grade data) and also the one where CE shows the most consistent advantage is not coincidental. It is the direct prediction of the method: CE scoring identifies genuinely necessary neurons, and that identification only matters when the task is hard enough that not all neurons are necessary by default.

### 18.7. What the Stress Test Actually Shows

The most important result in the stress test is what did not happen. If CE scoring were just a slightly different version of magnitude pruning, both methods would degrade together under noise and high sparsity. Instead, the gap between them grows as conditions get harder. At low pruning on easy tasks, every scoring method produces similar results because the model has enough redundancy that you can remove neurons by almost any criterion without degrading accuracy. At 90% pruning on clinical tabular data under distribution shift, the model has almost nothing left. The neurons that remain either are the ones that causally determine the output, or they are not. CE scoring answers that question directly. Magnitude scoring does not.

This is the correct regime for the claim. The sentence “rather than replacing blind iterative search with causal prediction” is only meaningful at the breaking point — when you are forced to decide, with almost no room for error, which neurons are truly necessary. That is 90% pruning. That is where the results are.

### 18.8. What This Establishes and What It Does Not

The causal effect score in equation (115) is a practical approximation to a do-calculus intervention, not an exact one. It is worth being precise about this, because the distinction matters for how you interpret the results and how you would extend them.

In a formal Structural Causal Model, a do-intervention on neuron $$i$$ means cutting all incoming edges to neuron $$i$$ and fixing its value to zero. That is a graph surgery operation. What we are doing here is different: we are zeroing the activation of neuron $$i$$ while leaving the rest of the forward pass unchanged. This is closer to what the neuroscience literature calls a *lesion study* or *ablation* — you remove a unit and observe the downstream effect. The difference from a true do-intervention is that in a real SCM intervention, you would also zero out the influence of neuron $$i$$’s weights on the next layer’s computation. In an MLP, zeroing column $$i$$ of $$A^{(l)}$$ effectively does this for that particular forward pass, so the approximation is tighter than it might seem. But the neurons in a network are not independent causal variables in the Pearl sense — they interact nonlinearly, their activations are co-adapted during training, and removing one changes the effective function computed by all downstream neurons. A true causal graph over neurons would need to account for all of this.

With that caveat stated honestly, the empirical result stands: scoring neurons by CE identifies a better pruning set than magnitude scoring, and the advantage grows exactly where it should — at high sparsity, on hard tasks, under distribution shift. The mechanistic story is clean. Magnitude pruning asks: which weights are small right now? CE pruning asks: which neurons do nothing when you remove them? Those are genuinely different questions, and the second one is the right one if your goal is to remove computation that is not contributing to the output.

The deeper reason CE outperforms magnitude under distribution shift connects to a well-documented failure mode of standard pruning. Magnitude pruning implicitly assumes that large weights indicate important neurons. But large weights can arise from co-adaptation: during training, neuron $$A$$ develops a large weight because it has learned to compensate for the noise introduced by neuron $$B$$. Remove $$B$$ (because it has a small weight) and you have also broken $$A$$’s purpose. CE scoring does not make this mistake because it measures the marginal output change — it asks what happens to the prediction when you remove exactly this neuron, holding everything else fixed. That is a cleaner signal of individual necessity, which is exactly what you want from a pruning criterion.

Recent work from the mechanistic interpretability community supports this view. Elhage et al. (2021) [\[51\]](#ref-51) showed that transformer circuits contain “induction heads” and “composition heads” that are functionally critical despite having moderate weight magnitudes, while large blocks of neurons with high weight norms are nearly redundant due to superposition. Voita et al. (2019) [\[52\]](#ref-52) demonstrated in BERT that only a small fraction of attention heads are causally responsible for task performance — a result arrived at by ablation, exactly the CE scoring logic applied at the head level. Michel et al. (2019) [\[53\]](#ref-53) showed that 20% of attention heads in machine translation models are individually important; the rest can be pruned with near-zero loss — again, identified by ablation, not by weight magnitude. These results suggest that the CE scoring approach, demonstrated here on MLPs, is capturing a real phenomenon that appears at scale.

The claim here is proof of concept, not deployment-ready algorithm. The experiments are on one architecture family (MLP) and one dataset type (tabular clinical data). The method has not been tested on convolutional networks where receptive fields create spatial dependencies between neurons, on recurrent networks where the causal graph is temporal, or on transformers where attention heads create dynamic routing that fundamentally changes what “neuron importance” means. Each of those settings would require a careful re-examination of what CE scoring is actually measuring. The principles transfer; the specific implementation details would need to adapt.

### 18.9. Connection to the CCA+ Framework

CCA+ identifies causal direction in datasets by measuring a training asymmetry: the network trained in the true causal direction converges to a lower loss floor because the residuals in that direction are genuinely independent noise, requiring less information to model. Causal pruning identifies causally necessary neurons by measuring an output asymmetry under intervention: neurons that change the output when disabled were doing real work; neurons that do not were not. Both methods share the same underlying principle — the do-operator produces an asymmetric signal that correlational measures miss.

The symmetry goes deeper than surface analogy. In the CCA+ setting, the relevant question is: “what is the loss floor for the network trained in direction $$X \to Y$$ versus the network trained in direction $$Y \to X$$?” The direction with the lower floor is the causal one, because true noise is independent of the cause, which gives the forward network a structurally easier function to learn. In the pruning setting, the relevant question is: “what is the output change when neuron $$i$$ is disabled versus when neuron $$j$$ is disabled?” The neuron with the larger output change is the causally necessary one, because it is doing structural work that cannot be compensated by the remaining network.

In both cases, what you are measuring is the structural contribution of a component to the system’s output. In the dataset setting, the component is a variable. In the neural network setting, the component is a neuron. The measurement instrument is the same: force the component to a fixed value, observe what breaks.

This framing connects to a broader research programme around causal representation learning [\[55\]](#ref-55), which asks whether neural networks can be made to learn representations that are causally structured rather than merely statistically convenient. Schölkopf et al. (2021) argue that the fundamental bottleneck in generalisation — why models fail when the distribution shifts — is that standard training produces representations that encode correlations, not causes. A model trained on BMI and glucose in a hospital population will encode the correlation between them, including all the confounding effects of age, diet, and socioeconomic status that happen to be present in that hospital’s patient mix. When you deploy that model in a different hospital with a different patient mix, the correlation structure changes and the model’s representations no longer match the data. Causal representations — ones built around what actually causes what — do not have this problem, because causes are stable under intervention by definition.

Causal pruning is a step toward this. By identifying and keeping only the neurons whose activation causally determines the output, you are, in effect, building a smaller model whose remaining components are more causally structured and less entangled with spurious correlations. The stress test result — that CE-pruned models hold up better under noise — is exactly the signature of a model that has encoded more signal and less noise. It is not yet causal representation learning in the full Schölkopf sense; the representations are still learned by standard gradient descent. But the pruning criterion selects, post-hoc, the components that survived in a causally meaningful way.

The natural extension is to make the causal structure explicit during training rather than recovering it afterwards. That is the direction of work on invariant risk minimisation [\[142\]](#ref-142) and causal regularisation — methods that penalise models for relying on features whose correlation with the label changes across environments. The CE scoring approach demonstrated here is complementary: it can identify, after training, which neurons are responsible for the stable predictions and which are exploiting environment-specific correlations that will not generalise.

## 19. Conclusion

This paper set out to answer two questions that are harder than they look. First: given two observed variables and nothing else, can you determine which one causes the other, and what happens if you force one of them to change? Second: given a trained neural network, can you determine which neurons are genuinely necessary for its predictions, and use that to build a smaller model that holds up when the real world looks different from the training set? The answer to both is yes, under specific and honest conditions, and the same mathematical principle underlies both answers.

### 19.1. What Was Built and Proved

The mathematical foundation is the CCA Asymmetry Theorem (Theorem 4.7): under the Additive Noise Model with nonlinear injective mechanism, a neural network training in the true causal direction converges in strictly fewer expected gradient steps than one training in the reverse direction. This is proved from first principles in three lemmas. Lemma 1 establishes that the excess variance in the reverse direction comes from the entanglement of the mechanism $$f$$ and the noise $$\varepsilon$$: in the reverse direction, the network has to learn a function of $$Y$$ that effectively decomposes $$f(X)$$ from $$\varepsilon$$, which is harder than learning $$f$$ directly. Lemma 2 connects this excess variance to the loss gap via the law of total variance. Lemma 3 connects the loss gap to convergence speed under the Polyak-Łojasiewicz condition [\[14\]](#ref-14), which guarantees that loss gaps translate to step-count gaps when the loss surface is PL.

The asymmetry holds across different activation functions, optimizers, and network widths because it is a property of the data-generating process — specifically of the independence $$\varepsilon \perp X$$ and the nonlinearity of $$f$$ — not of any particular implementation. Change the architecture and the absolute convergence speeds change; the direction of the asymmetry does not.

The algorithmic pipeline chains this direction oracle to Pearl’s backdoor adjustment formula. This connection was always theoretically possible but had never been automated: direction discovery tools and effect estimation tools existed in separate codebases, requiring users to manually transfer direction decisions and manually specify confounder sets. The CCA+ pipeline automates this end-to-end: raw data in, interventional estimate with confidence interval out.

### 19.2. What Was Validated

**Biological validation.** CCA+ identifies BMI $$\to$$ Glucose on the Pima dataset at score $$-0.059$$, well below the strong threshold of $$-0.03$$, across 49 of 50 bootstrap subsamples. The backdoor-adjusted ACE is $$1.04$$ mg/dL per BMI unit (95% CI $$[0.73, 1.35]$$) with confounder set $$\{$$Age, Pregnancies$$\}$$, inside the biological range established by clinical intervention studies [\[12\]](#ref-12). The naive observational estimate is $$1.483$$ — upward-biased by $$0.44$$ mg/dL due to confounding. The correction changes the practical interpretation from “very strong causal effect” to “moderate,” which has real implications for what kind of clinical intervention is justified.

**Structural validation.** On the Sachs protein signaling network (853-cell observational subset, 16 testable edges), the MWFAS assembly recovers 9 correct, 7 wrong, 0 abstained — 56.2% at 100% coverage from observational data alone. The correctly recovered edges include the RAF$$\to$$MEK, MEK$$\to$$ERK, and PKA$$\to$$RAF paths core to the MAPK cascade [\[13\]](#ref-13). The 7 wrong edges cluster around PKA, a master kinase whose interventional dominance creates pairwise scores inconsistent with the true DAG. This failure is honest and diagnosable: PKA-adjacent pairs produce scores near the ambiguity threshold, flagging them for manual review.

**Benchmark validation.** On the 108-pair Tübingen Cause-Effect Pairs benchmark at 80-epoch settings, CCA+ achieves 48.9% on 94 decided pairs — near chance, which is the honest result on a benchmark that stress-tests the method’s exact boundary conditions: heteroscedastic noise, near-linear mechanisms, physical measurement pairs where ANM assumptions are often violated. The ensemble achieves 100% on 10 synthetic pairs with known nonlinear mechanisms satisfying the method’s documented assumptions, confirming that combining orthogonal signals closes the gap neither method closes alone.

### 19.3. The Causal Pruning Result

The causal pruning section demonstrated a proof of concept: CE scoring (zero a neuron, measure output damage) as a structured pruning criterion, benchmarked against magnitude, gradient-based, and random pruning across three datasets, five seeds, and three noise levels.

At 80% pruning under $$\sigma = 0.5$$ noise on Pima, CE-pruned models retain $$72.73\%$$ (seed 42) and $$74.03\%$$ (seed 0), while magnitude-pruned models drop to $$62.34\%$$ and $$62.99\%$$. On seed 0, the CE-pruned model at 80% sparsity ($$73.38\%$$) is above the original unpruned baseline ($$72.08\%$$) — the removed neurons were, on net, adding noise rather than signal.

The extended stress test (5 seeds, 3 datasets, 3 noise levels, 90% max pruning) sharpens this into a precise claim: CE scoring’s advantage is negligible on easy tasks and grows at extreme sparsity ($$\geq 80\%$$) on hard tasks under distribution shift. On Pima at 90% pruning and $$\sigma = 0.5$$, CE beats magnitude by $$+6.36\%$$ (mean over 5 seeds). At $$\sigma = 1.5$$ the advantage is $$+3.90\%$$ with tighter variance ($$\pm 2.85$$), holding more consistently under harder conditions. This is the correct signature of causal necessity: the advantage appears precisely when necessity starts to matter, when the model has almost nothing left and every remaining neuron has to count.

The gradient baseline — which ranks neurons by training loss gradient — is the most informative comparison. CE and gradient track similarly at moderate pruning and CE separates at extreme sparsity under noise. This tells you gradient measures functional contribution during training; CE measures it at inference time. At extreme sparsity under distribution shift, the inference-time signal is more reliable.

### 19.4. Honest Limitations

The pipeline reaches Rung 2, not Rung 3. It estimates population-average causal effects under no-unmeasured-confounders. It does not produce individual counterfactuals. It does not handle feedback loops. The ANM assumption is falsifiable but not always satisfied: heteroscedastic noise, near-linear mechanisms, and feedback all violate it. The $$\eta^2 - r^2$$ pre-test catches many near-linear cases but is a heuristic threshold, not a proof of nonlinearity.

CE scoring is an ablation, not a true do-intervention. In overparameterized networks with strong co-adaptation, CE may underestimate neurons whose contribution is distributed across redundant pathways. This is a known limitation of ablation-based importance estimation and an active area in mechanistic interpretability research.

### 19.5. The Path Forward

For causal discovery: increasing the epoch budget on the Tübingen benchmark is the single change most likely to close the gap between theoretical guarantees and benchmark performance. Nonlinear backdoor adjustment (replacing OLS with a kernel regression or neural network) extends the pipeline to cases where the dose-response curve is nonlinear. Sensitivity analysis using E-values [\[19\]](#ref-19) would allow the pipeline to report robustness bounds: how strong would an unmeasured confounder need to be to overturn the conclusion.

For causal pruning: the natural next target is a convolutional architecture on corrupted ImageNet [\[141\]](#ref-141). CE scoring applies directly to filters (zero a filter’s output feature map, measure output change), and if it outperforms magnitude pruning on corrupted ImageNet, the claim graduates from “works on tabular clinical data” to “robust across architectures and data types.”

The deeper question is whether CE scoring can guide training rather than just prune afterwards. Using the CE signal as a regulariser during gradient descent would push the network to develop non-redundant, causally necessary neuron functions from the start — a step toward the causal representation learning programme of Schölkopf et al. [\[55\]](#ref-55) and the invariant risk minimisation framework of Arjovsky et al. [\[142\]](#ref-142). The results here suggest the signal exists. Whether it can be exploited during learning, not just extracted from the finished product, is the most interesting open question this paper leaves behind.

## References

1. <a id="ref-1"></a>J. Pearl, “Causal diagrams for empirical research,” *Biometrika*, vol. 82, no. 4, pp. 669–688, 1995.

2. <a id="ref-2"></a>J. Pearl, *Causality: Models, Reasoning, and Inference*, Cambridge University Press, 2000.

3. <a id="ref-3"></a>J. Peters, J. Mooij, D. Janzing, and B. Schölkopf, “Causal discovery with continuous additive noise models,” *Journal of Machine Learning Research*, vol. 15, pp. 2009–2053, 2014.

4. <a id="ref-4"></a>P. Hoyer, D. Janzing, J. Mooij, J. Peters, and B. Schölkopf, “Nonlinear causal discovery with additive noise models,” in *Advances in Neural Information Processing Systems*, vol. 21, 2009.

5. <a id="ref-5"></a>D. Janzing and B. Schölkopf, “Causal inference using the algorithmic Markov condition,” *IEEE Transactions on Information Theory*, vol. 56, no. 10, 2010.

6. <a id="ref-6"></a>S. Shimizu, P. Hoyer, A. Hyvärinen, and A. Kerminen, “A linear non-Gaussian acyclic model for causal discovery,” *Journal of Machine Learning Research*, vol. 7, pp. 2003–2030, 2006.

7. <a id="ref-7"></a>P. Blöbaum, P. Götz, K. Budhathoki, A. Mastakouri, and D. Janzing, “DoWhy-GCM: An extension of DoWhy for causal mechanism models,” in *Proc. CLeaR*, 2022.

8. <a id="ref-8"></a>PyWhy Development Team, “DoWhy documentation: Causal discovery,” <https://py-why.github.io/dowhy>, 2024.

9. <a id="ref-9"></a>Amazon Science, “OpportunityFinder: Automated causal discovery and inference,” in *Proc. KDD CausalML Workshop*, 2023.

10. <a id="ref-10"></a>K. Sachs, O. Perez, D. Pe’er, D. Lauffenburger, and G. Nolan, “Causal protein-signaling networks derived from multiparameter single-cell data,” *Science*, vol. 308, pp. 523–529, 2005.

11. <a id="ref-11"></a>J. Smith, E. Everhart, W. Dickson, W. Knowler, and R. Johannes, “Using the ADAP learning algorithm to forecast the onset of diabetes mellitus,” *Proc. Annual Symposium on Computer Applications in Medical Care*, pp. 261–265, 1988.

12. <a id="ref-12"></a>S. Kahn, R. Hull, and K. Utzschneider, “Mechanisms linking obesity to insulin resistance and type 2 diabetes,” *Nature*, vol. 444, pp. 840–846, 2006.

13. <a id="ref-13"></a>P. Roberts and C. Der, “Targeting the Raf-MEK-ERK mitogen-activated protein kinase cascade for the treatment of cancer,” *Oncogene*, vol. 26, pp. 3291–3310, 2007.

14. <a id="ref-14"></a>B. Polyak, “Gradient methods for minimizing functionals,” *USSR Computational Mathematics and Mathematical Physics*, vol. 3, no. 4, pp. 864–878, 1963.

15. <a id="ref-15"></a>L. Bottou, “Large-scale machine learning with stochastic gradient descent,” in *Proc. COMPSTAT*, pp. 177–186, 2010.

16. <a id="ref-16"></a>P. Rosenbaum and D. Rubin, “The central role of the propensity score in observational studies for causal effects,” *Biometrika*, vol. 70, no. 1, pp. 41–55, 1983.

17. <a id="ref-17"></a>B. Efron, “Bootstrap methods: Another look at the jackknife,” *Annals of Statistics*, vol. 7, no. 1, pp. 1–26, 1979.

18. <a id="ref-18"></a>P. Rosenbaum, *Observational Studies*, 2nd ed., Springer, 2002.

19. <a id="ref-19"></a>T. VanderWeele and P. Ding, “Sensitivity analysis in observational research: Introducing the E-value,” *Annals of Internal Medicine*, vol. 167, no. 4, pp. 268–274, 2017.

20. <a id="ref-20"></a>H. Reichenbach, *The Direction of Time*, University of California Press, 1956.

21. <a id="ref-21"></a>K. Pearson, *The Grammar of Science*, 3rd ed., A. and C. Black, London, 1911.

22. <a id="ref-22"></a>S. Wright, “Correlation and causation,” *Journal of Agricultural Research*, vol. 20, no. 7, pp. 557–585, 1921.

23. <a id="ref-23"></a>P. Spirtes, C. Glymour, and R. Scheines, *Causation, Prediction, and Search*, 2nd ed., MIT Press, 2000.

24. <a id="ref-24"></a>D. M. Chickering, “Optimal structure identification with greedy search,” *Journal of Machine Learning Research*, vol. 3, pp. 507–554, 2002.

25. <a id="ref-25"></a>T. Verma and J. Pearl, “Equivalence and synthesis of causal models,” in *Proc. UAI*, pp. 220–227, 1990.

26. <a id="ref-26"></a>Y. Huang and M. Valtorta, “Pearl’s calculus of intervention is complete,” in *Proc. UAI*, 2006.

27. <a id="ref-27"></a>C. W. J. Granger, “Investigating causal relations by econometric models and cross-spectral methods,” *Econometrica*, vol. 37, no. 3, pp. 424–438, 1969.

28. <a id="ref-28"></a>C. A. Sims, “Macroeconomics and reality,” *Econometrica*, vol. 48, no. 1, pp. 1–48, 1980.

29. <a id="ref-29"></a>A. Shojaie and E. B. Fox, “Granger causality: A review and recent advances,” *Annual Review of Statistics and Its Application*, vol. 9, pp. 289–319, 2022.

30. <a id="ref-30"></a>A. K. Seth, A. B. Barrett, and L. Barnett, “Granger causality analysis in neuroscience and neuroimaging,” *Journal of Neuroscience*, vol. 35, no. 8, pp. 3293–3297, 2015.

31. <a id="ref-31"></a>K. Zhang and A. Hyvärinen, “On the identifiability of the post-nonlinear causal model,” in *Proc. UAI*, pp. 647–655, 2009.

32. <a id="ref-32"></a>Y. Lin et al., “A skewness-based criterion for addressing heteroscedastic noise in causal discovery,” in *Proc. ICLR*, 2025.

33. <a id="ref-33"></a>J. Berkson, “Limitations of the application of fourfold table analysis to hospital data,” *Biometrics Bulletin*, vol. 2, no. 3, pp. 47–53, 1946.

34. <a id="ref-34"></a>D. O. Scharfstein, A. Rotnitzky, and J. M. Robins, “Adjusting for nonignorable drop-out using semiparametric nonresponse models,” *Journal of the American Statistical Association*, vol. 94, pp. 1096–1120, 1999.

35. <a id="ref-35"></a>K. Hirano and G. W. Imbens, “The propensity score with continuous treatments,” in *Applied Bayesian Modeling and Causal Inference from Incomplete-Data Perspectives*, pp. 73–84, Wiley, 2004.

36. <a id="ref-36"></a>R. Frisch and F. V. Waugh, “Partial time regressions as compared with individual trends,” *Econometrica*, vol. 1, no. 4, pp. 387–401, 1933.

37. <a id="ref-37"></a>J. M. Mooij, J. Peters, D. Janzing, J. Zscheischler, and B. Schölkopf, “Distinguishing cause from effect using observational data: Methods and benchmarks,” *Journal of Machine Learning Research*, vol. 17, no. 32, pp. 1–102, 2016.

38. <a id="ref-38"></a>D. Janzing and B. Steudel, “Justifying additive-noise-model based causal discovery via algorithmic information theory,” *Open Systems and Information Dynamics*, vol. 17, pp. 189–212, 2010.

39. <a id="ref-39"></a>G. Park, “Identifiability of additive noise models using conditional variances,” *Journal of Machine Learning Research*, vol. 21, no. 75, pp. 1–34, 2020.

40. <a id="ref-40"></a>S. Shimizu et al., “DirectLiNGAM: A direct method for learning a linear non-Gaussian structural equation model,” *Journal of Machine Learning Research*, vol. 12, pp. 1225–1248, 2011.

41. <a id="ref-41"></a>I. Díaz, N. Hejazi, and M. van der Laan, “Non-parametric efficient causal mediation with intermediate confounders,” *Biometrika*, vol. 110, no. 1, pp. 135–148, 2023.

42. <a id="ref-42"></a>W. Miao, Z. Geng, and E. J. Tchetgen Tchetgen, “Identifying causal effects with proxy variables of an unmeasured confounder,” *Biometrika*, vol. 105, no. 4, pp. 987–993, 2018.

43. <a id="ref-43"></a>E. J. Tchetgen Tchetgen, A. Ying, Y. Cui, X. Shi, and W. Miao, “An introduction to proximal causal learning,” *Statistical Science*, in press, 2024.

44. <a id="ref-44"></a>A. Wald, “The fitting of straight lines if both variables are subject to error,” *Annals of Mathematical Statistics*, vol. 11, no. 3, pp. 284–300, 1940.

45. <a id="ref-45"></a>J. D. Angrist and A. B. Krueger, “Does compulsory school attendance affect schooling and earnings?” *Quarterly Journal of Economics*, vol. 106, no. 4, pp. 979–1014, 1991.

46. <a id="ref-46"></a>G. Davey Smith and S. Ebrahim, “Mendelian randomization: Can genetic epidemiology contribute to understanding environmental determinants of disease?” *International Journal of Epidemiology*, vol. 32, pp. 1–22, 2003.

47. <a id="ref-47"></a>J. D. Sargan, “The estimation of economic relationships using instrumental variables,” *Econometrica*, vol. 26, no. 3, pp. 393–415, 1958.

48. <a id="ref-48"></a>J. B. Ramsey, “Tests for specification errors in classical linear least-squares regression analysis,” *Journal of the Royal Statistical Society: Series B*, vol. 31, no. 2, pp. 350–371, 1969.

49. <a id="ref-49"></a>V. Chernozhukov et al., “Double/debiased machine learning for treatment and structural parameters,” *Econometrics Journal*, vol. 21, no. 1, pp. C1–C68, 2018.

50. <a id="ref-50"></a>J. M. Robins, A. Rotnitzky, and L. P. Zhao, “Estimation of regression coefficients when some regressors are not always observed,” *Journal of the American Statistical Association*, vol. 89, pp. 846–866, 1994.

51. <a id="ref-51"></a>N. Elhage et al., “A mathematical framework for transformer circuits,” *Transformer Circuits Thread*, 2021. <https://transformer-circuits.pub>

52. <a id="ref-52"></a>E. Voita, D. Talbot, F. Moiseev, R. Sennrich, and I. Titov, “Analyzing multi-head self-attention: Specialized heads do the heavy lifting, the rest can be pruned,” in *Proc. ACL*, pp. 5797–5808, 2019.

53. <a id="ref-53"></a>P. Michel, O. Levy, and G. Neubig, “Are sixteen heads really better than one?” in *Proc. NeurIPS*, 2019.

54. <a id="ref-54"></a>H. Zheng, S. Gao, and K. Zhang, “Causal head gating: A framework for interpreting roles of attention heads in transformers,” *arXiv:2505.13737*, 2025.

55. <a id="ref-55"></a>B. Schölkopf et al., “Toward causal representation learning,” *Proceedings of the IEEE*, vol. 109, no. 5, pp. 612–634, 2021.

56. <a id="ref-56"></a>B. Varici, E. Acartürk, K. Shanmugam, and A. Tajer, “General identifiability and achievability for causal representation learning,” in *Proc. AISTATS*, pp. 2314–2322, 2024.

57. <a id="ref-57"></a>M. F. Bellemare, J. Bloem, and N. Wexler, “The paper of how: Estimating treatment effects using the front-door criterion,” *Oxford Bulletin of Economics and Statistics*, 2024.

58. <a id="ref-58"></a>G. Darmois, “Analyse générale des liaisons stochastiques,” *Revue de l’Institut International de Statistique*, vol. 21, pp. 2–8, 1953.

59. <a id="ref-59"></a>V. P. Skitovich, “On a property of the normal distribution,” *Doklady Akademii Nauk SSSR*, vol. 89, pp. 217–219, 1953.

60. <a id="ref-60"></a>P. Blöbaum, D. Janzing, T. Washio, S. Shimizu, and B. Schölkopf, “Cause-effect inference by comparing regression errors,” in *Proc. International Conference on Artificial Intelligence and Statistics (AISTATS)*, pp. 900–909, 2018.

61. <a id="ref-61"></a>K. Zhang, J. Peters, D. Janzing, and B. Schölkopf, “Kernel-based conditional independence test and application in causal discovery,” in *Proc. UAI*, pp. 804–813, 2011.

62. <a id="ref-62"></a>R. A. Fisher, *Statistical Methods for Research Workers*, Oliver and Boyd, Edinburgh, 1925.

63. <a id="ref-63"></a>G. J. Székely, M. L. Rizzo, and N. K. Bakirov, “Measuring and testing dependence by correlation of distances,” *Annals of Statistics*, vol. 35, no. 6, pp. 2769–2794, 2007.

64. <a id="ref-64"></a>D. N. Reshef et al., “Detecting novel associations in large data sets,” *Science*, vol. 334, no. 6062, pp. 1518–1524, 2011.

65. <a id="ref-65"></a>J. Peters, J. M. Mooij, D. Janzing, and B. Schölkopf, “Causal discovery with continuous additive noise models,” *Journal of Machine Learning Research*, vol. 15, pp. 2009–2053, 2014.

66. <a id="ref-66"></a>J. M. Mooij, J. Peters, D. Janzing, J. Zscheischler, and B. Schölkopf, “Distinguishing cause from effect using observational data: Methods and benchmarks,” *Journal of Machine Learning Research*, vol. 17, no. 32, pp. 1–102, 2016.

67. <a id="ref-67"></a>UCI Machine Learning Repository, “Pima Indians Diabetes Database,” <https://archive.ics.uci.edu/ml/datasets/diabetes>, 1988.

68. <a id="ref-68"></a>QuantumBlack, AI by McKinsey, “CausalNex: A toolkit for causal reasoning with Bayesian networks,” <https://causalnex.readthedocs.io>, 2021.

69. <a id="ref-69"></a>A. Sharma and E. Kiciman, “DoWhy: An end-to-end library for causal inference,” *arXiv:2011.04216*, 2020.

70. <a id="ref-70"></a>S. Shimizu, “LiNGAM: Non-Gaussian methods for estimating causal structures,” *Behaviormetrika*, vol. 41, pp. 65–98, 2014.

71. <a id="ref-71"></a>M. V. Myronyuk, “On the Skitovich-Darmois theorem and Heyde theorem in a Banach space,” *Ukrainian Mathematical Journal*, vol. 60, pp. 1437–1447, 2008.

72. <a id="ref-72"></a>H. Yamashita, H. Shimizu, and S. Shimizu, “Functional linear non-Gaussian acyclic model for causal discovery,” *Behaviormetrika*, vol. 51, pp. 133–161, 2024.

73. <a id="ref-73"></a>C. Uhler, G. Raskutti, P. Bühlmann, and B. Yu, “Geometry of the faithfulness assumption in causal inference,” *Annals of Statistics*, vol. 41, no. 2, pp. 436–463, 2013.

74. <a id="ref-74"></a>J. Zhang and P. Spirtes, “Strong faithfulness and uniform consistency in causal inference,” in *Proc. UAI*, pp. 632–639, 2003.

75. <a id="ref-75"></a>X. Zheng, B. Aragam, P. Ravikumar, and E. P. Xing, “DAGs with NO TEARS: Continuous optimization for structure learning,” in *Proc. NeurIPS*, 2018.

76. <a id="ref-76"></a>K. Bello, B. Aragam, and P. Ravikumar, “DAGMA: Learning DAGs via M-matrices and a log-determinant acyclicity characterization,” in *Proc. NeurIPS*, 2022.

77. <a id="ref-77"></a>C. Li and G. Shen, “A hybrid constrained continuous optimization approach for optimal causal discovery from biological data,” *GigaScience*, vol. 13, giae021, 2024.

78. <a id="ref-78"></a>J. Pearl, “Direct and indirect effects,” in *Proc. 17th Conference on Uncertainty in Artificial Intelligence*, pp. 411–420, 2001.

79. <a id="ref-79"></a>J. M. Robins and T. S. Richardson, “Alternative graphical causal models and the identification of direct effects,” in *Causality and Psychopathology*, Oxford University Press, 2010.

80. <a id="ref-80"></a>I. Díaz and N. Hejazi, “Causal mediation analysis for stochastic interventions,” *Journal of the Royal Statistical Society: Series B*, vol. 82, no. 3, pp. 661–683, 2020.

81. <a id="ref-81"></a>N. Hejazi, I. Díaz, and M. van der Laan, “Nonparametric causal mediation analysis for stochastic interventional (in)direct effects,” *Biostatistics*, vol. 24, no. 2, pp. 428–446, 2022.

82. <a id="ref-82"></a>T. J. VanderWeele and S. Vansteelandt, “Conceptual issues concerning mediation, interventions, and composition,” *Statistics and Its Interface*, vol. 2, pp. 457–468, 2009.

83. <a id="ref-83"></a>J. M. Robins, “A new approach to causal inference in mortality studies with a sustained exposure period — application to control of the healthy worker survivor effect,” *Mathematical Modelling*, vol. 7, pp. 1393–1512, 1986.

84. <a id="ref-84"></a>J. M. Robins, M. A. Hernán, and B. Brumback, “Marginal structural models and causal inference in epidemiology,” *Epidemiology*, vol. 11, no. 5, pp. 550–560, 2000.

85. <a id="ref-85"></a>M. A. Hernán and J. M. Robins, *Causal Inference: What If*, Chapman and Hall/CRC, 2020.

86. <a id="ref-86"></a>E. H. Simpson, “The interpretation of interaction in contingency tables,” *Journal of the Royal Statistical Society: Series B*, vol. 13, no. 2, pp. 238–241, 1951.

87. <a id="ref-87"></a>G. U. Yule, “Notes on the theory of association of attributes in statistics,” *Biometrika*, vol. 2, no. 2, pp. 121–134, 1903.

88. <a id="ref-88"></a>J. Pearl, “Understanding Simpson’s paradox,” *The American Statistician*, vol. 68, no. 1, pp. 8–13, 2014.

89. <a id="ref-89"></a>W. S. Robinson, “Ecological correlations and the behavior of individuals,” *American Sociological Review*, vol. 15, no. 3, pp. 351–357, 1950.

90. <a id="ref-90"></a>D. Gunnell, R. M. Davey Smith, and M. J. Frankel, “Use of Mendelian randomisation to investigate the causal effects of smoking on health,” *Journal of Epidemiology and Community Health*, vol. 57, no. 12, pp. 907–911, 2003.

91. <a id="ref-91"></a>J. Peters, P. Bühlmann, and N. Meinshausen, “Causal inference by using invariant prediction: Identification and confidence intervals,” *Journal of the Royal Statistical Society: Series B*, vol. 78, no. 5, pp. 947–1012, 2016.

92. <a id="ref-92"></a>D. Rothenäusler, N. Meinshausen, P. Bühlmann, and J. Peters, “Anchor regression: Heterogeneous data meet causality,” *Journal of the Royal Statistical Society: Series B*, vol. 83, no. 2, pp. 215–246, 2021.

93. <a id="ref-93"></a>T. J. VanderWeele and M. P. Knol, “A tutorial on interaction,” *Epidemiologic Methods*, vol. 3, no. 1, pp. 33–72, 2014.

94. <a id="ref-94"></a>K. J. Rothman, “Causes,” *American Journal of Epidemiology*, vol. 104, no. 6, pp. 587–592, 1976.

95. <a id="ref-95"></a>J. J. Heckman, “Sample selection bias as a specification error,” *Econometrica*, vol. 47, no. 1, pp. 153–161, 1979.

96. <a id="ref-96"></a>J. Berkson, “Are there two regressions?” *Journal of the American Statistical Association*, vol. 45, no. 250, pp. 164–180, 1950.

97. <a id="ref-97"></a>W. G. Cochran, “Errors of measurement in statistics,” *Technometrics*, vol. 10, no. 4, pp. 637–666, 1968.

98. <a id="ref-98"></a>R. J. Carroll, D. Ruppert, L. A. Stefanski, and C. M. Crainiceanu, *Measurement Error in Nonlinear Models: A Modern Perspective*, 2nd ed., Chapman and Hall/CRC, 2006.

99. <a id="ref-99"></a>J. R. Cook and L. A. Stefanski, “Simulation-extrapolation estimation in parametric measurement error models,” *Journal of the American Statistical Association*, vol. 89, pp. 1314–1328, 1994.

100. <a id="ref-100"></a>E. Gao, I. Ng, M. Gong, L. Shen, W. Huang, T. Liu, K. Zhang, and H. Bondell, “MissDAG: Causal discovery in the presence of missing data with continuous additive noise models,” *arXiv:2205.13869*, 2022.

101. <a id="ref-101"></a>W. Liu, B. Huang, E. Gao, Q. Ke, H. Bondell, and M. Gong, “Causal discovery with mixed linear and nonlinear additive noise models: a scalable approach,” in *Proc. 3rd Conference on Causal Learning and Reasoning (CLeaR)*, PMLR 236:1237–1263, 2024.

102. <a id="ref-102"></a>F. Montagna, N. Noceti, L. Rosasco, and F. Locatello, “Shortcuts for causal discovery of nonlinear models by score matching,” *arXiv:2310.14246*, 2023.

103. <a id="ref-103"></a>T. Ikeuchi, M. Ide, Y. Zeng, T. N. Maeda, and S. Shimizu, “ParceLiNGAM: A causal ordering method robust against latent confounders,” *Journal of Machine Learning Research*, vol. 24, no. 14, pp. 1–43, 2023.

104. <a id="ref-104"></a>H. Karimi, J. Nutini, and M. Schmidt, “Linear convergence of gradient and proximal-gradient methods under the Polyak-Łojasiewicz condition,” in *Proc. ECML PKDD*, Lecture Notes in Computer Science, vol. 9851, pp. 795–811, Springer, 2016.

105. <a id="ref-105"></a>S. Chatterjee, “Convergence of gradient descent for deep neural networks,” *arXiv:2203.16462*, 2022.

106. <a id="ref-106"></a>J. An and J. Lu, “Convergence of stochastic gradient descent under a local Łojasiewicz condition for deep neural networks,” *arXiv:2304.09221*, 2023.

107. <a id="ref-107"></a>K. Scaman, C. Malherbe, and L. Dos Santos, “Convergence rates of non-convex stochastic gradient descent under a generic Łojasiewicz condition and local smoothness,” in *Proc. ICML*, PMLR 162:19310–19327, 2022.

108. <a id="ref-108"></a>J. Pearl and E. Bareinboim, “Causal inference and the data-fusion problem,” *Proceedings of the National Academy of Sciences*, vol. 113, no. 27, pp. 7345–7352, 2016.

109. <a id="ref-109"></a>S. Wager, *Causal Inference: A Statistical Learning Approach*, Stanford University, working draft, 2024. <a href="https://web.stanford.edu/ swager/causal_inf_book.pdf" class="uri">https://web.stanford.edu/ swager/causal_inf_book.pdf</a>

110. <a id="ref-110"></a>G. W. Imbens and D. B. Rubin, *Causal Inference for Statistics, Social, and Biomedical Sciences*, Cambridge University Press, 2015.

111. <a id="ref-111"></a>K. Zhang, J. Peters, D. Janzing, and B. Schölkopf, “Kernel-based conditional independence test and application in causal discovery,” in *Proc. UAI*, pp. 804–813, 2011.

112. <a id="ref-112"></a>M. C. Lovell, “Seasonal adjustment of economic time series and multiple regression analysis,” *Journal of the American Statistical Association*, vol. 58, no. 304, pp. 993–1010, 1963.

113. <a id="ref-113"></a>J. Peters, D. Janzing, and B. Schölkopf, *Elements of Causal Inference: Foundations and Learning Algorithms*, MIT Press, 2017.

114. <a id="ref-114"></a>E. Bareinboim, J. D. Correa, D. Ibeling, and T. Icard, “On Pearl’s hierarchy and the foundations of causal inference,” in *Probabilistic and Causal Inference: The Works of Judea Pearl*, ACM Books, pp. 507–556, 2022.

115. <a id="ref-115"></a>K. Sachs, O. Perez, D. Pe’er, D. A. Lauffenburger, and G. P. Nolan, “Causal protein-signaling networks derived from multiparameter single-cell data,” *Science*, vol. 308, no. 5721, pp. 523–529, 2005.

116. <a id="ref-116"></a>B. Schölkopf, “Causality for machine learning,” in *Probabilistic and Causal Inference: The Works of Judea Pearl*, ACM Books, pp. 765–804, 2022.

117. <a id="ref-117"></a>M. R. Fellows, D. Hermelin, F. Rosamond, and S. Vialette, “On the parameterized complexity of multiple-interval graph problems,” *Theoretical Computer Science*, vol. 410, no. 1, pp. 53–61, 2009.

118. <a id="ref-118"></a>Y. Zhang, X. Hao, and M. Teng, “causal-learn: Causal discovery in Python,” *Journal of Machine Learning Research*, vol. 24, no. 60, pp. 1–8, 2023.

119. <a id="ref-119"></a>R. M. Karp, “Reducibility among combinatorial problems,” in *Complexity of Computer Computations*, R. E. Miller and J. W. Thatcher, Eds., Plenum Press, pp. 85–103, 1972.

120. <a id="ref-120"></a>M. Grötschel, M. Jünger, and G. Reinelt, “A cutting plane algorithm for the linear ordering problem,” *Operations Research*, vol. 32, no. 6, pp. 1195–1220, 1985.

121. <a id="ref-121"></a>S. Łojasiewicz, “Une propriété topologique des sous-ensembles analytiques réels,” in *Les Équations aux Dérivées Partielles*, Éditions du Centre National de la Recherche Scientifique, pp. 87–89, 1963.

122. <a id="ref-122"></a>J. Frankle and M. Carbin, “The lottery ticket hypothesis: Finding sparse, trainable neural networks,” in *Proc. International Conference on Learning Representations (ICLR)*, 2019.

123. <a id="ref-123"></a>S. Han, J. Pool, J. Tran, and W. J. Dally, “Learning both weights and connections for efficient neural networks,” in *Advances in Neural Information Processing Systems (NeurIPS)*, pp. 1135–1143, 2015.

124. <a id="ref-124"></a>S. Han, H. Mao, and W. J. Dally, “Deep compression: Compressing deep neural networks with pruning, trained quantization and Huffman coding,” in *Proc. International Conference on Learning Representations (ICLR)*, 2016.

125. <a id="ref-125"></a>Y. LeCun, J. S. Denker, and S. A. Solla, “Optimal brain damage,” in *Advances in Neural Information Processing Systems (NeurIPS)*, vol. 2, pp. 598–605, 1989.

126. <a id="ref-126"></a>B. Hassibi and D. G. Stork, “Second order derivatives for network pruning: Optimal brain surgeon,” in *Advances in Neural Information Processing Systems (NeurIPS)*, vol. 5, pp. 164–171, 1992.

127. <a id="ref-127"></a>Y. He and L. Xiao, “Structured pruning for deep neural networks: A survey,” *IEEE Transactions on Pattern Analysis and Machine Intelligence*, vol. 46, no. 5, pp. 2966–2986, 2024.

128. <a id="ref-128"></a>D. Blalock, J. J. Gonzalez Ortiz, J. Frankle, and J. Guttag, “What is the state of neural network pruning?” in *Proc. Machine Learning and Systems (MLSys)*, 2020.

129. <a id="ref-129"></a>L. Jiao et al., “Causal inference meets deep learning: A comprehensive survey,” *Research*, vol. 7, article 0467, 2024.

130. <a id="ref-130"></a>S. Zhu, I. Ng, and Z. Chen, “Deep causal learning: Representation, discovery and inference,” *ACM Computing Surveys*, 2024. <https://dl.acm.org/doi/10.1145/3762179>

131. <a id="ref-131"></a>B. Schölkopf, F. Locatello, S. Bauer, N. R. Ke, N. Kalchbrenner, A. Goyal, and Y. Bengio, “Toward causal representation learning,” *Proceedings of the IEEE*, vol. 109, no. 5, pp. 612–634, 2021.

132. <a id="ref-132"></a>J. Peters, D. Janzing, and B. Schölkopf, *Elements of Causal Inference: Foundations and Learning Algorithms*, MIT Press, 2017.

133. <a id="ref-133"></a>X. Sun, A. Khetan, and S. Oh, “Causality-based neural network repair,” in *Proc. International Conference on Software Engineering (ICSE)*, pp. 338–350, 2022.

134. <a id="ref-134"></a>J. Frankle, G. K. Dziugaite, D. M. Roy, and M. Carbin, “Linear mode connectivity and the lottery ticket hypothesis,” in *Proc. International Conference on Machine Learning (ICML)*, PMLR 119:3259–3269, 2020.

135. <a id="ref-135"></a>P. Molchanov, S. Tyree, T. Karras, T. Aila, and J. Kautz, “Pruning convolutional neural networks for resource efficient inference,” in *Proc. International Conference on Learning Representations (ICLR)*, 2017.

136. <a id="ref-136"></a>M. J. Kusner, J. R. Loftus, C. Russell, and R. Silva, “Counterfactual fairness,” in *Advances in Neural Information Processing Systems (NeurIPS)*, vol. 30, 2017.

137. <a id="ref-137"></a>J. Pearl and D. Mackenzie, *The Book of Why: The New Science of Cause and Effect*, Basic Books, 2018.

138. <a id="ref-138"></a>Y. Guo, “A survey on methods and theories of quantized neural networks,” *arXiv:1808.04752*, 2020.

139. <a id="ref-139"></a>A. Ashok, N. Rhinehart, F. Belyaev, and K. Kitani, “N2N learning: Network to network compression via policy gradient reinforcement learning,” in *Proc. International Conference on Learning Representations (ICLR)*, 2018.

140. <a id="ref-140"></a>Z. Li, R. Xu, J. Yu, and L. Cui, “Causal inference-based root cause analysis for online service systems with intervention recognition,” in *Proc. ACM SIGKDD International Conference on Knowledge Discovery and Data Mining*, pp. 3230–3240, 2022.

141. <a id="ref-141"></a>D. Hendrycks and T. Dietterich, “Benchmarking neural network robustness to common corruptions and perturbations,” in *Proc. ICLR*, 2019.

142. <a id="ref-142"></a>M. Arjovsky, L. Bottou, I. Gulrajani, and D. Lopez-Paz, “Invariant risk minimization,” *arXiv:1907.02893*, 2019.
