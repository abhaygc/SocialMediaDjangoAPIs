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
      
    
    def test_follow_sucessful(self):
        self.client.post(reverse("login"), {"email":"t1@t.com", "password" : "t1000"})
        response = self.client.post(reverse("follow",args=(self.user2.data["id"],)))
        jsonResponse = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual("Connection added", jsonResponse["message"])
        connectionCount = Connections.objects.filter(following = self.user2.data["id"], follower = self.user1.data["id"]).count()
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
        connectionCount = Connections.objects.filter(following = self.user2.data["id"], follower = self.user1.data["id"]).count()
        self.assertEqual(connectionCount,1)


    def test_unfollow_sucessful(self):
        self.client.post(reverse("login"), {"email":"t1@t.com", "password" : "t1000"})
        response = self.client.post(reverse("follow",args=(self.user2.data["id"],)))
        response = self.client.post(reverse("unfollow",args=(self.user2.data["id"],)))
        jsonResponse = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual("Connection deleted", jsonResponse["message"])
        connectionCount = Connections.objects.filter(following = self.user2.data["id"], follower = self.user1.data["id"]).count()
        self.assertEqual(connectionCount,0)

    def test_unfollow_unsucessful_to_user_not_existing(self):
        connectionTableCountBefore = Connections.objects.count()
        self.client.post(reverse("login"), {"email":"t1@t.com", "password" : "t1000"})
        response = self.client.post(reverse("follow",args=(44,)))
        jsonResponse = json.loads(response.content)
        self.assertEqual(response.status_code, 404)
        self.assertEqual("User not found", jsonResponse["message"])
        connectionTableCount = Connections.objects.count()
        self.assertEqual(connectionTableCount,connectionTableCountBefore)

    def test_unfollow_to_not_already_followed(self):
        connectionTableCountBefore = Connections.objects.count()
        self.client.post(reverse("login"), {"email":"t1@t.com", "password" : "t1000"})
        response = self.client.post(reverse("unfollow",args=(self.user2.data["id"],)))
        jsonResponse = json.loads(response.content)
        self.assertEqual(response.status_code, 404)
        self.assertEqual("Connection does not exist", jsonResponse["message"])
        connectionTableCount = Connections.objects.count()
        self.assertEqual(connectionTableCount,connectionTableCountBefore)

    def test_getUser1(self):
        self.client.post(reverse("login"), {"email":"t1@t.com", "password" : "t1000"})
        self.client.post(reverse("follow",args=(self.user2.data["id"],)))
        response = self.client.get(reverse("user"))
        jsonResponse = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user1.data["name"], jsonResponse["name"])
        followersCount = Connections.objects.filter(following = self.user1.data["id"]).count()
        followingCount = Connections.objects.filter(follower = self.user1.data["id"]).count()
        self.assertEqual(followersCount, jsonResponse["followersCount"])
        self.assertEqual(followingCount, jsonResponse["followingCount"])

    ##  POST CREATION
    def test_successful_post_creation(self):
        postsTableCountBefore = Posts.objects.count()
        self.client.post(reverse("login"), {"email":"t1@t.com", "password" : "t1000"})
        data = {"title":"Title for post", "description" : "description For the Post"}
        response = self.client.post(reverse("createPost"), data)
        jsonResponse = json.loads(response.content)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data["title"], jsonResponse["title"])
        self.assertEqual(data["description"], jsonResponse["desc"])
        self.assertEqual(self.user1.data["id"], jsonResponse["author"])
        postsTableCountAfter = Posts.objects.count()
        self.assertEqual(postsTableCountBefore+1, postsTableCountAfter)

    def test_unsuccessful_post_creation_with_title_missing(self):
        postsTableCountBefore = Posts.objects.count()
        self.client.post(reverse("login"), {"email":"t1@t.com", "password" : "t1000"})
        data = {"description" : "description For the Post"}
        response = self.client.post(reverse("createPost"), data)
        jsonResponse = json.loads(response.content)
        self.assertEqual(response.status_code, 422)
        self.assertEqual("Please enter a valid Title", jsonResponse["message"])
        
        postsTableCountAfter = Posts.objects.count()
        self.assertEqual(postsTableCountBefore, postsTableCountAfter)

    def test_unsuccessful_post_creation_with_title_empty(self):
        postsTableCountBefore = Posts.objects.count()
        self.client.post(reverse("login"), {"email":"t1@t.com", "password" : "t1000"})
        data = {"title":"","description" : "description For the Post"}
        response = self.client.post(reverse("createPost"), data)
        jsonResponse = json.loads(response.content)
        self.assertEqual(response.status_code, 422)
        self.assertEqual("Please enter a valid Title", jsonResponse["message"])
        
        postsTableCountAfter = Posts.objects.count()
        self.assertEqual(postsTableCountBefore, postsTableCountAfter)


    def test_unsuccessful_post_creation_with_description_missing(self):
        postsTableCountBefore = Posts.objects.count()
        self.client.post(reverse("login"), {"email":"t1@t.com", "password" : "t1000"})
        data = {"title" : "description missing"}
        response = self.client.post(reverse("createPost"), data)
        jsonResponse = json.loads(response.content)
        self.assertEqual(response.status_code, 422)
        self.assertEqual("Please enter a valid Description", jsonResponse["message"])
        postsTableCountAfter = Posts.objects.count()
        self.assertEqual(postsTableCountBefore, postsTableCountAfter)

    def test_unsuccessful_post_creation_with_description_empty(self):
        postsTableCountBefore = Posts.objects.count()
        self.client.post(reverse("login"), {"email":"t1@t.com", "password" : "t1000"})
        data = {"title" : "description empty", "description": ""}
        response = self.client.post(reverse("createPost"), data)
        jsonResponse = json.loads(response.content)
        self.assertEqual(response.status_code, 422)
        self.assertEqual("Please enter a valid Description", jsonResponse["message"])
        postsTableCountAfter = Posts.objects.count()
        self.assertEqual(postsTableCountBefore, postsTableCountAfter)

    ## POST DELETION
    def test_successful_post_deletion(self):
        self.client.post(reverse("login"), {"email":"t1@t.com", "password" : "t1000"})
        data = {"title":"Title for post", "description" : "description For the Post"}
        responseForPostCreated = self.client.post(reverse("createPost"), data)
        jsonResponseForPostCreated = json.loads(responseForPostCreated.content)

        postsTableCountBefore = Posts.objects.count()
        
        response = self.client.delete(reverse("getDeletePost", args = (jsonResponseForPostCreated["id"],)))
        jsonResponse = json.loads(response.content)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual("Post deleted", jsonResponse["message"])
        
        postsTableCountAfter = Posts.objects.count()
        self.assertEqual(postsTableCountBefore-1, postsTableCountAfter)

    def test_unsuccessful_post_deletion_when_post_not_existing(self):
        self.client.post(reverse("login"), {"email":"t1@t.com", "password" : "t1000"})
        
        postsTableCountBefore = Posts.objects.count()
        
        response = self.client.delete(reverse("getDeletePost", args = (1000,)))
        jsonResponse = json.loads(response.content)
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual("Post does not exist", jsonResponse["message"])
        
        postsTableCountAfter = Posts.objects.count()
        self.assertEqual(postsTableCountBefore, postsTableCountAfter)

    def test_unsuccessful_post_deletion_not_authored_by_user(self):
        self.client.post(reverse("login"), {"email":"t2@t.com", "password" : "t1000"})
        data = {"title":"Title for post", "description" : "description For the Post"}
        responseForPostCreated = self.client.post(reverse("createPost"), data)
        jsonResponseForPostCreated = json.loads(responseForPostCreated.content)

        postsTableCountBefore = Posts.objects.count()
        
        self.client.post(reverse("login"), {"email":"t1@t.com", "password" : "t1000"})
        response = self.client.delete(reverse("getDeletePost", args = (jsonResponseForPostCreated["id"],)))
        jsonResponse = json.loads(response.content)

        self.assertEqual(response.status_code, 401)
        self.assertEqual("Unauthorized to delete this post", jsonResponse["message"])
        
        postsTableCountAfter = Posts.objects.count()
        self.assertEqual(postsTableCountBefore, postsTableCountAfter)

    ## LIKE
    def test_successful_like(self):
        self.client.post(reverse("login"), {"email":"t2@t.com", "password" : "t1000"})
        data = {"title":"Title for post", "description" : "description For the Post"}
        responseForPostCreated = self.client.post(reverse("createPost"), data)
        jsonResponseForPostCreated = json.loads(responseForPostCreated.content)

        likesForThePostBefore = Likes.objects.filter(post = jsonResponseForPostCreated["id"]).count()
        
        self.client.post(reverse("login"), {"email":"t1@t.com", "password" : "t1000"})
        response = self.client.post(reverse("like", args = (jsonResponseForPostCreated["id"],)))
        jsonResponse = json.loads(response.content)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual("Post liked", jsonResponse["message"])

        likesForThePostAfter = Likes.objects.filter(post = jsonResponseForPostCreated["id"]).count()

        self.assertEqual(likesForThePostBefore+1, likesForThePostAfter)

    def test_unsuccessful_like_to_post_not_existing(self):
        
        likesTableCountBefore = Likes.objects.count()
        self.client.post(reverse("login"), {"email":"t1@t.com", "password" : "t1000"})
        response = self.client.post(reverse("like", args = (1000,)))
        jsonResponse = json.loads(response.content)
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual("Post not found", jsonResponse["message"])

        likesTableCountAfter = Likes.objects.count()

        self.assertEqual(likesTableCountBefore, likesTableCountAfter)

    def test_unsuccessful_like_for_already_liked_post(self):
        self.client.post(reverse("login"), {"email":"t2@t.com", "password" : "t1000"})
        data = {"title":"Title for post", "description" : "description For the Post"}
        responseForPostCreated = self.client.post(reverse("createPost"), data)
        jsonResponseForPostCreated = json.loads(responseForPostCreated.content)
        
        self.client.post(reverse("login"), {"email":"t1@t.com", "password" : "t1000"})
        self.client.post(reverse("like", args = (jsonResponseForPostCreated["id"],)))
        likesTableCountBefore = Likes.objects.count()
        likesForThePostBefore = Likes.objects.filter(post = jsonResponseForPostCreated["id"]).count()

        response = self.client.post(reverse("like", args = (jsonResponseForPostCreated["id"],)))
        
        self.assertEqual(response.status_code, 304)

        likesTableCountAfter = Likes.objects.count()
        likesForThePostAfter = Likes.objects.filter(post = jsonResponseForPostCreated["id"]).count()

        self.assertEqual(likesTableCountBefore, likesTableCountAfter)
        self.assertEqual(likesForThePostBefore, likesForThePostAfter)

    ## UNLIKE
    def test_successful_unlike(self):
        self.client.post(reverse("login"), {"email":"t2@t.com", "password" : "t1000"})
        data = {"title":"Title for post", "description" : "description For the Post"}
        responseForPostCreated = self.client.post(reverse("createPost"), data)
        jsonResponseForPostCreated = json.loads(responseForPostCreated.content)

        self.client.post(reverse("login"), {"email":"t1@t.com", "password" : "t1000"})
        self.client.post(reverse("like", args = (jsonResponseForPostCreated["id"],)))

        likesForThePostBefore = Likes.objects.filter(post = jsonResponseForPostCreated["id"]).count()
        
        response = self.client.post(reverse("unlike", args = (jsonResponseForPostCreated["id"],)))
        jsonResponse = json.loads(response.content)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual("Like deleted", jsonResponse["message"])

        likesForThePostAfter = Likes.objects.filter(post = jsonResponseForPostCreated["id"]).count()

        self.assertEqual(likesForThePostBefore-1, likesForThePostAfter)

    def test_unsuccessful_unlike_to_post_not_existing(self):
        
        likesTableCountBefore = Likes.objects.count()
        self.client.post(reverse("login"), {"email":"t1@t.com", "password" : "t1000"})
        response = self.client.post(reverse("unlike", args = (1000,)))
        jsonResponse = json.loads(response.content)
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual("Post not found", jsonResponse["message"])

        likesTableCountAfter = Likes.objects.count()

        self.assertEqual(likesTableCountBefore, likesTableCountAfter)

    def test_unsuccessful_like_for_not_liked_post(self):
        self.client.post(reverse("login"), {"email":"t2@t.com", "password" : "t1000"})
        data = {"title":"Title for post", "description" : "description For the Post"}
        responseForPostCreated = self.client.post(reverse("createPost"), data)
        jsonResponseForPostCreated = json.loads(responseForPostCreated.content)
        
        self.client.post(reverse("login"), {"email":"t1@t.com", "password" : "t1000"})

        likesTableCountBefore = Likes.objects.count()
        likesForThePostBefore = Likes.objects.filter(post = jsonResponseForPostCreated["id"]).count()

  
        response = self.client.post(reverse("unlike", args = (jsonResponseForPostCreated["id"],)))
        jsonResponse = json.loads(response.content)

        self.assertEqual(response.status_code, 404)
        self.assertEqual("Like does not exist", jsonResponse["message"])

        likesTableCountAfter = Likes.objects.count()
        likesForThePostAfter = Likes.objects.filter(post = jsonResponseForPostCreated["id"]).count()

        self.assertEqual(likesTableCountBefore, likesTableCountAfter)
        self.assertEqual(likesForThePostBefore, likesForThePostAfter)
    
    ## COMMENT
    def test_successful_comment_creation(self):
        self.client.post(reverse("login"), {"email":"t2@t.com", "password" : "t1000"})
        data = {"title":"Title for post", "description" : "description For the Post"}
        responseForPostCreated = self.client.post(reverse("createPost"), data)
        jsonResponseForPostCreated = json.loads(responseForPostCreated.content)

        self.client.post(reverse("login"), {"email":"t1@t.com", "password" : "t1000"})

        commentsTableCountBefore = Comments.objects.count()
        commentsForThePostBefore = Comments.objects.filter(post = jsonResponseForPostCreated["id"], user = self.user1.data["id"]).count()

        comment = {"comment": "This a comment for a post"}
        response = self.client.post(reverse("comment", args = (jsonResponseForPostCreated["id"],)), data = comment)
        jsonResponse = json.loads(response.content)

        self.assertEqual(response.status_code, 201)

        commentsTableCountAfter = Comments.objects.count()
        commentsForThePostAfter = Comments.objects.filter(post = jsonResponseForPostCreated["id"], user = self.user1.data["id"]).count()
        
        self.assertEqual(commentsTableCountBefore+1, commentsTableCountAfter)
        self.assertEqual(commentsForThePostBefore+1, commentsForThePostAfter)
    
    def test_unsuccessful_comment_creation_with_missing_text(self):
        self.client.post(reverse("login"), {"email":"t2@t.com", "password" : "t1000"})
        data = {"title":"Title for post", "description" : "description For the Post"}
        responseForPostCreated = self.client.post(reverse("createPost"), data)
        jsonResponseForPostCreated = json.loads(responseForPostCreated.content)

        self.client.post(reverse("login"), {"email":"t1@t.com", "password" : "t1000"})

        commentsTableCountBefore = Comments.objects.count()
        commentsForThePostBefore = Comments.objects.filter(post = jsonResponseForPostCreated["id"], user = self.user1.data["id"]).count()

        comment = {}
        response = self.client.post(reverse("comment", args = (jsonResponseForPostCreated["id"],)), data = comment)
        jsonResponse = json.loads(response.content)

        self.assertEqual(response.status_code, 422)
        self.assertEqual("Please enter a valid commment", jsonResponse["message"])

        commentsTableCountAfter = Comments.objects.count()
        commentsForThePostAfter = Comments.objects.filter(post = jsonResponseForPostCreated["id"], user = self.user1.data["id"]).count()
        
        self.assertEqual(commentsTableCountBefore, commentsTableCountAfter)
        self.assertEqual(commentsForThePostBefore, commentsForThePostAfter)

    def test_unsuccessful_comment_creation_with_empty_text(self):
        self.client.post(reverse("login"), {"email":"t2@t.com", "password" : "t1000"})
        data = {"title":"Title for post", "description" : "description For the Post"}
        responseForPostCreated = self.client.post(reverse("createPost"), data)
        jsonResponseForPostCreated = json.loads(responseForPostCreated.content)

        self.client.post(reverse("login"), {"email":"t1@t.com", "password" : "t1000"})

        commentsTableCountBefore = Comments.objects.count()
        commentsForThePostBefore = Comments.objects.filter(post = jsonResponseForPostCreated["id"], user = self.user1.data["id"]).count()

        comment = {"comment": ""}
        response = self.client.post(reverse("comment", args = (jsonResponseForPostCreated["id"],)), data = comment)
        jsonResponse = json.loads(response.content)

        self.assertEqual(response.status_code, 422)
        self.assertEqual("Please enter a valid commment", jsonResponse["message"])

        commentsTableCountAfter = Comments.objects.count()
        commentsForThePostAfter = Comments.objects.filter(post = jsonResponseForPostCreated["id"], user = self.user1.data["id"]).count()
        
        self.assertEqual(commentsTableCountBefore, commentsTableCountAfter)
        self.assertEqual(commentsForThePostBefore, commentsForThePostAfter)

    def test_unsuccessful_comment_for_post_which_not_exists(self):
        self.client.post(reverse("login"), {"email":"t1@t.com", "password" : "t1000"})

        commentsTableCountBefore = Comments.objects.count()
        commentsByTheUserBefore = Comments.objects.filter(user = self.user1.data["id"]).count()

        comment = {"comment": "This comment"}
        response = self.client.post(reverse("comment", args = (10000,)), data = comment)
        jsonResponse = json.loads(response.content)

        self.assertEqual(response.status_code, 404)
        self.assertEqual("Post not found", jsonResponse["message"])

        commentsTableCountAfter = Comments.objects.count()
        commentsByTheUserAfter = Comments.objects.filter(user = self.user1.data["id"]).count()
        
        self.assertEqual(commentsTableCountBefore, commentsTableCountAfter)
        self.assertEqual(commentsByTheUserBefore, commentsByTheUserAfter)
        
    
    ## ALL POSTS    
    def test_get_all_posts(self):
        self.client.post(reverse("login"), {"email":"t1@t.com", "password" : "t1000"})
        data = {"title":"Title for post", "description" : "description For the Post"}
        self.client.post(reverse("createPost"), data)

        self.client.post(reverse("login"), {"email":"t2@t.com", "password" : "t2000"})
        data = {"title":"Title for post 2", "description" : "description For the Post 2#"}
        self.client.post(reverse("createPost"), data)

        posts = Posts.objects.all().order_by('created_at')
        postsSerialized = serializers.PostsSerializer(posts, many = True)
        response = self.client.get(reverse("allPosts"))
        jsonResponse = json.loads(response.content)

        print(postsSerialized.data)
        print(jsonResponse["posts"])

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(postsSerialized.data), len(jsonResponse["posts"]))
        
        for (index, post) in enumerate(postsSerialized.data):
            self.assertEqual(post["id"], jsonResponse["posts"][index]["id"])
            self.assertEqual(post["created_at"], jsonResponse["posts"][index]["created_at"])


        