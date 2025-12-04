
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard
    path('dashboard/', views.dashboard_profile, name='dashboard_profile'),  # profile page
    path('dashboard/home/', views.dashboard_home, name='dashboard_home'),   # feed page
    path('dashboard/upload/', views.upload_recipe, name='upload_recipe'),
    path('dashboard/edit-profile/', views.edit_profile, name='edit_profile'),
    path('recipe/<int:recipe_id>/', views.recipe_detail, name='recipe_detail'),
    path('recipe/<int:recipe_id>/like/', views.like_recipe, name='like_recipe'),
    path('dashboard/recipe/delete/<int:recipe_id>/', views.delete_recipe, name='delete_recipe'),

    path("follow/<int:user_id>/", views.follow_user, name="follow_user"),
    path("unfollow/<int:user_id>/", views.unfollow_user, name="unfollow_user"),
    path("connections/<str:username>/", views.connections_view, name="connections"),
    

    # urls.py
    path('dashboard/profile/<str:username>/', views.dashboard_profile, name='dashboard_profile'),
    # urls.py
    path('dashboard/profile/', views.my_profile, name='my_profile'),

    path('settings/', views.settings_page, name='settings'),
    
    path('settings/', views.settings_page, name='settings'),
    path('delete-account/', views.delete_account, name='delete_confirm'),


    path("recipe/<int:recipe_id>/reply/<int:comment_id>/", views.add_reply, name="add_reply"),
    path("recipe/<int:recipe_id>/comment/<int:comment_id>/delete/", views.delete_comment, name="delete_comment"),
    path("recipe/<int:recipe_id>/reply/<int:reply_id>/delete/", views.delete_reply, name="delete_reply"),
    path('recipe/<int:recipe_id>/likes/', views.recipe_likes_list, name='recipe_likes_list'),

    




]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


