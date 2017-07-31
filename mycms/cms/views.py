#coding:utf-8
from django.shortcuts import render
from django.http import request
from cms import models

# Create your views here.
def index(request):
    navbarinfo=models.webinfo.objects.all()
    
    carousel1=models.carousel.objects.filter(carousel_title="第一个幻灯片")
    carousel2=models.carousel.objects.filter(carousel_title="第二个幻灯片")
    carousel3=models.carousel.objects.filter(carousel_title="第三个幻灯片")
    
    intro1=models.introduction.objects.filter(heading="产品1")
    intro2=models.introduction.objects.filter(heading="产品2")
    intro3=models.introduction.objects.filter(heading="产品3")
    
    f_heading1=models.feature.objects.filter(feature_heading="特性1的标题")
    f_heading2=models.feature.objects.filter(feature_heading="特性2的标题")
    f_heading3=models.feature.objects.filter(feature_heading="特性3的标题")
    
    return render(request, "index.html", {'navbarinfo': navbarinfo,
                                          'carousel1':carousel1,
                                          'carousel2':carousel2,
                                          'carousel3':carousel3,
                                          'intro1':intro1,
                                          'intro2':intro2,
                                          'intro3':intro3,
                                          'feature1':f_heading1,
                                          'feature2':f_heading2,
                                          'feature3':f_heading3
                                          })
    