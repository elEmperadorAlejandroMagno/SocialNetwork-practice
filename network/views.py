from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User


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
    
    :param request: request data
    :param username: id de usuariio para busqueda en db

    retorna template con data del usuario
    """
    pass

def new_post(request):
    pass

def edit_post(request):
    pass

def like_unlike(request):
    """
    Recuperar user de la sesion y post id desde request para hacer un post
    en caso de que ya exista el like eliminarlo
    
    :param request: request data

    retorna json response con nuevo conteo de likes 
    """
    pass

def follow_unfollow(request):
    """
    Recuperar user de la sesion y usuario a seguir desde request para hacer un follow
    en caso de que ya exista el follow eliminarlo
    
    :param request: request data
    retorna json response con nuevo conteo de followers
    """
    pass