import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics.pairwise import cosine_similarity
import re

def clean_poster_url(raw_url):
    if pd.isna(raw_url):
        return ""
    match = re.search(r'\((.*?)\)', raw_url)
    if match:
        return match.group(1)
    return raw_url

def load_movie_data():
    movies = pd.read_csv("movies.csv")
    movies['poster'] = movies['poster'].apply(clean_poster_url)  # Clean the poster URLs
    movies['genre_list'] = movies['genre'].str.split('|')
    return movies

def build_genre_similarity(movies):
    mlb = MultiLabelBinarizer()
    genre_matrix = mlb.fit_transform(movies['genre_list'])
    genre_sim = cosine_similarity(genre_matrix, genre_matrix)
    return genre_sim

def recommend_by_genre(movie_name, n=5):
    movies = load_movie_data()
    genre_sim = build_genre_similarity(movies)

    idx_list = movies[movies['title'].str.lower() == movie_name.lower()].index.tolist()
    if not idx_list:
        return []
    idx = idx_list[0]

    sim_scores = list(enumerate(genre_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:n+1]

    results = []
    for i, score in sim_scores:
        row = movies.iloc[i]
        results.append({
            "title": row["title"],
            "director": row.get("director", ""),
            "genre": row["genre"],
            "poster": row["poster"],
            "rating": row["rating"],
            "year": row.get("year", ""),
            "duration": row.get("duration", ""),
            "language": row.get("language", ""),
            "link": row.get("link", ""),
            "similarity": round(score, 3)
        })
    return results
