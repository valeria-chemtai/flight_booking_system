from django.conf.urls import url

from authentication import views


urlpatterns = [
    url(r'^signup/$', views.UserSignupViewset.as_view(
        actions={'post': 'create'}), name='signup'),
    url(r'^sign-in/$', views.UserSignInView.as_view(), name='sign-in'),
    url(r'^users/$', views.UserProfileViewset.as_view(
        actions={'get': 'list'}), name='users-list'),
    url(r'^users/(?P<pk>[a-f0-9-]+)/$', views.UserProfileViewset.as_view(
        actions={'get': 'retrieve', 'put': 'update'}), name='user-detail'),
    url(r'^change-password/$', views.UserChangePasswordView.as_view(), name='change-password')
]
