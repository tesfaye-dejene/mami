from django.contrib.auth import authenticate, get_user_model
from django.db import transaction
from rest_framework import permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.customers.infrastructure.models import Customer

User = get_user_model()

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    @transaction.atomic
    def post(self, request):
        username = str(request.data.get("username", "")).strip()
        password = str(request.data.get("password", ""))
        full_name = str(request.data.get("full_name", "")).strip()
        email = str(request.data.get("email", "")).strip()
        phone = str(request.data.get("phone", "")).strip()
        address = str(request.data.get("address", "")).strip()
        if not username or not password or not full_name:
            return Response({"detail":"username, password and full_name are required."}, status=400)
        if len(password) < 8:
            return Response({"detail":"Password must contain at least 8 characters."}, status=400)
        if User.objects.filter(username=username).exists():
            return Response({"detail":"Username already exists."}, status=400)
        if email and User.objects.filter(email=email).exists():
            return Response({"detail":"Email already exists."}, status=400)
        user = User.objects.create_user(username=username, email=email, password=password)
        Customer.objects.create(user=user, full_name=full_name, email=email, phone=phone, address=address)
        token = Token.objects.create(user=user)
        return Response({"token":token.key, "user":user_payload(user)}, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        username = str(request.data.get("username", "")).strip()
        password = str(request.data.get("password", ""))
        user = authenticate(username=username, password=password)
        if not user:
            return Response({"detail":"Invalid username or password."}, status=400)
        if not user.is_active:
            return Response({"detail":"This account is inactive."}, status=403)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token":token.key, "user":user_payload(user)})

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response({"detail":"Logged out successfully."})

class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        return Response(user_payload(request.user))

def user_payload(user):
    customer = getattr(user, "customer", None)
    return {
        "id": user.id, "username": user.username, "email": user.email,
        "is_staff": user.is_staff, "full_name": customer.full_name if customer else user.get_full_name(),
        "customer_id": str(customer.id) if customer else None,
    }
