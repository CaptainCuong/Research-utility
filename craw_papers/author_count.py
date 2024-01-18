import pandas as pd

year = 2019
venue = "aaai"
'''
[acl,emnlp,naacl,eacl,
neurips,icml,iclr,
cvpr,iccv,wacv,
aaai,ijcai,uai,
aistats]
'''

# Create a DataFrame from your data
df = pd.read_csv(f'{venue}{year}_full.csv')

# Split authors into a list of authors
df['authors'] = df['authors'].str.split(', ')

# Flatten the list of authors and count the occurrences
authors_count = df.explode('authors')['authors'].value_counts()

# Sort the authors by the number of papers
authors_count = authors_count.sort_values(ascending=False)

print(authors_count)
authors_count.to_csv(f'{venue}{year}_author_count.csv')