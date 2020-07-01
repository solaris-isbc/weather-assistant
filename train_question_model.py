import os
from pprint import pprint
import spacy
import random
import csv

matrix = []

with open('question_model_training_data/training.csv') as f:
   reader = csv.reader(f, delimiter=';')
   matrix.append(list(reader))

training_data = []
training_data_strings = matrix[0]
categories = training_data_strings[0]
amount_of_training_examples = 37

def add_document_to_training_documents(document_text, category_name):
  document = [document_text,{}]
  for i in range(len(categories)):
    if categories[i] is category_name:
        document[1][categories[i]] = True
    else:
        document[1][categories[i]] = False
  training_data.append(document)

for j in range(len(categories)):
    for i in range(1,amount_of_training_examples):
        add_document_to_training_documents(training_data_strings[i][j], categories[j])

pprint(training_data)
nlp = spacy.blank("de")
category = nlp.create_pipe("textcat")

for cat in categories:
    category.add_label(cat)

nlp.add_pipe(category)

# Start the training
nlp.begin_training()

for itn in range(100):
    # See progress in training
    print(itn," %")
    # Shuffle the training data
    random.shuffle(training_data)
    losses = {}
    # Batch the examples and iterate over them
    for batch in spacy.util.minibatch(training_data, size=3):
        texts = [nlp(text) for text, entities in batch]
        annotations = [{"cats": entities} for text, entities in batch]
        nlp.update(texts, annotations, losses=losses, drop=0.001)

# Save model
output_dir=os.getcwd()+"/question_model"
print(output_dir)
nlp.to_disk(output_dir)

nlp_categorizer = spacy.load(output_dir)

while True:
    query = input("Query: ")
    query_doc = nlp_categorizer(query)
    docs = query_doc.cats
    categorized_label = max(docs, key=docs.get)
    print(categorized_label," , [OTHERS: ",docs, "]")