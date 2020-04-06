# Create your views here.
from django_filters.rest_framework import DjangoFilterBackend

from drawing.models import LineROI
from drawing.serializers import LineROISerializer
from trontheim.views import PublishingModelViewSet


class LineROIViewSet(PublishingModelViewSet):
    queryset = LineROI.objects.all()
    serializer_class = LineROISerializer
    publishers = [["nodeid",]]
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ("representation","creator")
