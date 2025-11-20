from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.db.models import Q, Sum
from django.core.paginator import Paginator
from decimal import Decimal
from .models import (
    Product, Category, Cart, Wishlist, Order, OrderItem,
    DeliveryMethod
)
from .forms import UserRegistrationForm, ProductForm, CheckoutForm, UserProfileForm
from .decorators import admin_required


def home(request):
    categories = Category.objects.all()[:6]
    featured_products = Product.objects.filter(is_active=True)[:8]
    return render(request, 'shop/home.html', {
        'categories': categories,
        'featured_products': featured_products,
    })


def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account for {username} has been created successfully!')
            login(request, user)
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'shop/register.html', {'form': form})


class CustomLoginView(LoginView):
    template_name = 'shop/login.html'
    redirect_authenticated_user = True
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, 'You are already logged in.')
            from django.urls import reverse
            from django.shortcuts import redirect
            return redirect(reverse('home'))
        return super().dispatch(request, *args, **kwargs)
    
    def get_success_url(self):
        from django.urls import reverse
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse('home')


class CustomLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        request.session.flush()
        return super().dispatch(request, *args, **kwargs)
    
    def get_success_url(self):
        from django.urls import reverse
        return reverse('home')


def product_list(request):
    products = Product.objects.filter(is_active=True)
    category_slug = request.GET.get('category')
    search_query = request.GET.get('search')
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(specifications__icontains=search_query)
        )
    
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.all()
    
    return render(request, 'shop/product_list.html', {
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': category_slug,
        'search_query': search_query,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:4]
    
    in_wishlist = False
    in_cart = False
    cart_quantity = 0
    
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()
        cart_item = Cart.objects.filter(user=request.user, product=product).first()
        if cart_item:
            in_cart = True
            cart_quantity = cart_item.quantity
    
    return render(request, 'shop/product_detail.html', {
        'product': product,
        'related_products': related_products,
        'in_wishlist': in_wishlist,
        'in_cart': in_cart,
        'cart_quantity': cart_quantity,
    })


def category_list(request):
    categories = Category.objects.all()
    return render(request, 'shop/category_list.html', {'categories': categories})


@admin_required
def admin_dashboard(request):
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_users = User.objects.count()
    recent_orders = Order.objects.all()[:5]
    
    return render(request, 'shop/admin/dashboard.html', {
        'total_products': total_products,
        'total_orders': total_orders,
        'total_users': total_users,
        'recent_orders': recent_orders,
    })


@admin_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Product "{product.name}" has been added successfully!')
            return redirect('product_detail', slug=product.slug)
    else:
        form = ProductForm()
    return render(request, 'shop/admin/product_form.html', {'form': form, 'title': 'Add Product'})


@admin_required
def product_edit(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Product "{product.name}" has been updated successfully!')
            return redirect('product_detail', slug=product.slug)
    else:
        form = ProductForm(instance=product)
    return render(request, 'shop/admin/product_form.html', {
        'form': form,
        'product': product,
        'title': 'Edit Product'
    })


@admin_required
def product_delete(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'Product "{product_name}" has been deleted successfully!')
        return redirect('product_list')
    return render(request, 'shop/admin/product_delete.html', {'product': product})


@admin_required
def order_update_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f'Order #{order.id} status updated to {order.get_status_display()}.')
        else:
            messages.error(request, 'Invalid status selected.')
        return redirect('admin_dashboard')
    return redirect('admin_dashboard')


@admin_required
def admin_product_list(request):
    products = Product.objects.all()
    search_query = request.GET.get('search')
    
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    paginator = Paginator(products, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'shop/admin/product_list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
    })


@login_required
def cart_view(request):
    cart_items = Cart.objects.filter(user=request.user)
    total = sum(item.get_total_price() for item in cart_items)
    
    return render(request, 'shop/cart.html', {
        'cart_items': cart_items,
        'total': total,
    })


@login_required
def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    if not product.is_in_stock():
        messages.error(request, 'Product is not available in stock!')
        return redirect('product_detail', slug=product.slug)
    
    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': 1}
    )
    
    if not created:
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            cart_item.save()
        else:
            messages.error(request, 'Available quantity has been exceeded!')
            return redirect('cart')
    
    messages.success(request, f'{product.name} has been added to cart!')
    next_url = request.GET.get('next', 'cart')
    return redirect(next_url)


@login_required
def cart_update(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0 and quantity <= cart_item.product.stock:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Cart has been updated!')
        else:
            messages.error(request, 'Invalid quantity!')
    
    return redirect('cart')


@login_required
def cart_remove(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
    cart_item.delete()
    messages.success(request, 'Product has been removed from cart!')
    return redirect('cart')


@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, 'shop/wishlist.html', {'wishlist_items': wishlist_items})


@login_required
def wishlist_add(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )
    
    if created:
        messages.success(request, f'{product.name} has been added to wishlist!')
    else:
        messages.info(request, f'{product.name} is already in wishlist!')
    
    next_url = request.GET.get('next', 'product_detail')
    if next_url == 'product_detail':
        return redirect('product_detail', slug=product.slug)
    return redirect(next_url)


@login_required
def wishlist_remove(request, wishlist_id):
    wishlist_item = get_object_or_404(Wishlist, id=wishlist_id, user=request.user)
    product_name = wishlist_item.product.name
    wishlist_item.delete()
    messages.success(request, f'{product_name} has been removed from wishlist!')
    return redirect('wishlist')


@login_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    
    if not cart_items.exists():
        messages.error(request, 'Cart is empty!')
        return redirect('cart')
    
    for item in cart_items:
        if item.quantity > item.product.stock:
            messages.error(request, f'Insufficient stock for {item.product.name}!')
            return redirect('cart')
    
    total = sum(item.get_total_price() for item in cart_items)
    delivery_methods = DeliveryMethod.objects.all()
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.total_price = total
            
            if order.delivery_method:
                order.delivery_cost = order.delivery_method.cost
                order.total_price += order.delivery_cost
            
            order.save()
            
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
                cart_item.product.stock -= cart_item.quantity
                cart_item.product.save()
            
            cart_items.delete()
            
            messages.success(request, f'Order #{order.id} has been placed successfully!')
            return redirect('order_detail', order_id=order.id)
    else:
        initial_data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        }
        form = CheckoutForm(initial=initial_data)
    
    return render(request, 'shop/checkout.html', {
        'form': form,
        'cart_items': cart_items,
        'total': total,
        'delivery_methods': delivery_methods,
    })


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'shop/order_list.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'shop/order_detail.html', {'order': order})


@login_required
def profile(request):
    from .models import UserProfile
    profile_obj, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'shop/profile.html', {'profile': profile_obj})


@login_required
def profile_edit(request):
    from .models import UserProfile
    profile_obj, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile_obj, user=request.user)
        if form.is_valid():
            profile_obj = form.save()
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.email = form.cleaned_data['email']
            request.user.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile_obj, user=request.user)
    
    return render(request, 'shop/profile_edit.html', {'form': form, 'profile': profile_obj})
