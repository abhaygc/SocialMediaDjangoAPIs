from django.contrib import admin
from .models import Users, Connections, Posts, Comments, Likes

admin.site.register([Users, Connections, Posts, Comments, Likes])