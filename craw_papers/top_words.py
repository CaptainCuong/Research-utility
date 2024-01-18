import pandas as pd
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter
import re
import pandas as pd

year = 2022
column = 'title'
venue = 'neurips' # ['cvpr','acl','emnlp','neurips','icml','iclr']
rank_file = 'selective' # ['full','selective']

df = pd.read_csv(f'{venue}{year}_{rank_file}.csv')

# Combine 'title' and 'authors' columns into a single column 'text'
df['text'] = df['title']

# Tokenize the words and remove stop words
stop_words = set(stopwords.words('english'))
df['text'] = df['text'].apply(lambda x: [word.lower() for word in word_tokenize(x) if word.isalnum() and word.lower() not in stop_words])

# Count the occurrences of each word
word_counts = Counter(word for words in df['text'] for word in words)

# Print the most common words
most_common_words = word_counts.most_common()
word_list = []
word_count = []
for word, count in most_common_words:
    word_list.append(word)
    word_count.append(count)
    print(f"{word}: {count}")

pd.DataFrame({'word':word_list,'count':word_count}).to_csv(f'{venue.lower()}{year}_rank_keyword.csv',index=False)