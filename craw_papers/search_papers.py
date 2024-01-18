import re
import pandas as pd

year = 2023
column = 'title'
venue = 'neurips' # ['cvpr','iccv','naacl','acl','emnlp','neurips','icml','iclr']
match_all_key = True

df = pd.read_csv(f'{venue}{year}_full.csv')

# custom keywords
keywords = [['causal']]
ex_keywords = ['prompt','image','multimodal','bench','node','graph','vae',
               'diffusion','bandit','reinforce','language','pre-train',
               'off-poli','dataset','federate','video','scene','caption',
               'amorti']
ex_keywords = ['optimal']
'''
Keyword bank:
shift, robust, adversa, efficient, priva, shot, fair, safe, nois, defense, certif
perturb, transferability, distill, memory, fast
optimization, stochastic, bayesian, gradient, convex, minimax, convergence, constrain, black-box, minima, SGD, noise
combinatorial,bilevel,rate,local,linear,proximal,submodular
reinforcement learning, agent, arm, bandit, imitat
open-set, subset, coreset
former, quantiz
expla, interpret, are, you need, is, not, as, analysis, mechanistic
continual, online, lifelong, incremental, catastrophic forgetting, replay
represent
supervis, centric
domain, adaptation, test-time, adaptive, source-free
ensembl
ordinal
convergence
select, sampl
boost
bayes
project
information-theoretic (generalization bounds), information (bottleneck|decomposition), (mutual|partial) information
causal effect indentification/regularization, discovery, interventions, treatment, independence, inference, additive noise model, 
invariant causal structure, spurious correlation detection, surface similarity/correlation,
counter, counterfactual
calibrat, certain, epistemic, quantifi, confor, active, surrogate
temperature
search
retriev, translation, generation, question, answer, fact, check, name, entity, query, retriev, summar, lingual
prompt optimization/tuning/learning, soft prompt, instruction
unlearning, edit
knowledge, graph, multi-hop, typing, matching, disambiguation, temporal
nas, neural architecture search
cross-model, multi-teacher, adversarial, offline, online, response-based, feature-based, relation-based knowledge , self-distillation
magnitude, prun
lipschitz, ridge regression, lasso, least square, orthogonal
(kernel) density estimation, manifold learning, cluster, affinity propagation, covariance estimation, novelty/outlier detection
'''

def is_valid_string(input_string, list_A, list_B):
    # Check if none of the words in list B are present in the input string
    if any(word.lower() in input_string for word in list_B):
        return False
    # Check if any word in list A is present in the input string
    if list_A is None:
        return True
    for sublist in list_A:
        if all(word.lower() not in input_string for word in sublist):
            return False
    return True

matched = df[column].apply(lambda x: is_valid_string(x.lower(), keywords, ex_keywords))
df = df[matched > 0]

df['year'] = [year for i in range(len(df.index))]
df['venue'] = [venue.upper()+str(year)[-2:] if venue != 'neurips' else 'NeurIPS'+str(year)[-2:] for i in range(len(df.index))]

df[['title','venue']].to_csv(f'{venue}{year}_selective.csv', index=False)