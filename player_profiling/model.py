from sklearn.cluster import KMeans
from sklearn.cluster import SpectralClustering


def initialize_model_kmeans(n_clusters = 32):
    '''
    Function to return initialized model with Kmeans
    '''

    model = KMeans(n_clusters = n_clusters)
    return model

def initialize_model_spectral(n_clusters = 32, assign_labels = 'kmeans', affinity = 'nearest_neighbors', n_init = 5):
    '''
    Function to return initialized model with Spectral Clustering
    '''

    model = SpectralClustering(n_clusters = n_clusters,
                               assign_labels = assign_labels,
                               affinity = affinity,
                               n_init = n_init,
                               n_jobs=-1)
    return model

def fit_model(model, data):
    '''
    Function to return fitted model
    '''

    fitted_model = model.fit(data)
    return fitted_model
