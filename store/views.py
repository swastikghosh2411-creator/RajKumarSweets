from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.db.models import Q
from .models import Product
from django.contrib import messages
from django.urls import reverse

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
    return render(request, 'signin.html')


def signup(request):
    return render(request, 'signup.html')


def contact(request):
    return HttpResponse("This is the contact page")


def add_to_cart(request, product_id):
    if request.method == "POST":
        product = get_object_or_404(Product, id=product_id)

        cart = request.session.get('cart', {})
        product_id_str = str(product.id)

        current_quantity = cart.get(product_id_str, 0)

        if current_quantity < product.stock:
            cart[product_id_str] = current_quantity + 1
            request.session['cart'] = cart
            request.session.modified = True
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'message': f"Only {product.stock} item(s) available."})

    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)

def cart(request):
    cart = request.session.get('cart', {})

    print("CART IN CART PAGE:", cart)

    cart_items = []
    total_price = 0

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=int(product_id))

        subtotal = product.price * quantity
        total_price += subtotal

        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,
        })

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
    })


def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        del cart[product_id_str]

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart')


def increase_cart_item(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    cart = request.session.get('cart', {})
    product_id_str = str(product.id)

    current_quantity = cart.get(product_id_str, 0)

    if current_quantity < product.stock:
        cart[product_id_str] = current_quantity + 1
        request.session['cart'] = cart
        request.session.modified = True
    else:
        messages.warning(request, f"Only {product.stock} item(s) of {product.name} are available.")

    return redirect('cart')


def decrease_cart_item(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        cart[product_id_str] -= 1

        if cart[product_id_str] <= 0:
            del cart[product_id_str]

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart')