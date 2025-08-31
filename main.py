from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import re
from recommender import load_movie_data

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def clean_poster_url(raw_url):
    if pd.isna(raw_url):
        return ""
    match = re.search(r'\((.*?)\)', raw_url)
    if match:
        return match.group(1)
    return raw_url

# Load and clean movies on startup
movies_df = pd.read_csv("movies.csv")
movies_df["poster"] = movies_df["poster"].apply(clean_poster_url)

# Split genres by comma, lowercase, and strip whitespace from each genre
movies_df['genre_list'] = movies_df['genre'].str.lower().str.split(',')
movies_df['genre_list'] = movies_df['genre_list'].apply(lambda genres: [g.strip() for g in genres])


@app.get("/recommend")
def recommend(
    type: str = Query(..., description="search by 'movie title' or 'director'"),
    query: str = Query(..., description="movie title or director name"),
    n: int = Query(5, description="number of recommendations"),
):
    try:
        q_lower = query.lower()
        if type == "movie title":
            movie_row = movies_df[movies_df['title'].str.lower() == q_lower]
            if movie_row.empty:
                return {"movies": []}
            movie_row = movie_row.iloc[0]

            query_director = movie_row['director'].lower()
            query_genres = set(movie_row['genre_list'])

            def matches_criteria(row):
                if row['title'].lower() == q_lower:
                    return False  # exclude the queried movie itself
                same_director = row['director'].lower() == query_director
                genre_overlap = len(set(row['genre_list']).intersection(query_genres)) > 0
                return same_director or genre_overlap

            filtered = movies_df[movies_df.apply(matches_criteria, axis=1)]

            results = []
            for _, row in filtered.head(n).iterrows():
                results.append({
                    "title": row["title"],
                    "director": row.get("director", ""),
                    "genre": row.get("genre", ""),
                    "poster": row.get("poster", ""),
                    "rating": row.get("rating", ""),
                    "year": row.get("year", ""),
                    "duration": row.get("duration", ""),
                    "language": row.get("language", ""),
                })
            return {"movies": results}

        elif type == "director":
            director_movies = movies_df[movies_df['director'].str.lower() == q_lower]
            results = []
            for _, row in director_movies.head(n).iterrows():
                results.append({
                    "title": row["title"],
                    "director": row.get("director", ""),
                    "genre": row.get("genre", ""),
                    "poster": row.get("poster", ""),
                    "rating": row.get("rating", ""),
                    "year": row.get("year", ""),
                    "duration": row.get("duration", ""),
                    "language": row.get("language", ""),
                })
            return {"movies": results}

        else:
            return {"movies": []}

    except Exception as e:
        print(f"Error in /recommend endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))
