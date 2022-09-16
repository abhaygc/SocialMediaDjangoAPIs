from rest_framework.test import APITestCase
from django.urls import reverse
from .models import Users, Connections, Posts, Comments, Likes
from social_media import serializers
import json


class TestListSocialMediaAPI(APITestCase):
    user1 = None
    user2 = None
    user1Name = None
    user2Name = None

    def setUp(self):
        # self.user1 = Users.objects.createUser({"name":"testUser1", "email":"t1@t.com", "password":"t1000"})
        self.user1 = serializers.UsersSerializer(data={"name":"testUser1", "email":"t1@t.com", "password":"t1000"})
        self.user1.is_valid(raise_exception=True)
        self.user1.save()
        # self.user2 = Users.objects.createUser({"name":"testUser2", "email":"t2@t.com", "password":"t1000"})
        self.user2 = serializers.UsersSerializer(data={"name":"testUser2", "email":"t2@t.com", "password":"t1000"})
        self.user2.is_valid(raise_exception=True)
        self.user2.save()

    def test_registerUser1(self):
        response = self.client.post(reverse("register"), {"name":"testUser1", "email":"t1@t.com", "password":"t1000"})
        jsonResponse = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual("testUser1", jsonResponse["name"])

    def test_authenticateUser1(self):
        response = self.client.post(reverse("login"), {"email":"t1@t.com", "password" : "t1000"})
        jsonResponse = json.loads(response.content)
        self.client.cookies = response.client.cookies
      
    def test_getUser1(self):
        self.client.post(reverse("login"), {"email":"t1@t.com", "password" : "t1000"})
        response = self.client.get(reverse("user"))
        jsonResponse = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user1.data["name"], jsonResponse["name"])

    def test_follow_sucessful(self):
        self.client.post(reverse("login"), {"email":"t1@t.com", "password" : "t1000"})
        response = self.client.post(reverse("follow",args=(self.user2.data["id"],)))
        jsonResponse = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual("Connection added", jsonResponse["message"])
        connectionCount = Connections.objects.filter(following = self.user2, follower = self.user1).count()
        self.assertEqual(connectionCount,1)

    def test_follow_unsucessful_to_user_not_existing(self):
        connectionTableCountBefore = Connections.objects.count()
        self.client.post(reverse("login"), {"email":"t1@t.com", "password" : "t1000"})
        response = self.client.post(reverse("follow",args=(44,)))
        jsonResponse = json.loads(response.content)
        self.assertEqual(response.status_code, 404)
        self.assertEqual("User not found", jsonResponse["message"])
        connectionTableCount = Connections.objects.count()
        self.assertEqual(connectionTableCount,connectionTableCountBefore)

    def test_follow_unsucessful_to_itself(self):
        connectionTableCountBefore = Connections.objects.count()
        self.client.post(reverse("login"), {"email":"t1@t.com", "password" : "t1000"})
        response = self.client.post(reverse("follow",args=(self.user1.data["id"],)))
        self.assertEqual(response.status_code, 304)
        connectionTableCount = Connections.objects.count()
        self.assertEqual(connectionTableCount,connectionTableCountBefore)
        
    
    def test_follow_to_already_followed(self):
        self.client.post(reverse("login"), {"email":"t1@t.com", "password" : "t1000"})
        response = self.client.post(reverse("follow",args=(self.user2.data["id"],)))
        response = self.client.post(reverse("follow",args=(self.user2.data["id"],)))
        self.assertEqual(response.status_code, 304)
        connectionCount = Connections.objects.filter(following = self.user2, follower = self.user1).count()
        self.assertEqual(connectionCount,1)
        