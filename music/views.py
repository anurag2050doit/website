from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.shortcuts import render, redirect , get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.views.generic import View
from django.core.urlresolvers import reverse_lazy
from .models import Album, Song
from .forms import UserForm, SongForm
from django.http import JsonResponse
from django.db.models import Q


AUDIO_FILE_TYPES = ['wav', 'mp3', 'ogg']


#Front Page
def index(request):
    if not request.user.is_authenticated():
        username = None
    else: username = request.user.get_short_name()
    albums = Album.objects.all()
    song_results = Song.objects.all()
    query = request.GET.get("q")
    if query:
        albums = albums.filter(
            Q(album_title__icontains=query) |
            Q(artist__icontains=query) | Q(genre__icontains=query)
        ).distinct()
        song_results = song_results.filter(
            Q(song_title__icontains=query)
        ).distinct()
        return render(request, 'music/index.html', {
            'all_albums': albums,
            'songs': song_results,
            'username' : username,
        })
    else:
        return render(request, 'music/index.html', {'all_albums': albums,
            'username' : username, })


#Album Stuff
def album_view(request, pk):
    album = Album.objects.get(id=pk)
    if not request.user.is_authenticated(): username = None
    else: username = request.user.get_short_name()
    return render(request, 'music/detail.html', {'username': username, 
        'album': album})

class AlbumCreate(CreateView):
    model = Album
    fields = ['artist', 'album_title', 'genre', 'album_logo']

class AlbumUpdate(UpdateView):
	model = Album
	fields = ['artist', 'album_title', 'genre', 'album_logo']

class AlbumDelete(DeleteView):
	model = Album
	success_url = reverse_lazy('music:index')

def delete_album(request,pk):
    if not request.user.is_authenticated():
        return render(request, 'music/login.html', {'error_message': 
            'Need to Login'} )
    elif not request.user.is_staff: 
        return render(request, 'music/login.html', {'error_message': 
            'Only Admin can delete Album'} )
    else:
        album = get_object_or_404(Album, pk=pk)
        album.delete()
        return redirect('music:index')

def favorite_album(request, album_id):
    if not request.user.is_authenticated():
        return render(request, 'music/login.html', {'error_message': 
            'Need to Login'} )
    if request.method == "GET":
        album = get_object_or_404(Album, pk=album_id)
        try:
            if album.is_favorite:
                album.is_favorite = False
            else:
                album.is_favorite = True
            album.save()
        except (KeyError, Album.DoesNotExist):
            return JsonResponse({'success': False})
        else:
            return redirect('music:index')


#User Stuff

class UserFormView(View):
	form_class = UserForm
	template_name = 'music/registration_form.html'

	def get(self, request):
		form= self.form_class(None)
		return render(request, self.template_name, {'form': form})

	def post(self, request):
		form= self.form_class(request.POST) 

		if form.is_valid():

			user = form.save(commit=False)

			username = form.cleaned_data['username']
			password = form.cleaned_data['password']
			user.set_password(password)
			user.save()

			user = authenticate(username=username, password=password)

			if user is not None:

				if user.is_active:
					login(request, user)
					request.user
					return redirect('music:index')

		else :
			return render(request, self.template_name, {'form': form})

def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None :
            if user.is_active:
                login(request, user)
                albums = Album.objects.all()
                username = user.get_short_name() 
                return redirect('music:index')
            elif user.is_authenticated():
                return render(request, 'music/login.html', {'error_message': 
                    'Your are alrady loggedin'})
            else:
                return render(request, 'music/login.html', {'error_message': 
                    'Your account has been disabled'})
        else:
            return render(request, 'music/login.html', {'error_message': 
                'Invalid login'})
    return render(request, 'music/login.html')

def logout_user(request):
    logout(request)
    form = UserForm(request.POST or None)
    context = {
        "form": form,
    }
    return render(request, 'music/login.html', context)


#Song Stuff

def create_song(request, album_id):
    if not request.user.is_authenticated():
        return render(request, 'music/login.html', {'error_message': 
            'Need to Login First'})
    else: 
        username = request.user.get_short_name()
        form = SongForm(request.POST or None, request.FILES or None)
        album = get_object_or_404(Album, pk=album_id)
        if form.is_valid():
            albums_songs = album.song_set.all()
            for s in albums_songs:
                if s.song_title == form.cleaned_data.get("song_title"):
                    context = {
                        'album': album,
                        'form': form,
                        'error_message': 'You already added that song',
                        'username': username
                    }
                    return render(request, 'music/create_song.html', context)
            song = form.save(commit=False)
            song.album = album
            song.song_file = request.FILES['song_file']
            file_type = song.song_file.url.split('.')[-1]
            file_type = file_type.lower()
            if file_type not in AUDIO_FILE_TYPES:
                context = {
                    'album': album,
                    'form': form,
                    'error_message': 'Audio file must be WAV, MP3, or OGG',
                    'username': username
                }
                return render(request, 'music/create_song.html', context)

            song.save()
            return render(request, 'music/detail.html', {'album': album,
                'username': username })
        context = {
            'album': album,
            'form': form,
            'username': username
        }
        return render(request, 'music/create_song.html', context)
		

def play_song(request, album_id, song_id): 
    if request.user.is_authenticated():
        username = request.user.get_short_name()
    else: 
        username= None
    album = get_object_or_404(Album, pk=album_id)
    song = Song.objects.get(pk=song_id)
    return render(request, 'music/play_audio.html', 
        {'song': song ,'album': album, 'username': username })

def delete_song(request, album_id, song_id):
    if not request.user.is_authenticated():
        return render(request, 'music/login.html', {'error_message': 
            'Need to Login'} )
    elif not request.user.is_staff: 
        return render(request, 'music/login.html', {'error_message': 
            'Only Admin can delete Song'} )
    else:
    	album = get_object_or_404(Album, pk=album_id)
    	song = Song.objects.get(pk=song_id)
    	song.delete()
    	return render(request, 'music/detail.html', {'album': album})

def favorite(request, song_id, album_id):
    if not request.user.is_authenticated():
        return render(request, 'music/login.html', {'error_message': 
            'Need to Login'} )
    else:
        username = request.user.get_short_name()
        album = get_object_or_404(Album, pk=album_id)
        song = get_object_or_404(Song, pk=song_id)
        try:
            if song.is_favorite:
                song.is_favorite = False
            else:
                song.is_favorite = True
            song.save()
        except (KeyError, Song.DoesNotExist):
            return JsonResponse({'success': False})
        album = Album.objects.get(pk=album_id)
        return render(request , 'music/detail.html', 
            {'album': album,'username': username } )


def songs(request, filter_by):
    if not request.user.is_authenticated():
        username = None
    else: username = request.user.get_short_name()
    try:
        song_ids = []
        for album in Album.objects.all():
            for song in album.song_set.all():
                song_ids.append(song.pk)
        users_songs = Song.objects.filter(pk__in=song_ids)
        if filter_by == 'favorites':
            users_songs = users_songs.filter(is_favorite=True)
    except Album.DoesNotExist:
        users_songs = []
    return render(request, 'music/songs.html', {
        'song_list': users_songs,
        'filter_by': filter_by,
        'username': username,
    })