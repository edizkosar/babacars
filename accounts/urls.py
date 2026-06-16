from django.urls import path
from accounts import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('verify-email/', views.verify_email_view, name='verify_email'),
    path('verify-email/notice/', views.verify_email_notice_view, name='verify_email_notice'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('become-seller/', views.become_seller_view, name='become_seller'),
    path('seller/<int:seller_id>/', views.seller_profile_view, name='seller_profile'),
    path('seller/<int:seller_id>/review/', views.create_review_view, name='create_review'),
    path('review/<int:review_id>/delete/', views.delete_review_view, name='delete_review'),
    path('change-password/', views.change_password_view, name='change_password'),
    path('resend-verification/', views.resend_verification_email_view, name='resend_verification'),
    path('set-theme/', views.set_theme_view, name='set_theme'),
    path('2fa/', views.two_factor_setup_view, name='two_factor_setup'),
    path('2fa/verify/', views.two_factor_verify_view, name='two_factor_verify'),
]
