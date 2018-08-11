from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^blockheight/$', views.blockheight, name='blockheight'),
    url(r'^segwit/$', views.segwit, name='segwit'),
    url(r'^difficulty/$', views.difficulty, name='difficulty'),
    url(r'^blocksize/$', views.blocksize, name='blocksize'),
    # blockheight/2009-10-31/2010-10-31/
    url(r'^blockheight/(?P<date_begin>[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{2}:[0-9]{2})/(?P<date_end>[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{2}:[0-9]{2})',
        views.blockheight, name='blockheight'),
]