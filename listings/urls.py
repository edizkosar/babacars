from django.urls import path
from listings import views

app_name = 'listings'

urlpatterns = [
    path('', views.index_view, name='index'),
    path('search/', views.search_view, name='search'),
    path('map/', views.map_view, name='map'),
    path('map/data/', views.map_data_view, name='map_data'),
    path('create/', views.create_listing_view, name='create'),
    path('compare/', views.compare_view, name='compare'),
    path('favorites/', views.my_favorites_view, name='favorites'),
    path('<slug:slug>/', views.listing_detail_view, name='detail'),
    path('<slug:slug>/pdf/', views.listing_pdf_view, name='pdf'),
    path('<slug:slug>/edit/', views.edit_listing_view, name='edit'),
    path('<int:listing_id>/delete/', views.delete_listing_view, name='delete'),
    path('<int:listing_id>/favorite/', views.toggle_favorite_view, name='toggle_favorite'),
    path('<int:listing_id>/report/', views.report_listing_view, name='report'),
    path('<int:listing_id>/refresh/', views.refresh_listing_view, name='refresh'),
    path('bulk-update/', views.bulk_update_view, name='bulk_update'),
]
