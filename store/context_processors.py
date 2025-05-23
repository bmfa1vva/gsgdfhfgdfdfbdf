from .models import HeaderBanner

def header_banner(request):
    banner = HeaderBanner.objects.filter(is_active=True).first()
    return {'header_banner': banner}
