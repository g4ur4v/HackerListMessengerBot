from django.conf.urls import include, url

from django.contrib import admin
admin.autodiscover()

import chatbot_main.views

# Examples:
# url(r'^$', 'gettingstarted.views.home', name='home'),
# url(r'^blog/', include('blog.urls')),

urlpatterns = [
    url(r'^webhook', chatbot_main.views.webhook, name='webhook'),
    url(r'^admin/', include(admin.site.urls)),
]
