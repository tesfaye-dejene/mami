from decimal import Decimal, InvalidOperation
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.db.models import Count, Sum, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from apps.customers.infrastructure.models import Customer
from apps.inventory.infrastructure.models import Product
from apps.orders.infrastructure.models import Order, OrderItem
from apps.orders.application.use_cases.create_order import CreateOrder
from apps.services.infrastructure.models import Service

User = get_user_model()


def is_staff_user(user):
    return user.is_authenticated and user.is_staff


def get_cart(request):
    return request.session.get("cart", {})


def save_cart(request, cart):
    request.session["cart"] = cart
    request.session.modified = True


def cart_details(request):
    cart = get_cart(request)
    items = []
    total = Decimal("0.00")
    for product_id, qty in cart.items():
        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except (Product.DoesNotExist, ValueError):
            continue
        quantity = int(qty)
        subtotal = product.price * quantity
        items.append({"product": product, "quantity": quantity, "subtotal": subtotal})
        total += subtotal
    return items, total


# ---------- Public / Customer ----------

def home(request):
    products = Product.objects.filter(is_active=True, is_available=True).prefetch_related("images")
    services = Service.objects.filter(is_active=True)
    items, total = cart_details(request)
    return render(request, "shop/home.html", {
        "products": products,
        "services": services,
        "cart_count": sum(i["quantity"] for i in items),
        "cart_total": total,
    })


@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True, is_available=True)
    cart = get_cart(request)
    key = str(product.id)
    cart[key] = cart.get(key, 0) + 1
    save_cart(request, cart)
    messages.success(request, f"{product.name} added to cart.")
    return redirect(request.POST.get("next") or "shop:home")


@require_POST
def cart_update(request, product_id):
    cart = get_cart(request)
    key = str(product_id)
    try:
        qty = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        qty = 1
    if qty <= 0:
        cart.pop(key, None)
    else:
        cart[key] = qty
    save_cart(request, cart)
    messages.success(request, "Cart updated.")
    return redirect("shop:cart")


@require_POST
def cart_remove(request, product_id):
    cart = get_cart(request)
    cart.pop(str(product_id), None)
    save_cart(request, cart)
    messages.success(request, "Item removed from cart.")
    return redirect("shop:cart")


def cart_view(request):
    items, total = cart_details(request)
    return render(request, "shop/cart.html", {
        "items": items,
        "cart_total": total,
        "cart_count": sum(i["quantity"] for i in items),
    })


@login_required
@require_POST
def checkout(request):
    items, total = cart_details(request)
    if not items:
        messages.error(request, "Your cart is empty.")
        return redirect("shop:cart")

    try:
        customer = Customer.objects.get(user=request.user, is_active=True, deleted_at__isnull=True)
    except Customer.DoesNotExist:
        messages.error(request, "Customer profile not found. Please complete registration.")
        return redirect("shop:home")

    order_items = [
        {"product_id": item["product"].id, "quantity": item["quantity"]}
        for item in items
    ]
    try:
        order = CreateOrder().execute(customer, order_items)
    except Exception as exc:
        messages.error(request, str(exc))
        return redirect("shop:cart")

    save_cart(request, {})
    messages.success(
        request,
        f"Order placed successfully! Order ID: {str(order.id)[:8]}… "
        "Only you and the shop owner can see this order."
    )
    return redirect("shop:my_orders")


def register_view(request):
    if request.user.is_authenticated:
        return redirect("shop:home")
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        password2 = request.POST.get("password2", "")
        full_name = request.POST.get("full_name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        address = request.POST.get("address", "").strip()

        errors = []
        if not username or not password or not full_name:
            errors.append("Username, password and full name are required.")
        if password != password2:
            errors.append("Passwords do not match.")
        if len(password) < 8:
            errors.append("Password must be at least 8 characters.")
        if User.objects.filter(username=username).exists():
            errors.append("Username already exists.")
        if email and User.objects.filter(email=email).exists():
            errors.append("Email already exists.")

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, "shop/register.html", {"form": request.POST})

        user = User.objects.create_user(username=username, email=email, password=password)
        Customer.objects.create(
            user=user, full_name=full_name, email=email, phone=phone, address=address
        )
        login(request, user)
        messages.success(request, "Account created. Welcome!")
        return redirect("shop:home")

    return render(request, "shop/register.html")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("shop:home")
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is None:
            messages.error(request, "Invalid username or password.")
            return render(request, "shop/login.html", {"username": username})
        if not user.is_active:
            messages.error(request, "This account is inactive.")
            return render(request, "shop/login.html")
        login(request, user)
        messages.success(request, f"Welcome back, {user.username}!")
        next_url = request.GET.get("next") or "shop:home"
        if user.is_staff:
            next_url = request.GET.get("next") or "shop:admin_dashboard"
        return redirect(next_url)
    return render(request, "shop/login.html")


