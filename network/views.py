from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
from django.core import serializers
from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder

from .models import Follower, User, Post, Like

import datetime 
from datetime import datetime
from dateutil import tz
import json


@login_required
def new_post(request):
    # Get data
    content = request.POST["post-text"]
    user = request.user
        
    # Save entry 
    post = Post(user=user, content=content)
    post.save()    


def show_post(request, status):

    # Get all entries
    if status == "allPosts":
        posts = Post.objects.all().order_by('-timestamp')
    elif status == "Follow":
        follows = Follower.objects.filter(follower = request.user)
        accounts = []
        for follow in follows:
            accounts.append(follow.follows)
        posts = Post.objects.filter(user__in = accounts).order_by('-timestamp') 
    else:
        posts = Post.objects.filter(user=status).order_by('-timestamp')


    for post in posts:
        # Add number of likes
        post.likes = len(Like.objects.filter(post=post.id))
        # Add heart color
        userLike = len(Like.objects.filter(post=post.id, user=request.user.username))
        if userLike == 0:
            post.userLike = "" #css class
        else:
            post.userLike = "like"

    return posts


def paginator(posts):
    
    # Formatting
    for post in posts:
        
        # Convert time zone
        to_zone = tz.gettz('Europe/Berlin') # Get local timezone
        utc = post.timestamp.astimezone(to_zone)
        post.timestamp = utc.strftime('%b %d, %Y, %-I:%M %p')

    # Prepare paginator
    p = Paginator(posts,10)
    pages = p.page_range
    postsPage = p.page(1)

    # Return results
    return pages, postsPage


@login_required
def edit_post(request):
    # Get data
    id = request.POST["id"]
    post = Post.objects.get(id=id)
    post.content = request.POST["text"]
    post.save()

    return JsonResponse(data={
        'status': "Post has been edited successfully"
    })    


def index(request):
    
    # New Post
    if request.method =="POST":
        new_post(request)

    status = "allPosts"
    results = paginator(show_post(request, status))

    return render(request, "network/index.html", {
        "pages": results[0],
        "posts": results[1],
        "pagination": ['none','inline-block'], # Previous / Next Buttons default 
        "status": "All Posts"
    })


@login_required
def followPage (request):
    # New Post
    if request.method =="POST":
        new_post(request)

    status = "Follow"
    results = paginator(show_post(request, status))

    return render(request, "network/index.html", {
        "pages": results[0],
        "posts": results[1],
        "status": "Following",
        "pagination": ['none','inline-block'], # Previous / Next Buttons default 
    })    


def load_more(request):
    page = int(request.POST['page'])
    start = page * 10 - 10
    end = page * 10

    # Determine page characteristics
    if request.POST['status'] == "All Posts":
        status = "allPosts"
    else:
        status = "Follow"
    
    # Get Posts
    posts = show_post(request, status)

    # Set pagination button visibility
    if start == 0:
        pagination = ['none','inline-block']
    elif len(posts) >= end - 10:
        pagination = ['inline-block','none']
    else:
        pagination = ['inline-block','inline-block']

    # Transformation required as annotations are not serialized
    posts_values = posts.values() 
    posts_values = posts_values[start:end]

    # Add further data to query
    for post in posts_values:
        # Add number of likes
        post['likes'] = len(Like.objects.filter(post=list(post.values())[0]))
        # Add heart color
        userLike = len(Like.objects.filter(post=list(post.values())[0], user=request.user.username))
        if userLike == 0:
            post['userLike'] = "" #css class
        else:
            post['userLike'] = "like"
        if request.user.username == post['user']:
            post['edit'] = 'block'
        else:
            post['edit'] = 'none'

    json_posts = json.dumps(list(posts_values), cls=DjangoJSONEncoder)
    totalData = Post.objects.count()

    return JsonResponse(data={
        'posts':json_posts,
        'totalResult':totalData,
        'pagination':pagination
    })
    # Thanks for the introduction: https://www.youtube.com/watch?v=LoRcRUuxN1U


@login_required
def like(request, post):
    # Get data
    user = request.user
    post_id = post
    try:
        likes = Like.objects.get(user=user, post = post_id)
    except:
        likes = []

    # Unlike
    if likes != []:
        likes.delete()
        status = 'unlike'
    #Like
    else:
        Like.objects.create(user=user, post = post_id)
        status = 'like'
    
    # Total number of likes
    totalLikes = len(Like.objects.filter(post = post_id))

    # Return JSON Response
    return JsonResponse(data={
        'status':status,
        'totalLikes':totalLikes
    })


def user(request, user):

    # Get user information
    username = request.user

    # Get posts
    posts = show_post(request,status=user)

    # Get follower information
    follower = len(Follower.objects.filter(follows=user)) # How many follower does the user have
    follows = len(Follower.objects.filter(follower=user)) # How many accounts does the user follow
    followStatus = len(Follower.objects.filter(follows=user, follower=username)) # Does the viewing user follows the viewed account
    if followStatus == 0:
        strFollowStatus = "Follow"
    else:
        strFollowStatus = "Unfollow"

    # Render page
    return render(request, "network/profile.html", {
        "follower": follower,
        "follows": follows,
        "account": user, #user profile
        "username": username,
        "followStatus": followStatus,
        "strFollowStatus": strFollowStatus,
        "posts": posts
    })    


@login_required
def follow(request):

    # Get user information
    username = request.POST['user']
    account = request.POST['account']

    # Check followStatus
    followStatus = Follower.objects.filter(follows=account, follower=username)

    # Unfollow
    if len(followStatus) == 1:
        followStatus.delete()
        # pack response:
        response = {
            'status' : 'unfollow'
        }

    # Follow
    else:
        f = Follower(follower=username, follows=account)
        f.save()
        # pack response:
        response = {
            'status' : 'follow'
        }

    # Send response
    return JsonResponse(response)


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
