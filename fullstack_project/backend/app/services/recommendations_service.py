from typing import List
from math import log
from fastapi import HTTPException, status
import numpy as np
from sklearn.neighbors import NearestNeighbors
from app.repositories.reservations_repo import load_all as load_reservations
from app.repositories.ratings_repo import load_all as load_ratings
from app.repositories.analytics_repo import load_all

#Collects all userids and book isbn in ratings and reservations file
def _build_index_maps(reservations, ratings):
    users = set()
    books = set()

    for entry in reservations:
        books.add(entry.get('isbn'))
        users.add(entry.get('userid'))

    for entry in ratings:
        users.add(entry.get('userid'))
        books.add(entry.get('isbn'))

    user_to_index = {uid: idx for idx, uid in enumerate(sorted(users))}
    book_to_index = {isbn: idx for idx, isbn in enumerate(sorted(books))}

    return user_to_index, book_to_index

#fills the supplied matrix with rating data
def _fill_ratings(matrix, ratings, user_to_index, book_to_index):
    for entry in ratings:
        uid = entry['userid']
        isbn = entry['isbn']
        rating = entry['rating']

        u_idx = user_to_index[uid]
        b_idx = book_to_index[isbn]

        matrix[u_idx, b_idx] = rating

#fills the supplied matrix with reservation data
def _fill_reservations(matrix, reservations, user_to_index, book_to_index):
    for isbn, userids in reservations.items():
        b_idx = book_to_index[isbn]
        for uid in userids:
            u_idx = user_to_index[uid]
            matrix[u_idx, b_idx] = 1

#buils a matrix with reservation data and rating data
def _build_user_book_matrix():
    ratings = load_ratings()
    reservations = load_reservations()

    user_to_index, book_to_index = _build_index_maps(reservations, ratings)

    matrix = np.zeros((len(user_to_index), len(book_to_index)))

    _fill_reservations(matrix, reservations, user_to_index, book_to_index)

    _fill_ratings(matrix, ratings, user_to_index, book_to_index)

    return matrix, user_to_index, book_to_index

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
def get_similar_books(book_index : int, k : int = 10):
    knn, item_user_matrix, _ = get_recommender()

    _, indices = knn.kneighbors(
        item_user_matrix[book_index].reshape(1, -1),
        n_neighbors=k+1
    )
    return indices[0][1:]

#recommends n books to a user based on past reservations
def recommend_for_user(userid : str, N : int = 5):
    _, _, matrix, user_to_index, _ = get_recommender()
    
    if userid not in user_to_index:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"User {userid} not found in matrix try borrowing and rating more books")

    user_row = matrix[user_to_index[userid]]
    used_books = np.where(user_row > 0)[0]

    scores = {}

    for book in used_books:
        neighbors = get_similar_books(book, k=10)
        for nb in neighbors:
            scores[nb] = scores.get(nb, 0) + 1

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    return [book for book, score in ranked[:N]]


#sorts books by popularity
def get_popular_books(num_books : int) -> List[str]:
    analytics = load_all()
    popularity_table : List[tuple[str, float]] = []
    
    for analytic in analytics:
        request_count = int(analytic.get('request_count'))
        unique_users = int(analytic.get('unique_users'))
        popularity_score = log(1 + request_count) + log(1 + unique_users)
        
        popularity_table.append((analytic.get('book_id'), popularity_score))
        
    popularity_table.sort(key= lambda pair: pair[1], reverse=True)
    return popularity_table[0:num_books]

#sorts books by engagement
def get_books_by_engagement(num_books : int) -> List[str]:
    analytics = load_all()
    rating_table : List[tuple[str, float]] = []
    
    for analytic in analytics:
        request_count = analytic.get('request_count')
        rating_count = analytic.get('rating_count')
        unique_users = analytic.get('unique_users')
        
        engagement = request_count + rating_count + unique_users
        
        rating_table.append((analytic.get('book_id'), engagement))
    
    rating_table.sort(key= lambda pair: pair[1], reverse=True)
    return rating_table[0:num_books]

#sorts books by their rating
def get_best_rated_books(num_books : int) -> List[str]:
    analytics = load_all()
    rating_table : List[tuple[str, float]] = []
    
    for analytic in analytics:
        avg_rating = analytic.get('avg_rating')
        rating_count = analytic.get('rating_count')
        
        rating_score = avg_rating * log(1 + rating_count)
        
        rating_table.append((analytic.get('book_id'), rating_score))
    
    rating_table.sort(key= lambda pair: pair[1], reverse=True)
    return rating_table[0:num_books]