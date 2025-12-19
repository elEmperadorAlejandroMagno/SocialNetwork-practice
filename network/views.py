from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from django.utils.formats import date_format
from django.core.paginator import Paginator
import json

from .models import User, Follow, Post, Comment, Like

from .utils import create_new_post, update_post, toggle_like, toggle_follow, post_comment, del_comment, del_post, likes_count

def index(request):
    if request.method == "GET":
        posts = None
        page_number = request.GET.get('page')
        if request.user.is_authenticated:   
            filter_param = request.GET.get("filter")
            if filter_param == "following":
                following_users = [follow.following for follow in Follow.objects.filter(follower=request.user)]
                posts = Post.objects.filter(author__in=following_users).order_by("-created_at")
                if posts.count() < 1:
                    return render(request, 'network/index.html', { "message": "No posts from followed users." })
                paginator = Paginator(posts, 10)  # Mostrar 10 posts por página
                posts = paginator.get_page(page_number)
            else:
                posts = Post.objects.all().order_by("-created_at")
                paginator = Paginator(posts, 10)  # Mostrar 10 posts por página
                posts = paginator.get_page(page_number)

        else:
            posts = Post.objects.all().order_by("-created_at")
            paginator = Paginator(posts, 10)  # Mostrar 10 posts por página
            posts = paginator.get_page(page_number)
    # Añadir flag para saber si el usuario actual dio like a cada post
    if request.user.is_authenticated:
        for p in posts:
            p.liked_by_user = p.likes.filter(user=request.user).exists()
    else:
        for p in posts:
            p.liked_by_user = False

    return render(request, "network/index.html", { "page_obj": posts })

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

@login_required # type: ignore
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
        # marcar si cada post fue liked por el usuario autenticado
        if request.user.is_authenticated:
            for p in posts:
                p.liked_by_user = p.likes.filter(user=request.user).exists()
        else:
            for p in posts:
                p.liked_by_user = False

        context = {
            "profile_user": profile_user,
            "posts": posts,
            "is_following": is_following,
        }
        return render(request, "network/profile.html", context)

@login_required # type: ignore # type: ignore
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
                    "likes_count": likes_count("post", post.id),
                    # Formatear igual que en los templates de Django
                    "created_at": date_format(post.created_at, format='N j, Y, P', use_l10n=True),
                },
                "is_author": True 
            }
            messages.success(request, "Post created successfully!")
            return JsonResponse(response_data)
        except ValueError:
            messages.error(request, "Error creating post. Invalid data.")
            return HttpResponseRedirect(reverse("index"))

@login_required # type: ignore
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
    
@login_required # type: ignore
def delete_post(request):
    if request.method == "POST":
        user = request.user
        data = json.loads(request.body)
        post_id = data.get("post_id")

        try:
            del_post(user, post_id)
            messages.success(request, "Post deleted successfully!")
        except Post.DoesNotExist:
            messages.error(request, "Post not found.")
            return JsonResponse({"status": "error", "message": "Post not found"}, status=404)
        except IntegrityError:
            messages.error(request, "Error deleting post.")
            return JsonResponse({"status": "error", "message": "Error deleting post"}, status=404)
        return JsonResponse({"status": "success", "message": "Post deleted"})

@login_required # type: ignore
def like_unlike_in_post(request):
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
            content_type = data.get("content_type")
            post_id = int(data.get("post_id"))
        except (json.JSONDecodeError, AttributeError):
            return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)
        
        try:
            likes_count, action = toggle_like(user, content_type, post_id)
        except ValueError as e:
            return JsonResponse({"status": "error", "message": "Data invalid", "error": str(e)}, status=400)
        except IntegrityError:
            return JsonResponse({"status": "error", "message": "Error processing like"}, status=400)
        except Post.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Post not found"}, status=404)
        return JsonResponse({"status": "success", "likes_count": likes_count, "action": action})

