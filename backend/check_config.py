#!/usr/bin/env python
"""Quick diagnostic to check Django configuration"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    django.setup()
    print("✅ Django setup successful\n")
    
    # Check installed apps
    from django.conf import settings
    print("📦 INSTALLED_APPS:")
    for app in settings.INSTALLED_APPS:
        print(f"  - {app}")
    
    # Check if api app is there
    if 'api' in settings.INSTALLED_APPS or 'api.apps.ApiConfig' in settings.INSTALLED_APPS:
        print("\n✅ 'api' app is installed")
    else:
        print("\n❌ 'api' app is NOT installed!")
    
    # Check ROOT_URLCONF
    print(f"\n🔗 ROOT_URLCONF: {settings.ROOT_URLCONF}")
    
    # Try to import and show URLs
    print("\n📍 Checking URL patterns...")
    from django.urls import get_resolver
    resolver = get_resolver()
    
    print("\nRegistered URL patterns:")
    for pattern in resolver.url_patterns:
        print(f"  - {pattern}")
    
    # Try to resolve specific URLs
    print("\n🧪 Testing URL resolution:")
    from django.urls import resolve
    
    test_urls = [
        '/api/auth/register/',
        '/api/auth/login/',
        '/api/auth/user/',
        '/admin/',
    ]
    
    for url in test_urls:
        try:
            match = resolve(url)
            print(f"  ✅ {url} → {match.func}")
        except Exception as e:
            print(f"  ❌ {url} → ERROR: {e}")
    
    # Check if rest_framework is installed
    print("\n📚 Checking packages:")
    try:
        import rest_framework
        print(f"  ✅ djangorestframework installed (v{rest_framework.__version__})")
    except ImportError:
        print("  ❌ djangorestframework NOT installed")
    
    try:
        import rest_framework_simplejwt
        print(f"  ✅ djangorestframework-simplejwt installed")
    except ImportError:
        print("  ❌ djangorestframework-simplejwt NOT installed")
    
except Exception as e:
    print(f"\n❌ Error during setup: {e}")
    import traceback
    traceback.print_exc()
