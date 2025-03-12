from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .forms import ProfileForm
from core.models import Profile, Movie
from django.http import FileResponse, StreamingHttpResponse, HttpResponse
from django.utils.text import slugify
import os

# Apply the login_required decorator globally to all views
@method_decorator(login_required, name='dispatch')
class BaseView(View):
    pass

class HomeView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('core:profile_list')
        return render(request, 'index.html')

class ProfileListView(BaseView):
    def get(self, request, *args, **kwargs):
        user_profiles = request.user.profiles.all()
        return render(request, 'profileList.html', {'profiles': user_profiles})

class ProfileCreateView(BaseView):
    def get(self, request, *args, **kwargs):
        return render(request, 'profileCreate.html', {'form': ProfileForm()})
    
    def post(self, request, *args, **kwargs):
        form = ProfileForm(request.POST)
        if form.is_valid():
            profile = Profile.objects.create(**form.cleaned_data)
            request.user.profiles.add(profile)
            return redirect('core:profile_list')
        return render(request, 'profileCreate.html', {'form': form})

class MovieListView(BaseView):
    def get(self, request, profile_id, *args, **kwargs):
        user_profile = get_object_or_404(Profile, uuid=profile_id)
        
        # Ensure the profile belongs to the user
        if user_profile not in request.user.profiles.all():
            return redirect('core:profile_list')

        movies = Movie.objects.filter(age_limit=user_profile.age_limit)
        showcase_movie = movies.first()

        return render(request, 'movieList.html', {
            'movies': movies,
            'show_case': showcase_movie
        })

class ShowMovieDetail(BaseView):
    def get(self, request, movie_id, *args, **kwargs):
        movie = get_object_or_404(Movie, uuid=movie_id)
        return render(request, 'movieDetail.html', {'movie': movie})

class ShowMovie(BaseView):
    def get(self, request, movie_id, *args, **kwargs):
        movie = get_object_or_404(Movie, uuid=movie_id)
        video_file = movie.videos.first()

        if not video_file:
            return redirect('core:profile_list')

        return self.stream_video(request, video_file)

class ShowMovie(BaseView):
    def get(self, request, movie_id, *args, **kwargs):
        movie = get_object_or_404(Movie, uuid=movie_id)
        video_file = movie.videos.first()
        if not video_file:
            return redirect('core:profile_list')
        file_path = video_file.file.path
        file_size = os.path.getsize(file_path)
        range_header = request.headers.get('Range', None)
        
        if range_header:
            start_byte, end_byte = self.parse_range(range_header, file_size)
            if start_byte >= file_size:
                return HttpResponse(status=416)
            file = open(file_path, 'rb')
            file.seek(start_byte)
            remaining_bytes = end_byte - start_byte + 1
            
            def file_chunk_generator(file, remaining):
                chunk_size = 4096
                while remaining > 0:
                    bytes_to_read = min(chunk_size, remaining)
                    data = file.read(bytes_to_read)
                    if not data:
                        break
                    yield data
                    remaining -= bytes_to_read
                file.close()

            response = StreamingHttpResponse(
                file_chunk_generator(file, remaining_bytes),
                content_type='video/mp4',
                status=206
            )
            response['Content-Range'] = f'bytes {start_byte}-{end_byte}/{file_size}'
            response['Content-Length'] = str(remaining_bytes)
        else:
            file = open(file_path, 'rb')
            response = FileResponse(file, content_type='video/mp4')
            response['Content-Length'] = file_size

        response['Accept-Ranges'] = 'bytes'
        response['Content-Disposition'] = f'inline; filename="{slugify(video_file.title)}.mp4"'
        return response

    def parse_range(self, header, size):
        header = header.replace('bytes=', '')
        parts = header.split('-')
        start_str = parts[0]
        end_str = parts[1] if len(parts) > 1 else ''
        
        if not start_str and end_str:
            end = size - 1
            start = max(0, size - int(end_str))
        elif start_str and not end_str:
            start = int(start_str)
            end = size - 1
        else:
            start = int(start_str) if start_str else 0
            end = int(end_str) if end_str else size - 1

        end = min(end, size - 1)
        return start, end