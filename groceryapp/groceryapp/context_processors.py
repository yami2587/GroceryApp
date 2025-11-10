from orders.models import CartItem
#context processor to add cart count and user role to templates
def cart_and_role(request):
    cart_count = 0
    is_manager = False
    if request.user.is_authenticated:
        cart_count = CartItem.objects.filter(user=request.user).count()
        is_manager = getattr(request.user, "role", "") == "manager"
    return {"cart_count": cart_count, "is_manager": is_manager}
