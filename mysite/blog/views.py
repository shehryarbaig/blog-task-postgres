from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, DetailView, ListView
from django.views.generic.edit import DeleteView

from taggit.models import Tag

from .models import Post


class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'


class HomePageView(ListView):
    model = Post
    template_name = 'home.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        return Post.objects.order_by('-created_on')


class PostDetailView(DetailView):
    model = Post
    template_name = 'post_detail.html'
    context_object_name = 'post'

    def post(self, request, *args, **kwargs):

        self.object = self.get_object()
        if not request.user.is_authenticated:
            return redirect('login')

        form_data = request.POST
        self.object.content = form_data.get('post_content_text')
        self.object.save()

        return HttpResponseRedirect(reverse('blog:post_detail', args=[str(self.object.id)]))


class PostCreateView(CreateView):
    model = Post
    fields = ['title', 'content', 'tags']
    success_url = reverse_lazy('blog:home')
    template_name = 'create_post.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('blog:home')

    def get_object(self, queryset=None):
        obj = get_object_or_404(Post, pk=self.kwargs['pk'])
        return obj

    def test_func(self):
        obj = self.get_object()
        return obj.owner == self.request.user

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

