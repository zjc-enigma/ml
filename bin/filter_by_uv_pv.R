rm(list=ls())
#setwd('/data/users/jiancheng.zhai/project/advertiser_cluster/bin')
getwd()
options(scipen=200)
source('../lib/utils.R')

args <- commandArgs(T)
industry  <- args[1]
percent <- args[2]

visit.file <- paste0("../data/", industry, "/visit_data")
visit.data <- read.file.func(visit.file)
visit.data <- visit.data[ ,1:2]
colnames(visit.data) <- c("company_id", "pyid")

stat.uv <- tapply(visit.data$pyid, visit.data$company_id, FUN = function(x) length(unique(x)))
stat.uv.data <- as.data.frame(stat.uv)
stat.uv.data$company_id <- row.names(stat.uv.data)

stat.pv <- tapply(visit.data$pyid, visit.data$company_id, FUN = function(x) length(x))
stat.pv.data <- as.data.frame(stat.pv)
stat.pv.data$company_id <- row.names(stat.pv.data)

merge.data <- merge(stat.pv.data, stat.uv.data, by=c("company_id"), all.x=F)

quan.uv <- quantile(stat.uv, probs=percent)
quan.pv <- quantile(stat.pv, probs=percent)

merge.data <- merge.data[merge.data$stat.pv >= quan.pv & merge.data$stat.uv >= quan.uv, ]

company.thresh.file <- paste0("../data/", industry, "/company_thresh_file")
write.file.func(merge.data, company.thresh.file)
