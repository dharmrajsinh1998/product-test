import random
import time
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from .models import Category, Product
from .serializers import MyTokenObtainPairSerializer, CategorySerializer, ProductSerializer
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
import threading
from django.utils.decorators import method_decorator
import csv


class MyObtainTokenPairView(TokenObtainPairView):
    """
    Handles obtaining JWT tokens using a custom serializer.

    Attributes:
        permission_classes (tuple): Permissions required for this view.
        serializer_class (class): Serializer class used for token creation.
    """
    permission_classes = (AllowAny,)
    serializer_class = MyTokenObtainPairSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """
    Manages CRUD operations for Category objects.

    Attributes:
        queryset (QuerySet): Queryset for retrieving all Category objects.
        serializer_class (class): Serializer class for Category objects.
        permission_classes (list): List of permissions required for this viewset.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]


class ProductViewSet(viewsets.ModelViewSet):
    """
    Manages CRUD operations for Product objects. Includes an export action to download product data as a CSV file.

    Attributes:
        queryset (QuerySet): Queryset for retrieving all Product objects.
        serializer_class (class): Serializer class for Product objects.
        permission_classes (list): List of permissions required for this viewset.

    Methods:
        export(request): Handles exporting product data as a CSV file.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def export(self, request):
        """
        Exports product data to a CSV file.

        Args:
            request (HttpRequest): The request object.

        Returns:
            HttpResponse: A response object containing the CSV file.
        """
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="products.csv"'

        writer = csv.writer(response)
        writer.writerow(['ID', 'Category', 'Title', 'Description', 'Price', 'Status', 'Created At', 'Updated At'])

        for product in Product.objects.all():
            writer.writerow(
                [product.id, product.category.name, product.title, product.description, product.price, product.status,
                 product.created_at, product.updated_at])

        return response


class GenerateDummyProductTread(threading.Thread):
    """
   A thread class for generating dummy products.

   Attributes:
       number (int): The number of dummy products to generate.

   Methods:
       run(): Generates the dummy products.
   """
    def __init__(self, number):
        threading.Thread.__init__(self)
        self.number = number

    def run(self):
        """
        Generates the specified number of dummy products, creating categories if none exist.
        """
        categories = Category.objects.all()
        if not categories.exists():
            for i in range(10):
                Category.objects.create(name=f"Category {i+1}")
            categories = Category.objects.all()
        for _ in range(self.number):
            categorie = random.choice(categories)
            Product.objects.create(
                categorie=categorie,
                title=f"Product {random.randint(1,1000)}",
                description="Product description",
                price=random.uniform(10.0, 100.0),
                status=True
            )
            time.sleep(0.01)


class GenerateDummyProducts(APIView):
    """
    An API view to trigger the generation of dummy products.

    Methods:
        post(request, *args, **kwargs): Starts the generation of dummy products in a separate thread.
    """
    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        """
        Starts the generation of dummy products in a separate thread.

        Args:
            request (HttpRequest): The request object.

        Returns:
            Response: A response object indicating that the generation has started.
        """
        numbers = int(request.data.get('number',1000))
        thread = GenerateDummyProductTread(numbers)
        thread.start()
        return Response({'status': 'Dummy products generation stated'}, status=status.HTTP_200_OK)


def generate_view(request):
    """
    Renders the "generate.html" template.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: A response object with the rendered template.
    """
    return render(request, "generate.html")
