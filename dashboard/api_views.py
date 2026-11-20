from rest_framework import viewsets, permissions
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from main.api_auth import CsrfExemptSessionAuthentication
from .models import GreenTrack
from .serializers import GreentrackSerializer

class GreentrackViewSet(viewsets.ModelViewSet):
    serializer_class = GreentrackSerializer
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get_queryset(self):
        qs = GreenTrack.objects.filter(user=self.request.user)
        return qs
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
