from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Q

from .models import Blog, Category, Comment

from google import genai

GEMINI_API_KEY = "AIzaSyAvE013OreC8c2gCOVwPPJ2o_orFcJDiR4"
# Create your views here.

def posts_by_category(request, category_id):
    posts = Blog.objects.filter(status='Published', category_id = category_id)
    
    # handle category_id error
    # try:
    #     category = Category.objects.get(id=category_id)
    # except:
    #     return redirect('home')
    
    category = get_object_or_404(Category, pk=category_id)
    
    
    context = {
        'posts': posts,
        'category': category,
    }

    return render(request, 'posts_by_category.html', context)

def blogs(request, slug):
    single_blog = get_object_or_404(Blog, slug=slug, status='Published')
    
    if request.method == 'POST':
        comment = Comment()
        comment.user = request.user
        comment.blog = single_blog
        comment.comment = request.POST['comment']
        comment.save()
        return HttpResponseRedirect(request.path_info)

    # Generate AI summary using Gemini
    ai_summary = None
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        content_to_summarize = f"{single_blog.short_description}\n\n{single_blog.blog_body}"
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=(
                "Please provide a concise 2-3 sentence summary of the following blog post content. "
                "Be informative and engaging:\n\n"
                f"{content_to_summarize}"
            ),
        )
        ai_summary = response.text
    except Exception as e:
        ai_summary = None

    # comments
    comments= Comment.objects.filter(blog=single_blog)
    comment_count = comments.count()
    context = {
        'single_blog': single_blog,
        'comments': comments,
        'comment_count': comment_count,
        'ai_summary': ai_summary,
    }
    return render(request, 'blogs.html', context)

def search(request):
    keyword = request.GET.get('keyword')
    print('search called')
    print(keyword)
    blogs = Blog.objects.filter(Q(title__icontains=keyword) |  Q(short_description__icontains=keyword) | Q(blog_body__icontains=keyword), status='Published')
    context = {
        'blogs': blogs,
        'keyword': keyword,
    }
    return render(request, 'search.html', context)