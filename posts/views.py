from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import CreateView
from django.core.paginator import Paginator
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from .models import Post, Group, User, Comment, Follow
from .forms import PostForm, CommentForm


def index(request):
    post_list = Post.objects.order_by('-pub_date').all()
    paginator = Paginator(post_list, 10)

    # переменная в URL с номером запрошенной страницы
    page_number = request.GET.get('page')
    # получить записи с нужным смещением
    page = paginator.get_page(page_number)
    return render(
        request,
        'posts/index.html',
        {'page': page, 'paginator': paginator}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)

    posts = Post.objects.filter(group=group).order_by("-pub_date")
    paginator = Paginator(posts, 10)

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "group.html", {'page': page, 'paginator': paginator, 'group': group})


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = request.user
        new_post.save()
        return redirect("index")
    return render(request, "posts/new_post.html", {"form": form})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(user=author).count()
    followers = Follow.objects.filter(author=author).count()
    posts = Post.objects.filter(author=author).order_by("-pub_date")
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following = False
    flag_me = False
    if request.user.is_authenticated:
        user = User.objects.get(username=request.user)
        following = True if Follow.objects.filter(
            author=author, user=user).count() > 0 else False
    if request.user.username == username:
        flag_me = True
    context = {
        'page': page,
        'paginator': paginator,
        'author': author,
        'following': following,
        'followers': followers,
        'follow': follow,
        'flag_me': flag_me
    }
    return render(request, 'posts/profile.html', context)


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = Post.objects.get(author=author, pk=post_id)
    comments = Comment.objects.filter(post=post).order_by('-created')
    follow = Follow.objects.filter(user=author).count()
    followers = Follow.objects.filter(author=author).count()
    form = CommentForm()
    context = {
        'author': author,
        'post': post,
        'form': form,
        'comments': comments,
        'followers': followers,
        'follow': follow,
    }
    return render(request, 'posts/post.html', context)


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, pk=post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None, instance=post)
    if post.author != request.user:
        return redirect("post", username=username, post_id=post_id)
    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.save()
        return redirect("post", username=username, post_id=post_id)
    return render(request, 'posts/new_post.html', {'form': form, 'post': post})


def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию,
    # выводить её в шаблон пользователской страницы 404 мы не станем
    return render(
        request,
        "../templates/misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "../templates/misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        new_comment = form.save(commit=False)
        new_comment.author = request.user
        new_comment.post = post
        new_comment.save()
        return redirect("post", username=username, post_id=post_id)
    return redirect("post", username=username, post_id=post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, 10)
    # переменная в URL с номером запрошенной страницы
    page_number = request.GET.get('page')
    # получить записи с нужным смещением
    page = paginator.get_page(page_number)
    return render(request, "posts/follow.html", {'page': page, 'paginator': paginator})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user.username == username or Follow.objects.filter(author=author, user=request.user).count() != 0:
        # os.path.exists() не работает как нужно, иного экзиста не нашел
        return redirect(reverse('profile', kwargs={
            'username': username}))
    Follow.objects.create(author=author, user=request.user)
    return redirect(reverse('profile', kwargs={
        'username': username}))


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(author=author, user=request.user).delete()
    return redirect(reverse('profile', kwargs={
        'username': username}))
