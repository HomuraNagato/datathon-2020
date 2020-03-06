
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.manifold import TSNE

train = ["is this good?", "this is bad", "some other text here", "i am hero", "blue jeans", "red carpet", "red dog",
     "blue sweater", "red hat", "kitty blue"]

vect = TfidfVectorizer()  
X = vect.fit_transform(train)
clf = KMeans(n_clusters=3)
data = clf.fit(X)
centroids = clf.cluster_centers_
print("len:", len(centroids), len(centroids[0]))
print("centroids:\n", centroids)
