from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal


class UserProfile(models.Model):
    """Extended user profile with profile picture"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True, verbose_name="Profile Picture")
    bio = models.TextField(blank=True, max_length=500, verbose_name="Bio")
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
    
    def __str__(self):
        return f"{self.user.username}'s Profile"


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Name")
    slug = models.SlugField(unique=True, verbose_name="Slug")
    description = models.TextField(blank=True, verbose_name="Description")
    image = models.ImageField(upload_to='categories/', blank=True, null=True, verbose_name="Image")

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class Supplier(models.Model):
    name = models.CharField(max_length=100, verbose_name="Name")
    contact_email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Phone")
    address = models.TextField(blank=True, verbose_name="Address")

    class Meta:
        verbose_name = "Supplier"
        verbose_name_plural = "Suppliers"

    def __str__(self):
        return self.name


class DeliveryMethod(models.Model):
    name = models.CharField(max_length=100, verbose_name="Name")
    description = models.TextField(blank=True, verbose_name="Description")
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Cost")

    class Meta:
        verbose_name = "Delivery Method"
        verbose_name_plural = "Delivery Methods"

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Name")
    slug = models.SlugField(unique=True, verbose_name="Slug")
    description = models.TextField(verbose_name="Description")
    specifications = models.TextField(verbose_name="Specifications", help_text="Detailed technical specifications")
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], verbose_name="Price")
    stock = models.PositiveIntegerField(default=0, verbose_name="Stock")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name="Category")
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name='products', verbose_name="Supplier")
    delivery_method = models.ForeignKey(DeliveryMethod, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Delivery Method")
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="Main Image")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")
    is_active = models.BooleanField(default=True, verbose_name="Active")

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def is_in_stock(self):
        return self.stock > 0


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/', verbose_name="Image")
    alt_text = models.CharField(max_length=200, blank=True, verbose_name="Alt Text")

    class Meta:
        verbose_name = "Product Image"
        verbose_name_plural = "Product Images"


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart', verbose_name="User")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Product")
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)], verbose_name="Quantity")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Added At")

    class Meta:
        verbose_name = "Cart"
        verbose_name_plural = "Carts"
        unique_together = ['user', 'product']

    def __str__(self):
        return f"{self.user.username} - {self.product.name} x{self.quantity}"

    def get_total_price(self):
        return self.product.price * self.quantity


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist', verbose_name="User")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Product")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Added At")

    class Meta:
        verbose_name = "Wishlist"
        verbose_name_plural = "Wishlists"
        unique_together = ['user', 'product']

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name="User")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Status")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total Price")
    delivery_method = models.ForeignKey(DeliveryMethod, on_delete=models.SET_NULL, null=True, verbose_name="Delivery Method")
    delivery_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Delivery Cost")
    
    # Delivery information
    first_name = models.CharField(max_length=100, verbose_name="First Name")
    last_name = models.CharField(max_length=100, verbose_name="Last Name")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Phone")
    address = models.TextField(verbose_name="Address")
    city = models.CharField(max_length=100, verbose_name="City")
    postal_code = models.CharField(max_length=20, verbose_name="Postal Code")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Order Date")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ['-created_at']

    def __str__(self):
        return f"Comanda #{self.id} - {self.user.username}"

    def get_products_total(self):
        """Calculate total products price without delivery cost"""
        return self.total_price - self.delivery_cost


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="Order")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Product")
    quantity = models.PositiveIntegerField(verbose_name="Quantity")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Price")

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"

    def __str__(self):
        return f"{self.order} - {self.product.name} x{self.quantity}"

    def get_total_price(self):
        return self.price * self.quantity

