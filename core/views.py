from django.shortcuts import redirect, render
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .forms import ProfileForm
from core.models import Profile, Movie

class HomeView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('core:profile_list')
        
        return render(request, 'index.html')

@method_decorator(login_required, name='dispatch')
class ProfileListView(View):
    def get(self, request, *args, **kwargs):
        user_profiles = request.user.profiles.all()
        return render(request, 'profileList.html', {'profiles': user_profiles})

@method_decorator(login_required, name='dispatch')
class ProfileCreateView(View):
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

@method_decorator(login_required, name='dispatch')
class MovieListView(View):
    def get(self, request, profile_id, *args, **kwargs):
        try:
            user_profile = Profile.objects.get(uuid=profile_id)
            
            movies_by_age_limit = Movie.objects.filter(age_limit=user_profile.age_limit)
            showcase_movie = movies_by_age_limit.first()  

            if user_profile not in request.user.profiles.all():
                return redirect('core:profile_list')

            return render(request, 'movieList.html', {
                'movies': movies_by_age_limit,
                'show_case': showcase_movie
            })

        except Profile.DoesNotExist:
            return redirect('core:profile_list')
