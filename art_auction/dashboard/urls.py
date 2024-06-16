from django.urls import path
from dashboard import views
from django.conf import settings
from django.conf.urls.static import static

app_name = "dashboard"
urlpatterns = [
    path('', views.Index.as_view(), name="dashboard"),
    path('addproduct/', views.ArtworkCreateView.as_view(), name="add_product"),
    path('product/', views.ArtworkListView.as_view(), name="product_list"),
    path('bidlist/', views.BidListView.as_view(), name="bid_list"),
    path('productupdate/<int:pk>/', views.ArtworkUpdateView.as_view(), name="product_update"),
    path('product/<int:pk>/delete/', views.ArtworkDeleteView.as_view(), name="product_delete"),
    path('order/', views.OrderListView.as_view(), name="order_list"),
    path('placebid/', views.BidCreateView.as_view(), name="place_bid"),
    path('artwork/<int:pk>/', views.ArtworkDetailView.as_view(), name='artwork_list'),
    path('latest_bid/<int:pk>/', views.latest_bid, name='latest_bid'),  # Updated to use views.latest_bid
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
