from orders.models import CartItem

def cart_and_role(request):
    cart_count = 0
    is_manager = False
    if request.user.is_authenticated:
        cart_count = CartItem.objects.filter(user=request.user).count()
        is_manager = getattr(request.user, "role", "") == "manager"
    return {"cart_count": cart_count, "is_manager": is_manager}
