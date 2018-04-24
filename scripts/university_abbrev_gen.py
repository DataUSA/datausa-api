import pandas as pd
import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

df = pd.read_csv("schools.csv")
stop_words = set(stopwords.words('english')).union(set(["&", "-"]))


def abbrev(x):
    x = x.replace("-", " ")
    x = re.sub(r"('|:)", "", x)
    tokens = word_tokenize(x)
    filtered = [w[0] for w in tokens if w not in stop_words]
    return "".join(filtered).lower()


df['abbrev'] = df.name.apply(abbrev)
df.to_csv("school_abrevs.csv")
