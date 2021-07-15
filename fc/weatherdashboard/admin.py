from django.contrib import admin
from django.apps import apps

from weatherdashboard.models import *

class WeatherAdmin(admin.ModelAdmin):
    list_display = [
        'city',
        'country',
        'country_code',
        'temperature',
        'condition',
        'unix_last_update'
    ]
    ordering = [
        '-unix_last_update',
        'raw_data__name',
    ]
admin.site.register(Weather, WeatherAdmin)


class CountryAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'code'
    ]
    ordering = [
        'name',
        'code'
    ]
admin.site.register(Country, CountryAdmin)


class LocationAdmin(admin.ModelAdmin):
    list_display = [
        'city',
        'get_country_name',
        'get_country_code',
        'get_last_weather'
    ]
    ordering = [
        'city',
        'country__name',
        'country__code',
    ]

    def get_country_name(self, obj):
        return obj.country.name

    def get_country_code(self, obj):
        return obj.country.code

    def get_last_weather(self, obj):
        if obj.last_weather is None:
            return None
        return obj.last_weather.temperature
admin.site.register(Location, LocationAdmin)