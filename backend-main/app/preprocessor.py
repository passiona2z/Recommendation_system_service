import pandas as pd
import requests
import sys
from tqdm import tqdm
import time

# url
def add_url(row): 

    return f"http://www.imdb.com/title/tt{row}/"


# rating
def add_rating(df):

    ratings_df = pd.read_csv('data/ratings.csv')
    ratings_df['movieId'] = ratings_df['movieId'].astype(str)

    agg_df = ratings_df.groupby('movieId').agg(
        rating_count=('rating', 'count'),
        rating_avg=('rating', 'mean'))

    rating_added_df = df.merge(agg_df, on='movieId')

    return rating_added_df


# poster
def add_poster(df):

    # Here's an example API request:
    # https://api.themoviedb.org/3/movie/550?api_key=''

    api_key = '' # need api_key

    for i, row in tqdm(df.iterrows(), total=df.shape[0]):

        
        tmdb_id = row["tmdbId"]
        tmdb_url = f"https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={api_key}"
        result = requests.get(tmdb_url)

        # final url : https://image.tmdb.org/t/p/original/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg 
        #             https://image.tmdb.org/t/p/original/gPbM0MK8CP8A174rmUwGsADNYKD.jpg

        try:
            df.loc[i, "poster_path"] = "https://image.tmdb.org/t/p/original" + result.json()['poster_path']
            time.sleep(0.1)

        except :
            # toy story poster as default
            df.loc[i, "poster_path"] = "https://image.tmdb.org/t/p/original/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg"
        
    return df


# main
if __name__ == "__main__" :
    
    movies_df = pd.read_csv('./data/movies.csv')
    movies_df['movieId'] = movies_df['movieId'].astype(str)
    links_df = pd.read_csv('./data/links.csv', dtype=str)

    merged_df = movies_df.merge(links_df, on='movieId', how='left')
    merged_df['url'] = merged_df['imdbId'].apply(lambda x : add_url(x))
    
    result_df = add_rating(merged_df)

    result_df['poster_path'] = None
    result_df = add_poster(result_df)

    result_df.to_csv("./data/movies_final.csv", index=None)