from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('products/', views.product_list, name='product_list'),
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),
    path('categories/', views.category_list, name='category_list'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/update/<int:cart_id>/', views.cart_update, name='cart_update'),
    path('cart/remove/<int:cart_id>/', views.cart_remove, name='cart_remove'),
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/add/<int:product_id>/', views.wishlist_add, name='wishlist_add'),
    path('wishlist/remove/<int:wishlist_id>/', views.wishlist_remove, name='wishlist_remove'),
    path('wishlist/toggle/<int:product_id>/', views.wishlist_toggle, name='wishlist_toggle'),
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/products/', views.admin_product_list, name='admin_product_list'),
    path('dashboard/products/add/', views.product_create, name='product_create'),
    path('dashboard/products/<slug:slug>/edit/', views.product_edit, name='product_edit'),
    path('dashboard/products/<slug:slug>/delete/', views.product_delete, name='product_delete'),
    path('dashboard/orders/<int:order_id>/update-status/', views.order_update_status, name='order_update_status'),
]

