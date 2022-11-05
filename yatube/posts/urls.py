from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from posts import views

app_name = 'posts'

handler404 = 'core.views.page_not_found'

urlpatterns = [
    path('', views.index, name='index'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('group/<slug:slug>/', views.group_posts, name='group_posts'),
    path('create/', views.create_post, name='create_post'),
    path('posts/<int:post_id>/edit/', views.post_edit, name='post_edit'),
    path('posts/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('follow/', views.follow_index, name='follow_index'),
    path('profile/<str:username>/follow/', views.profile_follow,
         name='profile_follow'),
    path('profile/<str:username>/unfollow/', views.profile_unfollow,
         name="profile_unfollow")
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
