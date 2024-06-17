from django.urls import path, re_path
from art_auction.consumers import BidConsumer, NotificationConsumer, BidUpdateConsumer

websocket_urlpatterns = [
    path('ws/bid/<str:artwork_id>/', BidConsumer.as_asgi()),
    re_path(r'ws/notifications/$', NotificationConsumer.as_asgi()),
    path('ws/bid_updates/<str:product_id>/', BidUpdateConsumer.as_asgi()),
]
