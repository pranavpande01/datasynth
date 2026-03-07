import spacy

nlp = spacy.load("en_core_web_trf")

text = "Karim's near Jama Masjid serves amazing kebabs."

doc = nlp(text)

for ent in doc.ents:
    print(ent.text, ent.label_)