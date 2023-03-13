from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, DetailView, ListView
from django.views.generic.edit import DeleteView


from .models import Post, Tag


class CustomLoginRequiredMixin(LoginRequiredMixin):
    login_url = reverse_lazy('login') 
    redirect_field_name = 'redirect_to'


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

    def post(self, request, *args, **kwargs):

        object = self.get_object()
        if not request.user.is_authenticated:
            return redirect('login')

        form_data = request.POST
        object.content = form_data.get('post_content_text')
        object.save()

        return HttpResponseRedirect(reverse('blog:post_detail', args=[str(self.object.id)]))


class PostCreateView(CustomLoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content']
    success_url = reverse_lazy('blog:home')
    template_name = 'create_post.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        post = form.save(commit=False)
        tag_names = self.request.POST.get('tag_names')
        if tag_names:
            tag_names_list = [name.strip() for name in tag_names.split(',')]
            post.save()
            for name in tag_names_list:
                tag, created = Tag.objects.get_or_create(name=name)
                post.tags.add(tag)
        else:
            post.save()
        return super().form_valid(form)


class PostDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('blog:home')
    permission_required = 'blog.delete_post'

    def get_object(self, queryset=None):
        obj = get_object_or_404(Post, pk=self.kwargs['pk'])
        return obj

    def has_permission(self):
        post = self.get_object()
        return post.author == self.request.user

    def handle_no_permission(self):
        return HttpResponseForbidden()
    
def search_results(request):
    query = request.GET.get('searched')
    search_by = request.GET.get('search_by')

    if search_by == 'title':
        posts = Post.objects.filter(title__icontains=query)
    elif search_by == 'author':
        posts = Post.objects.filter(author__username__icontains=query)
    elif search_by == 'tag':
        try:
            tag = Tag.objects.get(name=query)
            posts = Post.objects.filter(tags=tag)
        except:
            posts = Post.objects.none()
    else:
        posts = Post.objects.none()
    
    context = {'posts': posts, 'query': query, 'search_by': search_by}
    return render(request, 'search_results.html', context)
