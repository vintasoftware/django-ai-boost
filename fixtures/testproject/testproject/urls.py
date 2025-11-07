"""
URL configuration for testproject.
"""

from django.contrib import admin
from django.urls import path

from blog import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.post_list, name="post_list"),
    path("post/<int:pk>/", views.post_detail, name="post_detail"),
    path("api/posts/", views.api_post_list, name="api_post_list"),
]
