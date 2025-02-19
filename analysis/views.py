from . import utils
from .models import History, WatchlistItems
from .forms import CustomUserCreationForm
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.urls import reverse


def home(request):
    return render(request, 'home.html')


def search(request):
    # Check if the request is AJAX and GET
    if request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        query = request.GET.get('symbol', '').strip()
        if query:
            matches = utils.get_matches(query)
            return JsonResponse({'matches': matches}, status=200)
        else:
            return JsonResponse({'matches': []}, status=200)
    else:
        # If not an AJAX request, show an error or a fallback page
        return JsonResponse({'error': 'Invalid request'}, status=400)


def matches(request):
    if request.method == 'GET':
        query = request.GET.get('symbol', '').strip()
        if query:
            matches = utils.get_matches(query)
            return render(request, 'matches.html', {'matches': matches})
        else:
            return render(request, 'matches.html')
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)


def analysis(request):
    if request.method == 'GET':
        symbol = request.GET.get('symbol', '').strip()
        cache_timeout = 600 # Cache data for 10 minutes
        days = max(int(request.GET.get('days', 30)), 1)
        rows_per_page = max(int(request.GET.get('rows_per_page', 10)), 10)
        page_number = int(request.GET.get('page', 1))

        crnt_search = f"{symbol}_{days}"
        prev_search = cache.get("prev_search")
        if crnt_search != prev_search and request.user.is_authenticated:
            History.objects.create(user=request.user, symbol=symbol, days=days)
            cache.set("prev_search", crnt_search, timeout=cache_timeout)

        # Use cache to store API data for 10 minutes (done to reduce API calls)
        data_cache_key = f"alpha_data_{symbol}_compact" if days <= 100 else f"alpha_data_{symbol}_full"
        alpha_data = cache.get(data_cache_key)
        if not alpha_data:
            compact = True if days <= 100 else False
            alpha_data = utils.get_alpha_data(symbol, compact)
            if not alpha_data:
                return render(request, 'error.html')
            cache.set(data_cache_key, alpha_data, timeout=cache_timeout)

        alpha_data = dict(sorted(alpha_data.items(), key=lambda x: x[0], reverse=True)[:days]) # Get only the days specified
        pattern_data = utils.get_pattern_data(alpha_data)

        # Check if the request wants a JSON response
        if request.headers.get('Accept') == 'application/json':
            return JsonResponse({
                'symbol': symbol,
                'days': days,
                'candlestick_data': pattern_data,
            }, status=200)

        paginator = Paginator(pattern_data, rows_per_page)
        current_page_data = paginator.get_page(page_number)

        chart_cache_key = f"chart_{symbol}_{days}"
        chart_html = cache.get(chart_cache_key)
        if not chart_html:
            chart_html = utils.get_chart_html(pattern_data)
            cache.set(chart_cache_key, chart_html, timeout=cache_timeout)

        return render(request, 'analysis.html', {
            'symbol': symbol,
            'table_data': current_page_data,
            'chart_html': chart_html,
            'paginator': paginator,
            'rows_per_page': rows_per_page,
            'days': days,
        })
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)
    

def imageinsert(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('image')
        if uploaded_file:
            fs = FileSystemStorage()
            filename = fs.save(uploaded_file.name, uploaded_file)
            file_url = fs.url(filename)
            # CNN logic
            messages.success(request, "Image successfully uploaded")
            return render(request, 'imageanalysis.html')
        else:
            messages.error(request, "No image uploaded")
            return render(request, 'imageinsert.html')
    else:
        return render(request, 'imageinsert.html')
    

def imageanalysis(request):
    return render(request, 'imageanalysis.html')


@login_required
def add_to_watchlist(request):
    if request.method == 'POST':
        symbol = request.POST.get('symbol', '').strip()
        days = request.POST.get('days', 30).strip()
        if not symbol:
            messages.error(request, "Invalid symbol.")
            return redirect(f"{reverse('analysis')}?symbol={symbol}&days={days}")

        exists = WatchlistItems.objects.filter(user=request.user, symbol=symbol).exists()
        if not exists:
            WatchlistItems.objects.create(user=request.user, symbol=symbol)
            messages.success(request, f"{symbol} has been added to your watchlist.")
        else:
            messages.warning(request, f"{symbol} is already in your watchlist.")
        return redirect(f"{reverse('analysis')}?symbol={symbol}&days={days}")
    else:
        messages.error(request, "Invalid request method.")
        return redirect(f"{reverse('analysis')}?symbol={symbol}&days={days}")



@login_required
def watchlist(request):
    watchlist_items = WatchlistItems.objects.filter(user=request.user)
    return render(request, 'watchlist.html', {'watchlist_items': watchlist_items})


@login_required
def remove_from_watchlist(request):
    if request.method == 'POST':
        symbol = request.POST.get('symbol', '').strip()
        WatchlistItems.objects.filter(user=request.user, symbol=symbol).delete()
        messages.success(request, f"{symbol} has been removed from your watchlist.")
        return redirect('watchlist')
    else:
        messages.error(request, "Invalid request.")
        return redirect('watchlist')


@login_required
def history(request):
    search_history = History.objects.filter(user=request.user).order_by('-search_date')
    # search_history = History.objects.raw("SELECT id, symbol, days, search_date \
    #                                       FROM analysis_history \
    #                                       WHERE user_id = %s \
    #                                       ORDER BY search_date DESC", [request.user.id])
    return render(request, 'history.html', {'search_history': search_history})


@login_required
def clear_history(request):
    if request.method == 'POST':
        History.objects.filter(user=request.user).delete()
        messages.success(request, "Your search history has been cleared.")
    return HttpResponseRedirect(reverse('history'))


def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save() 
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})


def signout(request):
    logout(request)
    return redirect('/')