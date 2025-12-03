
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Recipe, Comment, Profile, Follow,Reply
from django.db.models import Q
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.db.models import Count


# Home page
def index(request):
    return render(request, 'index.html')

# Signup view
def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect("signup")

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, "Account created successfully!")
        return redirect("login")

    return render(request, "login.html", {"mode": "signup"})

# Login view
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user:
             login(request, user)
             return redirect('dashboard_profile', username=request.user.username) 
        else:
            messages.error(request, "Invalid username or password.")
            return redirect("login")

    return render(request, "login.html", {"mode": "login"})


# Logout view
def logout_view(request):
    logout(request)
    return redirect("login")


# Dashboard (User-specific homepage)


# Profile Page
@login_required
def dashboard_profile(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('dashboard_home')
    
    profile = getattr(user, 'profile', None)  
    user_recipes = Recipe.objects.filter(user=user).order_by('-created_at')
    
    # Check if current user is following this user
    is_following = request.user.following.filter(following=user).exists()
     # Corrected line
    total_likes = user_recipes.aggregate(total_likes=Count('likes'))['total_likes'] or 0

    return render(request, 'dashboard_profile.html', {
        'user': user,
        'profile': profile,
        'user_recipes': user_recipes,
        'is_following': is_following,
        "total_likes": total_likes
    })
     

# Feed / Home Page
@login_required
def dashboard_home(request):
    query = request.GET.get('q')

    # All recipes
    recipes_all = Recipe.objects.all().order_by('-created_at')
    if query:
        recipes_all = recipes_all.filter(
            Q(title__icontains=query) | Q(user__username__icontains=query)
        )

    # Recipes from followed users
    following_users = request.user.following.values_list("following", flat=True)
    recipes_followed = recipes_all.filter(user__id__in=following_users)
    
    # Recipes from others
    recipes_others = recipes_all.exclude(user__id__in=following_users)

    # Combine, followed recipes first
    recipes = list(recipes_followed) + list(recipes_others)

     # --- Users / Profiles ---
    if query:
        users = User.objects.filter(username__icontains=query).exclude(id=request.user.id)
    else:
        users = User.objects.none()  # empty queryset if no search

    return render(request, 'dashboard_home.html', {
        'recipes': recipes,
        'users': users,
        'query': query
    })



@login_required
def upload_recipe(request):
    if request.method == "POST":
        title = request.POST.get("title")
        short_description = request.POST.get("short_description")

        ingredients = request.POST.get("ingredients")
        difficulty = request.POST.get("difficulty")
        cuisine = request.POST.get("cuisine")
        prep_time = request.POST.get("prep_time")
        cook_time = request.POST.get("cook_time")

        image = request.FILES.get("image")
        video = request.FILES.get("video")

        # Must have at least image or video
        if not image and not video:
            messages.error(request, "Please upload an image or a video.")
            return redirect("upload_recipe")

        # Duplicate title check for same user
        if Recipe.objects.filter(user=request.user, title=title).exists():
            messages.error(request, "You already have a recipe with this title.")
            return redirect("upload_recipe")

        Recipe.objects.create(
            user=request.user,
            title=title,
            short_description=short_description,
            ingredients=ingredients,
            difficulty=difficulty,
            cuisine=cuisine,
            prep_time=prep_time,
            cook_time=cook_time,
            image=image,
            video=video
        )
        messages.success(request, "Recipe uploaded successfully.")
        return redirect('dashboard_profile', username=request.user.username)
        

    return render(request, "upload_recipe.html")


# Edit Profile

@login_required
def edit_profile(request):
    profile = request.user.profile
    user = request.user

    if request.method == 'POST':
        new_username = request.POST.get('username')
        new_email = request.POST.get('email')

        # Validate uniqueness
        if User.objects.exclude(pk=user.pk).filter(username=new_username).exists():
            return redirect('edit_profile')

        if User.objects.exclude(pk=user.pk).filter(email=new_email).exists():
            return redirect('edit_profile')

        user.username = new_username
        user.email = new_email
        user.save()
        messages.success(request, "Profile updated successfully.")

        profile.full_name = request.POST.get('full_name')
        profile.bio = request.POST.get('bio')
        if request.FILES.get('profile_image'):
            profile.profile_image = request.FILES.get('profile_image')
        profile.save()

        
        return redirect('dashboard_profile', username=user.username)

    return render(request, 'edit_profile.html', {
        'profile': profile,
        'user': user,
    })



# Recipe Details / Expand
@login_required
def recipe_detail(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if request.method == 'POST':
        # Add comment
        content = request.POST.get('content')
        if content:
            Comment.objects.create(user=request.user, recipe=recipe, content=content)
    return render(request, 'recipe_detail.html', {'recipe': recipe})
    
# Like / Unlike recipe
@login_required
def like_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if request.user in recipe.likes.all():
        recipe.likes.remove(request.user)
        messages.success(request, "You unliked the recipe.")
    else:
        recipe.likes.add(request.user)
        messages.success(request, "You liked the recipe.")
    return redirect(request.META.get('HTTP_REFERER', 'dashboard_home'))


@login_required
def delete_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id, user=request.user)

    # Delete uploaded image
    if recipe.image:
        recipe.image.delete(save=False)

    # Delete uploaded video
    if recipe.video:
        recipe.video.delete(save=False)

    # Delete recipe record
    recipe.delete()
    messages.success(request, "Recipe deleted successfully.")

    return redirect('dashboard_profile', username=request.user.username)




@login_required
def follow_user(request, user_id):
    user_to_follow = get_object_or_404(User, id=user_id)
    Follow.objects.get_or_create(follower=request.user, following=user_to_follow)
    return redirect('dashboard_profile', username=user_to_follow.username)

@login_required
def unfollow_user(request, user_id):
    user_to_unfollow = get_object_or_404(User, id=user_id)
    Follow.objects.filter(follower=request.user, following=user_to_unfollow).delete()
    return redirect('dashboard_profile', username=user_to_unfollow.username)

# views.py
@login_required
def profile_view(request, username):
    user_profile = get_object_or_404(User, username=username)
    is_following = Follow.objects.filter(follower=request.user, following=user_profile).exists()
    user_recipes = user_profile.recipe_set.all()
    
    return render(request, "profile.html", {
        "user": user_profile,
        "profile": getattr(user_profile, "profile", None),  # if you have a Profile model
        "user_recipes": user_recipes,
        "is_following": is_following,
    })


def followers_list(request, username):
    user_profile = get_object_or_404(User, username=username)
    followers = user_profile.followers.all()
    return render(request, "partials/followers_list.html", {
        "followers": [f.follower for f in followers]
    })

def following_list(request, username):
    user_profile = get_object_or_404(User, username=username)
    following = user_profile.following.all()
    return render(request, "partials/following_list.html", {
        "following": [f.following for f in following]
    })


@login_required
def connections_view(request, username):
    user = get_object_or_404(User, username=username)

    followers = User.objects.filter(following__following=user)   # people who follow this user
    following = User.objects.filter(followers__follower=user)    # people this user follows

    # Compute if the current user follows each of them
    followers_data = []
    for f in followers:
        followers_data.append({
            'user': f,
            'is_following': request.user.following.filter(following=f).exists()
        })

    following_data = []
    for f in following:
        following_data.append({
            'user': f,
            'is_following': request.user.following.filter(following=f).exists()
        })

    return render(request, "connections.html", {
        "user": user,
        "followers": followers_data,
        "following": following_data,
    })


@login_required
@csrf_exempt
def ajax_follow(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    data = json.loads(request.body)
    action = data.get('action')

    if action == 'follow':
        Follow.objects.get_or_create(follower=request.user, following=target_user)
        return JsonResponse({'status': 'ok', 'action': 'follow'})
    elif action == 'unfollow':
        Follow.objects.filter(follower=request.user, following=target_user).delete()
        return JsonResponse({'status': 'ok', 'action': 'unfollow'})
    return JsonResponse({'status': 'error'})


@login_required
def my_profile(request):
    return redirect('dashboard_profile', username=request.user.username)



@login_required
def settings_page(request):
    """
    Page shows password dropdown + delete account option.
    """
    password_form = PasswordChangeForm(user=request.user)

    if request.method == "POST":
        # Only password change happens here
        password_form = PasswordChangeForm(user=request.user, data=request.POST)
        
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)   # Keep user logged in
            messages.success(request, "Password changed successfully.")
            return redirect("settings")
        else:
            messages.error(request, "Invalid password details.")
            return redirect("settings")

    return render(request, "settings.html", {
        "password_form": password_form,
    })


@login_required
def delete_account(request):
    """
    Confirmation page + delete on POST only
    """
    if request.method == "POST":
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, "Your account has been deleted.")
        return redirect("login")

    return render(request, "delete_confirm.html")





@login_required
def add_reply(request, recipe_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if request.method == "POST":
        reply_text = request.POST.get("reply")

        Reply.objects.create(
            comment=comment,
            user=request.user,
            content=reply_text
        )

    return redirect("recipe_detail", recipe_id=recipe_id)


@login_required
def delete_comment(request, recipe_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    recipe = comment.recipe

    # Only recipe owner OR comment owner can delete
    if request.user == comment.user or request.user == recipe.user:
        comment.delete()

    return redirect("recipe_detail", recipe_id=recipe_id)



@login_required
def delete_reply(request, recipe_id, reply_id):
    reply = get_object_or_404(Reply, id=reply_id)
    comment = reply.comment
    recipe = comment.recipe

    # Only reply owner OR recipe owner can delete
    if request.user == reply.user or request.user == recipe.user:
        reply.delete()

    return redirect("recipe_detail", recipe_id=recipe_id)





from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Recipe  # adjust path if needed


@login_required
def recipe_likes_list(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)


    liked_users = recipe.likes.all()  # assuming ManyToMany field named 'likes'

    return render(request, "likes.html", {
        "recipe": recipe,
        "liked_users": liked_users
    })


