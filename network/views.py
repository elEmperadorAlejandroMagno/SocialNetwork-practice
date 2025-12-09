from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse

from .models import User

from .utils import create_new_post, update_post, toggle_like, toggle_follow

def index(request):
    return render(request, "network/index.html")

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
    pass

@login_required
def new_post(request):
    if request.method == "POST":
        data = request.POST.get("content")
        user = request.user
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
        post_id = request.POST.get("post_id")
        new_content = request.POST.get("content")
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
def like_unlike(request):
    """
    Recuperar user de la sesion y post id desde request para hacer un post
    en caso de que ya exista el like eliminarlo
    
    :param request: request data

    retorna json response con nuevo conteo de likes 
    """
    if request.method == "POST":
        user = request.user
        post_id = request.POST.get("post_id")
        try:
            likes_count, action = toggle_like(user, post_id)
        except ValueError:
            return JsonResponse({"status": "error"}, status=400)
        except IntegrityError:
            return JsonResponse({"status": "error"}, status=404)
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
        username_to_follow = request.POST.get("username")
        try:
            followers_count, action = toggle_follow(user, username_to_follow)
        except ValueError:
            return JsonResponse({"status": "error"}, status=400)
        except IntegrityError:
            return JsonResponse({"status": "error"}, status=404)
        return JsonResponse({"status": "success", "followers_count": followers_count, "action": action})