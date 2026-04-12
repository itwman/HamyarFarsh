from django.urls import path
from . import views

app_name = 'gallery'

urlpatterns = [
    # گالری ویدیو
    path('videos/', views.video_gallery, name='video_gallery'),
    path('videos/<int:pk>/', views.video_detail, name='video_detail'),

    # گالری تصاویر
    path('images/', views.image_gallery, name='image_gallery'),
    path('images/<int:pk>/', views.image_detail, name='image_detail'),

    # API endpoints (AJAX)
    path('api/videos/', views.api_videos_filter, name='api_videos'),
    path('api/images/', views.api_images_filter, name='api_images'),
    path('api/images/<int:pk>/similar/', views.api_similar_images, name='api_similar_images'),
]
