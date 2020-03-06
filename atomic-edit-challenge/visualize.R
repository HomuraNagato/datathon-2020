library('ggplot2')

getwd()
setwd('C:/Users/homur/OneDrive/NovaCrystalis/moonPrism/datathon-2020/atomic-edit-challenge/')

S2 <- read.csv('kmeans_result.csv', header=TRUE)
colnames(S2)

plt <- ggplot(S2, aes(phrases,kmeans_prediction)) + geom_point()

plt