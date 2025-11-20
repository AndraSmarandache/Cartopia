from django.core.management.base import BaseCommand
from django.core.files import File
from shop.models import Category
import urllib.request
import tempfile
import os


class Command(BaseCommand):
    help = 'Add images to categories that don\'t have them'

    def handle(self, *args, **options):
        # Category images URLs
        category_images = {
            'electronice': 'https://images.unsplash.com/photo-1468495244123-6c6c332eeece?w=500&h=500&fit=crop',
            'laptopuri': 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=500&h=500&fit=crop',
            'telefoane': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500&h=500&fit=crop',
            'accesorii': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&h=500&fit=crop',
            'gaming': 'https://images.unsplash.com/photo-1552820728-8b83bb6b773f?w=500&h=500&fit=crop',
        }

        categories = Category.objects.all()
        added_count = 0
        
        for category in categories:
            if not category.image and category.slug in category_images:
                try:
                    image_url = category_images[category.slug]
                    self.stdout.write(f'Downloading image for {category.name}...')
                    
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
                    
                    # Save to category
                    with open(temp_path, 'rb') as f:
                        category.image.save(f"{category.slug}.jpg", File(f), save=True)
                    
                    # Clean up
                    os.unlink(temp_path)
                    added_count += 1
                    self.stdout.write(self.style.SUCCESS(f'[OK] Image added to: {category.name}'))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'[ERROR] Could not download image for {category.name}: {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n[SUCCESS] Successfully added {added_count} images!'))

