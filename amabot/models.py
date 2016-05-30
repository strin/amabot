from django.db import models

MAX_CHARFIELD_LEN = 100

class ConversationModel(models.Model):
    id = models.AutoField(primary_key=True)
    imposter_id = models.CharField(max_length=MAX_CHARFIELD_LEN)
    fan_id = models.CharField(max_length=MAX_CHARFIELD_LEN)
    imposter_page = models.CharField(max_length=MAX_CHARFIELD_LEN)
    fan_page = models.CharField(max_length=MAX_CHARFIELD_LEN)
    content = models.TextField()
    rating = models.IntegerField(default=0) # not rated by default.
    

class ImposterModel(models.Model):
    imposter_id = models.CharField(max_length=MAX_CHARFIELD_LEN)
    imposter_page = models.CharField(max_length=MAX_CHARFIELD_LEN)
    is_free = models.BooleanField()
    

