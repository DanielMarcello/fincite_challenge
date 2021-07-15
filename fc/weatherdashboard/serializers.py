# Django
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db import transaction
from django.db.models import JSONField
from django.contrib.gis.db.models import PointField
from django.contrib.gis.geos import Point

from dateutil import tz
import datetime

# Django rest
from rest_framework import serializers
from rest_framework import status

# Models
from weatherdashboard.models import Location, Country, Weather


class CountrySerializer(serializers.ModelSerializer):
    """
    Swrializer for listing Countries
    """
    class Meta:
        model = Country
        fields = (
            'name',
            'code'
        )


class LocationSerializer(serializers.ModelSerializer):
    """
    Serializer for listing all Locations objects
    """
    country = serializers.SerializerMethodField()
    last_weather_reading = serializers.SerializerMethodField()

    class Meta:
        model = Location
        fields = (
            'country',
            'city',
            'last_weather_reading'
        )

    def get_country(self, instance):
        return CountrySerializer(instance.country).data

    def get_last_weather_reading(self, instance):
        last_weather = instance.last_weather
        if last_weather is None:
            return None
        last_weather_data = LocationWeatherSerializer(last_weather).data
        return last_weather_data


class CreateLocationSerializer(serializers.Serializer):
    """
    Serializer for creating Locations
    """
    city = serializers.CharField(max_length=300)
    country_code = serializers.CharField(max_length=2)
    last_weather = serializers.IntegerField()

    def validate(self, data):
        if not 'city' in data:
            return serializers.ValidationError('city must exist.')
        if not 'country_code' in data:
            return serializers.ValidationError('country code must exist.')
        if not 'last_weather' in data:
            return serializers.ValidationError('last weather must exist.')
        data['last_weather'] = Weather.objects.get(id=data['last_weather'])
        data['city'] = data['last_weather'].city
        try:
            data['country'] = Country.objects.get(code=data['country_code'])
        except:
            return serializers.ValidationError(
                '{} is not a valid country code.'.format(data['country_code'])
            )
        return data

    def create(self, validated_data):
        location = Location.objects.create(
            city=validated_data['city'],
            country=validated_data['country'],
            last_weather=validated_data['last_weather'],
        )
        return location


class LocationWeatherSerializer(serializers.ModelSerializer):
    """
    Serializer for listing weathers without raw data
    """
    coordinates = serializers.SerializerMethodField()

    class Meta:
        model = Weather
        fields = (
            'unix_last_update',
            'coordinates',
            'temperature',
            'condition',
        )

    def get_coordinates(self, instance):
        return {
            'lat': instance.coordinates.coords[1],
            'lon': instance.coordinates.coords[0]
        }


class WeatherSerializer(serializers.ModelSerializer):
    """
    Serializer for listing weathers
    """
    coordinates = serializers.SerializerMethodField()

    class Meta:
        model = Weather
        fields = (
            'raw_data',
            'city',
            'country',
            'country_code',
            'unix_last_update',
            'coordinates',
            'temperature',
            'condition',
        )

    def get_coordinates(self, instance):
        return {
            'lat': instance.coordinates.coords[1],
            'lon': instance.coordinates.coords[0]
        }


class CreateWeatherSerializer(serializers.Serializer):
    """
    Serializer for creation weather
    """
    raw_data = serializers.JSONField()

    def validate(self, data):
        if not 'raw_data' in data:
            return serializers.ValidationError('raw_data must exist.')
        raw_data = data['raw_data']
        if not 'dt' in raw_data:
            return serializers.ValidationError('dt must exists.')
        if not 'coord' in raw_data:
            return serializers.ValidationError('coord must exist.')
        coord = raw_data['coord']
        if not 'lat' in coord or not 'lon' in coord:
            return serializers.ValidationError('lat and lon must exist.')

        from_zone = tz.tzutc()
        dt = datetime.datetime.utcfromtimestamp(raw_data['dt'])
        dt = dt.replace(tzinfo=from_zone)
        data['unix_last_update'] = dt
        data['coordinates'] = Point(coord['lon'], coord['lat'])
        return data

    def create(self, validated_data):
        new_weather = Weather.objects.create(
            raw_data=validated_data['raw_data'],
            unix_last_update=validated_data['unix_last_update'],
            coordinates=validated_data['coordinates']
        )
        return new_weather
