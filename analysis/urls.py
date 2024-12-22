from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.home, name="home"),
    path('search/', views.search, name='search'),
    path('matches/', views.matches, name='matches'),
    path('analysis/', views.analysis, name='analysis'),
    path('imageinsert/', views.imageinsert, name='imageinsert'),
    path('imageanalysis/', views.imageanalysis, name='imageanalysis'),
    path('watchlist/', views.watchlist, name='watchlist'),
    path('history/', views.history, name='history'),
    path('history/clear/', views.clear_history, name='clear_history'),
    path('signin/', auth_views.LoginView.as_view(template_name='signin.html'), name='signin'),
    path('signout/', views.signout, name='signout'),
    path('signup/', views.signup, name='signup'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)