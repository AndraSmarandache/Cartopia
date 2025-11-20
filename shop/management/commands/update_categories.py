from django.core.management.base import BaseCommand
from shop.models import Category


class Command(BaseCommand):
    help = 'Update category names and descriptions from Romanian to English'

    def handle(self, *args, **options):
        updates = {
            'Electronice': {
                'name': 'Electronics',
                'description': 'Electronic products and gadgets',
            },
            'Laptopuri': {
                'name': 'Laptops',
                'description': 'Laptops and computers',
            },
            'Telefoane': {
                'name': 'Phones',
                'description': 'Mobile phones and smartphones',
            },
            'Accesorii': {
                'name': 'Accessories',
                'description': 'Electronic accessories',
            },
            'Gaming': {
                'name': 'Gaming',
                'description': 'Gaming products',
            },
        }
        
        for old_name, new_data in updates.items():
            category = Category.objects.filter(name=old_name).first()
            if category:
                category.name = new_data['name']
                category.description = new_data['description']
                category.save()
                self.stdout.write(self.style.SUCCESS(f'Updated: {old_name} -> {new_data["name"]}'))
        
        self.stdout.write(self.style.SUCCESS('\nCategories updated!'))

