import hashlib
import json
import pickle
import uuid
from imp import find_module
from importlib import import_module

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import OperationalError
from django.db.models import Manager, Model

from larvik.logging import get_module_logger

CONSUMERS = {}

ISDISCOVER = False

def setDiscover(mode):
    global ISDISCOVER
    ISDISCOVER = mode

NODES = {}

NonePath = "NO PATH APPLICABLE"

logger = get_module_logger(__file__)

def createUniqeNodeName(channel=None):
    """This function generate 10 character long hash"""
    hash = hashlib.sha1()
    salt = channel if channel is not None else str(uuid.uuid4())
    hash.update(salt.encode('utf-8'))
    return  hash.hexdigest()

class NodeType(object):
    inputs = []
    outputs = []
    name = None
    path = None
    settings = {}
    type = None


def saveConsumers(CONSUMERLIST):
    pickle.dump(CONSUMERLIST, "consumers")



class register_consumer(object):

    def __init__(self, channel, model: Model= None):
        """
        If there are decorator arguments, the function
        to be decorated is not passed to the constructor!
        """
        self.channel = channel
        self.model = model


    def getModelForPuts(self, puts):
        return json.dumps([input.lower() if isinstance(input,str) else input.__name__.lower() for input in puts]) if puts is not None else json.dumps([])

    def __call__(self, cls: NodeType):
        self.name = cls.name if cls.name is not None else self.channel
        if cls.path is not None :
            self.path = cls.path 
        else:
            raise NotImplementedError(f"Please specify a path in {repr(cls)}")
        self.type = cls.type if cls.type is not None else "consumer"
        self.inputmodel = self.getModelForPuts(cls.inputs)
        self.outputmodel = self.getModelForPuts(cls.outputs)
        self.settings = json.dumps(cls.settings) if cls.settings is not None else json.dumps({})


        """
        If there are decorator arguments, __call__() is only called
        once, as part of the decoration process! You can only give
        it a single argument, which is the function object.
        """



        if self.channel in NODES: raise Exception(f"The node {self.node} does already exist. Check for Duplicates")
        if self.channel in CONSUMERS: raise Exception(f"The node {self.node} does already exist. Check for Duplicates")

        if self.model is not None and ISDISCOVER:

            from flow.models import Node
            logger.info(f"{self.name} checking {self.model.__name__} - Checking")

            manager: Manager = self.model.objects
            try:
                try:
                    object = manager.get(channel=self.channel)
                    object.name = self.name
                    object.channel = self.channel
                    object.save()

                except ObjectDoesNotExist as e:
                    logger.info(f"{self.name} did not yet exist on {self.model.__name__} - Creating")
                    object = manager.create(name=self.name, channel=self.channel, settings=self.settings)

                try:
                    node = Node.objects.get(hash=createUniqeNodeName(self.channel))
                    node.name = self.name
                    node.path = self.path
                    node.variety = self.type
                    node.inputmodel = self.inputmodel
                    node.outputmodel = self.outputmodel
                    node.defaultsettings = self.settings
                    node.channel = self.channel
                    node.entityid = object.id
                    node.save()



                except ObjectDoesNotExist as e:
                    node = Node.objects.create(hash=createUniqeNodeName(self.channel),
                                               entityid=object.id,
                                               name=self.name,
                                               path=self.path,
                                               variety=self.type,
                                               channel=self.channel,
                                               inputmodel=self.inputmodel,
                                               outputmodel=self.outputmodel,
                                               defaultsettings=self.settings)
                    logger.info(f"{self.name} did not yet exist on {self.channel} - Creating")


            # TODO: When everything was mirated consumers should be called here CONSUMERS[self.name] = cls
            except OperationalError as e:
                logger.error(f'Consumer cannot be installed, migrate first: {e}')



        CONSUMERS[self.channel] = cls
        NODES[self.channel] = cls
        return cls



