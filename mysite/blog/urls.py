from django.urls import include, path

from blog import views

app_name = "blog"
post_urls = [
     path('create', views.PostCreateView.as_view(), name='create_post'),
     path('<int:pk>', views.PostDetailView.as_view(), name='post_detail'),
     path('<int:pk>/post_delete', views.PostDeleteView.as_view(), name='post_delete'),
]

urlpatterns = [
    path('home/', views.HomePageView.as_view(), name='home'),
    path('posts/', include(post_urls)),
]
