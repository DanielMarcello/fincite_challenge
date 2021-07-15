from django.shortcuts import render
from dateutil import tz
import requests
import datetime

from django.contrib.gis.geos import GEOSGeometry

# Django rest
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework import serializers

# Models
from weatherdashboard.models import (
    Location,
    Weather,
    Country
)

# Serializers
from weatherdashboard.serializers import (
    LocationSerializer,
    CreateLocationSerializer,
    WeatherSerializer,
    CreateWeatherSerializer,
    CountrySerializer
)

# ENV data
import environ
env = environ.Env()
environ.Env.read_env()
API_KEY = env('WEATHER_API_KEY')
LOCATION_BY_PLACE_API = env('LOCATION_BY_PLACE_API')
LOCATION_BY_COORD_API = env('LOCATION_BY_COORD_API')
FORECAST_BY_COORD_API = env('FORECAST_BY_COORD_API')

class CountryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    Viewset for listing all countries in the world
    """

    def get_queryset(self):
        return Country.objects.all();

    def get_serializer_class(self):
        return CountrySerializer


class LocationViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    Viewset for listing locations
    """

    def get_queryset(self):
        return Location.objects.all();

    def get_serializer_class(self):
        if self.action in ['create', 'add_location']:
            return CreateLocationSerializer
        return LocationSerializer

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        return context

    def create(self, request, *args, **kwargs):
        """
        create action and returns the data of Location
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        location = serializer.save()
        location_serializer = LocationSerializer(location)
        return Response(location_serializer, status=status.HTTP_201_CREATED)

    def unix_to_utc(self, timestamp):
        """
        Converts timestamp into utc datetime
        """
        from_zone = tz.tzutc()
        dt = datetime.datetime.utcfromtimestamp(timestamp)
        dt = dt.replace(tzinfo=from_zone)
        return dt

    @action(detail=False, methods=['post'])
    def add_location(self, request, *args, **kwargs):
        """
        Tries to get new location weather data
            - verifies if request data is correct
            - if location already exists returns exception
            - if API returns 200 adds new Location
            - if API returns another status_code return the object
        """
        data = request.data
        if not 'city' in data:
            raise serializers.ValidationError('missing city attribute in body')
        if not 'country_code' in data:
            raise serializers.ValidationError(
                'missing country code attribute in body'
            )
        stored_location = Location.objects.filter(
            city__iexact=data['city'],
            country__code=data['country_code']
        )
        if stored_location.exists():
            stored_location = stored_location.first()
            city = stored_location.city
            country = stored_location.country.name
            code = stored_location.country.code
            raise serializers.ValidationError(
                '{}, {}({}) already exists'.format(city, country, code)
            )

        url = LOCATION_BY_PLACE_API.format(
            data['city'],
            data['country_code'],
            API_KEY
        )
        response = requests.get(url)
        response_data = response.json()

        if response_data['cod'] != 200:
            raise serializers.ValidationError(response_data['message'])

        dt = self.unix_to_utc(response_data['dt'])

        weather_data = {"raw_data": response_data}
        weather_serializer = CreateWeatherSerializer(data=weather_data)
        weather_serializer.is_valid()
        weather = weather_serializer.save()
        data['last_weather'] = weather.id
        location_serializer = self.get_serializer(data=data)
        location_serializer.is_valid()
        location = location_serializer.save()
        new_location_serializer = LocationSerializer(location)
        return Response(
            new_location_serializer.data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=['get'])
    def update_weather(self, request, *args, **kwargs):
        """
        iterates by all Locations and updates its weathre attribute
        for each location:
            - gets weather by city and country code
            - if weather doesn't exists creates a new with the weather API data
            - points weather to location
        """
        for location in Location.objects.iterator():
            data = request.query_params
            if not 'dt' in data:
                raise serializers.ValidationError('missing dt param')

            dt = self.unix_to_utc(int(data['dt']))

            weather_return = None
            stored_weathers = Weather.objects.filter(
                unix_last_update=dt,
                raw_data__sys__country=location.country.code,
                raw_data__name=location.city
            )
            if stored_weathers.exists():
                weather_return = stored_weathers.first()

            if weather_return is None:
                url = LOCATION_BY_PLACE_API.format(
                    location.city,
                    location.country.code,
                    API_KEY
                )
                response = requests.get(url)
                response_data = response.json()

                dt = self.unix_to_utc(response_data['dt'])
                second_weather_filter = Weather.objects.filter(
                    unix_last_update=dt,
                    raw_data__sys__country=response_data['sys']['country'],
                    raw_data__name=response_data['name']
                )
                if second_weather_filter.exists():
                    weather_return = second_weather_filter.first()

            if weather_return is None:
                data = {"raw_data": response_data}
                serializer = CreateWeatherSerializer(data=data)
                serializer.is_valid()
                weather_return = serializer.save()

            no_weather = location.last_weather is None
            if no_weather or (location.last_weather.id != weather_return.id):
                location.last_weather = weather_return
                location.save()
        location_serializer = LocationSerializer(
            Location.objects.all().order_by('city'),
            many=True
        )
        return Response(location_serializer.data, status=status.HTTP_200_OK)


class WeatherViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    Viewset for listing weathers and current weather with forecast
    """

    def get_queryset(self):
        return Weather.objects.all().order_by('-unix_last_update')

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateWeatherSerializer
        return WeatherSerializer

    def create(self, request, *args, **kwargs):
        """
        create action and returns the data of weather
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        weather = serializer.save()
        weather_serializer = WeatherSerializer(weather)
        return Response(weather_serializer.data, status=status.HTTP_201_CREATED)

    def unix_to_utc(self, timestamp):
        """
        Converts timestamp into utc datetime
        """
        from_zone = tz.tzutc()
        dt = datetime.datetime.utcfromtimestamp(timestamp)
        dt = dt.replace(tzinfo=from_zone)
        return dt

    @action(detail=False, methods=['get'])
    def current_weather(self, request, *args, **kwargs):
        """
        gets current weather from weather Api adding 2 conditions:
            - if there is a Weather object with the same timestamp of the requests
              returns that without creating a new Object
            - if there is a Weather object with the same timestamp of the new Api
              reading, returns that without creating a new object
            - else creates a new object
        """
        data = request.query_params
        if not 'lat' in data or not 'lon' in data:
            raise serializers.ValidationError('missing lat, lon params')

        dt = self.unix_to_utc(int(data['dt']))
        pnt = GEOSGeometry('POINT({} {})'.format(
            data['lon'], data['lat']),
            srid=4326
        )
        stored_weathers = Weather.objects.filter(
            unix_last_update=dt,
            coordinates__dwithin=(pnt, 20)
        )
        if stored_weathers.exists():
            weather = stored_weathers.first()
            weather_serializer = WeatherSerializer(weather)
            return Response(weather_serializer.data, status.HTTP_200_OK)

        lat = data['lat']
        lon = data['lon']
        url = LOCATION_BY_COORD_API.format(lat, lon, API_KEY)
        response = requests.get(url)
        response_data = response.json()

        dt = self.unix_to_utc(response_data['dt'])
        second_weather_filter = Weather.objects.filter(
            unix_last_update=dt,
            coordinates__dwithin=(pnt, 20)
        )
        if second_weather_filter.exists():
            weather = second_weather_filter.first()
            weather_serializer = WeatherSerializer(weather)
            return Response(weather_serializer.data, status.HTTP_200_OK)

        serializer = CreateWeatherSerializer(data={"raw_data": response_data})
        serializer.is_valid()
        weather = serializer.save()
        weather_serializer = WeatherSerializer(weather)
        return Response(weather_serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def forecast_weather(self, request, *args, **kwargs):
        data = request.query_params
        if not 'lat' in data or not 'lon' in data:
            raise serializers.ValidationError('missing lat,lon params')

        lat = data['lat']
        lon = data['lon']
        url = FORECAST_BY_COORD_API.format(lat, lon, API_KEY)
        response = requests.get(url)
        response_data = response.json()
        return_data = None
        if not 'cod' in response_data == 200:
            return_data = []
            for forecast in response_data['daily'][1:6]:
                dt = self.unix_to_utc(forecast['dt'])
                unix_last_update = dt
                temperature = forecast['temp']['day'] - 273.15
                condition = None
                if len(forecast['weather']) > 0:
                    condition = "{} ({})".format(
                        forecast['weather'][0]['main'],
                        forecast['weather'][0]['description']
                    )
                return_data.append({
                    'unix_last_update': unix_last_update,
                    'temperature': temperature,
                    'condition': condition
                })
        return Response(return_data, status=status.HTTP_200_OK)
