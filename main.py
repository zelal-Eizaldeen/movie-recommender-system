import pandas as pd
import numpy as np

import dash
from dash import dcc, html


DATA_DIR='ml-1m'
IMAGES_URL='/assets'


ratings = pd.read_csv(f'{DATA_DIR}/ratings.dat', sep='::', engine = 'python', header=None)
ratings.columns = ['UserID', 'MovieID', 'Rating', 'Timestamp']
movies = pd.read_csv(f'{DATA_DIR}/movies.dat', sep='::', engine = 'python',
                     encoding="ISO-8859-1", header = None)
movies.columns = ['MovieID', 'Title', 'Genres']

movies['PosterURL'] = movies['MovieID'].apply(lambda x: f"{IMAGES_URL}/{x}.jpg")


multiple_idx = pd.Series([("|" in movie) for movie in movies['Genres']])
movies.loc[multiple_idx, 'Genres'] = 'Multiple'

rating_merged = ratings.merge(movies, left_on = 'MovieID', right_on = 'MovieID')
mean_ratings = rating_merged[['Rating', 'Genres']].groupby('Genres').mean()


# Calculate the number of ratings and the average rating for each movie
movie_stats = rating_merged.groupby('MovieID').agg(
    num_ratings=('Rating', 'count'),
    avg_rating=('Rating', 'mean')
).reset_index()

# Normalize the average rating (assuming a rating scale of 1-5)
movie_stats['normalized_rating'] = (movie_stats['avg_rating'] - 1) / 4  # Normalize to [0,1] range
# Calculate the popularity score
movie_stats['popularity_score'] = movie_stats['num_ratings'] * movie_stats['normalized_rating']
# Merge with movie titles to get more useful information
movie_popularity = movie_stats.merge(movies[['MovieID', 'Title','PosterURL']], on='MovieID')
# Sort by popularity score and select the top 10 movies
top_10_popular_movies = movie_popularity.sort_values(by='popularity_score', ascending=False).head(10)
# Display the top 10 popular movies
print(top_10_popular_movies[['MovieID', 'Title', 'num_ratings', 'avg_rating', 'popularity_score', 'PosterURL']])

# Create a Dash app
app = dash.Dash(__name__)

# For deployment

server=app.server

# Layout of the Dash app
app.layout = html.Div(children=[
    html.H1("Top 10 Most Popular Movies"),
    html.Div(
        className="movie-grid",
        children=[
            html.Div(
                className="movie-card",
                children=[
                    html.Img(src=row['PosterURL'], style={'width': '150px', 'height': '225px'}),
                    html.H3(row['Title']),
                    html.P(f"Movie ID: {row['MovieID']}"),
                    html.P(f"Popularity: {row['popularity_score']:.2f}")
                ]
            ) for index, row in top_10_popular_movies.iterrows()
        ],
        style={'display': 'grid', 'gridTemplateColumns': 'repeat(5, 1fr)', 'gap': '20px', 'padding': '20px'}
    )
])
# Run the server
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=9000)


