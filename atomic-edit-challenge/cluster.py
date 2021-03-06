
#https://nlpforhackers.io/recipe-text-clustering/

import string
import collections
 
import nltk
#nltk.download('stopwords')
#nltk.download('punkt')

from nltk import word_tokenize
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
from sklearn.feature_extraction.text import TfidfVectorizer

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')
import seaborn as sns
sns.set(rc={'figure.figsize':(12,12)})
sns.set_style("white")

 
def process_text(text, stem=True):
    """ Tokenize text and stem words removing punctuation """
    #text = text.translate(None, string.punctuation)
    text = text.translate(string.punctuation)
    #print("text", text)
    tokens = word_tokenize(text)
    #print("process_text tokens", tokens)
 
    if stem:
        stemmer = PorterStemmer()
        tokens = [stemmer.stem(t) for t in tokens]
        #print("stemmer tokens:", tokens)

    return tokens
 
 
def cluster_texts(texts, n_clusters=3, return_type='dict'):
    """ Transform texts to Tf-Idf coordinates and cluster texts using K-Means """
    #vectorizer = TfidfVectorizer(tokenizer=process_text,
    #                             stop_words=stopwords.words('english'),
    #                             max_df=0.5,
    #                             min_df=0.1,
    #                             lowercase=True)
    vectorizer = TfidfVectorizer(tokenizer=process_text, lowercase=True, sublinear_tf=True)

    # embed string 
    X = vectorizer.fit_transform(texts)
    print("tokenized shape:", X.shape)

    # perform pca
    mu = 3
    pca = PCA(n_components=n_clusters * mu)
    X = pca.fit_transform(X.toarray())
    print("pca shape:", X.shape)

    # compute kmeans
    km_model = KMeans(n_clusters=n_clusters)
    X = km_model.fit_transform(X)
    

    print("kmeans shape:", X.shape)

    centroids = km_model.cluster_centers_
    centroids = km_model.transform(centroids)
    labels = km_model.labels_
    
    ''' dict of index to assigned cluster
    clustering = collections.defaultdict(list)
    if return_type == 'dict':
        for idx, label in enumerate(km_model.labels_):
            clustering[label].append(idx)
    '''
    
    return X, labels, centroids
    
def load_text(file_path, block_size=100, col='phrase'):
    S2 = pd.read_csv(file_path, sep='\t', chunksize=block_size, iterator=True)
    yield next(S2)[col]

def t_sne(X, centroids):
    '''
    collapse embedding down to two dimensions (n_components=2) for visualization
    '''
    # perform t_sne with centroids so x and y dimensions match
    XC = np.concatenate((X, centroids), axis = 0)
    #print("X_C shape:", X_C.shape)
    random_state = 1
    tsne_init = 'pca'  # chose 'random' or 'pca'
    tsne_perplexity = 20.0
    tsne_early_exaggeration = 4.0
    tsne_learning_rate = 1000
    tsne_model = TSNE(n_components=2, random_state=random_state, init=tsne_init, perplexity=tsne_perplexity,
         early_exaggeration=tsne_early_exaggeration, learning_rate=tsne_learning_rate)
    
    transformed_XC = tsne_model.fit_transform(XC)
    # vsplit (oddly?) separates into three sub-arrays
    null, transformed_X, transformed_centroids = np.vsplit(transformed_XC, [0, X.shape[0]])
    #print("transformed_X shape:\n", transformed_X.shape)
    #print("transformed_centroid shape:\n", transformed_centroids.shape)

    return transformed_X, transformed_centroids
    
def visualize_cluster(S2, centroids, n_clusters, index, save=True):
    """
    """

    fig, ax = plt.subplots()
    
    ax = sns.scatterplot(x='x', y='y', hue='label', palette=sns.color_palette("hls", 10), data=centroids, ax=ax, alpha=0.3, s=500, legend=False)
    ax = sns.scatterplot(x='x', y='y', hue='label', palette=sns.color_palette("hls", 10), data=S2, ax=ax, alpha=0.3, legend="full")

    #subset_text = np.random.choice(S2.shape[0], 10)
    S2 = S2.join(centroids, on='label', rsuffix='_c')
    S2['centroid_dist'] = np.sqrt((S2['x_c']-S2['x'])**2 + (S2['y_c']-S2['y'])**2)
    subset_t = S2.sort_values('centroid_dist', ascending=True).drop_duplicates('label', keep='first')
    print("subset_t:\n",subset_t.to_string())

    for line in range(0,subset_t.shape[0]):
        ax.text(subset_t['x'].iloc[line], subset_t['y'].iloc[line], subset_t['phrase'].iloc[line], horizontalalignment='center', size='medium', color='black', weight='semibold')

    '''
    for line in range(0, centroids.shape[0]):
        ax.text(centroids['x'].iloc[line], centroids['y'].iloc[line], centroids['phrase'].iloc[line], horizontalalignment='center', size='medium', color='black', weight='semibold')
    '''
    path = 'cluster_n' + format(n_clusters, '02d') + '_i' + format(index, '02d') + '.png'
    fig = ax.get_figure()
    fig.savefig(path)
    

 
if __name__ == "__main__":

    # load_text is both an iterator and a generator!
    block_size= 1000
    # base_sentence, phrase, edited_sentence
    col = 'phrase'
    articles_iterator = load_text('/mnt/c/Users/homur/Documents/hacker_data/wikiedits_english/insertions.tsv', block_size=block_size, col=col)
    n_clusters = 10
    index = 0

    for articles in articles_iterator:
        # load text and transform into clusters
        X, labels, centroids = cluster_texts(articles, n_clusters=n_clusters, return_type='list')
        # collapse clusters down to two dimension
        transformed_X, transformed_centroids = t_sne(X, centroids)
        
        # insert as dataframe
        S2 = pd.DataFrame( data = { 'phrase': articles,
                                    'label': labels,
                                    'x': transformed_X[:, 0],
                                    'y': transformed_X[:, 1] } )
        
        S2_centroid = pd.DataFrame(data = { 'phrase': [ 'center_' + format(i, '02d') for i in range(n_clusters) ],
                                            'label': [ i for i in range(n_clusters) ],
                                            'x': transformed_centroids[:, 0],
                                            'y': transformed_centroids[:, 1] } )

        print("articles head:\n", S2.head())
        print("centroids head:\n", S2_centroid.head())
        
        visualize_cluster(S2, S2_centroid, n_clusters, index, save=True)
        index += 1
        
        exit(0)
