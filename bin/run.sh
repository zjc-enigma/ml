industry="家装"
thresh=0.75

# python get_company_id.py $industry

# python get_company_user_visit_data.py $industry "{2016/01/01,2016/01/09,2016/01/18}"

# Rscript filter_by_thresh.R $industry $thresh

# python parse_company_user_visit.py $industry

# python word2vec.py ../data/$industry/user_file ../data/$industry/user_model ../data/$industry/user_vector

# python train_word2vec_model.py $industry

# python calc_wmd_dist_matrix.py $industry

Rscript calc_cluster.R $industry
