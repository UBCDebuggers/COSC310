from typing import List
from math import log
import numpy as np
from fastapi import HTTPException, status
from scipy.sparse import lil_matrix
from sklearn.neighbors import NearestNeighbors
from app.repositories.reservations_repo import load_all as load_reservations
from app.repositories.ratings_repo import load_all as load_ratings
from app.repositories.analytics_repo import load_all

#buils a matrix with reservation data and rating data
def _build_user_book_matrix():
    interactions = load_ratings()
    user_to_index = {}
    book_to_index = {}

    for row in interactions:
        user = row["userid"]
        book = row["isbn"]

        if user not in user_to_index:
            user_to_index[user] = len(user_to_index)
        if book not in book_to_index:
            book_to_index[book] = len(book_to_index)

    matrix = lil_matrix((len(user_to_index), len(book_to_index)), dtype=float)

    for row in interactions:
        u = user_to_index[row["userid"]]
        b = book_to_index[row["isbn"]]

        rating = row.get("rating", 1)  # or engagement score
        matrix[u, b] = rating

    return matrix.tocsr(), user_to_index, book_to_index

#fits NearestNeighbors model to the item_user_matrix
def _fit_knn_model(matrix, metric : str = 'cosine'):
    item_user_matrix = matrix.T

    knn = NearestNeighbors(
        metric=metric,
        algorithm='brute'
    )

    knn.fit(item_user_matrix)
    return knn, item_user_matrix

#composes helper methods
def get_recommender():
    if not hasattr(get_recommender, "model"):
        matrix, user_to_index, book_to_index = _build_user_book_matrix()
        knn, item_user_matrix = _fit_knn_model(matrix)
        get_recommender.model = (knn, item_user_matrix, user_to_index, book_to_index)
    return get_recommender.model

#gets the closest books to the index
def get_similar_books(book_index: int, k: int = 10):
    knn, item_user_matrix, user_to_index, book_to_index = get_recommender()

    _, indices = knn.kneighbors(
        item_user_matrix[book_index].reshape(1, -1),
        n_neighbors=k + 1
    )
    return indices[0][1:]


#recommends n books to a user based on past reservations
def recommend_for_user(userid: str, N: int = 5):
    knn, item_user_matrix, user_to_index, book_to_index = get_recommender()

    if userid not in user_to_index:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {userid} not found in matrix. Try borrowing/rating more books."
        )

    u_idx = user_to_index[userid]

    col = item_user_matrix[:, u_idx]
    if hasattr(col, "toarray"):
        user_row = col.toarray().flatten()
    else:
        user_row = col.flatten()

    used_books = np.where(user_row > 0)[0]

    scores = {}

    for book in used_books:
        neighbors = get_similar_books(book, k=10)
        for nb in neighbors:
            scores[nb] = scores.get(nb, 0) + 1

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    index_to_book = {v: k for k, v in book_to_index.items()}

    return [index_to_book[book] for book, score in ranked[:N]]


#sorts books by popularity
def get_popular_books(num_books : int) -> List[dict]:
    analytics = load_all()
    popularity_table : List[tuple[str, float]] = []
    
    for analytic in analytics:
        request_count = int(analytic.get('request_count'))
        unique_users = int(analytic.get('unique_users'))
        popularity_score = log(1 + int(request_count)) + log(1 + int(unique_users))
        
        popularity_table.append((analytic.get('book_id'), popularity_score))
        
    popularity_table.sort(key= lambda pair: pair[1], reverse=True)
    return [{"isbn" : item[0], "rating" : item[1]} for item in popularity_table[0:num_books]]

#sorts books by engagement
def get_books_by_engagement(num_books : int) -> List[dict]:
    analytics = load_all()
    engagement_table : List[tuple[str, float]] = []
    
    for analytic in analytics:
        request_count = analytic.get('request_count')
        rating_count = analytic.get('rating_count')
        unique_users = analytic.get('unique_users')
        
        engagement = int(request_count) + int(rating_count) + int(unique_users)
        
        engagement_table.append((analytic.get('book_id'), engagement))
    
    engagement_table.sort(key= lambda pair: pair[1], reverse=True)
    return [{"isbn" : item[0], "engagement_score" : item[1]} for item in engagement_table[0:num_books]]

#sorts books by their rating
def get_best_rated_books(num_books : int) -> List[dict]:
    analytics = load_all()
    rating_table : List[tuple[str, float]] = []
    
    for analytic in analytics:
        avg_rating = analytic.get('avg_rating')
        rating_count = analytic.get('rating_count')
        
        rating_score = float(avg_rating) * log(1 + int(rating_count))
        
        rating_table.append((analytic.get('book_id'), rating_score))
    
    rating_table.sort(key= lambda pair: pair[1], reverse=True)
    
    return [{"isbn" : item[0], "rating" : item[1]} for item in rating_table[0:num_books]]