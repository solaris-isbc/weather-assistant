import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from nltk.corpus import stopwords
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import LogisticRegression
from nltk.stem.snowball import SnowballStemmer
import pickle

df = pd.read_csv('question_model_training_data/training.csv')

def clean_text(text):
    text = text.lower() #lowercase the query
    text = ' '.join(word for word in text.split() if word not in stopword_list)  # delete stopwors from text
    text = ' '.join(stemmer.stem(word) for word in text.split())
    return text

stopword_list = set(stopwords.words('german'))
stemmer = SnowballStemmer("german")
df['post'] = df['post'].apply(clean_text)
posts = df.post
tags = df.tag

nb = Pipeline([('vect', CountVectorizer()),('tfidf', TfidfTransformer()),('clf', LogisticRegression(n_jobs=1, C=1e5))])
nb.fit(posts, tags)

with open('question_model.pkl','wb') as f:
    pickle.dump(nb,f)