from django.db import models
from django.db.models import JSONField
from django.contrib.gis.db.models import PointField

class Weather(models.Model):
    """
    Stores an openweathermap API reading and stores datetime according to
    local timezone

    from dateutil import tz
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    dt = datetime.datetime.utcfromtimestamp(1625969973)
    dt = dt.replace(tzinfo=from_zone)
    central = dt.astimezone(to_zone)
    """

    raw_data = JSONField(
        help_text=u"Content from openweathermap API"
    )
    unix_last_update = models.DateTimeField(
        help_text=u"Unix by default"
    )
    coordinates = PointField(
        help_text=u"API location"
    )

    @property
    def temperature(self):
        kelvin_value = self.raw_data['main']['temp']
        celcius_value = kelvin_value - 273.15
        return celcius_value

    @property
    def condition(self):
        weather_conditions = self.raw_data['weather']
        if len(weather_conditions) == 0:
            return None
        return "{} ({})".format(
            weather_conditions[0]['main'],
            weather_conditions[0]['description']
        )

    @property
    def country_code(self):
        return self.raw_data['sys']['country']

    @property
    def country(self):
        countries_obj = Country.objects.filter(
            code=self.raw_data['sys']['country']
        )
        if countries_obj.exists():
            return countries_obj.first().name
        return None

    @property
    def city(self):
        return self.raw_data['name']

    class Meta:
        ordering = ['-unix_last_update']


class Country(models.Model):
    """
    Stores all the world countries
    """

    name = models.CharField(
        help_text=u"Country name",
        max_length=300
    )
    code = models.CharField(
        help_text=u"Country code",
        max_length=2
    )

    class Meta:
        verbose_name_plural = "Countries"

class Location(models.Model):
    """
    Stores Locations of countries with its capitals and has a relation to
    Weather model
    """

    city = models.CharField(
        help_text=u"City name",
        max_length=300
    )
    country = models.ForeignKey(
        'weatherdashboard.Country',
        on_delete=models.CASCADE,
        related_name='countries',
        help_text=u"Countries"
    )
    last_weather = models.ForeignKey(
        'weatherdashboard.Weather',
        on_delete=models.CASCADE,
        related_name='locations',
        blank=True,
        null=True,
        help_text=u"Last weather reading"
    )
