import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from nltk.corpus import stopwords
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import LogisticRegression
from nltk.stem.snowball import SnowballStemmer
import pickle

df = pd.read_csv('question_model_training_data/training.csv')
stopword_list = set(stopwords.words('german'))
# Documentation of stemmer: https://www.nltk.org/howto/stem.html
stemmer = SnowballStemmer("german")

def clean_query(text):
    text = text.lower()  # lowercase the query
    text = ' '.join(word for word in text.split() if word not in stopword_list)  # delete stopwors from text
    text = ' '.join(stemmer.stem(word) for word in text.split())
    return text

df['post'] = df['post'].apply(clean_query)
posts = df.post
tags = df.tag

# Documentations we used for vector-representation of words/queries and logistic regression:
# [1] https://realpython.com/logistic-regression-python/
# [2] https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfTransformer.html
# [3] https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.CountVectorizer.html
# [4] https://stackoverflow.com/questions/10592605/save-classifier-to-disk-in-scikit-learn

nb = Pipeline(
    [('vect', CountVectorizer()), ('tfidf', TfidfTransformer()), ('lr', LogisticRegression(C=10, multi_class='ovr'))])
nb.fit(posts, tags)

with open('question_model.pkl', 'wb') as f:
    print("Model trained.")
    pickle.dump(nb, f)
