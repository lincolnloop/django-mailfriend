from django.db import models

class FakeItem(models.Model):
    """Used for testing purposes only"""
    slug = models.CharField(max_length=100)

    def __unicode__(self):
        return "Fake item: %s" % self.slug
        
    def get_absolute_url(self):
        return "/fake-item/%s/" % self.slug
