from .cart import Cart
from .models import BackgroundImage, SiteLogo


def cart(request):
    return {'cart': Cart(request)}


def site_settings(request):
    return {
        'active_background': BackgroundImage.get_active(),
        'active_logo': SiteLogo.get_active(),
    }
