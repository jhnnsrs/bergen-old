from django.http import HttpResponse, HttpResponseRedirect
# Create your views here.
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action

from trontheim.views import PublishingModelViewSet, TaskPublishingViewSet
from test.serializers import *
from test.models import *



class TesterViewSet(PublishingModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Tester.objects.all()
    serializer_class = TesterSerializer


class TestingViewSet(TaskPublishingViewSet):
    '''Enables publishing to the channel Layed.
    Publishers musst be Provided'''
    queryset = Testing.objects.all()
    serializer_class = TestingSerializer
    publishers = [["creator"]]
    actionpublishers = {"result": [("listener",)]}
    # this publishers will be send to the Action Handles and then they can send to the according
    channel = "test"

    def preprocess_jobs(self, serializer):
        tester = Tester.objects.get(pk=serializer.data["tester"])
        print(tester.channel)
        return [self.create_job(data=serializer.data,job=serializer.data,channel=tester.channel)]


