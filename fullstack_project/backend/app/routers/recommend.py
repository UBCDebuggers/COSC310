from app.services.recommendations_service import (get_best_rated_books, get_books_by_engagement, 
                                                  get_popular_books, recommend_for_user)
from app.core.security import verify_access_token
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(tags= ["recommend"], prefix= "/recommend")

#Returns the top n highest rated books
@router.get("/toprated/{n}", status_code=status.HTTP_200_OK, summary="Returns the top n highest rated books")
def get_top_rated(n: int):
    return get_best_rated_books(n)

#Returns the top n books with the highest user engagement
@router.get("/topengagement/{n}", status_code=status.HTTP_200_OK, summary="Returns the top n books with the highest user engagement")
def get_books_by_engagment(n : int):
    return get_books_by_engagement(n)

#Returns the top n most popular books
@router.get("/popular/{n}", status_code=status.HTTP_200_OK, summary="Returns the top n most popular books")
def get_books_by_popularity(n : int):
    return get_popular_books(n)

#Recommends user a book based on loan history
@router.get("", status_code=status.HTTP_200_OK, summary="Recommends user a book based on loan history")
def get_recommended_for_user(current_user : dict = Depends(verify_access_token)):
    return recommend_for_user(current_user.get('userid'))