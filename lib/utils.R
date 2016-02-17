options(scipen=200)

read.file.func <- function(file.path){
    d <- read.csv(file=file.path,
                  header=F,
                  quote="",
                  stringsAsFactors=F,
                  sep='\t')

    return(d)
}



merge.by.col.func <- function(clk.data, cvt.sub,
                              col.list){
    m.data <- merge(clk.data,
                    cvt.sub,
                    by=col.list,
                    all=F)
    return(m.data)
}

write.file.func <- function(res.data,
                            res.file){

    write.table(res.data,
                file=res.file,
                col.names=F,
                row.names=F,
                sep='\t',
                quote=F)


}



shuffle.by.row.func <- function(src.data){

    res.data <- src.data[sample(nrow(src.data),
                                nrow(src.data),
                                replace=F), ]
    return(res.data)

}
