from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import DisplayUsers,Employee_Count,SignUpUser,SignInUser

urlpatterns = [
    path('', views.signin, name="signin"),
    path('signup', views.signup, name="signup"),
    path('signupAPI', SignUpUser.as_view(), name="signup"),
    path('signinAPI', SignInUser.as_view(), name="signup"),
    path('index', views.home, name="home"),
    path('signout', views.signout, name="signout"),
    path('display_users/', DisplayUsers.as_view(), name="display_users"),
    path('display/', views.display, name="display_users"),
    path('upload-image/', views.upload_image, name="upload_image"),
    path('uploaded-image/', views.uploaded_images, name="uploaded_images"),
    path('upload_data', views.upload_data, name="upload_data"),
    path('employee_count/', Employee_Count.as_view(), name='employee count'),
    # path('api/',include(router.urls)),
    # path('authors-sellers/', views.authors_sellers_page.as_view(), name='authors_sellers_page'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)