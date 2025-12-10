from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
import json

from .models import User, Follow, Post

from .utils import create_new_post, update_post, toggle_like, toggle_follow

def index(request):
    if request.method == "GET":
        posts = None
        if request.user.is_authenticated:   
            filter_param = request.GET.get("filter")
            if filter_param == "following":
                following_users = [follow.following for follow in Follow.objects.filter(follower=request.user)]
                posts = Post.objects.filter(author__in=following_users).order_by("-created_at")
                if posts.count() < 1:
                    return render(request, 'network/index.html', { "message": "No posts from followed users." })
            else:
                posts = Post.objects.all().order_by("-created_at")

        else:
            posts = Post.objects.all().order_by("-created_at")
    return render(request, "network/index.html", { "posts": posts })

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

@login_required
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

def profile(request, username):
    """
    Obtener User data y post de un usuario específico
    El usuario no pueder darse follow a si mismo
    
    :param request: request data
    :param username: id de usuariio para busqueda en db

    retorna template con data del usuario
    """
    if request.method == "GET":
        user = request.user
        try:
            profile_user = User.objects.get(username=username)
        except Exception:
            messages.error(request, "User not found.")
            return redirect("index")

        is_following = False
        if user.username != username:
            is_following = Follow.objects.filter(follower=user, following=profile_user).exists()
        posts = profile_user.posts.all().order_by("-created_at")
        context = {
            "profile_user": profile_user,
            "posts": posts,
            "is_following": is_following,
        }
        return render(request, "network/profile.html", context)

@login_required
def new_post(request):
    if request.method == "POST":
        data = request.POST.get("content")
        user = request.user
        if len(data) < 1:
            messages.error(request, "Post content cannot be empty.")
            return JsonResponse({"status": "error", "message": "Post content cannot be empty" }, status=400)
        try:
            post = create_new_post(user, data)
            response_data = {
                "status": "success",
                "post": {
                    "id": post.id,
                    "author":  user.username,
                    "content": post.content,
                    "likes_count": post.likes_count(),
                },
                "is_author": True 
            }
            messages.success(request, "Post created successfully!")
            return JsonResponse(response_data)
        except ValueError:
            messages.error(request, "Error creating post. Invalid data.")
            return HttpResponseRedirect(reverse("index"))

@login_required
def edit_post(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            post_id = data.get("post_id")
            new_content = data.get("content")

            post_to_update = Post.objects.get(pk=post_id)
            if post_to_update.author != request.user:
                return JsonResponse({"status": "error", "message": "Unauthorized"}, status=403)
        except (json.JSONDecodeError, AttributeError):
            return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)
        
        try:
            updated_post = update_post(post_id, new_content)
            messages.success(request, "Post updated successfully!")
        except ValueError:
            messages.error(request, "Error updating post. Invalid data.")
            return JsonResponse({"status": "error", "message": "Invalid data"}, status=400)
        except IntegrityError:
            messages.error(request, "Post not found.")
            return JsonResponse({"status": "error", "message": "Post not found"}, status=404)
        return JsonResponse({"status": "success", "new_content": updated_post.content})
    
@login_required
def delete_post(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            post_id = data.get("post_id")
        except (json.JSONDecodeError, AttributeError):
            return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)
        
        try:
            post_to_delete = Post.objects.get(id=post_id)
            if post_to_delete.author != request.user:
                return JsonResponse({"status": "error", "message": "Unauthorized"}, status=403)
            post_to_delete.delete()
            messages.success(request, "Post deleted successfully!")
        except Post.DoesNotExist:
            messages.error(request, "Post not found.")
            return JsonResponse({"status": "error", "message": "Post not found"}, status=404)
        except IntegrityError:
            messages.error(request, "Error deleting post.")
            return JsonResponse({"status": "error", "message": "Error deleting post"}, status=404)
        return JsonResponse({"status": "success", "message": "Post deleted"})

@login_required
def like_unlike(request):
    """
    Recuperar user de la sesion y post id desde request para hacer un post
    en caso de que ya exista el like eliminarlo
    
    :param request: request data

    retorna json response con nuevo conteo de likes 
    """
    if request.method == "POST":
        user = request.user
        try:
            data = json.loads(request.body)
            post_id = data.get("post_id")
        except (json.JSONDecodeError, AttributeError):
            return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)
        
        try:
            likes_count, action = toggle_like(user, post_id)
        except ValueError:
            return JsonResponse({"status": "error", "message": "Post not found"}, status=400)
        except IntegrityError:
            return JsonResponse({"status": "error", "message": "Error processing like"}, status=404)
        return JsonResponse({"status": "success", "likes_count": likes_count, "action": action})

@login_required
def follow_unfollow(request):
    """
    Recuperar user de la sesion y usuario a seguir desde request para hacer un follow
    en caso de que ya exista el follow eliminarlo
    
    :param request: request data
    retorna json response con nuevo conteo de followers
    """
    if request.method == "POST":
        user = request.user
        try:
            data = json.loads(request.body)
            username_to_follow = data.get("username")
        except (json.JSONDecodeError, AttributeError):
            return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)
        
        try:
            followers_count, action = toggle_follow(user, username_to_follow)
        except ValueError:
            return JsonResponse({"status": "error", "message": "User not found"}, status=400)
        except IntegrityError:
            return JsonResponse({"status": "error", "message": "Error processing follow"}, status=404)
        return JsonResponse({"status": "success", "followers_count": followers_count, "action": action})