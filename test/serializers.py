from rest_framework import serializers

from test.models import *


class TesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tester
        fields = "__all__"

class TestingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testing
        fields = "__all__"

