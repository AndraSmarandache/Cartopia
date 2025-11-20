from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.files import File
from shop.models import Category, Supplier, DeliveryMethod, Product, UserProfile
import urllib.request
import tempfile
import os


class Command(BaseCommand):
    help = 'Incarca date de test in baza de date'

    def handle(self, *args, **options):
        self.stdout.write('Loading sample data...')

        # Category images URLs
        category_images = {
            'electronice': 'https://images.unsplash.com/photo-1468495244123-6c6c332eeece?w=500&h=500&fit=crop',
            'laptopuri': 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=500&h=500&fit=crop',
            'telefoane': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500&h=500&fit=crop',
            'accesorii': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&h=500&fit=crop',
            'gaming': 'https://images.unsplash.com/photo-1603302576837-3756b0720b18?w=500&h=500&fit=crop',
        }

        # Create categories
        categories_data = [
            {'name': 'Electronics', 'slug': 'electronice', 'description': 'Electronic products and gadgets'},
            {'name': 'Laptops', 'slug': 'laptopuri', 'description': 'Laptops and computers'},
            {'name': 'Phones', 'slug': 'telefoane', 'description': 'Mobile phones and smartphones'},
            {'name': 'Accessories', 'slug': 'accesorii', 'description': 'Electronic accessories'},
            {'name': 'Gaming', 'slug': 'gaming', 'description': 'Gaming products'},
        ]

        categories = {}
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            
            # Download and save category image
            if created and category.slug in category_images and not category.image:
                try:
                    image_url = category_images[category.slug]
                    req = urllib.request.Request(
                        image_url,
                        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                    )
                    img_response = urllib.request.urlopen(req, timeout=15)
                    img_data = img_response.read()
                    
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as img_temp:
                        img_temp.write(img_data)
                        temp_path = img_temp.name
                    
                    with open(temp_path, 'rb') as f:
                        category.image.save(f"{category.slug}.jpg", File(f), save=True)
                    
                    os.unlink(temp_path)
                    self.stdout.write(self.style.SUCCESS(f'Category created with image: {category.name}'))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Could not download image for category {category.name}: {e}'))
                    self.stdout.write(self.style.SUCCESS(f'Category created: {category.name}'))
            elif created:
                self.stdout.write(self.style.SUCCESS(f'Category created: {category.name}'))
            
            categories[cat_data['slug']] = category

        # Create suppliers
        suppliers_data = [
            {'name': 'TechSupplier Inc', 'contact_email': 'contact@techsupplier.com', 'phone': '+1-555-0123'},
            {'name': 'ElectroWorld', 'contact_email': 'info@electroworld.com', 'phone': '+1-555-0456'},
            {'name': 'GamingStore', 'contact_email': 'sales@gamingstore.com', 'phone': '+1-555-0789'},
        ]

        suppliers = {}
        for supp_data in suppliers_data:
            supplier, created = Supplier.objects.get_or_create(
                name=supp_data['name'],
                defaults=supp_data
            )
            suppliers[supp_data['name']] = supplier
            if created:
                self.stdout.write(self.style.SUCCESS(f'Supplier created: {supplier.name}'))

        # Create delivery methods
        delivery_methods_data = [
            {'name': 'Courier', 'description': 'Fast courier delivery', 'cost': 15.00},
            {'name': 'Fan Courier', 'description': 'Fan Courier delivery', 'cost': 12.00},
            {'name': 'Pickup', 'description': 'Store pickup', 'cost': 0.00},
            {'name': 'Standard Mail', 'description': 'Standard mail delivery', 'cost': 8.00},
        ]

        delivery_methods = {}
        for del_data in delivery_methods_data:
            delivery, created = DeliveryMethod.objects.get_or_create(
                name=del_data['name'],
                defaults=del_data
            )
            delivery_methods[del_data['name']] = delivery
            if created:
                self.stdout.write(self.style.SUCCESS(f'Delivery method created: {delivery.name}'))

        # Creare produse
        products_data = [
            {
                'name': 'Laptop ASUS VivoBook 15',
                'slug': 'laptop-asus-vivobook-15',
                'description': 'ASUS VivoBook 15 laptop with Intel Core i5 processor, 8GB RAM, 512GB SSD',
                'specifications': 'Processor: Intel Core i5-1135G7\nRAM: 8GB DDR4\nStorage: 512GB SSD\nDisplay: 15.6" Full HD\nGraphics: Intel Iris Xe',
                'price': 2999.99,
                'stock': 15,
                'category': categories['laptopuri'],
                'supplier': suppliers['TechSupplier Inc'],
                'delivery_method': delivery_methods['Courier'],
            },
            {
                'name': 'iPhone 14 Pro',
                'slug': 'iphone-14-pro',
                'description': 'iPhone 14 Pro with 6.1" Super Retina XDR display, A16 Bionic processor',
                'specifications': 'Display: 6.1" Super Retina XDR\nProcessor: A16 Bionic\nStorage: 128GB\nCamera: 48MP + 12MP + 12MP\nBattery: Up to 23 hours video',
                'price': 5499.99,
                'stock': 8,
                'category': categories['telefoane'],
                'supplier': suppliers['ElectroWorld'],
                'delivery_method': delivery_methods['Fan Courier'],
            },
            {
                'name': 'Samsung Galaxy S23 Ultra',
                'slug': 'samsung-galaxy-s23-ultra',
                'description': 'Samsung Galaxy S23 Ultra with 6.8" Dynamic AMOLED 2X display, Snapdragon 8 Gen 2 processor',
                'specifications': 'Display: 6.8" Dynamic AMOLED 2X\nProcessor: Snapdragon 8 Gen 2\nRAM: 12GB\nStorage: 256GB\nCamera: 200MP + 10MP + 10MP + 12MP',
                'price': 4999.99,
                'stock': 12,
                'category': categories['telefoane'],
                'supplier': suppliers['ElectroWorld'],
                'delivery_method': delivery_methods['Fan Courier'],
            },
            {
                'name': 'Mouse Gaming Logitech G502',
                'slug': 'mouse-gaming-logitech-g502',
                'description': 'Logitech G502 Hero gaming mouse with HERO 25K sensor, 11 programmable buttons',
                'specifications': 'Sensor: HERO 25K\nDPI: 100-25,600\nButtons: 11 programmable\nLighting: RGB\nConnection: USB',
                'price': 299.99,
                'stock': 25,
                'category': categories['gaming'],
                'supplier': suppliers['GamingStore'],
                'delivery_method': delivery_methods['Standard Mail'],
            },
            {
                'name': 'Mechanical RGB Keyboard',
                'slug': 'mechanical-rgb-keyboard',
                'description': 'Mechanical gaming keyboard with Cherry MX switches, RGB lighting',
                'specifications': 'Switches: Cherry MX Red\nLayout: Full-size\nLighting: RGB\nConnection: USB-C\nAnti-ghosting: Full NKRO',
                'price': 599.99,
                'stock': 18,
                'category': categories['gaming'],
                'supplier': suppliers['GamingStore'],
                'delivery_method': delivery_methods['Standard Mail'],
            },
            {
                'name': 'Sony WH-1000XM4 Bluetooth Headphones',
                'slug': 'sony-wh1000xm4-bluetooth-headphones',
                'description': 'Premium wireless headphones with noise cancellation, 30-hour battery',
                'specifications': 'Type: Over-ear\nNoise Cancelling: Yes\nBattery: 30 hours\nBluetooth: 5.0\nMicrophone: Yes',
                'price': 1299.99,
                'stock': 10,
                'category': categories['accesorii'],
                'supplier': suppliers['TechSupplier Inc'],
                'delivery_method': delivery_methods['Courier'],
            },
            {
                'name': 'iPad Air Tablet',
                'slug': 'ipad-air-tablet',
                'description': 'iPad Air with 10.9" Liquid Retina display, M1 processor',
                'specifications': 'Display: 10.9" Liquid Retina\nProcessor: Apple M1\nStorage: 64GB\nCamera: 12MP\nBattery: Up to 10 hours',
                'price': 3499.99,
                'stock': 6,
                'category': categories['electronice'],
                'supplier': suppliers['ElectroWorld'],
                'delivery_method': delivery_methods['Fan Courier'],
            },
            {
                'name': 'Apple Watch Series 8',
                'slug': 'apple-watch-series-8',
                'description': 'Apple Watch Series 8 with Always-On Retina display, GPS, water resistant',
                'specifications': 'Display: Always-On Retina\nGPS: Yes\nWater Resistant: Yes (50m)\nBattery: Up to 18 hours\nSensors: Heart rate, ECG',
                'price': 2299.99,
                'stock': 14,
                'category': categories['accesorii'],
                'supplier': suppliers['ElectroWorld'],
                'delivery_method': delivery_methods['Standard Mail'],
            },
            {
                'name': 'Webcam Logitech C920',
                'slug': 'webcam-logitech-c920',
                'description': 'Full HD 1080p webcam with stereo microphone, perfect for video conferencing',
                'specifications': 'Resolution: 1080p Full HD\nFrame rate: 30fps\nMicrophone: Stereo\nAuto-focus: Yes\nCompatibility: USB 2.0',
                'price': 399.99,
                'stock': 20,
                'category': categories['accesorii'],
                'supplier': suppliers['TechSupplier Inc'],
                'delivery_method': delivery_methods['Standard Mail'],
            },
            {
                'name': 'Laptop Gaming ASUS ROG Strix',
                'slug': 'laptop-gaming-asus-rog-strix',
                'description': 'ASUS ROG Strix gaming laptop with AMD Ryzen 9 processor, RTX 3070, 16GB RAM',
                'specifications': 'Processor: AMD Ryzen 9 5900HX\nGraphics: NVIDIA RTX 3070\nRAM: 16GB DDR4\nStorage: 1TB SSD\nDisplay: 15.6" Full HD 144Hz',
                'price': 8999.99,
                'stock': 5,
                'category': categories['gaming'],
                'supplier': suppliers['GamingStore'],
                'delivery_method': delivery_methods['Courier'],
            },
        ]

        # Product images URLs - using reliable image sources
        product_images = {
            'laptop-asus-vivobook-15': 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=500&h=500&fit=crop',
            'iphone-14-pro': 'https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=500&h=500&fit=crop',
            'samsung-galaxy-s23-ultra': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500&h=500&fit=crop',
            'mouse-gaming-logitech-g502': 'https://images.unsplash.com/photo-1527814050087-3793815479db?w=500&h=500&fit=crop',
            'mechanical-rgb-keyboard': 'https://images.unsplash.com/photo-1541140532154-b024d705b90a?w=500&h=500&fit=crop',
            'sony-wh1000xm4-bluetooth-headphones': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&h=500&fit=crop',
            'ipad-air-tablet': 'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=500&h=500&fit=crop',
            'apple-watch-series-8': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&h=500&fit=crop',
            'webcam-logitech-c920': 'https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=500&h=500&fit=crop',
            'laptop-gaming-asus-rog-strix': 'https://images.unsplash.com/photo-1603302576837-3756b0720b18?w=500&h=500&fit=crop',
        }

        for prod_data in products_data:
            product, created = Product.objects.get_or_create(
                slug=prod_data['slug'],
                defaults=prod_data
            )
            
            # Download and save product image (for both new and existing products without images)
            if product.slug in product_images and not product.image:
                try:
                    image_url = product_images[product.slug]
                    self.stdout.write(f'Downloading image for {product.name}...')
                    req = urllib.request.Request(
                        image_url,
                        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                    )
                    img_response = urllib.request.urlopen(req, timeout=15)
                    img_data = img_response.read()
                    
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as img_temp:
                        img_temp.write(img_data)
                        temp_path = img_temp.name
                    
                    with open(temp_path, 'rb') as f:
                        product.image.save(f"{product.slug}.jpg", File(f), save=True)
                    
                    os.unlink(temp_path)
                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Product created with image: {product.name}'))
                    else:
                        self.stdout.write(self.style.SUCCESS(f'Image added to existing product: {product.name}'))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Could not download image for {product.name}: {e}'))
                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Product created without image: {product.name}'))
            elif created:
                self.stdout.write(self.style.SUCCESS(f'Product created: {product.name}'))

        # Create admin user if doesn't exist
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            # Create profile for admin
            UserProfile.objects.get_or_create(user=admin_user)
            self.stdout.write(self.style.SUCCESS('Admin user created: admin / admin123'))

        # Create normal test user
        if not User.objects.filter(username='testuser').exists():
            test_user = User.objects.create_user(
                username='testuser',
                email='test@example.com',
                password='test123',
                first_name='Test',
                last_name='User'
            )
            # Create profile for test user
            UserProfile.objects.get_or_create(user=test_user)
            self.stdout.write(self.style.SUCCESS('Test user created: testuser / test123'))

        self.stdout.write(self.style.SUCCESS('\nSample data loaded successfully!'))
        self.stdout.write(self.style.WARNING('\nTest credentials:'))
        self.stdout.write(self.style.WARNING('Admin: admin / admin123'))
        self.stdout.write(self.style.WARNING('User: testuser / test123'))

