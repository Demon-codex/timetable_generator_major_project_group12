"""
URL configuration for project_name project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    # Django built-in auth views (login, logout, password change, etc.)
    path('accounts/', include('django.contrib.auth.urls')),
    # i created this path, which says if url starts with timetable go to urls of timetable app
    path('timetable/',include('timetable.urls')),
    # Redirect root URL to timetable app
    path('', RedirectView.as_view(url='/timetable/', permanent=False)),
]
