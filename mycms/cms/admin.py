from django.contrib import admin

from cms.models import webinfo,carousel,introduction,feature

# Register your models here.
admin.site.register([webinfo,carousel,
                     introduction,
                     feature
                     ])