@login_required # type: ignore
def follow_unfollow(request):
    """
    Recuperar user de la sesion y usuario a seguir desde request para hacer un follow
    en caso de que ya exista el follow eliminarlo
    
    :param request: request data
    retorna json response con nuevo conteo de followers
    """
    if request.method == "POST":
        user = request.user
        username_to_follow = None

        # Support JSON body or form data without accessing body after POST parsing
        if request.content_type == "application/json":
            try:
                data = json.loads(request.body)
                username_to_follow = data.get("username")
            except (json.JSONDecodeError, AttributeError):
                return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)
        else:
            username_to_follow = request.POST.get("username")

        try:
            followers_count, action = toggle_follow(user, username_to_follow)
        except ValueError:
            return JsonResponse({"status": "error", "message": "User not found"}, status=400)
        except IntegrityError:
            return JsonResponse({"status": "error", "message": "Error processing follow"}, status=404)
        return JsonResponse({"status": "success", "followers_count": followers_count, "action": action})
    
@login_required # type: ignore
def mark_notifications_as_read(request):
    """
    Marca todas las notificaciones del usuario autenticado como leídas.
    
    :param request: request data
    :return: JsonResponse con el estado de la operación
    """
    if request.method == "POST":
        user = request.user
        notif_id = json.loads(request.body).get("id")
        try:
            notif = user.notifications.get(pk=notif_id)
            notif.is_read = True
            notif.save()
            # eliminar después de marcar como leída
            notif.delete()
            return JsonResponse({"status": "success", "message": "All notifications marked as read"})
        except IntegrityError:
            return JsonResponse({"status": "error", "message": "Error marking notifications as read"}, status=404)
        
@login_required # type: ignore
def create_comment(request):
    if request.method == "POST":
        user = request.user
        post_id = int(request.POST["post_id"])
        content = request.POST["content"]
        try:
            commentObj = post_comment(user, post_id, content)
            new_comment = {
                "id": commentObj.id,
                "author": user.username,
                "content": commentObj.content,
                "likes_count": likes_count("comment", commentObj.id),
                "created_at": date_format(commentObj.created_at, format='N j, Y, P', use_l10n=True),
            }
            return JsonResponse({"status": "success", "message": "Comment added successfully!", "new_comment": new_comment})
        except ValueError:
            return JsonResponse({"status": "error", "message": "The text must be a valid string"}, status=404)
        except IntegrityError:
            return JsonResponse({"status": "error", "message": "Error adding comment"}, status=404)
        except Post.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Post not found"}, status=404)
        
@login_required # type: ignore
def like_unlike_in_comment(request):
    if request.method == "POST":
        user = request.user
        try:
            data = json.loads(request.body)
            content_type = data.get("content_type")
            comment_id = int(data.get("comment_id"))
        except (json.JSONDecodeError, AttributeError):
            return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)
        try:
            likes_count, action = toggle_like(user, content_type, comment_id)
        except Comment.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Comment not found"}, status=404)
        return JsonResponse({"status": "success", "action": action, "likes_count": likes_count})
        
@login_required # type: ignore
def delete_comment(request):
    if request.method == "POST":
        comment_id = json.loads(request.body).get("id")
        user = request.user
        try:
            del_comment(user, comment_id)
            return JsonResponse({'status': 'success', 'message': 'Comment deleted successfully.'})
        except IntegrityError:
            return JsonResponse({'status': 'error', 'message': 'Error deleting comment.'}, status=400)
        except Comment.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Comment not found.'}, status=404)
        except PermissionDenied:
            return JsonResponse({'status': 'error', 'message': 'You are not authorized to delete this comment.'}, status=403)
        
def post_details(request, post_id):
    try:
        post = Post.objects.get(pk=post_id)
        comments = post.comments.all().order_by("-created_at")
    except Post.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Post not found.'}, status=404)

    # marcar si el post y los comments fueron liked por el usuario actual
    if request.user.is_authenticated:
        post.liked_by_user = post.likes.filter(user=request.user).exists()
        for c in comments:
            c.liked_by_user = c.likes.filter(user=request.user).exists()
    else:
        post.liked_by_user = False
        for c in comments:
            c.liked_by_user = False

    return render(request, 'network/post_details.html', {'post': post, "comments": comments})