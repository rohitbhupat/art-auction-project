from django.urls import path
from ..art_auction.consumers import BidConsumer

websocket_urlpatterns = [
    path('ws/bid/<str:product_id>/', BidConsumer.as_asgi()),
]
