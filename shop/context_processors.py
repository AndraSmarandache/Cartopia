from .models import Cart


def cart_context(request):
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        cart_count = sum(item.quantity for item in cart_items)
        cart_total = sum(item.get_total_price() for item in cart_items)
    else:
        cart_count = 0
        cart_total = 0
    
    return {
        'cart_count': cart_count,
        'cart_total': cart_total,
    }

