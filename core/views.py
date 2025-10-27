from django.shortcuts import render
from django.db.models import Q, Count
from django.http import JsonResponse
from django.template.loader import render_to_string
from pins.models import Pin
from boards.models import Board


def home(request):
    """Homepage view - All pins feed like Pinterest (infinite scroll)"""
    page = int(request.GET.get('page', 1))
    per_page = 20
    start = (page - 1) * per_page
    end = start + per_page
    
    # Show ALL pins (including user's own) - simple chronological feed
    pins = Pin.objects.all().order_by('-created_at')[start:end]
    
    # AJAX request for infinite scroll
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('core/_pin_grid.html', {
            'pins': pins,
            'request': request
        })
        return JsonResponse({
            'html': html,
            'has_more': len(pins) == per_page
        })
    
    context = {
        'pins': pins,
    }
    return render(request, 'core/home.html', context)


def explore(request):
    """Explore page - Discover trending and popular content with infinite scroll"""
    page = int(request.GET.get('page', 1))
    section = request.GET.get('section', 'popular')
    per_page = 20
    
    start = (page - 1) * per_page
    end = start + per_page
    
    if section == 'popular':
        # Get popular pins (most liked)
        pins = Pin.objects.annotate(
            total_likes=Count('likes')
        ).filter(total_likes__gt=0).order_by('-total_likes')[start:end]
    elif section == 'recent':
        # Get recent pins
        pins = Pin.objects.all().order_by('-created_at')[start:end]
    else:  # random
        # Get random pins
        pins = Pin.objects.all().order_by('?')[start:end]
    
    # AJAX request for infinite scroll
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('core/_pin_grid.html', {
            'pins': pins,
            'request': request,
            'show_likes': section == 'popular'
        })
        return JsonResponse({
            'html': html,
            'has_more': len(pins) == per_page
        })
    
    # Initial page load
    popular_pins = Pin.objects.annotate(
        total_likes=Count('likes')
    ).filter(total_likes__gt=0).order_by('-total_likes')[:20]
    
    recent_pins = Pin.objects.all().order_by('-created_at')[:20]
    random_pins = Pin.objects.all().order_by('?')[:20]
    
    context = {
        'popular_pins': popular_pins,
        'recent_pins': recent_pins,
        'random_pins': random_pins,
    }
    return render(request, 'core/explore.html', context)


def search(request):
    """Search view"""
    query = request.GET.get('q', '')
    results = []
    
    if query:
        results = Pin.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(tags__icontains=query)
        )
    
    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'core/search.html', context)
