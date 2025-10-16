from django.conf import settings

def site_constants(request):
    return {
        "SITE_NAME": getattr(settings, "SITE_NAME", "App")
    }
