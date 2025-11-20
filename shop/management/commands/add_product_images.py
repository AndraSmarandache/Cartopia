from django.core.management.base import BaseCommand
from django.core.files import File
from shop.models import Product
import urllib.request
import tempfile
import os


class Command(BaseCommand):
    help = 'Add images to products that don\'t have them'

    def handle(self, *args, **options):
        # Product images URLs - using reliable image sources with different images for similar products
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

        products = Product.objects.all()
        added_count = 0
        
        for product in products:
            if not product.image and product.slug in product_images:
                try:
                    image_url = product_images[product.slug]
                    self.stdout.write(f'Downloading image for {product.name}...')
                    
                    # Create request with user agent to avoid blocking
                    req = urllib.request.Request(
                        image_url,
                        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                    )
                    
                    # Download image to temporary file
                    img_response = urllib.request.urlopen(req, timeout=15)
                    img_data = img_response.read()
                    
                    # Create temporary file
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as img_temp:
                        img_temp.write(img_data)
                        temp_path = img_temp.name
                    
                    # Save to product
                    with open(temp_path, 'rb') as f:
                        product.image.save(f"{product.slug}.jpg", File(f), save=True)
                    
                    # Clean up
                    os.unlink(temp_path)
                    added_count += 1
                    self.stdout.write(self.style.SUCCESS(f'[OK] Image added to: {product.name}'))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'[ERROR] Could not download image for {product.name}: {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n[SUCCESS] Successfully added {added_count} images!'))

