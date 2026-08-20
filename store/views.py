from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import transaction

from .models import Product, Order, OrderItem, Coupon
from account.models import Profile

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
            return JsonResponse({
                'success': False,
                'message': f"Only {product.stock} item(s) available."
            })

    return JsonResponse({
        'success': False,
        'message': 'Invalid request'
    }, status=400)


def cart(request):
    cart = request.session.get('cart', {})

    print("CART IN CART PAGE:", cart)

    cart_items = []
    total_price = Decimal('0')

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=int(product_id))

        subtotal = product.price * quantity
        total_price += subtotal

        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,
        })

    # Get coupon information from session
    coupon_code = request.session.get('coupon_code')

    discount_amount = Decimal(
        request.session.get('coupon_discount', '0')
    )

    # Safety check: discount should never be greater than cart total
    if discount_amount > total_price:
        discount_amount = Decimal('0')

        request.session.pop('coupon_code', None)
        request.session.pop('coupon_discount', None)
        request.session.pop('coupon_final_total', None)

        coupon_code = None

    final_total = total_price - discount_amount

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'discount_amount': discount_amount,
        'final_total': final_total,
        'coupon_code': coupon_code,
        'is_checkout_page': False,
    })


def apply_coupon(request):
    if request.method != "POST":
        return redirect('cart')

    code = request.POST.get('coupon_code', '').strip().upper()

    if not code:
        messages.error(request, "Please enter a coupon code.")
        return redirect('cart')

    try:
        coupon = Coupon.objects.get(code=code)

    except Coupon.DoesNotExist:
        messages.error(request, "Invalid coupon code.")
        return redirect('cart')

    now = timezone.now()

    # Check whether coupon is active
    if not coupon.active:
        messages.error(request, "This coupon is not active.")
        return redirect('cart')

    # Check start date
    if now < coupon.valid_from:
        messages.error(request, "This coupon is not valid yet.")
        return redirect('cart')

    # Check expiry
    if now > coupon.valid_until:
        messages.error(request, "This coupon has expired.")
        return redirect('cart')

    # Check usage limit
    if (
        coupon.usage_limit is not None
        and coupon.times_used >= coupon.usage_limit
    ):
        messages.error(
            request,
            "This coupon has reached its usage limit."
        )
        return redirect('cart')

    # Calculate current cart total
    cart = request.session.get('cart', {})

    if not cart:
        messages.error(
            request,
            "Your cart is empty."
        )
        return redirect('cart')

    total_price = Decimal('0')

    for product_id, quantity in cart.items():
        product = get_object_or_404(
            Product,
            id=int(product_id)
        )

        total_price += product.price * quantity

    # Check minimum order amount
    if total_price < coupon.minimum_order_amount:
        messages.error(
            request,
            f"This coupon requires a minimum order of "
            f"₹{coupon.minimum_order_amount}."
        )
        return redirect('cart')

    # Calculate discount
    discount_amount = (
        total_price *
        Decimal(coupon.discount_percent) /
        Decimal('100')
    )

    final_total = total_price - discount_amount

    # Store coupon information in session
    request.session['coupon_code'] = coupon.code
    request.session['coupon_discount'] = str(discount_amount)
    request.session['coupon_final_total'] = str(final_total)

    request.session.modified = True

    messages.success(
        request,
        f"Coupon {coupon.code} applied successfully!"
    )

    return redirect('cart')


def remove_coupon(request):
    if request.method == "POST":
        request.session.pop('coupon_code', None)
        request.session.pop('coupon_discount', None)
        request.session.pop('coupon_final_total', None)

        request.session.modified = True

        messages.success(
            request,
            "Coupon removed."
        )

    return redirect('cart')


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
        messages.warning(
            request,
            f"Only {product.stock} item(s) of {product.name} are available."
        )

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


