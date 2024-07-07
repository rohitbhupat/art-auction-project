from django.urls import path,include
from art import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

app_name = "art"
urlpatterns = [
   path('',views.index.as_view(),name="index"),
   path('signup/',views.register_user,name="register_user"),
   path('register_seller/',views.RegisterSeller.as_view(),name="register_seller"),
   path('accounts/login/',views.user_login,name="login"),
   path('profile/',views.Profile.as_view(),name="profile"),
   path('logout/',views.logout_view,name="logout"),
   path('viewdetails/<int:pk>/',views.ArtworkDetailView.as_view(),name="product_details"),
   path('addorder/<int:pk>',views.OrderCreateView.as_view(),name="place_order"),
   path('orderconfirm/',views.OrderCreateView.as_view(),name="confirm_order"),
   path("callback/", views.callback, name="callback"),
   path("arview/<int:id>", views.ArView.as_view(), name="view_3d"),
   path("about/", views.About.as_view(), name="about"),
   path("contact/", views.Contact.as_view(), name="contact"),
   path("faq/", views.FAQs.as_view(), name="faq"),
   path('unsold/',views.UnsoldListView.as_view(),name="unsold_items"),
   path('cat/<int:id>/',views.CatListView.catalog_products,name="catalog_products"),
   path('profile-settings/', views.profile_settings, name='profile_settings'),
]
if settings.DEBUG:
     urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)