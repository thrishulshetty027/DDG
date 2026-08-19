import urllib.parse
from django import template
from apps.dogs.models import SiteConfig

register = template.Library()


@register.simple_tag
def whatsapp_url(dog):
    """Generate WhatsApp URL for a dog card."""
    config = SiteConfig.load()
    message = (
        f"Hi, I'm interested in {dog.name} ({dog.breed.name})\n"
        f"Price: ₹{dog.price:,.0f}\n"
        f"Location: {dog.location}"
    )
    return (
        f"https://wa.me/{config.admin_whatsapp}"
        f"?text={urllib.parse.quote(message)}"
    )


@register.filter
def star_range(value):
    """Convert rating number to range for star display."""
    try:
        return range(int(value))
    except (ValueError, TypeError):
        return range(0)


@register.filter
def empty_star_range(value):
    """Remaining empty stars."""
    try:
        return range(5 - int(value))
    except (ValueError, TypeError):
        return range(5)
