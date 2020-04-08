# Create your views here.
# Create your views here.
from importer.models import * 
from importer.policies import *
from importer.serializers import *
from trontheim.views import TaskPublishingViewSet, PublishingModelViewSet

class ImporterViewSet(PublishingModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Importer.objects.all()
    serializer_class = ImporterSerializer



class ImportingViewSet(TaskPublishingViewSet):
    '''Enables publishing to the channel Layed.
    Publishers musst be Provided'''
    queryset = Importing.objects.all()
    serializer_class = ImportingSerializer
    permission_classes = (ImportingAccessPolicy,)
    publishers = [["nodeid"]]
    actionpublishers = {"importing": [("nodeid",)], "bioimage": [["nodeid"], ["locker"]]}
    # this publishers will be send to the Action Handles and then they can send to the according

    def preprocess_jobs(self, serializer):
        oracle = Importer.objects.get(pk=serializer.data["importer"])
        print(oracle.channel)
        return [self.create_job(data=serializer.data, job=serializer.data, channel=oracle.channel)]
