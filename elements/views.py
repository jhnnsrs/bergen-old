# Create your views here.
# import the logging library
import logging

from django_filters.rest_framework import DjangoFilterBackend

from elements.models import (ROI, Animal, Antibody, Experiment,
                             ExperimentalGroup, FileMatchString,
                             Representation, Sample, Transformation)
from elements.serializers import (AnimalSerializer, AntibodySerializer,
                                  ExperimentalGroupSerializer,
                                  ExperimentSerializer,
                                  FileMatchStringSerializer,
                                  RepresentationSerializer, ROISerializer,
                                  SampleSerializer)
from larvik.views import LarvikArrayMixIn
# Get an instance of a logger
from transformers.serializers import TransformationSerializer
from trontheim.views import PublishingModelViewSet
logger = logging.getLogger(__name__)

class AntibodyViewSet(PublishingModelViewSet):
    """
    Returns a list of all **active** accounts in the system.

    For more details on how accounts are activated please [see here][ref].

    [ref]: http://example.com/activating-accounts
    """
    filter_backends = (DjangoFilterBackend,)
    queryset = Antibody.objects.all()
    serializer_class = AntibodySerializer
    publishers = [["creator"]]

class FileMatchStringViewSet(PublishingModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    filter_backends = (DjangoFilterBackend,)
    queryset = FileMatchString.objects.all()
    serializer_class = FileMatchStringSerializer
    publishers = [["creator"]]

class AnimalViewSet(PublishingModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    filter_backends = (DjangoFilterBackend,)
    queryset = Animal.objects.all()
    serializer_class = AnimalSerializer
    publishers = [["creator"],["experiment"]]
    filter_fields = ("creator", "name","experiment","experimentalgroup")

class ExperimentalGroupViewSet(PublishingModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    filter_backends = (DjangoFilterBackend,)
    queryset = ExperimentalGroup.objects.all()
    serializer_class = ExperimentalGroupSerializer
    publishers = [["experiment"]]
    filter_fields = ("creator", "name", "experiment")



class SampleViewSet(PublishingModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Sample.objects.all()
    serializer_class = SampleSerializer

    filter_backends = (DjangoFilterBackend,)
    publishers = [("experiment",),("creator",),("nodeid",)]
    filter_fields = ("creator","experiment","bioseries","experimentalgroup","bioseries__bioimage","bioseries__bioimage__locker")


class ExperimentViewSet(PublishingModelViewSet):
    queryset = Experiment.objects.all()
    serializer_class = ExperimentSerializer

    filter_backends = (DjangoFilterBackend,)
    publishers = [["creator"]]
    filter_fields = ("creator",)


class RepresentationViewSet(PublishingModelViewSet, LarvikArrayMixIn):

    queryset = Representation.objects.all()
    serializer_class = RepresentationSerializer
    filter_backends = (DjangoFilterBackend,)
    publishers = [["sample"],["creator"]]
    filter_fields = ("sample",)


class TransformationViewSet(PublishingModelViewSet, LarvikArrayMixIn):
    """
    API endpoint that allows users to be viewed or edited.
    """
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ("representation",)
    queryset = Transformation.objects.all()
    serializer_class = TransformationSerializer


class RoiViewSet(PublishingModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ("representation",)
    queryset = ROI.objects.all()
    serializer_class = ROISerializer
