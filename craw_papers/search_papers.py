import re
import os
import pandas as pd

column = 'title'
venues = ['aaai','ijcai','uai']
venues = ['nips','icml','iclr']
venues = ['atal']
venues = ['cvpr','eccv','iccv','wacv']
venues = ['aaai']
venues = ['acl','naacl','coling','eacl','conll','emnlp']
venues = ['csur','pami','ijcv','tip','tsp','tkde','tnn','paa','tmi']
venues = ['all']
time_all = [2020,2024]
assert time_all[1] >= time_all[0]

'''
'all'
'sigmod','pods','vldb','icde', # Database
'www','wsdm', # World Wide Web
'acl','naacl','coling','eacl','conll','emnlp', # NLP
'kdd','icdm','cikm','pkdd','pakdd','sdm', # Data Mining
'sigir','jcdl','ecir','icadl', # Information Retrieval
'aaai','ijcai','uai','aistats','ecai', # Artificial Intelligence
'mm', # Multimedia
'cvpr','iccv','eccv','wacv', # Computer Vision
'nips','icml','iclr', # Machine Learning
'interspeech','icassp' # Speech
'sp','tifs','ccs','uss','ndss', # Security
'''                

# custom keywords
# keywords = [['optimal'],['transp'],['robust','adver','attack']]
keywords = [['adversarial'],['bandit','reinfor','agent']]
keywords = [['gromov'],['wasserstein']]
keywords = [['few'],['shot'],['robust']]
keywords = [['density'],['estima']]
keywords = [['advers'],['robust']]
keywords = [['knowledge']]
keywords = [['explor'],['the'],['role']]
keywords = [['advers'],['robust']]
keywords = [['machine'],['transla']]
keywords = [['reprogra']]
keywords = [['graph'],['robust']]
keywords = [['low'],['resour']]
keywords = [['detection']]
keywords = [['energy'],['base']]
keywords = [['causal'],['model']]
keywords = [['path'],['robust']]
keywords = [['fourier']]
keywords = [['vision'],['language']]
keywords = [['adver'],['defen']]
keywords = [['prompt'],['robust']]
keywords = [['causal','treatment','confound','exchangeab','unmeasured','instrumental','survival']]
keywords = [['priva']]
keywords = [['weak'],['superv']]
keywords = [['bias','fair']]
keywords = [['efficie','fast']]
keywords = [['diffu'],['robu']]
keywords = [['gan','generative adver']]
keywords = [['retriev'],['augment']]
keywords = [['implicit'],['function']]
keywords = [['multi'],['teacher']]
keywords = [['compre'],['read']]
keywords = [['prun','distil','quantiz','low-ran','factori']]
keywords = [['multi'],['task'],['knowledge'],['distil']]
keywords = [['name'],['entity'],['increme']]
keywords = [['knowledge'],['distil']]
keywords = [['increment'],['learn'],['few'],['shot']]
keywords = [['adver','robust'],['class'],['increme']]
keywords = [['online'],['distil']]
keywords = [['decoup'],['distil'],['robust']]
keywords = [['co-train','cotrain']]
keywords = [['bias','fair'],['quantiz']]
keywords = [['data'],['augme']]
keywords = [['distribution'],['shift']]
keywords = [['resampling']]
keywords = [['trade'],['off']]
keywords = [['importanc'],['sampl']]
keywords = [['adversari'],['augment']]
keywords = [['generative adversarial network','gan']]
keywords = [['data'],['free']]
keywords = [['data-free'],['adver','robust']]
keywords = [['bias','fair']]
keywords = [['fake'],['news']]
keywords = [['influence'],['function']]
keywords = [['multi-task','multitask']]
keywords = [['whether','what',' is ','does','what','how','when','who','where','wrong','are','was ','were ']]
keywords = [['free'],['lunch']]
keywords = [['bias'],['linear']]
keywords = [['prun','distil','quantiz','low-ran','factori','low rank'],['robus','advers']]
keywords = [['prun','distil','quantiz','low-ran','factori','low rank']]
keywords = [['interpre','influence','explain','explana','attribution','lime','abduct','induct','mechanist','counterfac','elicit']]
keywords = [['truthf','faithf','halluci']]
keywords = [['continual']]
keywords = [['detect','classifi'],['certain']]
keywords = [['dynamic'],['detect','classifi']]
keywords = [['generated'],['detect']]
keywords = [['uncertain'],['detect','classifi']]
keywords = [['uncertain']]
keywords = [['bias'],['detect','classifi']]
keywords = [['causal'],['detect','classifi']]
keywords = [['uncertain'],['estimate','quantif']]
keywords = [['cross-domain'],['classification','detection']]
keywords = [['causal','treatment','confound','exchangeab','unmeasured','instrumental','survival','interven']]
keywords = [['ductive','duction']]
keywords = [['generation']]
keywords = [['mixture'],['expert']]
keywords = [['composi']]
keywords = [['detect','classifi']]
keywords = [['causal'],['interven']]
keywords = [['error'],['correct']]
keywords = [['simulat']]
keywords = [['distill'],['knowledge'],['adver']]
keywords = [['continual'],['attack']]
keywords = [['increme','continual']]
keywords = [['collapse']]
keywords = [['continual'],['advers','robust']]
keywords = [['continual'],['cross-domain']]
keywords = [['continual'],['adversa']]
keywords = [['black'],['optimiz']]
keywords = [['adaptation'],['classifi','detect']]
keywords = [['increme','continual'],['classif','detection']]
keywords = [['bayesian']]
keywords = [['survey'],['event','timeline','diffusion']]
keywords = [['survey'],['continual']]
ex_keywords = ['prompt','image','multimodal','bench','node','graph','vae',
               'diffusion','bandit','reinforce','language','pre-train',
               'off-poli','dataset','federate','video','scene','caption',
               'amorti']
