from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test



urlpatterns = [
    path('',views.Home.as_view(), name="home"),
    path('render-post',views.RenderPost.as_view(),name="renderpost"),
    path('search/',views.search,name="search"),
    path('login_user',views.login_user,name='login'),
    path('sing_up_user',views.sing_up_user, name='singup'),
    path('logout',views.logout,name='logout'),
    path('settings/profile',views.edit_profile,name='edit_profile'),
    path('update_avatar',views.update_avatar,name="updateavatar"),
    path('<str:username>',views.profile_page_index, name="status"),
    path('<str:username>/post_twitte',views.post_twitte, name="posttwitte"),
    path('<str:post_id>/delete_twitte',views.DeleteTwitte.as_view(),name='delete'),
    path('<str:username>/status/<str:postid>',views.ReplayTwitte.as_view(),name='replytwitte'),
    path('<str:username>/follow_action',views.FollowUserView.as_view(),name="fallowuser"),
    path('<str:username>/index/<str:kind>',views.IndexFollows.as_view(),name="indexfollows"),
    path("like/<str:username>/<str:postid>",views.like_twitte,name='liketwitte')
 
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
