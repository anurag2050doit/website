from django.conf.urls import url
from . import views


app_name = 'music'

urlpatterns = [
    #Front URL
    url(r'^$', views.index, name='index'),

    #User URLS
    url(r'^register/$', views.UserFormView.as_view(), name='register'),
    url(r'^login_user/$', views.login_user, name='login_user'),
    url(r'^logout_user/$', views.logout_user, name='logout_user'),

    #Album URLS
    url(r'^(?P<pk>[0-9]+)/$',views.album_view, name='detail'),
    url(r'album/add/$', views.AlbumCreate.as_view(), name='album-add'),
    url(r'album/(?P<pk>[0-9]+)/$', views.AlbumUpdate.as_view(), name='album-update'),
    url(r'album/(?P<pk>[0-9]+)/delete/$', views.delete_album, name='album-delete'),
   	url(r'^(?P<album_id>[0-9]+)/favorite_album/$', views.favorite_album, name='favorite_album'),

    #Song URLS
    url(r'^(?P<album_id>[0-9]+)/create_song/$', views.create_song, name='create_song'),
    url(r'^(?P<album_id>[0-9]+)/favorite_song/(?P<song_id>[0-9]+)/$', views.favorite, name='favorite'),
   	url(r'^(?P<album_id>[0-9]+)/delete_song/(?P<song_id>[0-9]+)/$', views.delete_song, name='delete_song'),
   	url(r'^(?P<album_id>[0-9]+)/play_song/(?P<song_id>[0-9]+)/$', views.play_song, name='play_song'),
    url(r'^songs/(?P<filter_by>[a-zA_Z]+)/$', views.songs, name='songs'),
   	]
