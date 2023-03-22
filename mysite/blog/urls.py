from django.urls import include, path

from blog import views
from blog.views import PostUpdateView

app_name = "blog"
post_urls = [
     path('create', views.PostCreateView.as_view(), name='create_post'),
     path('<int:pk>', views.PostDetailView.as_view(), name='post_detail'),
     path('<int:pk>/delete', views.PostDeleteView.as_view(), name='post_delete'),
     path('<int:pk>/update/', PostUpdateView.as_view(), name='post_update'),

]

urlpatterns = [
    path('home/', views.HomePageView.as_view(), name='home'),
    path('search', views.PostSearchView.as_view(), name='search_results'),
    path('posts/', include(post_urls)),
]
