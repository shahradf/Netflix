from django.shortcuts import redirect, render
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .forms import ProfileForm
from core.models import Profile, Movie

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
        form = ProfileForm()
        return render(request, 'profileCreate.html', {'form': form})
    
    def post(self, request, *args, **kwargs):
        form = ProfileForm(request.POST)
        if form.is_valid():
            profile_data = form.cleaned_data
            profile = Profile.objects.create(**profile_data)
            request.user.profiles.add(profile)
            return redirect('core:profile_list')
        return render(request, 'profileCreate.html', {'form': form})

class MovieListView(BaseView):
    def get(self, request, profile_id, *args, **kwargs):
        try:
            user_profile = Profile.objects.get(uuid=profile_id)

            if user_profile not in request.user.profiles.all():
                return redirect('core:profile_list')

            movies_by_age_limit = Movie.objects.filter(age_limit=user_profile.age_limit)
            showcase_movie = movies_by_age_limit.first()

            return render(request, 'movieList.html', {
                'movies': movies_by_age_limit,
                'show_case': showcase_movie
            })

        except Profile.DoesNotExist:
            return redirect('core:profile_list')

class ShowMovieDetail(BaseView):
    def get(self, request, movie_id, *args, **kwargs):
        try:
            movie = Movie.objects.get(uuid=movie_id)
            return render(request, 'movieDetail.html', {'movie': movie})
        except Movie.DoesNotExist:
            return redirect('core:profile_list')

from django.http import StreamingHttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from core.models import Movie, Video

class ShowMovie(BaseView):
    def get(self, request, movie_id, *args, **kwargs):
        try:
            movie = Movie.objects.get(uuid=movie_id)
            video_file = movie.videos.first()  
            
            if not video_file:
                return redirect('core:profile_list')


            file_path = video_file.file.path  
            video_filename = video_file.file.name.split('/')[-1]
            
            # Create a streaming response for the video
            response = StreamingHttpResponse(open(file_path, 'rb'), content_type='video/mp4')
            response['Content-Disposition'] = f'inline; filename="{video_filename}"'

            return response

        except Movie.DoesNotExist:
            return redirect('core:profile_list')
