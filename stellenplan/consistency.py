# -*- coding: utf-8 -*-



# generic python 
from pprint import pprint as pp 
import datetime 


# django imports 
from django.views.generic import View
from django.shortcuts import render
from django.contrib.contenttypes.models  import ContentType 
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


# from this app: 
from stellenplanForms import * 


###########################################################


class konsistenz (View):
    @method_decorator (login_required)
    def get (self, request):
        return render (request,
                       'stellenplan/konsistenz.html',
                       {})
    
