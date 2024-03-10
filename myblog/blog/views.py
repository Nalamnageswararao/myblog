from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from .models import Blog, Comment


@csrf_exempt
def register_page(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Your Account has been Created")
            return redirect('login_page')
        else:
            # If the form is not valid, display error messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserCreationForm()

    return render(request, 'register4.html', {'form': form})


@csrf_exempt
def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('blog_list')  # Replace 'home_page' with the actual name of your home page URL
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'login4.html')


def blog_list(request):
    blogs = Blog.objects.all()
    return render(request, 'sample.html', {'blogs': blogs})


def like_blog(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        blog_id = request.POST.get('blog_id')
        try:
            blog = Blog.objects.get(id=blog_id)
            blog.likes_count += 1
            blog.save()
            return JsonResponse({'likes_count': blog.likes_count})
        except Blog.DoesNotExist:
            return JsonResponse({'error': 'Blog not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)


def dislike_blog(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        blog_id = request.POST.get('blog_id')
        try:
            blog = Blog.objects.get(id=blog_id)
            blog.dislikes_count += 1
            blog.save()
            return JsonResponse({'dislikes_count': blog.dislikes_count})
        except Blog.DoesNotExist:
            return JsonResponse({'error': 'Blog not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)


def add_comment(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        blog_id = request.POST.get('blog_id')
        comment_text = request.POST.get('comment_text')
        try:
            blog = Blog.objects.get(id=blog_id)
            blog.comments_count += 1
            blog.save()
            return JsonResponse({'comments_count': blog.comments_count})
        except Blog.DoesNotExist:
            return JsonResponse({'error': 'Blog not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)


def top_commented_blogs(request):
    # Retrieve the top commented blogs from the database
    top_commented_blogs = Blog.objects.order_by('-comments_count')[:5]

    # Serialize the data to send it back as JSON response
    serialized_blogs = []
    for blog in top_commented_blogs:
        serialized_blogs.append({
            'name': blog.name,
            'content': blog.content,
            'comments_count': blog.comments_count
        })

    return JsonResponse(serialized_blogs, safe=False)


def top_liked_disliked_blogs(request):
    # Get the date 3 days ago
    three_days_ago = timezone.now() - timedelta(days=3)

    # Retrieve the top 5 liked blogs in the last 3 days
    top_liked_blogs = Blog.objects.filter(created_date__gte=three_days_ago).order_by('-likes_count')[:5]

    # Retrieve the top 5 disliked blogs in the last 3 days
    top_disliked_blogs = Blog.objects.filter(created_date__gte=three_days_ago).order_by('-dislikes_count')[:5]

    # Serialize the data to send it back as JSON response
    serialized_data = {
        'top_liked_blogs': list(top_liked_blogs.values('name', 'content', 'likes_count')),
        'top_disliked_blogs': list(top_disliked_blogs.values('name', 'content', 'dislikes_count'))
    }

    return JsonResponse(serialized_data)


def recent_liked_blogs(request):
    # Calculate the date for recent blogs (let's say within the last 7 days)
    recent_date = timezone.now() - timedelta(days=7)

    # Fetch recent liked blogs created within the last 7 days and order by likes count
    recent_liked_blogs = Blog.objects.filter(created_date__gte=recent_date).order_by('-likes_count')[:5]

    # Serialize the data to send it back as JSON response
    serialized_data = {
        'recent_liked_blogs': list(recent_liked_blogs.values('name', 'content', 'likes_count')),
    }

    return JsonResponse(serialized_data)


def author_blog_stats(request, author_id):
    # Retrieve blogs of the specified author
    author_blogs = Blog.objects.filter(author_id=author_id)

    # Calculate likes, dislikes, and comments count for each blog
    blog_stats = []
    for blog in author_blogs:
        likes_count = blog.likes_count
        dislikes_count = blog.dislikes_count
        comments_count = blog.comments_count
        blog_data = {
            'id': blog.id,
            'name': blog.name,
            'likes_count': likes_count,
            'dislikes_count': dislikes_count,
            'comments_count': comments_count,
        }
        blog_stats.append(blog_data)

    return JsonResponse({'author_blog_stats': blog_stats})

def author_comment_count(request):
    # Query the User model to get the authors along with their comment counts
    authors_with_comment_count = User.objects.annotate(comment_count=Count('comments_made'))

    # Serialize the data to send it back as JSON response
    serialized_data = {
        'authors': [
            {'author_name': author.username, 'comment_count': author.comment_count}
            for author in authors_with_comment_count
        ]
    }

    return JsonResponse(serialized_data)


def get_blog_comments(request, blog_id):
    try:
        blog = Blog.objects.get(pk=blog_id)
        comments = Comment.objects.filter(blog_id=blog_id)

        comments_data = []
        for comment in comments:
            comment_data = {
                'text': comment.comment_text,
                'created_at': comment.created_date.strftime('%Y-%m-%d %H:%M:%S')
            }
            comments_data.append(comment_data)

        response_data = {
            'blog_name': blog.name,
            'comments': comments_data
        }
        return JsonResponse(response_data)
    except Blog.DoesNotExist:
        return JsonResponse({'error': 'Blog not found'}, status=404)
