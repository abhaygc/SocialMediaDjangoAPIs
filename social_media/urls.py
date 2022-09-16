"""social_media URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from social_media import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/register/', views.registerUser, name="register"),
    path('api/authenticate/', views.loginUser, name="register"),
    path('api/user/', views.userDetails, name="user"),
    path('api/follow/<int:id>/', views.follow, name="follow"),
    path('api/unfollow/<int:id>/', views.unfollow, name="unfollow"),
    path('api/posts/', views.createPost, name="createPost"),
    path('api/posts/<int:id>/', views.deletePost, name="getDeletePost"),
    path('api/like/<int:id>/', views.postLike, name="like"),
    path('api/unlike/<int:id>/', views.postUnlike, name="unlike"),
    path('api/comment/<int:id>/', views.addComment, name="comment"),
    path('api/all_posts/', views.getAllPosts, name="allPosts"),
]
