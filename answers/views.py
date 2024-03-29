# Create your views here.
from django.http import HttpResponse
# Create your views here.
from django_filters.rest_framework import DjangoFilterBackend
from pandas import DataFrame
from rest_framework.decorators import action

from answers.models import Answer, Answering, Oracle, Question
from answers.serializers import (AnsweringSerializer, AnswerSerializer,
                                 OracleSerializer, QuestionSerializer)
from trontheim.views import TaskPublishingViewSet, PublishingModelViewSet


class OracleViewSet(PublishingModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Oracle.objects.all()
    serializer_class = OracleSerializer

class QuestionViewSet(PublishingModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    filter_backends = (DjangoFilterBackend,)
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    filter_fields = ["creator", "nodeid"]
    publishers = [["creator"], ["nodeid"]]


class AnswerViewSet(PublishingModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    filter_backends = (DjangoFilterBackend,)
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    filter_fields = ["creator", "question"]
    publishers = [["creator"], ["nodeid"]]

    @action(methods=['get'], detail=True,
            url_path='csv', url_name='csv')
    def csv(self, request, pk):
        answer: Answer = self.get_object()
        dataframe: DataFrame = answer.pandas.get_dataframe()
        values = dataframe.to_csv()
        response = HttpResponse(values, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="{0}.csv"'.format(answer.name)
        return response

class AnsweringViewSet(TaskPublishingViewSet):
    '''Enables publishing to the channel Layed.
    Publishers musst be Provided'''
    queryset = Answering.objects.all()
    serializer_class = AnsweringSerializer
    publishers = [["nodeid"]]
    actionpublishers = {"answering": [("nodeid",)], "answer": [["creator"], ["nodeid"]]}
    # this publishers will be send to the Action Handles and then they can send to the according

    def preprocess_jobs(self, serializer):
        oracle = Oracle.objects.get(pk=serializer.data["oracle"])
        return [self.create_job(data=serializer.data, job=serializer.data, channel=oracle.channel)]
