from django.urls import path
from . import views

app_name = 'wishlist'

urlpatterns = [
    # علاقه‌مندی
    path('', views.wishlist_page, name='page'),
    path('toggle/', views.wishlist_toggle, name='toggle'),
    path('check/', views.wishlist_check, name='check'),
    path('ids/', views.wishlist_ids, name='ids'),

    # مقایسه
    path('compare/', views.compare_page, name='compare_page'),
    path('compare/toggle/', views.compare_toggle, name='compare_toggle'),
    path('compare/ids/', views.compare_ids, name='compare_ids'),
    path('compare/clear/', views.compare_clear, name='compare_clear'),

    # اخیراً بازدیدشده
    path('recently/', views.recently_viewed_api, name='recently_viewed'),
]
