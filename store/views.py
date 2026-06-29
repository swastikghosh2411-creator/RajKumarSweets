from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Q
from .models import Product


def home(request):
    products = Product.objects.all()

    search_query = request.GET.get('search', '')
    filter_type = request.GET.get('filter', '')

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )

    if filter_type == 'bestsellers':
        products = products.filter(is_bestseller=True)

    elif filter_type == 'popular':
        products = products.filter(is_popular=True)

    elif filter_type == 'available':
        products = products.filter(stock__gt=0)

    context = {
        'products': products,
        'search_query': search_query,
        'filter_type': filter_type,
    }

    return render(request, 'Landpage.html', context)


def signin(request):
    return HttpResponse("Signin backend route working")


def signup(request):
    return render(request, 'signup.html')


def contact(request):
    return HttpResponse("This is the contact page")


def cart(request):
    return render(request, 'cart.html')