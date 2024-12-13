import requests
from . import utils
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from .forms import CustomUserCreationForm  # Import the custom form


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
        days = 100 # TODO: Get from user input
        alpha_data = utils.get_alpha_data(symbol, days)
        pattern_data = utils.get_pattern_data(alpha_data)
        chart_html = utils.get_chart_html(pattern_data)
        
        return render(request, 'analysis.html', {'symbol': symbol, 'table_data': pattern_data, 'chart_html': chart_html})
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
            return render(request, 'imageanalysis.html', {})
        else:
            messages.error(request, "No image uploaded")
            return render(request, 'imageinsert.html')
    else:
        return render(request, 'imageinsert.html')
    

@login_required
def history(request):
    return render(request, 'history.html')


def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your account has been created! You can now sign in.")
            return redirect('signin')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})


def signout(request):
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect('/')