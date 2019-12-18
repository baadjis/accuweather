# -*- coding: utf-8 -*-

# Copyright(C) 2019      baadjis
#
# This file is part of a weboob module.
#
# This weboob module is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This weboob module is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this weboob module. If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals


from weboob.browser import PagesBrowser, URL

from .pages import  WeatherPage, CitiesPage, ForecastPage


class AccuweatherBrowser(PagesBrowser):
    BASEURL = 'https://www.accuweather.com'
    cities = URL('web-api/autocomplete', CitiesPage)
    weather = URL(r'/(?P<country>.*)/(?P<lang>.*)/(?P<cityname>.*)/(?P<pattern>.*)/current-weather/(?P<pattern2>.*)', WeatherPage)
    forecast = URL(r'/(?P<country>.*)/(?P<lang>.*)/(?P<cityname>.*)/(?P<pattern>.*)/(?P<freq>.*)-weather-forecast/(?P<pattern2>.*)', ForecastPage)
    city_name=''
    def iter_city_search(self, pattern):
        params={"query":pattern,"language":'fr'}
        self.city_name=pattern
        return self.cities.go(params=params).iter_cities()

    def iter_forecast_freq(self, city,freq):

        self.forecast.go(country=city.country,lang='fr',pattern=city.id,freq=freq, pattern2=city.id,cityname= city.name)

        return self.page.daily_forecast() if (freq=='daily') else(self.page.hourly_forecast() if (freq=='hourly') else '')

    def get_current(self, city):
        print(city)
        self.weather.go(country=city.country,lang='fr',pattern=city.id, pattern2=city.id,cityname= city.name)
        return self.page.get_current()


