from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (ListView, DetailView,
                                  CreateView, UpdateView, DeleteView)

from .forms import PostForm, CommentForm
from .mixins import PostMixin, AuthorPassesMixin, CommentMixin
from .models import Post, Category
from .utils import annotate_comments, get_published_posts

User = get_user_model()

POST_LIMIT = 10


class IndexListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = POST_LIMIT

    def get_queryset(self):
        queryset = Post.objects.all()
        queryset = annotate_comments(get_published_posts(queryset))
        return queryset


class CategoryListView(ListView):
    model = Post
    template_name = "blog/category.html"
    paginate_by = POST_LIMIT

    def get_object(self):
        return get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )

    def get_queryset(self):
        return annotate_comments(
            get_published_posts(self.get_object().posts)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_field = 'post_id'
    pk_url_kwarg = 'post_id'
    paginate_by = POST_LIMIT

    def get_object(self):
        post = get_object_or_404(Post, pk=self.kwargs[self.pk_url_kwarg])
        if self.request.user != post.author and (
            post.pub_date > timezone.now() or not post.is_published
        ):
            raise Http404
        return post

    def get_queryset(self):
        return self.get_object().comments.select_related('author')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        comments = post.comments.all()
        context['comments'] = comments
        context['form'] = CommentForm()
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostUpdateView(PostMixin, UpdateView):
    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostDeleteView(PostMixin, DeleteView):
    pass


class ProfileListView(ListView):
    model = User
    template_name = 'blog/profile.html'
    paginate_by = POST_LIMIT

    def get_object(self):
        return get_object_or_404(
            User,
            username=self.kwargs['username']
        )

    def get_queryset(self):
        profile = self.get_object()
        posts = annotate_comments(profile.posts)
        if self.request.user != profile:
            posts = get_published_posts(posts)
        return posts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'profile': self.get_object()})
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ('username', 'last_name', 'first_name', 'email')
    template_name = 'blog/user.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})


class CommentCreateView(CommentMixin, CreateView):
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().form_valid(form)


class CommentUpdateView(CommentMixin, AuthorPassesMixin, UpdateView):
    form_class = CommentForm


class CommentDeleteView(CommentMixin, AuthorPassesMixin, DeleteView):
    pass
