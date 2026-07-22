from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signin/', views.signin, name='signin'),
    path('signup/', views.signup, name='signup'),
    path('contact/', views.contact, name='contact'),

    # Cart URLs
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/increase/<int:product_id>/', views.increase_cart_item, name='increase_cart_item'),
    path('cart/decrease/<int:product_id>/', views.decrease_cart_item, name='decrease_cart_item'),

    path('checkout/', views.checkout, name='checkout'),
]