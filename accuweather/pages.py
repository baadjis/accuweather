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

from datetime import date, datetime

from weboob.browser.pages import JsonPage, HTMLPage
from weboob.browser.elements import ItemElement, ListElement, DictElement, method
from weboob.capabilities.base import NotAvailable
from weboob.capabilities.weather import Forecast, Current, City, Temperature
from weboob.browser.filters.json import Dict
from weboob.browser.filters.standard import CleanText, CleanDecimal, Regexp, Format, Eval


class SearchPage(HTMLPage):
    def do_stuff(self, _id):
        raise NotImplementedError()


class CitiesPage(JsonPage):
    @method
    class iter_cities(DictElement):
        ignore_duplicate = True

        # item_xpath ='/html/body/div/div[4]/div/div[1]/div[1]/div[1]'

        class item(ItemElement):
            klass = City
            obj_id = Dict('key')
            obj_name = Dict('localizedName')

            # ob_key=Dict('key')
            def obj_country(self):
                print(Dict('key')(self))
                print(Dict('country')(self)['id'].lower())
                return Dict('country')(self)['id'].lower()


class WeatherPage(HTMLPage):
    @method
    class get_current(ItemElement):
        klass = Current
        obj_id = date.today()
        obj_date = date.today()

        def obj_temp(self):
            temp = CleanDecimal('/html/body/div/div[5]/div[1]/div[1]/div[1]/div/div[1]/div[1]/div[1]/div/p[1]')(self)
            unit = CleanText('/html/body/div/div[5]/div[1]/div[1]/div[1]/div/div[1]/div[1]/div[1]/div/p[1]/span')(self)
            return Temperature(float(temp), unit)

        obj_text = Format('%s - %s - %s - %s -%s -%s - %s -%s ',
                          CleanText('/html/body/div/div[5]/div[1]/div[1]/div[1]/div/div[2]/div/div[1]/p[1]'),
                          CleanText('/html/body/div/div[5]/div[1]/div[1]/div[1]/div/div[2]/div/div[1]/p[2]'),
                          CleanText('/html/body/div/div[5]/div[1]/div[1]/div[1]/div/div[2]/div/div[1]/p[3]'),
                          CleanText('/html/body/div/div[5]/div[1]/div[1]/div[1]/div/div[2]/div/div[1]/p[4]'),
                          CleanText('/html/body/div/div[5]/div[1]/div[1]/div[1]/div/div[2]/div/div[1]/p[5]'),
                          CleanText('/html/body/div/div[5]/div[1]/div[1]/div[1]/div/div[2]/div/div[1]/p[6]'),
                          CleanText('/html/body/div/div[5]/div[1]/div[1]/div[1]/div/div[2]/div/div[2]/p[1]'),
                          CleanText('/html/body/div/div[5]/div[1]/div[1]/div[1]/div/div[2]/div/div[2]/p[2]')

                          )


class ForecastPage(HTMLPage):
    @method
    class daily_forecast(ListElement):
        item_xpath = '//html/body/div/div[5]/div[1]/div/div[1]/a'

        class item(ItemElement):
            klass = Forecast
            obj_id = CleanText('./div[1]')

            def obj_low(self):

                temp = Regexp(CleanText('./div[2]/span[2]', symbols=['/']), u'(\d*)\xb0.*')

                if temp != '':  # Sometimes website does not return low
                    temp = CleanDecimal(temp)(self)
                    unit = 'C'
                    return Temperature(float(temp), unit)
                return NotAvailable

            def obj_high(self):
                temp = Regexp(CleanText('./div[2]/span[1]'), u'(\d*)\xb0.*')
                if temp != '':  # Sometimes website does not return low
                    temp = CleanDecimal(temp)(self)
                    unit = 'C'
                    return Temperature(float(temp), unit)
                return NotAvailable

            obj_text = CleanText('./span')

            def obj_date(self):
                actual_day_number = Eval(int,
                                         Regexp(CleanText('./div[1]'),
                                                '\w{3}\. (\d+)'))(self)
                base_date = date.today()
                if base_date.day > actual_day_number:
                    base_date = base_date.replace(
                        month=(
                            (base_date.month + 1) % 12
                        )
                    )
                base_date = base_date.replace(day=actual_day_number)
                return base_date

    @method
    class hourly_forecast(ListElement):
        item_xpath = '//html/body/div/div[5]/div[1]/div[1]/div[1]/div'
        class item(ItemElement):
            klass = Forecast
            obj_id = CleanText('./div[1]/div/div/div[1]/p[1]')
            #obj_date = date.today()

            def obj_high(self):
                temp =CleanText('./div[1]/div/div/div[2]')
                if temp(self) !='':
                    temp = Regexp(CleanText('./div[1]/div/div/div[2]'), u'(\d*)\xb0.*')
                    if temp :
                      temp=CleanDecimal(temp)(self)
                      unit = 'C'
                      return Temperature(float(temp),unit)
                return NotAvailable
            def obj_low(self):
                return NotAvailable


            """def obj_low(self):
                temp =CleanText('./div[1]/div/div/div[2]')

                if temp(self) !='':
                    temp = Regexp(CleanText('./div[1]/div/div/div[2]'), u'(\d*)\xb0.*')
                    if temp !='':
                      temp = CleanDecimal(temp)(self)
                      unit = 'C'
                      return Temperature(float(temp),unit)
                return NotAvailable
            """
            def obj_date(self):
                daten=CleanText('./div[1]/div/div/div[1]/p[1]')
                if daten(self)!='':
                    actual_day_number = Eval(int,
                                             Regexp(CleanText('./div[1]/div/div/div[1]/p[1]'),
                                                    '(\d+)'))(self)
                    base_date = datetime.now()
                    if base_date.hour > actual_day_number:
                        base_date = base_date.replace(
                            hour=(
                                (base_date.hour + 1) % 24
                            )
                        )
                    base_date = base_date.replace(hour=actual_day_number,minute=0,second=0,microsecond=0)
                    return base_date
