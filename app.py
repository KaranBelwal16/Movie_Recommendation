import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import re

st.title("🎬 Movie Recommendation Search")

search_type = st.radio("Search by:", ("Movie Title", "Director"))

query_input = st.text_input(f"Enter {search_type}")

def clean_poster_url(raw_url):
    if not raw_url:
        return ""
    match = re.search(r'\((.*?)\)', raw_url)
    if match:
        return match.group(1)
    return raw_url

def get_image_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        return img
    except Exception:
        return None

if st.button("Search"):
    if not query_input.strip():
        st.warning(f"Please enter a {search_type.lower()} to search.")
    else:
        with st.spinner(f"Searching movies by {search_type.lower()}..."):
            try:
                backend_url = "http://localhost:8000/recommend"
                params = {
                    "type": search_type.lower(),
                    "query": query_input.strip()
                }
                response = requests.get(backend_url, params=params)

                if response.status_code == 200:
                    movies = response.json().get("movies", [])
                    if movies:
                        st.success(f"Found {len(movies)} recommendation(s)")
                        for movie in movies:
                            poster_url = clean_poster_url(movie.get("poster"))
                            img = get_image_from_url(poster_url)
                            if img:
                                st.image(img, width=120)
                            else:
                                st.text("No image available")

                            st.write(f"**Title:** {movie.get('title')}")
                            st.write(f"**Director:** {movie.get('director')}")
                            st.write(f"**Genre:** {movie.get('genre')}")
                            st.write(f"**Rating:** {movie.get('rating')}")
                            st.write(f"**Year:** {movie.get('year')}")
                            st.write(f"**Duration:** {movie.get('duration')}")
                            st.write(f"**Language:** {movie.get('language')}")
                            st.markdown("---")
                    else:
                        st.info("No recommendations found for this query.")
                else:
                    st.error("Failed to fetch recommendations from backend.")
            except requests.exceptions.RequestException:
                st.error("Could not connect to backend. Make sure the server is running.")

if st.button("Test Backend Connection"):
    try:
        test_resp = requests.get("http://localhost:8000/recommend", params={"type": "movie title", "query": "Inception"})
        st.write(f"Status code: {test_resp.status_code}")
        st.json(test_resp.json())
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {e}")
