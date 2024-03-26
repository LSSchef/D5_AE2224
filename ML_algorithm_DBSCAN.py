from calculate_parameters import parameters
from numpy import unique
from numpy import where
from matplotlib import pyplot
from sklearn.datasets import make_classification
from sklearn.cluster import DBSCAN

# initialize the data set we'll work with
training_data=parameters(1000)
# define the model
dbscan_model = DBSCAN(eps=0.25, min_samples=4)

# train the model
dbscan_model.fit(training_data)

# assign each data point to a cluster
dbscan_result = dbscan_model.fit_predict(training_data)

# get all of the unique clusters
dbscan_cluster = unique(dbscan_result)

# plot the DBSCAN clusters
for dbscan_cluster in dbscan_cluster:
    # get data points that fall in this cluster
    index = where(dbscan_result == dbscan_cluster)
    # make the plot
    for i in index[0]:
        pyplot.scatter(training_data[i][4], training_data[i][0])
# show the DBSCAN plot
pyplot.show()