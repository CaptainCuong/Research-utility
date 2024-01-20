import re
import os
import pandas as pd

year = 2023
column = 'title'
venue = 'all'
time_all = [2020,2023]
assert time_all[1] > time_all[0]
'''
[
all
acl,emnlp,naacl,eacl,
neurips,icml,iclr,
cvpr,iccv,wacv,
aaai,ijcai,uai,
aistats
]
'''

# custom keywords
keywords = [['optimal'],['transpo']]
ex_keywords = ['prompt','image','multimodal','bench','node','graph','vae',
               'diffusion','bandit','reinforce','language','pre-train',
               'off-poli','dataset','federate','video','scene','caption',
               'amorti']
ex_keywords = []
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
(unbalanced|robust|hierarchical|entropic) optimal transport, optimal transport (alignment|distances), optimal partial transport
sliced wasserstein, wasserstein (barycenters|gradient flow|distributionally robust)
information-theoretic (generalization bounds), information (bottleneck|decomposition), (mutual|partial) information
causal effect indentification/regularization, discovery, interventions, treatment, independence, inference, additive noise model, 
Partially Observable Markov Decision Process(POMDPs), zero-sum markov games
(neural|gaussian) process, variational gaussian process
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

def extract_venue_and_year(filename):
    flag = False
    if filename == 'iclr2020_full.csv':
        flag = True
    # Define a regular expression pattern to match the desired format
    pattern = re.compile(r'([a-zA-Z]+)(\d+)_full\.csv')

    # Use the pattern to match the filename and extract groups (venue and year)
    match = pattern.match(filename)

    if match:
        # Extract venue and year from the matched groups
        venue_ = match.group(1)
        year_ = int(match.group(2))  # Convert year to an integer
        return venue_, year_
    else:
        # Return None if the pattern doesn't match
        return None, None

def merge_csv_files(directory):
    # Get a list of all CSV files in the directory
    csv_files = [file for file in os.listdir(directory) if file.endswith('_full.csv')]

    # Check if there are any CSV files in the directory
    if not csv_files:
        print("No CSV files found in the specified directory.")
        return None

    # Initialize an empty DataFrame to store the merged data
    merged_data = pd.DataFrame()

    # Iterate through each CSV file and merge them into the DataFrame
    for csv_file in csv_files:
        venue_, year_ = extract_venue_and_year(csv_file)
        if not (year_ <= time_all[1] and year_ >= time_all[0]):
            continue
        file_path = os.path.join(directory, csv_file)
        df = pd.read_csv(file_path)
        df['venue'] = [venue_.upper()+str(year_)[-2:] if venue_ != 'neurips' else 'NeurIPS'+str(year_)[-2:] for i in range(len(df.index))]
        merged_data = pd.concat([merged_data, df], ignore_index=True)

    return merged_data

if venue == 'all':
    df = merge_csv_files('.')
else:
    df = pd.read_csv(f'{venue}{year}_full.csv')
df = df.dropna(subset=[column])

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
print(f'Number of match: {matched.sum()}')
df = df[matched > 0]

if venue != 'all':
    df['year'] = [year for i in range(len(df.index))]
    df['venue'] = [venue.upper()+str(year)[-2:] if venue != 'neurips' else 'NeurIPS'+str(year)[-2:] for i in range(len(df.index))]
    df[['title','venue']].to_csv(f'{venue}{year}_selective.csv', index=False)
else:
    df[['title','venue']].to_csv(f'all_selective.csv', index=False)