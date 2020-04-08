
from rest_framework import routers

from test.views import *

router = routers.SimpleRouter()
router.register(r"testers", TesterViewSet)
router.register(r"testing", TestingViewSet)