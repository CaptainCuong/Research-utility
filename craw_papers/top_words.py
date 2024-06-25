import pandas as pd
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter
import re
import os
import pandas as pd

years = [2020,2021,2022,2023,2024] # Just used for "full", not necessary for "selective"
column = 'title'
venues = ['www']
venues = ['naacl']
venues = ['acl','emnlp']
venues = ['nips','icml','iclr']
venues = ['acl','naacl','colingconf', 'eacl','emnlp']
'''
[
all,
acl,emnlp,naacl,eacl,
nips,icml,iclr,
cvpr,iccv,wacv,
aaai,ijcai,uai,
aistats
]
'''
rank_file = 'selective' # ['full','selective']
# assert not(rank_file == 'full' and venue == 'all'), 'Do not support search full for all venues'

def extract_venue_and_year(filename):
    # Define a regular expression pattern to match the desired format
    pattern = re.compile(r'([a-zA-Z0-9]+)(\d{4})')

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

def process_df(data):
    # Combine 'title' and 'authors' columns into a single column 'text'
    data['text'] = data['title']

    # Remove special characters and split into tokens
    data['text'] = data['text'].apply(lambda x: re.sub('[:"!?,.()-]', '', str(x).lower()).split(' '))

    # Count the occurrences of each word
    word_counts = Counter(word for words in data['text'] for word in words)

    # Print the most common words
    most_common_words = word_counts.most_common()
    word_list = []
    word_count = []
    for word, count in most_common_words:
        word_list.append(word)
        word_count.append(count)
    return word_list, word_count

unified_df = pd.DataFrame()
if "all" not in venues:
    for venue in venues:
        df = pd.DataFrame()
        if rank_file == "full":
            for year in years:
                if os.path.isfile(f'{venue}{year}_{rank_file}.csv'):
                    df = pd.concat([df, pd.read_csv(f'{venue}{year}_{rank_file}.csv')], ignore_index=True)
        else:
            if os.path.isfile(f'{venue}_{rank_file}.csv'):
                df = pd.concat([df, pd.read_csv(f'{venue}_{rank_file}.csv')], ignore_index=True)
        unified_df = pd.concat([unified_df,df], ignore_index=True)

        word_list, word_count = process_df(df)
        print(f'Most common words in {venue.upper()}:')
        for word, count in zip(word_list,word_count):
            print(f"{word}: {count}")
        print('-'*50)
        pd.DataFrame({'word':word_list,'count':word_count}).to_csv(f'{venue.lower()}_rank_keyword.csv',index=False)
else:
    csv_files = [file for file in os.listdir('.') if file.endswith(f'_{rank_file}.csv')]
    for csv_file in csv_files:
        venue_, year_ = extract_venue_and_year(csv_file)
        if year_ not in years:
            continue
        unified_df = pd.concat([unified_df, pd.read_csv(csv_file)], ignore_index=True)

word_list_unf, word_count_unf = process_df(unified_df)
if "all" not in venues:
    pd.DataFrame({'word':word_list_unf,'count':word_count_unf}).to_csv(f'unified_rank_keyword.csv',index=False)
else:
    pd.DataFrame({'word':word_list_unf,'count':word_count_unf}).to_csv(f'all_rank_keyword.csv',index=False)