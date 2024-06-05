from django.urls import path
from django.http import HttpResponse
from . import views
from django.contrib.auth import views as auth_views

app_name = 'registration'
def test_view(request):
    return HttpResponse("URL is working!")
urlpatterns = [
    path('test/', test_view),
    path('pagenotfound/', views.Get404View.as_view(), name="page_error"),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),  
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
]
