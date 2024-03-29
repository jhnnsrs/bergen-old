# Create your views here.
from django_filters.rest_framework import DjangoFilterBackend

from evaluators.models import Evaluator, Data, Evaluating, VolumeData, ClusterData, LengthData
from evaluators.serializers import EvaluatorSerializer, DataSerializer, EvaluatingSerializer, VolumeDataSerializer, \
    ClusterDataSerializer, LengthDataSerializer
from larvik.views import LarvikJobViewSet, LarvikViewSet
from trontheim.views import PublishingModelViewSet, TaskPublishingViewSet

class EvaluatorViewSet(PublishingModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Evaluator.objects.all()
    serializer_class = EvaluatorSerializer


class DataViewSet(PublishingModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    filter_backends = (DjangoFilterBackend,)
    queryset = Data.objects.all()
    serializer_class = DataSerializer
    publishers = [["sample"],["transformation"]]


class VolumeDataViewSet(PublishingModelViewSet):
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ["transformation","roi"]
    queryset = VolumeData.objects.all()
    serializer_class = VolumeDataSerializer
    publishers = [["sample"],["transformation"]]

class ClusterDataViewSet(PublishingModelViewSet):
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ["transformation","roi"]
    queryset = ClusterData.objects.all()
    serializer_class = ClusterDataSerializer
    publishers = [["sample"],["transformation"]]

class LengthDataViewSet(PublishingModelViewSet):
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ["transformation","roi"]
    queryset = LengthData.objects.all()
    serializer_class = LengthDataSerializer
    publishers = [["sample"],["transformation"]]


class EvaluatingViewSet(TaskPublishingViewSet):
    '''Enables publishing to the channel Layed.
    Publishers musst be Provided'''
    queryset = Evaluating.objects.all()
    serializer_class = EvaluatingSerializer
    publishers = [["sample"]]
    actionpublishers = {"sample": [("creator", "experiment")],
                        "data": [["transformation"],["creator"]],
                        "clusterdata": [["transformation"],["creator"],["nodeid"]],
                        "lengthdata": [["transformation"], ["creator"], ["nodeid"]],
                        "evaluating": [("nodeid",)]
                        }
    # this publishers will be send to the Action Handles and then they can send to the according
    channel = "maxisp"

    def preprocess_jobs(self, serializer):
        evaluator = Evaluator.objects.get(pk=serializer.data["evaluator"])
        return [self.create_job(data=serializer.data, job=serializer.data, channel=evaluator.channel)]