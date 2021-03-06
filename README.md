
# Introduction

At the datathon event hosted by Brown Data Science during the weekend of February 22, 2020,
a dataset offered for analysis was wikiedits, gathered by Professor Pavlick of the Lunar lab
at Brown. This dataset included edits made on wikipedia including three variables, the original phrase, either an insertion or deletion phrase, and the edited phrase. The goal was to find something interesting about the types of edits made.

One possible analysis is to cluster the edits into groups to see if there are commonalities
among the sort of edits made. This is the goal of this project, begun during the datathon
and completed afterwards.

There are three major steps towards reaching this goal
 - vectorize the text into an embedding of shape [n_samples, embedding_size]
 - cluster the embedding vector into k-cluster [n_samples, k]
 - compress k-clusters down to two dimensions using t_sne [n_samples, 2]

Once this is done, a scatterplot can be produced to visualize the clusters.


# Vectorize text into embedding

Use sklearn's TfidVectorizer to convert a list of strings to an embedding vector.

TfidVectorizer first learns a vocabulary from input text = embedding_size. The formula to
calculate a word's tf-idf is below (reformated in probability terms):

 perhaps this comment will work? -->

<!--
\[
idf(t|d) = log(\frac{1 + n}{1 + df(t)}) + 1
\[
-->

<a href="https://www.codecogs.com/eqnedit.php?latex=idf(t|d)&space;=&space;log(\frac{1&space;&plus;&space;n}{1&space;&plus;&space;df(t)})&space;&plus;&space;1" target="_blank"><img src="https://latex.codecogs.com/gif.latex?idf(t|d)&space;=&space;log(\frac{1&space;&plus;&space;n}{1&space;&plus;&space;df(t)})&space;&plus;&space;1" title="idf(t|d) = log(\frac{1 + n}{1 + df(t)}) + 1" /></a>

<!-- \[
tf-idf(t|d) = df(t|d) * idf(t|d)
\] -->

<a href="https://www.codecogs.com/eqnedit.php?latex=tf-idf(t|d)&space;=&space;df(t|d)&space;*&space;idf(t|d)" target="_blank"><img src="https://latex.codecogs.com/gif.latex?tf-idf(t|d)&space;=&space;df(t|d)&space;*&space;idf(t|d)" title="tf-idf(t|d) = df(t|d) * idf(t|d)" /></a>

$df(t)$ is the document frequency of the token $t$, the number of documents that include the token $t$; the more documents with $t$, the larger the value this will be.

$df(t|d)$ is the document frequency of the token $t$ given the document $d$, the number of occurences $t$ occurs in $d$; the more $t$ occurs in $d$, the larger the value will be.

$idf(t|d)$ is the inverse document frequency of the token $t$ in the document $d$, $n$ is the number of documents; the more a token is included in more documents, the lower this value will be.

$tf-idf(t|d)$ is the output value of the token given a specific document; the more a token occurs in a single document and less in every other document will produce a larger value and similarly a token that occurs infrequently in a particular document, but occurs frequently in all documents will have a small value.

In sum, this weights additional value to unique tokens in specific documents.

This produces something similar to a word embedding, converting a list of text into a matrix
of word vectors of shape [n_samples, vocabulary_size=embedding_size].


# cluster word embedding using k-means

Now that we vectorized our text, we wish to cluster. k-means transforms a vector of shape
[n_samples, embedding_size] to [n_samples, k], where $k$ are the number of clusters. The
formula used by sklearn is below

<!-- \[
 \sum_{i=0}^{n} {min_{\mu_j \in C} (||x_i - \mu_j||^2)}
\] -->

<a href="https://www.codecogs.com/eqnedit.php?latex=\sum_{i=0}^{n}&space;{min_{\mu_j&space;\in&space;C}&space;(||x_i&space;-&space;\mu_j||^2)}" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\sum_{i=0}^{n}&space;{min_{\mu_j&space;\in&space;C}&space;(||x_i&space;-&space;\mu_j||^2)}" title="\sum_{i=0}^{n} {min_{\mu_j \in C} (||x_i - \mu_j||^2)}" /></a>

This formula attempts to separate samples by inertia, or the within-cluster sum-of-squares. The
algorithm computes centroids with a stopping value when the computed centroids move less than
some tolerance. However in higher dimensions this minimization algorithm tends to perform poorly.
To accomodate this, first run PCA to reduce dimensions to some value larger than the number of clusters,
and smaller than the number of dimensions, for example three times the size of k used.

# collapse to two dimensions using t-sne

t-distributed Stochastic Neighbor Embedding (t-sne) uses gradient descent to minimize the Kullback-Leibler divergence between
the joint probabilities of the collapsed embedding and the higher dimensional data. This cost function
is not convex, suggesting care should be done during initialization. Also, since this cost function is
both noisy and expensive to compute, we should reduce the number of input dimensions. Because we used
k-means < 50, this satisfies this constraint.

The full cost function is below

<!-- \[
 C = \sum_i {KL(P_i | Q_i)} = \sum_i \sum_j {p_{j|i} \log{\frac{p_{j|i}}{q_{j|i}}}} 
\] -->

<a href="https://www.codecogs.com/eqnedit.php?latex=C&space;=&space;\sum_i&space;{KL(P_i&space;|&space;Q_i)}&space;=&space;\sum_i&space;\sum_j&space;{p_{j|i}&space;\log{\frac{p_{j|i}}{q_{j|i}}}}" target="_blank"><img src="https://latex.codecogs.com/gif.latex?C&space;=&space;\sum_i&space;{KL(P_i&space;|&space;Q_i)}&space;=&space;\sum_i&space;\sum_j&space;{p_{j|i}&space;\log{\frac{p_{j|i}}{q_{j|i}}}}" title="C = \sum_i {KL(P_i | Q_i)} = \sum_i \sum_j {p_{j|i} \log{\frac{p_{j|i}}{q_{j|i}}}}" /></a>

$P_i$ is the conditional probability distribution over all other data points given data point (represented
as a vector of dimensional data) $x_i$. $Q_i$ is the conditional probability distribution over all other
data points given map point $q_i$.

<!-- \[
 p_{j|i} = \frac{e^{-||x_i-x_j||^2 / 2 \sigma_i^2 }}{\sum_{k \neq i} e^{-||x_i-x_k||^2 / 2 \sigma_i^2}}
\] -->

<a href="https://www.codecogs.com/eqnedit.php?latex=p_{j|i}&space;=&space;\frac{e^{-||x_i-x_j||^2&space;/&space;2&space;\sigma_i^2&space;}}{\sum_{k&space;\neq&space;i}&space;e^{-||x_i-x_k||^2&space;/&space;2&space;\sigma_i^2}}" target="_blank"><img src="https://latex.codecogs.com/gif.latex?p_{j|i}&space;=&space;\frac{e^{-||x_i-x_j||^2&space;/&space;2&space;\sigma_i^2&space;}}{\sum_{k&space;\neq&space;i}&space;e^{-||x_i-x_k||^2&space;/&space;2&space;\sigma_i^2}}" title="p_{j|i} = \frac{e^{-||x_i-x_j||^2 / 2 \sigma_i^2 }}{\sum_{k \neq i} e^{-||x_i-x_k||^2 / 2 \sigma_i^2}}" /></a>

This says $p_{j|i}$ the conditional probability data point $x_i$ would choose $x_j$ as its neighbor under
a Gaussian centered at $x_i$. For nearby points, this probability will be larger, and for points far away,
this probability will be smaller. We set $x_{i|i} = 0$.

<!-- \[
 q_{j|i} = \frac{e^{-||y_i-y_j||^2  }}{\sum_{k \neq i} e^{-||y_i-y_k||^2 }}
\] -->

<a href="https://www.codecogs.com/eqnedit.php?latex=q_{j|i}&space;=&space;\frac{e^{-||y_i-y_j||^2&space;}}{\sum_{k&space;\neq&space;i}&space;e^{-||y_i-y_k||^2&space;}}" target="_blank"><img src="https://latex.codecogs.com/gif.latex?q_{j|i}&space;=&space;\frac{e^{-||y_i-y_j||^2&space;}}{\sum_{k&space;\neq&space;i}&space;e^{-||y_i-y_k||^2&space;}}" title="q_{j|i} = \frac{e^{-||y_i-y_j||^2 }}{\sum_{k \neq i} e^{-||y_i-y_k||^2 }}" /></a>

Similarly, q_{j|i} is the conditional probability map point $y_i$ would choose $y_j$ as its neighbor.

Together, If the map points $y_i$ and $y_j$ correctly model the similarity between the higher dimensional
data points $x_i$ and $x_j$, $p_{j|i}$ and $q_{j|i}$ will be similar as well, resulting in a lower cost.

# Visualization

Putting it all together, a visualization of the resulting data after t_sne has been applied is shown below.
To save on computation, only the first 1000 phrases in the wiki_edits insertions file have been computed.

![cluster_n10_i00_saved.png](atomic-edit-challenge/cluster_n10_i00_saved.png?raw=true "cluster_n10" )

The colors represent different clusters. Some example text has been included to somewhat show the text in
the groups. We can see that with ten clusters, some groups do appear. The number of members in each
group is unbalanced and some groups don't cluster nicely, such as cluster 0. This could be due to
limitations in visualizing a higher dimensional data, adjusts to variables used in the algorithms,
or inherit in the original data.

In summary, tf-idf, PCA, k-means, and t-sne we performed on textual data to cluster and visualize the data.