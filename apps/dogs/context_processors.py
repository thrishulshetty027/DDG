from .models import SiteConfig


def site_config(request):
    """Make site configuration available in every template as {{ config }}."""
    return {
        'config': SiteConfig.load()
    }
