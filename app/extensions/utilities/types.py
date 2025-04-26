from django.urls.resolvers import URLPattern, URLResolver


URLPatternsList = list[URLPattern | URLResolver]
"""Type alias specifically for urlpatterns lists."""
