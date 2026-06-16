from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from accounts.models import SellerProfile, Review

User = get_user_model()

def get_user_by_id(*, user_id: int) -> User:
    return User.objects.get(id=user_id)

def get_user_by_email(*, email: str) -> User:
    return User.objects.get(email=email)

def get_seller_profile(*, user) -> SellerProfile:
    return SellerProfile.objects.get(user=user)

def get_seller_profile_by_id(*, seller_profile_id: int) -> SellerProfile:
    return SellerProfile.objects.get(id=seller_profile_id)

def get_reviews_by_seller(*, seller_profile) -> QuerySet:
    return Review.objects.filter(seller=seller_profile).order_by('-created_at')

def get_review(*, reviewer, seller_profile) -> Review:
    return Review.objects.get(reviewer=reviewer, seller=seller_profile)

def get_review_by_id(*, review_id: int) -> Review:
    return Review.objects.get(id=review_id)