class register_node(object):

    def __init__(self, node):
        """
        If there are decorator arguments, the function
        to be decorated is not passed to the constructor!
        """
        self.node = node

    def getModelForPuts(self, puts):
        return json.dumps([input.lower() if isinstance(input,str) else input.__name__.lower() for input in puts]) if puts is not None else json.dumps([])


    def __call__(self, cls: NodeType):

        from flow.models import Node
        """
        If there are decorator arguments, __call__() is only called
        once, as part of the decoration process! You can only give
        it a single argument, which is the function object.
        """
        if self.node in NODES: raise Exception(f"The node {self.node} does already exist. Check for Duplicates")
        if ISDISCOVER is False:
            NODES[self.node] = cls
            return cls

        try:
            try:
                node = Node.objects.get(hash=createUniqeNodeName(self.node))
                node.name = cls.name
                node.path = cls.path
                node.variety = cls.type
                node.inputmodel = self.getModelForPuts(cls.inputs)
                node.outputmodel = self.getModelForPuts(cls.outputs)
                node.defaultsettings = json.dumps(cls.settings)
                node.channel = "None"
                node.entityid = None
                node.save()

                logger.info(f"Updating {cls.__name__} as {self.node} on {self.node}")

            except ObjectDoesNotExist as e:
                node = Node.objects.create(hash=createUniqeNodeName(self.node),
                                           entityid=None,
                                           name=cls.name,
                                           path=cls.path,
                                           variety=cls.type,
                                           channel="None",
                                           inputmodel=self.getModelForPuts(cls.inputs),
                                           outputmodel=self.getModelForPuts(cls.outputs),
                                           defaultsettings=json.dumps(cls.settings))

                logger.info(f"Installing {cls.__name__} as {self.node} on {self.node}")



        # TODO: When everything was mirated consumers should be called here CONSUMERS[self.name] = cls
        except OperationalError as e:
            logger.error(f'Consumer cannot be installed, migrate first: {e}')


        NODES[self.node] = cls
        return cls



def autodiscover():
    for app in settings.INSTALLED_APPS:
        # For each app, we need to look for an consumers.py inside that app's
        # package. We can't use os.path here -- recall that modules may be
        # imported different ways (think zip files) -- so we need to get
        # the app's __path__ and look for admin.py on that path.

        # Step 1: find out the app's __path__ Import errors here will (and
        # should) bubble up, but a missing __path__ (which is legal, but weird)
        # fails silently -- apps that do weird things with __path__ might
        # need to roll their own admin registration.
        try:
            app_path = import_module(app).__path__
        except AttributeError:
            continue

        # Step 2: use imp.find_module to find the app's consumers.py. For some
        # reason imp.find_module raises ImportError if the app can't be found
        # but doesn't actually try to import the module. So skip this app if
        # its admin.py doesn't exist
        try:
            find_module('consumers', app_path)
        except ImportError:
            continue

        # Step 3: import the app's admin file. If this has errors we want them
        # to bubble up.
        import_module("%s.consumers" % app)
    # autodiscover was successful, reset loading flag.
    for app in settings.INSTALLED_APPS:
        # For each app, we need to look for an consumers.py inside that app's
        # package. We can't use os.path here -- recall that modules may be
        # imported different ways (think zip files) -- so we need to get
        # the app's __path__ and look for admin.py on that path.

        # Step 1: find out the app's __path__ Import errors here will (and
        # should) bubble up, but a missing __path__ (which is legal, but weird)
        # fails silently -- apps that do weird things with __path__ might
        # need to roll their own admin registration.
        try:
            app_path = import_module(app).__path__
        except AttributeError:
            continue

        # Step 2: use imp.find_module to find the app's consumers.py. For some
        # reason imp.find_module raises ImportError if the app can't be found
        # but doesn't actually try to import the module. So skip this app if
        # its admin.py doesn't exist
        try:
            find_module('nodes', app_path)
        except ImportError:
            continue

        # Step 3: import the app's admin file. If this has errors we want them
        # to bubble up.
        import_module("%s.nodes" % app)
    # autodiscover was successful, reset loading flag.

    return CONSUMERS