def logout_view(request):
    logout(request)
    messages.success(request, "Logged out.")
    return redirect("shop:home")


@login_required
def my_orders(request):
    """Customer sees ONLY their own orders."""
    orders = (
        Order.objects.filter(customer__user=request.user)
        .prefetch_related("items")
        .order_by("-created_at")
    )
    return render(request, "shop/my_orders.html", {
        "orders": orders,
        "cart_count": sum(i["quantity"] for i in cart_details(request)[0]),
    })


@login_required
def order_detail(request, order_id):
    """Customer: only own order. Staff: any order."""
    qs = Order.objects.prefetch_related("items", "customer")
    if request.user.is_staff:
        order = get_object_or_404(qs, id=order_id)
    else:
        order = get_object_or_404(qs, id=order_id, customer__user=request.user)
    return render(request, "shop/order_detail.html", {
        "order": order,
        "cart_count": sum(i["quantity"] for i in cart_details(request)[0]),
        "status_choices": Order.Status.choices,
        "payment_choices": Order.PaymentStatus.choices,
    })


# ---------- Admin / Owner only ----------

@login_required
@user_passes_test(is_staff_user, login_url="shop:login")
def admin_dashboard(request):
    """Owner sees order counts and overview — not visible to regular customers."""
    total_orders = Order.objects.count()
    by_status = (
        Order.objects.values("status")
        .annotate(count=Count("id"))
        .order_by("status")
    )
    status_counts = {row["status"]: row["count"] for row in by_status}
    pending = status_counts.get(Order.Status.PENDING, 0)
    confirmed = status_counts.get(Order.Status.CONFIRMED, 0)
    processing = status_counts.get(Order.Status.PROCESSING, 0)
    completed = status_counts.get(Order.Status.COMPLETED, 0)
    cancelled = status_counts.get(Order.Status.CANCELLED, 0)

    revenue = (
        Order.objects.filter(status=Order.Status.COMPLETED)
        .aggregate(s=Sum("total_amount"))["s"]
        or Decimal("0")
    )
    recent = Order.objects.select_related("customer").prefetch_related("items")[:10]
    product_count = Product.objects.filter(is_active=True).count()
    customer_count = Customer.objects.filter(is_active=True, deleted_at__isnull=True).count()

    return render(request, "shop/admin_dashboard.html", {
        "total_orders": total_orders,
        "pending": pending,
        "confirmed": confirmed,
        "processing": processing,
        "completed": completed,
        "cancelled": cancelled,
        "revenue": revenue,
        "recent_orders": recent,
        "product_count": product_count,
        "customer_count": customer_count,
        "status_choices": Order.Status.choices,
    })


@login_required
@user_passes_test(is_staff_user, login_url="shop:login")
def admin_orders(request):
    """Full order list — admin/owner only."""
    qs = Order.objects.select_related("customer").prefetch_related("items")
    status_filter = request.GET.get("status", "")
    if status_filter:
        qs = qs.filter(status=status_filter)
    payment_filter = request.GET.get("payment", "")
    if payment_filter:
        qs = qs.filter(payment_status=payment_filter)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(customer__full_name__icontains=q)
            | Q(customer__email__icontains=q)
            | Q(id__icontains=q)
        )
    orders = qs.order_by("-created_at")[:100]
    total = Order.objects.count()
    return render(request, "shop/admin_orders.html", {
        "orders": orders,
        "total_orders": total,
        "status_filter": status_filter,
        "payment_filter": payment_filter,
        "q": q,
        "status_choices": Order.Status.choices,
        "payment_choices": Order.PaymentStatus.choices,
    })


@login_required
@user_passes_test(is_staff_user, login_url="shop:login")
@require_POST
def admin_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    new_status = request.POST.get("status")
    if new_status in dict(Order.Status.choices):
        order.status = new_status
        order.save(update_fields=["status", "updated_at"])
        messages.success(request, f"Order status updated to {new_status}.")
    else:
        messages.error(request, "Invalid status.")
    return redirect(request.POST.get("next") or "shop:admin_orders")


@login_required
@user_passes_test(is_staff_user, login_url="shop:login")
@require_POST
def admin_order_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    new_pay = request.POST.get("payment_status")
    if new_pay in dict(Order.PaymentStatus.choices):
        order.payment_status = new_pay
        order.save(update_fields=["payment_status", "updated_at"])
        messages.success(request, f"Payment status updated to {new_pay}.")
    else:
        messages.error(request, "Invalid payment status.")
    return redirect(request.POST.get("next") or "shop:admin_orders")


@login_required
@user_passes_test(is_staff_user, login_url="shop:login")
def admin_products(request):
    products = Product.objects.prefetch_related("images").order_by("-created_at")
    return render(request, "shop/admin_products.html", {"products": products})
