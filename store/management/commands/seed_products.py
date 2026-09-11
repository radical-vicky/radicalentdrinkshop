from django.core.management.base import BaseCommand
from django.utils.text import slugify

from store.models import Category, DeliveryZone, Product, Promotion

SAMPLE_ZONES = [
    # Nairobi estates — same-day, short-haul
    ('Kilimani', 100, 30),
    ('Westlands', 120, 35),
    ('Lavington', 120, 35),
    ('Kileleshwa', 100, 30),
    ('South B', 150, 45),
    ('South C', 150, 45),
    # Other major towns — we deliver Kenya-wide via courier partners,
    # so these carry a higher fee and longer ETA than in-city Nairobi drops.
    ('Mombasa', 350, 1440),
    ('Kisumu', 350, 1440),
    ('Nakuru', 300, 720),
    ('Eldoret', 350, 1440),
    ('Thika', 200, 180),
]

SAMPLE = {
    'Sodas': [
        ('Coca-Cola 500ml', 80, 500),
        ('Fanta Orange 500ml', 80, 500),
        ('Sprite 500ml', 80, 500),
    ],
    'Juices': [
        ('Del Monte Mango 1L', 220, 1000),
        ('Minute Maid Pulpy Orange 1L', 210, 1000),
    ],
    'Water': [
        ('Dasani Water 500ml', 50, 500),
        ('Keringet Water 1L', 90, 1000),
    ],
    'Energy Drinks': [
        ('Red Bull 250ml', 250, 250),
        ('Monster Energy 500ml', 300, 500),
    ],
}


FEATURED = {
    'Coca-Cola 500ml': ('20% off today', 'Chilled sodas, at your door', ''),
    'Del Monte Mango 1L': ('New arrivals', 'Real fruit juices, restocked weekly', ''),
    'Red Bull 250ml': ('Weekend pick', 'Fuel your night out', ''),
}


SAMPLE_PROMOTIONS = [
    {
        'kicker': 'First order', 'title': '20% off your first cart',
        'description': 'New customers save on any order over KES 1,000. Applies to non-alcoholic drinks.',
        'voucher_code': 'WELCOME20', 'tone': Promotion.Tone.GREEN, 'sort_order': 1,
    },
    {
        'kicker': 'This week', 'title': 'Free delivery over KES 2,000',
        'description': 'Stock up on juices and sodas — delivery fee waived automatically at that cart size.',
        'voucher_code': 'FREESHIP', 'tone': Promotion.Tone.ORANGE, 'sort_order': 2,
    },
    {
        'kicker': 'Gifting', 'title': "Send a drinks hamper",
        'description': "Pick a friend's saved address and we deliver the crate with a gift note attached.",
        'voucher_code': 'GIFTIT', 'tone': Promotion.Tone.GOLD, 'sort_order': 3,
    },
]


class Command(BaseCommand):
    help = 'Seed the database with sample non-alcoholic drink categories/products.'

    def handle(self, *args, **options):
        for zone_name, fee, minutes in SAMPLE_ZONES:
            DeliveryZone.objects.get_or_create(
                name=zone_name,
                defaults={'delivery_fee': fee, 'estimated_minutes': minutes},
            )

        for category_name, products in SAMPLE.items():
            category, _ = Category.objects.get_or_create(
                name=category_name, slug=slugify(category_name)
            )
            for name, price, volume_ml in products:
                tagline, headline, description = FEATURED.get(name, ('', '', ''))
                Product.objects.get_or_create(
                    name=name,
                    defaults={
                        'category': category,
                        'slug': slugify(name),
                        'price': price,
                        'volume_ml': volume_ml,
                        'stock': 100,
                        'is_alcoholic': False,
                        'is_active': True,
                        'is_featured': name in FEATURED,
                        'hero_tagline': tagline,
                        'hero_headline': headline,
                        'hero_description': description,
                    },
                )

        for promo_data in SAMPLE_PROMOTIONS:
            Promotion.objects.get_or_create(
                title=promo_data['title'],
                defaults={**promo_data, 'is_active': True},
            )

        self.stdout.write(self.style.SUCCESS('Sample drinks seeded.'))
