from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm  # Import the custom form

@login_required
def history(request):
    return render(request, 'history.html')

def home(request):
    # stocks = Stock.objects.all()
    # portfolio = Portfolio.objects.get(user=request.user)
    # return render(request, 'home.html', {'stocks': stocks, 'portfolio': portfolio})
    return render(request, 'home.html', {})

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
    logout(request)  # Logs out the user
    messages.success(request, "You have been successfully logged out.")
    return redirect('/')