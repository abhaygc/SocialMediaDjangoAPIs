import re
import stat
from urllib import response
from .models import Users, Connections, Posts, Comments, Likes
from .serializers import UsersSerializer, ConnectionsSerializer, PostsSerializer, CommentsSerializer, LikesSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from social_media import serializers
import datetime
import jwt

SECRET_KEY = "secretKeyOfServer+=="
ALGORITHM = "HS256"

def authenticateUser(token):
    if not token:
        raise AuthenticationFailed("Token not found")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.InvalidSignatureError:
        raise AuthenticationFailed("Invalid Token")
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed("Token Expired. Login again")
    except:
        raise AuthenticationFailed("Some error occurred")

    return payload

@api_view(['POST'])
def registerUser(request):
    serializer = serializers.UsersSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)

@api_view(['POST'])
def loginUser(request):
    email = request.data['email']
    password = request.data['password']
    # serializer = serializers.UsersSerializer()

    user = Users.objects.filter(email=email).first()

    if user is None:
        raise AuthenticationFailed('User not Found')
    if not user.checkPassword(password):
        raise AuthenticationFailed('Incorrect password')
    payload = {
      'id' : user.id,
      'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
      'iat': datetime.datetime.utcnow()
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

    response = Response()

    response.set_cookie(key='jwt', value=token, httponly=True)
    response.data = {
      'jwt':token
    }
    response.status_code = 200
    return response

@api_view(['POST'])
def follow(request, id):
    token = request.COOKIES.get('jwt')
    payload = authenticateUser(token)

    loggedUser = Users.objects.get(id=payload['id'])
    
    try:
        toFollowUser = Users.objects.get(id=id)
    except Users.DoesNotExist:
        return Response({"message":"User not found"}, status=404)
    except:
        return Response({"message":"Some error occured"}, status=404)
    if loggedUser == toFollowUser:
        return Response(status=304)
    connection, created = Connections.objects.get_or_create(following=toFollowUser, follower = loggedUser)
    if not created:
        return Response(status=304)
    
    return Response({"message" : "Connection added"}, status=200)
    
@api_view(['POST'])
def unfollow(request, id):
    token = request.COOKIES.get('jwt')
    payload = authenticateUser(token)

    loggedUser = Users.objects.get(id=payload['id'])

    try:
        toUnfollowUser = Users.objects.get(id=id)
    except Users.DoesNotExist:
        return Response({"message":"User not found"}, status=404)
    except:
        return Response({"message":"Some error occured"}, status=404)

    try:
        connection = Connections.objects.get(following=toUnfollowUser, follower = loggedUser)
    except Connections.DoesNotExist:
        return Response({"message" : "Connection does not exist"}, status=404)
    except:
        return Response({"message" : "Some error occured"}, status=404) 

    connection.delete()

    return Response({"message" : "Connection deleted"}, status=200)


@api_view(["GET"])
def userDetails(request):
    token = request.COOKIES.get('jwt')

    payload = authenticateUser(token)
    
    user = Users.objects.get(id=payload['id'])
    
    serializer = serializers.UsersSerializer(user)

    followersCount = Connections.objects.filter(following = user).count()
    followingCount = Connections.objects.filter(follower = user).count()

    return Response({"name": serializer.data.get('name'), "followersCount":followersCount, "followingCount":followingCount}, status=200)

@api_view(["POST"])
def createPost(request):
    token = request.COOKIES.get('jwt')

    payload = authenticateUser(token)
    
    user = Users.objects.get(id=payload['id'])

    
    
    try:
        title = request.data["title"]
    except:
        title = None
    finally:
        if title is None or title.strip() == "":
            return Response({"message": "Please enter a valid Title"}, status=422)
    try:
        description = request.data["description"]
    except:
        description = None
    finally:
        if description is None or description.strip() == "":
            return Response({"message": "Please enter a valid Description"}, status=422)

    serializer = serializers.PostsSerializer(data={'title':title,'desc':description,"created_at":datetime.datetime.utcnow(),"author":user.id})
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    else:
        # print(serializer.errors)
        return Response({"message": "Some error occurred while creating the post"}, status=404)


@api_view(["GET","DELETE"])
def deletePost(request, id):
    print(request.method)
    if request.method == "DELETE":
        token = request.COOKIES.get('jwt')
        payload = authenticateUser(token)
        user = Users.objects.get(id=payload['id'])
        
        try:
            post = Posts.objects.get(id=id)
        except Posts.DoesNotExist:
            return Response({"message" : "Post does not exist"}, status=404)
        except:
            return Response({"message" : "Some error occured"}, status=404) 
        # print(user.id)
        # print(post.author.id)
        if user.id != post.author.id:
            return Response({"message": "Unauthorized to delete this post"}, status=401)
        
        post.delete()
        return Response({"message" : "Post deleted"}, status=200)


    if request.method == "GET":
        token = request.COOKIES.get('jwt')
        payload = authenticateUser(token)
        user = Users.objects.get(id=payload['id'])
        
        try:
            post = Posts.objects.get(id=id)
        except Posts.DoesNotExist:
            return Response({"message" : "Post does not exist"}, status=404)
        except:
            return Response({"message" : "Some error occured"}, status=404) 

        likesCount = Likes.objects.filter(post = id).count()
        comments = Comments.objects.filter(post = id)

        postSerialzer = serializers.PostsSerializer(post)
        commentSerializer = serializers.CommentsSerializer(comments, many = True)

        return Response({"postDetails":postSerialzer.data,"likes":likesCount,"comments":commentSerializer.data}, status=200)
        
@api_view(['POST'])
def postLike(request, id):
    token = request.COOKIES.get('jwt')
    payload = authenticateUser(token)

    loggedUser = Users.objects.get(id=payload['id'])

    try:
        toLikePost = Posts.objects.get(id=id)
    except Posts.DoesNotExist:
        return Response({"message":"Post not found"}, status=404)
    except:
        return Response({"message":"Some error occured"}, status=404)
    
    postLike, liked = Likes.objects.get_or_create(post=toLikePost, user = loggedUser)
    if not liked:
        return Response(status=304)
    
    return Response({"message" : "Post liked"}, status=200)
    
@api_view(['POST'])
def postUnlike(request, id):
    token = request.COOKIES.get('jwt')
    payload = authenticateUser(token)

    loggedUser = Users.objects.get(id=payload['id'])

    try:
        toUnlikePost = Posts.objects.get(id=id)
    except Posts.DoesNotExist:
        return Response({"message":"Post not found"}, status=404)
    except:
        return Response({"message":"Some error occured"}, status=404)

    try:
        like = Likes.objects.get(post=toUnlikePost, user = loggedUser)
    except Likes.DoesNotExist:
        return Response({"message" : "Like does not exist"}, status=404)
    except:
        return Response({"message" : "Some error occured"}, status=404) 

    like.delete()

    return Response({"message" : "Like deleted"}, status=200)


@api_view(["POST"])
def addComment(request, id):
    token = request.COOKIES.get('jwt')

    payload = authenticateUser(token)
    
    user = Users.objects.get(id=payload['id'])

    try:
        comment = request.data["comment"]
    except:
        comment = None
    finally:
        if comment is None or comment.strip() == "":
            return Response({"message": "Please enter a valid commment"}, status=422)

    try:
        toCommentOnPost = Posts.objects.get(id=id)
    except Posts.DoesNotExist:
        return Response({"message":"Post not found"}, status=404)
    except:
        return Response({"message":"Some error occured"}, status=404)

    serializer = serializers.CommentsSerializer(data={'text':comment,"post":id,"user":user.id})
    
    if serializer.is_valid():
        serializer.save()
        return Response({"Comment-ID":serializer.data.get("id")}, status=201)
    else:
        # print(serializer.errors)
        return Response({"message": "Some error occurred while adding the comment"}, status=404)

@api_view(["GET"])
def getAllPosts(request):
    token = request.COOKIES.get('jwt')

    payload = authenticateUser(token)
    
    posts = Posts.objects.all().order_by('created_at')
    
    serializer = serializers.PostsSerializer(posts, many=True)

    data = {"posts": []}
    try:
        for post in serializer.data:
            likesCount = Likes.objects.filter(post = post["id"]).count()

            comments = Comments.objects.filter(post = post["id"])
            commentSerializer = serializers.CommentsSerializer(comments, many = True)

            currentPostData = {"id":post["id"], "title":post["title"], "desc":post["desc"], "created_at":post["created_at"]}
            currentPostData["comments"] = commentSerializer.data
            currentPostData["likes"] = likesCount

            data["posts"].append(currentPostData)
    except:
        return Response({"message" : "Some error occured"}, status=404) 

    return Response(data, status=200)

