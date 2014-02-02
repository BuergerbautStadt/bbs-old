# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import Http404, render
from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.csrf import csrf_exempt
import json

import lib.views

from projekte.models import Projekt, Veroeffentlichung, Verfahrensschritt, Verfahren, Behoerde, Bezirk

def projektGeoJson(projekt):
    response = {
        'type': "Feature",
        'geometry': {
            'type': 'Point',
            'coordinates': [projekt.lon,projekt.lat]
        },
        'properties': {
            'bezeichner': projekt.bezeichner,
            'adresse': projekt.adresse,
            'beschreibung': projekt.beschreibung,
            'bezirke': [],
            'veroeffentlichungen': []
        }
    }
    for bezirk in projekt.bezirke.all():
        response['properties']['bezirke'].append(bezirk.name)
    for veroeffentlichung in projekt.veroeffentlichungen.all():
        response['properties']['veroeffentlichungen'].append({
            'beschreibung': veroeffentlichung.beschreibung,
            'verfahrensschritt': veroeffentlichung.verfahrensschritt.name,
            'beginn': veroeffentlichung.beginn,
            'ende': veroeffentlichung.ende,
            'auslegungsstelle': veroeffentlichung.auslegungsstelle,
            'behoerde': veroeffentlichung.behoerde.name,
            'link': veroeffentlichung.link
        })
    return response

class ProjekteView(lib.views.View):
    http_method_names = ['get']

    def get(self, request):
        bezirk = request.GET.get('bezirk', None)

        if bezirk:
            projekte = Projekt.objects.filter(bezirke__name=bezirk)
        else: 
            projekte = Projekt.objects.all()

        if self.accept == 'json':
            response = {'type': 'FeatureCollection','features': []}
            for projekt in projekte:
                response['features'].append(projektGeoJson(projekt))
            return self.renderJson(request,response)
        else:
            response = {'projekte': projekte}
            return render(request,'projekte/projekte.html', response)

class ProjektView(lib.views.View):
    http_method_names = ['get']

    def get(self, request, pk):
        try:
            projekt = Projekt.objects.get(pk=int(pk))
        except Projekt.DoesNotExist:
            raise Http404

        if self.accept == 'json':
            response = projektGeoJson(projekt)
            return self.renderJson(request, response)
        else:
            response = {'projekt': projekt}
            return render(request, 'projekte/projekt.html', response)
