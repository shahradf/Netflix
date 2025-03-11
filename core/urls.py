from django.urls import path
from .views import HomeView, ProfileListView, ProfileCreateView, MovieListView,ShowMovieDetail,ShowMovie

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('profile/', ProfileListView.as_view(), name='profile_list'),
    path('profile/create/', ProfileCreateView.as_view(), name='profile_create'),
    path('watch/<str:profile_id>/', MovieListView.as_view(), name='watch'),
    path('movie/detail/<str:movie_id>/',ShowMovieDetail.as_view(),name='show_det'),
    path('movie/play/<str:movie_id>/',ShowMovie.as_view(),name='play')
]