import csv
import os
import spacy
from irrelevance_detection import irrelevance_detector as id

output_dir = os.getcwd()+"/question_model"
nlp2 = spacy.load(output_dir)

matrix = []

with open('question_model_training_data/evaluation.csv') as f:
   reader = csv.reader(f, delimiter=';')
   matrix.append(list(reader))

matrix = matrix[0]

num_of_docs_predicted_correctly = 0
for i in range(100):
    query = matrix[i][0]
    doc2 = nlp2(query)
    docs = doc2.cats
    print("-----")
    print(query)
    if docs[max(docs, key=docs.get)] < 0.99999 and id.query_has_relevant_tokens(query) is False:
        print("Predicted: ", "NONE")
        if "NONE" == matrix[i][1]:
            num_of_docs_predicted_correctly = num_of_docs_predicted_correctly + 1
    else:
        if max(docs, key=docs.get) == matrix[i][1]:
            num_of_docs_predicted_correctly = num_of_docs_predicted_correctly + 1
        else:
            print("wrong prediction!")
            print(id.query_has_relevant_tokens(query))
        print("Predicted: ",max(docs, key=docs.get),docs[max(docs, key=docs.get)])

    print("True: ",matrix[i][1])
    print("-----")
    print(max(docs, key=docs.get),matrix[i][1])
    #pprint(docs)
print(num_of_docs_predicted_correctly)

while True:
    query = input("Query: ")
    print(query)
    doc2 = nlp2(query)
    print(nlp2.pipeline, nlp2.vocab)
    docs = doc2.cats
    print("IS:",max(docs, key=docs.get))
    print(doc2.cats)