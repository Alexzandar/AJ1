from process.views import TestAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response


class TestView(APIView):
    def get(self, request):
        return Response({})


class TestAuthentication(TestAuthentication):
    pass



