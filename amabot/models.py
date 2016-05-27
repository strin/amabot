from django.db import models


class Conversation(models.Model):
    id = models.AutoField(primary_key=True)
    imposter_id = models.CharField(max_length=100)
    fan_id = models.CharField(max_length=100)
    imposter_page = models.CharField(max_length=100)
    fan_page = models.CharField(max_length=100)
    content = models.TextField()
    