ex_keywords = []
'''
Keyword bank:
shift, robust, adversa, efficient, priva, shot, fair, safe, nois, defense, certif
perturb, transferability, distill, memory, fast
optimization, stochastic, bayesian, gradient, convex, minimax, convergence, constraint
black-box, minima, noise, gradient clipping, overparameterized, stepsize
(local|decentralized|distributed|private|adaptive|asynchronous|implicit regularization) SGD, SGD (noise|dynamics|momentum)
combinatorial,bilevel,rate,local,linear,proximal,submodular
reinforcement learning, agent, arm, bandit, imitat
simulate, modeling
open-set, subset, coreset
former, quantiz
expla, interpret, are, you need, is, not, as, analysis, mechanistic, shapley, lime, attribution, abduct, induct
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
correct, dropout
(attention|schema|semantic|response|feature|CAM|Question|task|pose|relation|self) guided
statistical (analysis|inference|rate|estimation|guarantees), statistically (Efficient|robust|significant|consistent|meaningful|optimal)
(unbalanced|robust|hierarchical|entropic|low-rank|near-) optimal transport, optimal transport (alignment|distances), optimal partial transport
sliced wasserstein, wasserstein (barycenters|gradient flow|distributionally robust)
information-theoretic (generalization bounds), information (bottleneck|decomposition), (mutual|partial) information
causal effect indentification/regularization, treatment, independence, additive noise model, causal mediation analysis
Event Causality Identification, linear causal models
causal (inference|discovery|reasoning|models|structure|analysis|interventions|estimation|representation|bayesian|discovery)
structural causal models, invariant causal structure, spurious correlation detection, surface similarity/correlation,
instrumental variable, survival analysis
(unobserved|latent) confounders
Counterfactual
(latent|instrumental|unobserved|control|causal) variable
Partially Observable Markov Decision Process(POMDPs), zero-sum markov games
(neural|gaussian) process, variational gaussian process
calibrat, certain, epistemic, quantifi, confor, active, surrogate
temperature
search
(adversarial|compositional|sample|sample|synthetic|generative|dynamic) data augmentation for (imbalance|long-tail)
retrival(-)augmented|augmentation
retriev, translation, generation, question, answer, fact, check, name, entity, query, retriev, summar, lingual
prompt optimization/tuning/learning, soft prompt, instruction
unlearning, edit
knowledge, graph, multi-hop, typing, matching, disambiguation, temporal
nas, neural architecture search
cross-model, adversarial, offline, online, response-based, feature-based, relation-based knowledge
(multi-teacher|online|adaptive|stochastic|decoupled|self|iterative|progressive|curriculum|global|structural|structured|intermediate layer|privileged) knowledge distillation
magnitude, prun
lipschitz, ridge regression, lasso, least square, orthogonal
(kernel) density estimation, manifold learning, cluster, affinity propagation, covariance estimation, novelty/outlier detection
'''

def extract_venue_and_year(filename):
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

def merge_csv_files(directory, venue):
    # Get a list of all CSV files in the directory
    if venue == "all":
        csv_files = [file for file in os.listdir(directory) if file.endswith('_full.csv')]
    else:
        csv_files = [file for file in os.listdir(directory) if file.endswith('_full.csv') and file.startswith(venue)]

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

match_all = 0
for venue in venues:
    print(venue)
    df = merge_csv_files('.', venue)
    if len(df.index) > 0:
        df = df.dropna(subset=[column])

        matched = df[column].apply(lambda x: is_valid_string(x.lower(), keywords, ex_keywords))
        print(f'Number of matches in {venue.upper()}: {matched.sum()}')
        match_all += matched.sum()
        df = df[matched > 0]

        df[['title','venue']].to_csv(f'{venue}_selective.csv', index=False)
print('-'*50)
print(f'Total number of matches: {match_all}')