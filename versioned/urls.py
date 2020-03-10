from django.urls import path, include

urlpatterns = [
    path('v1/', include('versioned.v1.process.urls'))
]
