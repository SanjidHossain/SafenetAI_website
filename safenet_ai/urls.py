from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('research/', include('research_papers.urls')),
    path('expert-topics/', include('expert_topics.urls')),
    path('blog/', include('blog.urls')),
    path('feedback/', include('feedback.urls')),
    path('about/', include('About.urls')),
    path('Guidelines/', include('Guidelines.urls')),
    path('Researchers/', include('Researchers.urls')),
    path('PublicationProject/', include('PublicationProject.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