@login_required(login_url='signin')
def checkout(request):
    cart = request.session.get('cart', {})

    cart_items = []
    total_price = Decimal('0')

    for product_id, quantity in cart.items():
        product = get_object_or_404(
            Product,
            id=int(product_id)
        )

        subtotal = product.price * quantity
        total_price += subtotal

        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,
        })

    # Get coupon information
    coupon_code = request.session.get('coupon_code')

    discount_amount = Decimal(
        request.session.get('coupon_discount', '0')
    )

    # Safety check
    if discount_amount > total_price:
        discount_amount = Decimal('0')

        request.session.pop('coupon_code', None)
        request.session.pop('coupon_discount', None)
        request.session.pop('coupon_final_total', None)

        coupon_code = None

    final_total = total_price - discount_amount

    profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    if request.method == 'POST':

        if not cart_items:
            messages.error(
                request,
                "Your cart is empty."
            )
            return redirect('cart')

        address_line1 = request.POST.get('new_address_line1', '')
        address_line2 = request.POST.get('new_address_line2', '')
        city = request.POST.get('new_city', '')
        state = request.POST.get('new_state', '')
        pincode = request.POST.get('new_pincode', '')

        # Always persist the address back to the profile
        profile.address_line1 = address_line1
        profile.address_line2 = address_line2
        profile.city = city
        profile.state = state
        profile.pincode = pincode
        profile.save()

        delivery_address = ', '.join(
            filter(
                None,
                [address_line1, address_line2, city, state, pincode]
            )
        )

        with transaction.atomic():
            # Lock every product row involved in this order for the duration
            # of the transaction, so two simultaneous checkouts can't both
            # oversell the same stock between "check" and "decrement".
            locked_products = {}
            for product_id in cart.keys():
                locked_products[product_id] = get_object_or_404(
                    Product.objects.select_for_update(),
                    id=int(product_id)
                )

            # Re-validate against the LOCKED, current stock values —
            # not the possibly-stale ones loaded earlier in this view.
            insufficient = []
            for product_id, quantity in cart.items():
                product = locked_products[product_id]
                if quantity > product.stock:
                    insufficient.append((product, quantity))

            if insufficient:
                details = ", ".join(
                    f"{p.name} (only {p.stock} left)" for p, qty in insufficient
                )
                messages.error(
                    request,
                    f"Sorry, some items are no longer available in the "
                    f"requested quantity: {details}. Please update your cart."
                )
                return redirect('cart')

            order = Order.objects.create(
                user=request.user,
                customer_name=request.POST.get(
                    'full_name',
                    request.user.get_full_name() or request.user.username
                ),
                email=request.POST.get('email', request.user.email),
                phone=request.POST.get('phone', ''),
                delivery_address=delivery_address,
                payment_method=request.POST.get('payment_method', 'cod'),
                order_note=request.POST.get('order_note', ''),
                total_price=final_total,
            )

            for product_id, quantity in cart.items():
                product = locked_products[product_id]

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    price=product.price,
                    quantity=quantity,
                )

                # Decrement stock now that the order is confirmed
                product.stock -= quantity
                product.save(update_fields=['stock'])

            # Increase coupon usage only after order creation
            if coupon_code:
                try:
                    coupon = Coupon.objects.get(code=coupon_code)
                    coupon.times_used += 1
                    coupon.save()
                except Coupon.DoesNotExist:
                    pass

        # Clear cart
        request.session['cart'] = {}

        # Clear coupon
        request.session.pop('coupon_code', None)
        request.session.pop('coupon_discount', None)
        request.session.pop('coupon_final_total', None)

        request.session.modified = True

        return redirect(
            'confirmation',
            order_uuid=order.order_uuid
        )

    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'discount_amount': discount_amount,
        'final_total': final_total,
        'coupon_code': coupon_code,
        'profile': profile,
        'is_checkout_page': True,
    })

@login_required(login_url='signin')
def confirmation(request, order_uuid):
    order = get_object_or_404(
        Order,
        order_uuid=order_uuid,
        user=request.user
    )

    return render(request, 'confirmation.html', {
        'order': order,
        'cart_items': order.items.all(),
        'total_price': order.total_price,
    })


@login_required(login_url='signin')
def my_orders(request):
    orders = (
        Order.objects
        .filter(user=request.user)
        .order_by('-created_at')
        .prefetch_related('items')
    )

    return render(request, 'my_orders.html', {
        'orders': orders
    })
