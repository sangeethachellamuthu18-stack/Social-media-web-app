from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.user_login, name="user_login"),
    path("register/", views.user_register, name="user_register"),
    path("dashboard/", views.user_dashboard, name="user_dashboard"),
    path("create_post/", views.create_post, name="user_create_post"),
    path("like/<int:post_id>/", views.like_post, name="like_post"),
    path("comment/<int:post_id>/", views.add_comment, name="add_comment"),
    path("inbox/", views.inbox, name="inbox"),
    path("sent/", views.sent_messages, name="sent_messages"),
    path("send/<int:user_id>/", views.send_message, name="send_message"),
    path('search/', views.search_users, name='search_users'),
    path("profile/<int:user_id>/", views.view_profile, name="view_profile"),
    path("profile/<int:user_id>/follow/", views.toggle_follow, name="toggle_follow"),
    path("profile/<int:user_id>/followers/", views.followers_list, name="followers_list"),
    path("profile/<int:user_id>/following/", views.following_list, name="following_list"),
    path("edit_profile/", views.edit_profile, name="edit_profile"),
    path("notifications/", views.notifications, name="notifications"),
    path("logout/",views.user_logout, name='user_logout'),
    path('migrate-now/', views.migrate_now),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)