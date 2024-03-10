from django.urls import path
# from .views import author_dashboard, reader_dashboard
from blog import views

from .views import author_comment_count

urlpatterns = [
    path('', views.login_page, name='login_page'),
    path('reg/', views.register_page, name='register_page'),
    path('blog/', views.blog_list, name='blog_list'),
    path('like-blog/', views.like_blog, name='like_blog'),
    path('dislike-blog/', views.dislike_blog, name='dislike_blog'),
    path('add-comment/', views.add_comment, name='add_comment'),
    path('top/', views.top_commented_blogs, name='top_commented_blogs'),
    path('liked/', views.top_liked_disliked_blogs, name='top_liked_disliked_blogs'),
    path('recent-liked-blogs/', views.recent_liked_blogs, name='recent_liked_blogs'),
    path('author-comment-count/', author_comment_count, name='author_comment_count'),
    path('author-blog-stats/<int:author_id>/', views.author_blog_stats, name='author_blog_stats'),
    path('get-blog-comments/<int:blog_id>/', views.get_blog_comments, name='get_blog_comments'),



]
