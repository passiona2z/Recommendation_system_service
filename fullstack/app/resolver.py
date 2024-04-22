import pandas as pd

item_fname = './data/movies_final.csv'


def random_items(n=10):

    movies_df = pd.read_csv(item_fname)
    result_items = movies_df.sample(n).to_dict("records")
    return result_items


def random_genres_items(genre, n=10):

    movies_df = pd.read_csv(item_fname)
    genre_df = movies_df[movies_df['genres'].apply(lambda x: genre in x.lower())]
    result_items = genre_df.sample(n).to_dict("records")
    
    return result_items