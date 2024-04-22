import pandas as pd
import numpy as np
from scipy.sparse import coo_matrix
from implicit.als import AlternatingLeastSquares
import pickle


# global
saved_model_fname = "./model/finalized_model.sav"
data_fname = "./data/ratings.csv"
item_fname = "./data/movies_final.csv"
weight = 10


# RS model
def model_train():
    ratings_df = pd.read_csv(data_fname)
    ratings_df["userId"] = ratings_df["userId"].astype("category")  # dtype : category
    ratings_df["movieId"] = ratings_df["movieId"].astype("category")

    # create a sparse matrix of all the users/repos
    '''
    This matrix should be a csr_matrix where 
    the rows of the matrix are the users, 
    the columns are the items liked that user, 
    and the value is the confidence that the user liked the item.
    '''

    rating_matrix = coo_matrix(
        (
            ratings_df["rating"].astype(np.float32),     # data
            (   
                ratings_df["userId"].cat.codes.copy(),  # row
                ratings_df["movieId"].cat.codes.copy()  # col 
                      
            ),
        )
    )

    als_model = AlternatingLeastSquares(
        factors=50, regularization=0.01, dtype=np.float64, iterations=50
    )

    als_model.fit(weight * rating_matrix)

    pickle.dump(als_model, open(saved_model_fname, "wb"))

    return als_model


# (CF) item_based : model_item_id <-> data_item_id
def calculate_item_based(model_item_id, items_dict,  n=11):

    loaded_model = pickle.load(open(saved_model_fname, "rb"))
    recs = loaded_model.similar_items(itemid=int(model_item_id), N=n)

    return [str(items_dict[id]) for id in recs[0]] # ID, 유사도


def item_based_recommendation(data_item_id):

    ratings_df = pd.read_csv(data_fname)
    ratings_df["userId"] = ratings_df["userId"].astype("category")
    ratings_df["movieId"] = ratings_df["movieId"].astype("category")
    movies_df = pd.read_csv(item_fname)

    items_dict = dict(enumerate(ratings_df["movieId"].cat.categories)) # {model item id : data item id} 

    try :
        model_item_id = ratings_df["movieId"].cat.categories.get_loc(int(data_item_id))
        result = calculate_item_based(model_item_id, items_dict)
    
        #result = [int(x) for x in result]
        result = [int(x) for x in result if x != data_item_id]
    
    except :
        result = []

    result_items = movies_df[movies_df["movieId"].isin(result)].to_dict("records")
    return result_items


# (CF) user_based : get dict_data
def calculate_user_based(user_items, items_dict):

    loaded_model = pickle.load(open(saved_model_fname, "rb"))
    
    # new user recommendation
    recs = loaded_model.recommend(
        userid=0, user_items=user_items, recalculate_user=True, N=10  # new user id : 0
    )
    return [str(items_dict[id]) for id in recs[0]] # {model item id : data item id} 


def build_matrix_input(input_rating_dict, items_dict):

    model = pickle.load(open(saved_model_fname, "rb"))
    
    # input rating list : <dict> {1: 4.0, 2: 3.5, 3: 5.0}
    item_ids = {r: i for i, r in items_dict.items()}  # (after) {data item id : model item id}

    mapped_idx = [item_ids[movie_id] for movie_id in input_rating_dict.keys() if movie_id in item_ids] # model item id
    data = [weight * float(rating) for rating in input_rating_dict.values()]


    rows = [0 for _ in mapped_idx]  # only 0
    shape = (1, model.item_factors.shape[0]) # (1,#)

                             # user  # item
    return coo_matrix((data, (rows, mapped_idx)), shape=shape).tocsr()


def user_based_recommendation(input_rating_dict):

    ratings_df = pd.read_csv(data_fname)
    ratings_df["userId"] = ratings_df["userId"].astype("category")
    ratings_df["movieId"] = ratings_df["movieId"].astype("category")
    movies_df = pd.read_csv(item_fname)

    items_dict = dict(enumerate(ratings_df["movieId"].cat.categories))

    input_matrix = build_matrix_input(input_rating_dict, items_dict)
    result = calculate_user_based(input_matrix, items_dict)

    result = [int(x) for x in result]
    result_items = movies_df[movies_df["movieId"].isin(result)].to_dict("records") # list filtering

    return result_items



if __name__ == "__main__" :

    model = model_train()
