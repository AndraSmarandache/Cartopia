from django.core.management.base import BaseCommand
from shop.models import Product


class Command(BaseCommand):
    help = 'Update product names and descriptions from Romanian to English'

    def handle(self, *args, **options):
        updates = {
            'Tableta iPad Air': {
                'name': 'iPad Air Tablet',
                'slug': 'ipad-air-tablet',
            },
            'Smartwatch Apple Watch Series 8': {
                'name': 'Apple Watch Series 8',
                'slug': 'apple-watch-series-8',
            },
            'Casti Bluetooth Sony WH-1000XM4': {
                'name': 'Sony WH-1000XM4 Bluetooth Headphones',
                'slug': 'sony-wh1000xm4-bluetooth-headphones',
            },
            'Tastatura mecanica RGB': {
                'name': 'Mechanical RGB Keyboard',
                'slug': 'mechanical-rgb-keyboard',
            },
        }
        
        for old_name, new_data in updates.items():
            product = Product.objects.filter(name=old_name).first()
            if product:
                product.name = new_data['name']
                product.slug = new_data['slug']
                product.save()
                self.stdout.write(self.style.SUCCESS(f'Updated: {old_name} -> {new_data["name"]}'))
        
        products_with_romanian_specs = Product.objects.filter(specifications__icontains='Procesor')
        for product in products_with_romanian_specs:
            if 'Procesor:' in product.specifications:
                product.specifications = product.specifications.replace('Procesor:', 'Processor:')
                product.specifications = product.specifications.replace('Placa video:', 'Graphics:')
                product.specifications = product.specifications.replace('Stocare:', 'Storage:')
                product.specifications = product.specifications.replace('Ecran:', 'Display:')
                product.save()
                self.stdout.write(self.style.SUCCESS(f'Updated specifications for: {product.name}'))
        
        description_updates = {
            'Laptop Gaming ASUS ROG Strix': 'ASUS ROG Strix gaming laptop with AMD Ryzen 9 processor, RTX 3070, 16GB RAM',
            'Webcam Logitech C920': 'Full HD 1080p webcam with stereo microphone, perfect for video conferencing',
            'Apple Watch Series 8': 'Apple Watch Series 8 with Always-On Retina display, GPS, water resistant',
            'iPad Air Tablet': 'iPad Air with 10.9" Liquid Retina display, M1 processor',
            'Sony WH-1000XM4 Bluetooth Headphones': 'Premium wireless headphones with noise cancellation, 30-hour battery',
            'Mechanical RGB Keyboard': 'Mechanical gaming keyboard with Cherry MX switches, RGB lighting',
            'Mouse Gaming Logitech G502': 'Logitech G502 Hero gaming mouse with HERO 25K sensor, 11 programmable buttons',
            'Casti Bluetooth Sony WH-1000XM4': 'Premium wireless headphones with noise cancellation, 30-hour battery',
            'Tastatura mecanica RGB': 'Mechanical gaming keyboard with Cherry MX switches, RGB lighting',
        }
        
        for product_name, new_description in description_updates.items():
            product = Product.objects.filter(name=product_name).first()
            if product and product.description != new_description:
                product.description = new_description
                product.save()
                self.stdout.write(self.style.SUCCESS(f'Updated description for: {product.name}'))
        
        self.stdout.write(self.style.SUCCESS('\nProduct names, descriptions and specifications updated!'))

