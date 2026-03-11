from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.contrib import messages
from .models import (
    UserProfile, Category, Supplier, DeliveryMethod, Product, ProductImage,
    Cart, Wishlist, Order, OrderItem, Review
)
from .pdf_utils import generate_and_attach_pdf

admin.site.site_header = "Cartopia Administration"
admin.site.site_title = "Cartopia Admin"
admin.site.index_title = "Welcome to Cartopia Administration"


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'profile_picture']
    search_fields = ['user__username', 'user__email']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_email', 'phone']


@admin.register(DeliveryMethod)
class DeliveryMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'cost']


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'has_descriptive_pdf', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]
    actions = ['generate_specification_pdf']

    def has_descriptive_pdf(self, obj):
        return bool(obj.descriptive_pdf)
    has_descriptive_pdf.boolean = True
    has_descriptive_pdf.short_description = 'PDF'

    @admin.action(description='Generate specification PDF')
    def generate_specification_pdf(self, request, queryset):
        count = 0
        for product in queryset:
            try:
                generate_and_attach_pdf(product)
                count += 1
            except Exception as e:
                self.message_user(request, f'Error for "{product.name}": {e}', level=messages.ERROR)
        if count:
            self.message_user(request, f'Generated specification PDF for {count} product(s).', level=messages.SUCCESS)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'quantity', 'created_at']
    list_filter = ['created_at']


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'created_at']
    list_filter = ['created_at']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['get_total_price']

    def get_total_price(self, obj):
        if obj.id:
            return obj.get_total_price()
        return '-'
    get_total_price.short_description = 'Total'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'total_price', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'email', 'first_name', 'last_name']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [OrderItemInline]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'rating', 'title', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_approved', 'created_at']
    search_fields = ['user__username', 'product__name', 'title', 'comment']
    readonly_fields = ['created_at', 'updated_at']

