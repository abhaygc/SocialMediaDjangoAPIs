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
    path('api/register/', views.registerUser),
    path('api/authenticate/', views.loginUser),
    path('api/user/', views.userDetails),
    path('api/follow/<int:id>/', views.follow),
    path('api/unfollow/<int:id>/', views.unfollow),
    path('api/posts/', views.createPost),
    path('api/posts/<int:id>/', views.deletePost),
    path('api/like/<int:id>/', views.postLike),
    path('api/unlike/<int:id>/', views.postUnlike),
    path('api/comment/<int:id>/', views.addComment),
    path('api/all_posts/', views.getAllPosts),
]
