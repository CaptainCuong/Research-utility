import pandas as pd

year = 2023
choice = "full" # ["selective","full"]
venue = "iclr"
'''
'all'
'unified'
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

# Create a DataFrame from your data
if choice == "full":
    df = pd.read_csv(f'{venue}{year}_full.csv')
else:
    df = pd.read_csv(f'{venue}_selective.csv')

# Drop rows with NaN values
df.dropna(inplace=True)

# Split authors into a list of authors, just take the first and last authors
df['authors'] = df['authors'].apply(lambda x: [x.split(', ')[0].strip(),x.split(', ')[-1].strip()] if ',' in x else [x.split(', ')[0].strip()])

# Flatten the list of authors and count the occurrences
authors_count = df.explode('authors')['authors'].value_counts()

# Sort the authors by the number of papers
authors_count = authors_count.sort_values(ascending=False)

print(authors_count)
if choice == "full":
    authors_count.to_csv(f'{venue}{year}_author_count.csv')
else:
    authors_count.to_csv(f'{venue}_author_count.csv')