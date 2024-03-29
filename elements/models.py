from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.core import serializers
from django.db import models
# Create your models here.
from pandas import HDFStore

from elements.managers import (DelayedRepresentationManager,
                               DelayedTransformationManager, PandasManager,
                               RepresentationManager, ROIManager,
                               TransformationManager)
from larvik.logging import get_module_logger
from larvik.models import LarvikArray

logger = get_module_logger(__name__)

def get_sentinel_user():
    return get_user_model().objects.get_or_create(username='deleted')[0]


class Antibody(models.Model):
    name = models.CharField(max_length=100)
    creator = models.ForeignKey(User, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return "{0}".format(self.name)


class Experiment(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=1000)
    description_long = models.TextField(null=True,blank=True)
    linked_paper = models.URLField(null=True,blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='experiment_banner',null=True,blank=True)

    def __str__(self):
        return "Experiment {0} by {1}".format(self.name,self.creator.username)

class ExperimentalGroup(models.Model):
    name = models.CharField(max_length=200, help_text="The experimental groups name")
    description = models.CharField(max_length=1000,  help_text="A brief summary of applied techniques in this group")
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, help_text="The experiment this Group belongs too")
    iscontrol = models.BooleanField(help_text="Is this Experimental Group a ControlGroup?")


    def __str__(self):
        return "ExperimentalGroup {0} on Experiment {1}".format(self.name,self.experiment.name)

class FileMatchString(models.Model):
    name = models.CharField(max_length=500)
    regexp = models.CharField(max_length=4000)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return "FileMatchString {0} created by {1}".format(self.name,self.creator.name)


class Animal(models.Model):
    name = models.CharField(max_length=100)
    age = models.CharField(max_length=400)
    type = models.CharField(max_length=500)
    creator = models.ForeignKey(User, blank=True, on_delete=models.CASCADE)
    experiment = models.ForeignKey(Experiment, blank=True, on_delete=models.CASCADE, null=True)
    experimentalgroup = models.ForeignKey(ExperimentalGroup, blank=True, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return "{0}".format(self.name)


class Sample(models.Model):
    creator = models.ForeignKey(User, on_delete=models.SET(get_sentinel_user))
    name = models.CharField(max_length=1000)
    experiment = models.ForeignKey(Experiment, on_delete=models.SET_NULL, blank=True, null=True)
    nodeid = models.CharField(max_length=400, null=True, blank=True)
    experimentalgroup = models.ForeignKey(ExperimentalGroup, on_delete=models.SET_NULL, blank=True, null=True)
    animal = models.ForeignKey(Animal, on_delete=models.SET_NULL, blank=True, null=True)


    def __str__(self):
        return "{0} by User: {1}".format(self.name,self.creator.username)


    def delete(self, *args, **kwargs):
        logger.info("Trying to remove Sample H5File")
        super(Sample, self).delete(*args, **kwargs)


    def _repr_html_(self):
        from django.core import serializers
        from django.forms.models import model_to_dict
        import pandas as pd

        return pd.DataFrame.from_records([model_to_dict(self)])._repr_html_()




class Pandas(models.Model):
    filepath = models.FilePathField(max_length=400) # aka pandas/$answerid.h5
    vid = models.CharField(max_length=1000) # aca vid0, vid1, vid2, vid3
    type = models.CharField(max_length=100)
    compression = models.CharField(max_length=300, blank=True, null=True)
    # Custom Manager to simply create an array
    objects = PandasManager()

    def get_dataframe(self):
        logger.info("Trying to access file {0} to get dataframe".format(self.filepath))
        with HDFStore(self.filepath) as store:
            path = self.type + "/" + self.vid
            dataframe = store.get(path)
        return dataframe

    def set_dataframe(self,dataframe):
        logger.info("Trying to access file {0} to set dataframe".format(self.filepath))
        with HDFStore(self.filepath) as store:
            path = self.type + "/" + self.vid
            store.put(path, dataframe)

    def delete(self, *args, **kwargs):
        logger.info("Trying to remove Dataframe from Filepath {0}".format(self.filepath))
        with HDFStore(self.filepath) as store:
            path = self.type + "/" + self.vid
            if path in store:
                store.delete(path)
                logger.info("Deleted Dataframe with VID {1} from file {0}".format(self.filepath, self.vid))

        super(Pandas, self).delete(*args, **kwargs)

    def __str__(self):
        return "Pandas with VID " + str(self.vid) + " at " + str(self.filepath)


class Channel(object):
    pass


class Slice(object):
    pass

class Impuls(object):
    pass


class ChannelMap(object):
    pass


class Representation(LarvikArray):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    inputrep = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null= True)
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE,related_name='representations')
    type = models.CharField(max_length=400, blank=True, null=True)
    chain = models.CharField(max_length=9000, blank=True, null=True)
    nodeid = models.CharField(max_length=400, null=True, blank=True)
    meta = models.CharField(max_length=6000, null=True, blank=True) #deprecated

    objects = RepresentationManager()
    delayed = DelayedRepresentationManager()

    class Meta:
        base_manager_name = "objects"
        default_manager_name = "objects"

    def __str__(self):
        return f'Representation of {self.name}'

    def _repr_html_(self):
        return f"<h3>{self.name}</h3><ul><li>Sample Name: {self.sample.name}</li></ul>"


class ROI(models.Model):
    nodeid = models.CharField(max_length=400, null=True, blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    vectors = models.CharField(max_length=3000, help_text= "A json dump of the ROI Vectors (specific for each type)")
    color = models.CharField(max_length=100, blank=True, null=True)
    signature = models.CharField(max_length=300,null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True)
    representation = models.ForeignKey(Representation, on_delete=models.CASCADE,blank=True, null=True, related_name="rois")
    experimentalgroup = models.ForeignKey(ExperimentalGroup, on_delete=models.SET_NULL, blank=True, null=True)

    objects = ROIManager()

    class Meta:
        base_manager_name = "objects"
        default_manager_name = "objects"


    def __str__(self):
        return f"ROI created by {self.creator.username} on {self.representation.name}"

class Transformation(LarvikArray):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    nodeid = models.CharField(max_length=400, null=True, blank=True)
    roi = models.ForeignKey(ROI, on_delete=models.CASCADE, related_name='transformations')
    representation = models.ForeignKey(Representation, on_delete=models.SET_NULL, blank=True, null=True, related_name="transformations")
    inputtransformation = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null= True)

    objects = TransformationManager()
    delayed = DelayedTransformationManager()

    class Meta:
        base_manager_name = "objects"
        default_manager_name = "objects"

    def __str__(self):
        return self.name
