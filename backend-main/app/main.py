from typing import List, Optional
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from resolver import random_items, random_genres_items
from rs import item_based_recommendation, user_based_recommendation


app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
    "https://passiona2z.github.io/recommendation-project",
    "https://passiona2z.github.io",
]

app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
)




@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/all/")
async def all_movies():

    random_result = random_items()
    return {"result": random_result}


@app.get("/genres/{genre}")
async def genre_movies(genre: str):

    random_genres_result = random_genres_items(genre)

    return {"result": random_genres_result}


@app.get("/user-based/")
async def user_based(params: Optional[List[str]] = Query(None)): # 본질적으로 리스튼데 쿼리형태로 받겠다는

    try :
    
        input_ratings_dict = {int(x.split(":")[0]) : float(x.split(":")[1]) for x in params} # make_dict

        result = user_based_recommendation(input_ratings_dict)
    
        return {'result':result}
        
    except :

        return {"message": "please valid rating"}
    
    # http://127.0.0.1:8000/user-based/?params=2571:3&params=6365:4
    

@app.get("/item-based/{item_id}")
async def item_based(item_id: str):

    item_based_result = item_based_recommendation(item_id)
    return {"result": item_based_result}
