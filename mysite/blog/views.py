from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView
from django.views.generic.edit import DeleteView, UpdateView

from blog.forms import PostForm
from blog.models import Post


class CustomLoginRequiredMixin(LoginRequiredMixin):
    login_url = reverse_lazy('login') 
    redirect_field_name = 'redirect_to'

class CustomPermissionRequiredMixin(PermissionRequiredMixin):
        
    def has_permission(self):
        post = self.get_object()
        return post.author == self.request.user
    
    def handle_no_permission(self):
        return HttpResponseForbidden()


class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'


class HomePageView(ListView):
    template_name = 'home.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        return Post.objects.order_by('-created_at')


class PostDetailView(DetailView):
    model = Post
    template_name = 'post_detail.html'
    context_object_name = 'post'


class PostUpdateView(LoginRequiredMixin, CustomPermissionRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'post_update.html'

    def get_initial(self):
        initial = super().get_initial()
        post = self.get_object()
        initial['tags'] = ', '.join([tag.name for tag in post.tags.all()])
        return initial
    
    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'pk': self.object.pk})


class PostCreateView(CustomLoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    success_url = reverse_lazy('blog:home')
    template_name = 'create_post.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostDeleteView(LoginRequiredMixin, CustomPermissionRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('blog:home')
    permission_required = 'blog.delete_post'

    def get_object(self, queryset=None):
        obj = get_object_or_404(Post, pk=self.kwargs['pk'])
        return obj

class PostSearchView(ListView):
    model = Post
    template_name = 'search_results.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        searched = self.request.GET.get('searched')
        object_list = Post.objects.filter(
            Q(title__icontains=searched) | 
            Q(author__username__icontains=searched) |
            Q(tags__name__icontains=searched)
        ).distinct()
        
        return object_list
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('searched', '')
        return context
