rm(list=ls())
#setwd('/data/users/jiancheng.zhai/project/advertiser_cluster/bin')
getwd()

library(Matrix)
library(parallel)
library(skmeans)
library(slam)
library(cluster)
library(pvclust)
library(mclust)
library(flexclust)
options(scipen=200)
library(kknn)
library(reshape2)
library(scuba)
library(kernlab)

library(clValid)
source('../lib/utils.R')

calc.slihouette.func <- function(data.mat, data.cluster, lev=2) {
    diss <- daisy(as.matrix(data.mat))
    diss <- diss^lev
    s <- silhouette(data.cluster, diss)
#    plot(s)
    avr <- sum(s[,3])/nrow(s)
    return(avr)
}


stat.res.func <- function(data.set, clust, detail.file, visit.file) {
    ids <- rownames(data.set)
    clust.data <- as.data.frame(cbind(ids, clust))

    colnames(clust.data) <- c("company_id", "cluster")

    detail.data <- read.file.func(detail.file)

    colnames(detail.data) <- c("name", "class", "raw_data", "ad_id", "company_id")

    merge.data <- merge(clust.data, detail.data, by="company_id", all.x=T, all.y=F)


    visit.data <- read.file.func(visit.file)
    visit.data <- visit.data[ ,1:2]
    colnames(visit.data) <- c("company_id", "pyid")

    stat.uv <- tapply(visit.data$pyid, visit.data$company_id, FUN = function(x) length(unique(x)))
    stat.uv.data <- as.data.frame(stat.uv)
    colnames(stat.uv.data) <- c("uv")
    stat.uv.data$company_id <- row.names(stat.uv.data)
    merge.data <- merge(merge.data, stat.uv.data, by="company_id", all.x=T, all.y=F)

    return(merge.data[order(merge.data$cluster), ])
}


spectral.clustering.func <- function(var){
    sim.mat = var$mat
    clust.num = var$num
    n = nrow(sim.mat)

    K <- rowSums(sim.mat)
    D <- diag(K)
    inv.D <- diag(1/K)
    L <- diag(1, n) - sqrt(inv.D) %*% sim.mat %*% sqrt(inv.D)
    q <- eigen(L, symmetric=T)
    qq <- q$vectors[,nrow(sim.mat)]
    cls <- kmeans(qq, clust.num)

    ret <- list("mat"=qq, "cluster"=cls)
    return(ret)
}


try.cluster.num.func <- function(sim.matrix){
    cluster.num <- 2:10

    avr.list <- lapply(cluster.num, function(x) {
        var <- list("mat"=sim.matrix, "num"=x)
        ret <- spectral.clustering.func(var)
        avr <- calc.slihouette.func(ret$mat, ret$cluster$cl)
#        cast.cluster.plot.func(ret$mat, ret$cluster)
        return(avr)
    })
    avr.data <- do.call(rbind, avr.list)
    avr.data <- as.data.frame(cbind(cluster.num, avr.data))
    colnames(avr.data) <- c('num', 'sil')
    return(avr.data)

    ## plot(cluster.num, avr.data,
    ##      type="o",
    ##      xlab="Number of Cluster",
    ##      ylab="Silhouette Coefficient")
}

dist.pair.to.dist.matrix <- function(comp.distance.data){
    dd1 <- acast(comp.distance.data, V1~V2, fill=0)
    dd2 <- acast(comp.distance.data, V2~V1, fill=0)
    a = colnames(dd1)[!colnames(dd1) %in% colnames(dd2)]
    b = colnames(dd2)[!colnames(dd2) %in% colnames(dd1)]
    add1 = t(data.frame(c(a,a,0)))
    add2 = t(data.frame(c(b,b,0)))

    add1[,3] <- as.numeric(add1[,3])
    add2[,3] <- as.numeric(add2[,3])

    r = rbind(comp.distance.data, add1, add2)
    r$V3 <- as.numeric(r$V3)
    dd1 <- acast(r, V1~V2, fill=0)
    dd2 <- acast(r, V2~V1, fill=0)
    dd <- dd1+dd2
    return(dd)

}

dist.matrix.to.similar.matrix <- function(dist.matrix){
    std.data <- sd(dist.matrix)
    beta = 1
    similar.matrix <- apply(dist.matrix, 2, function(x){return(exp(-beta*x/std.data))})
    return(similar.matrix)
}

args <- commandArgs(T)
industry  <- args[1]

comp.distance.file <- paste0("../data/", industry, "/company_dist")
comp.distance.data <- read.file.func(comp.distance.file)

thresh.file <- paste0("../data/", industry, "/company_thresh_file")
thresh.list <- read.file.func(thresh.file)[,1]

comp.distance.data <- comp.distance.data[comp.distance.data[,1] %in% thresh.list, ]

comp.distance.data <- comp.distance.data[comp.distance.data[,2] %in% thresh.list, ]

dist.matrix <- dist.pair.to.dist.matrix(comp.distance.data)
similar.matrix <- dist.matrix.to.similar.matrix(dist.matrix)

# select best cluster num
avr.data <- try.cluster.num.func(similar.matrix) # wmd cosine
best.num <- avr.data[avr.data$sil==max(avr.data$sil),]$num

# use the best cluster num
var = list("mat"=similar.matrix, "num"=best.num)
cls <- spectral.clustering.func(var)

# stat cluster result
detail.file <- paste0("../data/", industry, "/detail")
visit.file <- paste0("../data/", industry, "/visit_data")
detail <- stat.res.func(similar.matrix,
                        cls$cluster$cluster,
                        detail.file,
                        visit.file)

res.file <- paste0("../data/", industry, "/cluster_result")
write.file.func(detail,
                res.file)
