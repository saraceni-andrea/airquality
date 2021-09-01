#!/usr/bin/env python3

'''
@attention:

    sudo apt-get install python3-pip
    sudo pip3 install --upgrade setuptools
    sudo pip3 install smbus
    sudo pip3 install smbus2
    sudo pip3 install unicornhatmini
    sudo pip3 install bme680
    sudo pip3 install pimoroni-sgp30
    sudo pip3 install rv3028

    sudo python3 diyzeniaq.py

@bug: Beta!
@summary: DIYzenIAQ
@see: https://work.saraceni.org/airquality/

@author: Andrea Saraceni
@contact: https://twitter.com/saraceni_andrea/
@license: MIT
@date: 31.08.2021
@version: 0.9.1
'''

from subprocess import call
from threading import Thread

import math, os, sys, time

import rv3028
import bme680
from sgp30 import SGP30

from unicornhatmini import UnicornHATMini
from gpiozero import Button

class DIYzenIAQ:
    def __init__(self):
        try:
            self.unicornhatmini = UnicornHATMini()
            self.unicornhatmini.clear()
            self.unicornhatmini.set_brightness(0.02)
            self.unicornhatmini.set_rotation(0)

            self.button_a = Button(5)
            self.button_b = Button(6)
            self.button_x = Button(16)
            self.button_y = Button(24)
            self.button_mode = 0

            self.rtc = rv3028.RV3028()
            self.rtc.set_battery_switchover("level_switching_mode")
            self.rtc_now = None

            self.bme680_data = bme680.BME680(0x77)
            self.bme680_data.set_humidity_oversample(bme680.OS_2X) # bme680.OS_16X
            self.bme680_data.set_temperature_oversample(bme680.OS_8X) # bme680.OS_16X
            self.bme680_data.set_filter(bme680.FILTER_SIZE_3)
            self.bme680_data.set_gas_status(bme680.ENABLE_GAS_MEAS)
            self.bme680_data.set_gas_heater_temperature(320)
            self.bme680_data.set_gas_heater_duration(150)
            self.bme680_data.select_gas_heater_profile(0)
            self.bme680_burn_in_time = 360 # 6 minutes = 360
            self.bme680_humidity_baseline = 45.0 # optimal humidity value 40.0
            self.bme680_humidity_weighting = 0.25 # humidity 25 : gas 75
            self.bme680_gas_baseline = self.bme680_aqs = self.bme680_temperature = self.bme680_humidity = self.bme680_gas = 0
            self.bme680_start_time = self.bme680_curr_time = time.time() # self.bme680_start_time = self.bme680_end_time = self.bme680_curr_time = time.time()

            self.burn_in_mode = 0

            self.sgp30 = SGP30()
            self.data_sgp30_equivalent_co2 = self.data_sgp30_total_voc = 0

            self.press_act = 1
            self.led_act = 0
            self.the_rgb = (0, 0, 0)

            self.led_brightness_1 = (
                (0, 0, 0, 0, 0), # (0.21, 0.21, 0.21, 0.21, 0.21),
                (0, 0, 0, 0, 0), # (0.09, 0.21, 0.18, 0.12, 0.09),
                (0, 0, 0, 0, 0), # (0.09, 0.21, 0.18, 0.12, 0.09),
                (0.21, 0.18, 0.15, 0.12, 0.09),
                (0.21, 0.18, 0.15, 0.12, 0.09),
                (0.09, 0.12, 0.15, 0.18, 0.21))

            self.led_brightness_2 = 0

            self.the_elements = ("time", "temperature", "humidity", "eCO2", "TVOC", "VOC IAQ")

            self.the_elements_range = (
                (600, 1200, 1800, 2400),
                (10, 16, 28, 35),
                (20, 40, 60, 90),
                (500, 1000, 1600, 2000),
                (120, 220, 660, 2200),
                (20, 40, 60, 80))

            self.the_elements_palette_1 = (
                ((232, 129, 127), (195, 114, 124), (141, 82, 115), (90, 51, 110), (49, 31, 98)),
                (
                    ((0, 0, 255), (0, 100, 255)),
                    ((0, 200, 255), (0, 255, 255)),
                    ((0, 255, 0), (100, 255, 0)),
                    ((255, 255, 0), (255, 200, 0)),
                    ((255, 100, 0), (255, 0, 0))
                ),
                (
                    ((255, 100, 0), (255, 0, 0)),
                    ((255, 255, 0), (255, 200, 0)),
                    ((0, 255, 0), (100, 255, 0)),
                    ((0, 200, 255), (0, 255, 255)),
                    ((0, 0, 255), (0, 100, 255))
                ),
                ((0, 255, 0), (128, 255, 0), (255, 255, 0), (255, 128, 0), (255, 0, 0)),
                ((0, 255, 0), (128, 255, 0), (255, 255, 0), (255, 128, 0), (255, 0, 0)),
                ((255, 0, 0), (255, 128, 0), (255, 255, 0), (128, 255, 0), (0, 255, 0)))

        except (KeyboardInterrupt, SystemExit):
            self.unicornhatmini.clear()
            self.button_a.close()
            self.button_b.close()
            self.button_x.close()
            self.button_y.close()
            print("*** Button close ***")

        except Exception as e:
            print("*** ERROR init: {0} ***".format(str(e)))
            raise
        else: self.fn_thread_go()

    def fn_rv3028(self):
        while True:
            self.rtc_now = self.rtc.get_time_and_date()
            # print("*** TIME DATE *** {:02d}:{:02d}:{:02d} *** {:02d}/{:02d}/{:02d} ***".format(self.rtc_now.hour, self.rtc_now.minute, self.rtc_now.second, self.rtc_now.day, self.rtc_now.month, self.rtc_now.year))
            time.sleep(1)

    def fn_bme680(self):

        def __bme680_comfort():
            # BETA

            temp = int(self.bme680_temperature)
            hum = int(self.bme680_humidity)

            if temp < 20 and hum < 30: print("__bme680_comfort 1 *** The air is dry, unhappy / L'aria è secca, infelice")
            elif temp < 20 and 30 <= hum <= 60: print("__bme680_comfort 2 *** Slightly cool and moist, moderate comfort / Leggermente fresco e umido, comfort moderato")
            elif temp < 20 and hum > 60: print("__bme680_comfort 3 *** Air-cooled, comfortable in general / Raffreddato ad aria, confortevole in generale")

            elif 20 <= temp <= 24 and hum < 30: print("__bme680_comfort 4 *** The air is dry, unhappy / L'aria è secca, infelice")
            elif 20 <= temp <= 24 and 30 <= hum <= 60: print("__bme680_comfort 5 *** Fresh and comfortable, feeling great / Fresco e confortevole, sentirsi benissimo")
            elif 20 <= temp <= 24 and hum > 60: print("__bme680_comfort 6 *** Air-cooled, comfortable in general / Raffreddato ad aria, confortevole in generale")

            elif temp > 24 and hum < 30: print("__bme680_comfort 7 *** Hot and dry, need more water / Caldo e asciutto, serve più acqua")
            elif temp > 24 and 30 <= hum <= 60: print("__bme680_comfort 8 *** Hot and dry, need more water / Caldo e asciutto, serve più acqua")
            elif temp > 24 and hum > 60: print("__bme680_comfort 9 *** Hot and humid, poor comfort / Caldo e umido, scarso comfort")

            else: print("__bme680_comfort 10 *** NO DATA!")

        def __bme680_iaq():
            hum = self.bme680_humidity
            gas_bme = self.bme680_gas
            gas_offset = self.bme680_gas_baseline - gas_bme
            hum_offset = hum - self.bme680_humidity_baseline
            if hum_offset > 0:
                hum_score = (100 - self.bme680_humidity_baseline - hum_offset)
                hum_score /= (100 - self.bme680_humidity_baseline)
                hum_score *= (self.bme680_humidity_weighting * 100)
            else:
                hum_score = (self.bme680_humidity_baseline + hum_offset)
                hum_score /= self.bme680_humidity_baseline
                hum_score *= (self.bme680_humidity_weighting * 100)
            if gas_offset > 0:
                gas_score = (gas_bme / self.bme680_gas_baseline)
                gas_score *= (100 - (self.bme680_humidity_weighting * 100))
            else:
                gas_score = 100 - (self.bme680_humidity_weighting * 100)
            self.bme680_aqs = hum_score + gas_score
            print("*** BME680 *** temperature {0:.2f} C *** humidity {1:.2f} %RH *** gas {2:.2f} Ohms *** IAQ {3:.2f} ***".format(self.bme680_temperature, self.bme680_humidity, self.bme680_gas, self.bme680_aqs))

        def __bme680_sense():
            while True:
                if self.bme680_data.get_sensor_data():
                    self.bme680_temperature = self.bme680_data.data.temperature
                    self.bme680_humidity = self.bme680_data.data.humidity
                    __bme680_comfort()
                    if self.bme680_data.data.heat_stable:
                        self.bme680_gas = self.bme680_data.data.gas_resistance
                        __bme680_iaq()
                    else: print("*** BME680 partial values ...")
                else: print("*** BME680 not ready ...")
                time.sleep(1)

        def __bme680_burn_in():
            print("*** BME680 burn-in ...")
            gas_burn = ""
            bme680_burn_data = []
            self.bme680_start_time = time.time()
            # self.bme680_end_time = self.bme680_start_time + self.bme680_burn_in_time
            while self.bme680_curr_time - self.bme680_start_time < self.bme680_burn_in_time:
                self.bme680_curr_time = time.time()
                if self.bme680_data.get_sensor_data() and self.bme680_data.data.heat_stable:
                    self.burn_in_mode = 1
                    gas_burn = self.bme680_data.data.gas_resistance
                    bme680_burn_data.append(gas_burn)
                    if len(bme680_burn_data) > 60: bme680_burn_data = bme680_burn_data[-60:]
                    else: pass
                    # print("*** BME680 *** gas {0:.2f} Ohms ***".format(gas_burn))
                    time.sleep(1)
                else:
                    self.burn_in_mode = 0
                    print("*** BME680 not ready ...")
            else:
                self.bme680_gas_baseline = sum(bme680_burn_data[-60:]) / 60.0
                self.burn_in_mode = 2
                del gas_burn
                del bme680_burn_data[:]
                del bme680_burn_data
                bme680_burn_data = {"bme680": []}
                # print("\n*** BME680 baseline *** gas {0:.2f} Ohms *** humidity {1:.2f} %RH ***".format(self.bme680_gas_baseline, self.bme680_humidity_baseline))
                __bme680_sense()

        __bme680_burn_in()

    def fn_sgp30(self):
        # self.sgp30.command('set_baseline', (0xFECA, 0xBEBA)) # (0x8973, 0x8AAE)
        self.sgp30.start_measurement()
        command_time_1 = command_time_2 = 0
        # sgp30_baseline = []
        # print(["*** SGP30 *** old baseline {:02x} ***".format(n) for n in self.sgp30.command('get_baseline')])
        while True:
            data_sgp30 = self.sgp30.get_air_quality()
            self.data_sgp30_equivalent_co2 = data_sgp30.equivalent_co2
            self.data_sgp30_total_voc = data_sgp30.total_voc
            # print("*** SGP30 *** eCO2 {0} ppm *** TVOC *** {1} ppb ***".format(self.data_sgp30_equivalent_co2, self.data_sgp30_total_voc))
            command_time_1 += 1
            command_time_2 += 1
            if command_time_1 == 360: # 1 ORA = 3600
                # sgp30_baseline = self.sgp30.command('get_baseline') # CO2, TVOC
                # self.sgp30.command('set_baseline', (sgp30_baseline[1], sgp30_baseline[0])) # TVOC, CO2 REVERSE ORDER
                # print(["*** SGP30 *** new baseline {:02x} ***".format(n) for n in self.sgp30.command('get_baseline')])
                command_time_1 = 0
            else: pass
            if command_time_2 == 180:
                if self.bme680_humidity > 0 and self.bme680_temperature > 0:
                    hum = self.bme680_humidity
                    temp = self.bme680_temperature
                    absolute_hum = int(1000 * 216.7 * (hum / 100 * 6.112 * math.exp(17.62 * temp / (243.12 + temp))) / (273.15 + temp))
                    self.sgp30.command('set_humidity', [absolute_hum])
                    print("*** SGP30 *** set humidity ...")
                else: pass
                command_time_2 = 0
            else: pass
            time.sleep(1)

    def fn_current_value(self, element_arg_1 = "", element_arg_2 = 0, element_arg_3 = ""):
        ''' message_1 = "{}".format(element_arg_1) # element_arg_1[:5]
        message_2 = "{}".format(element_arg_2)
        message_3 = "{}".format(element_arg_3) '''
        print(f"*** {element_arg_1} {element_arg_2} {element_arg_3} ***")

        range_limits = self.the_elements_range[self.button_mode]
        range_limits_len = len(range_limits)

        self.the_rgb = self.the_elements_palette_1[self.button_mode][0]
        self.led_brightness_2 = self.led_brightness_1[self.button_mode][0]

        for j in range(range_limits_len):
            if int(element_arg_2) > range_limits[j]:
                self.the_rgb = self.the_elements_palette_1[self.button_mode][j + 1]
                self.led_brightness_2 = self.led_brightness_1[self.button_mode][j + 1]
            else: pass

    def fn_led_1(self):
        led_rgb_2 = [0, 0, 0]

        def __next_colour(the_rgb):
            self.led_act = 1

            while len(self.the_rgb) == 2 and led_rgb_2[0] != the_rgb[0] or led_rgb_2[1] != the_rgb[1] or led_rgb_2[2] != the_rgb[2]:

                if led_rgb_2[0] > the_rgb[0]: led_rgb_2[0] -= 1
                elif led_rgb_2[0] < the_rgb[0]: led_rgb_2[0] += 1
                else: pass

                if led_rgb_2[1] > the_rgb[1]: led_rgb_2[1] -= 1
                elif led_rgb_2[1] < the_rgb[1]: led_rgb_2[1] += 1
                else: pass

                if led_rgb_2[2] > the_rgb[2]: led_rgb_2[2] -= 1
                elif led_rgb_2[2] < the_rgb[2]: led_rgb_2[2] += 1
                else: pass
                    
                self.unicornhatmini.set_all(led_rgb_2[0], led_rgb_2[1], led_rgb_2[2])
                self.unicornhatmini.show()

            self.led_act = 0

        led_cur_width = led_brightness_3 = 0
        led_rgb = [0, 0, 0]
        i = 0.00
        
        load_line = int(self.bme680_burn_in_time / 17) + 1

        for x in range(0, 17):
            for y in range(0, 7):
                self.unicornhatmini.set_pixel(x, y, 255, 255, 255)
            if self.burn_in_mode == 0:
                while self.burn_in_mode == 0: pass
                else: pass
            elif self.burn_in_mode == 2: load_line = 0.5
            else: pass
            self.unicornhatmini.show()
            print("*** ", 17 - x)
            time.sleep(load_line) # time.sleep(0.5 / 17)

        self.unicornhatmini.clear()

        while True:
            if len(self.the_rgb) == 3:
                while len(self.the_rgb) == 3 and i <= 10: # for i in range(0, 10, 1):
                    i += 0.50
                    if led_rgb == self.the_rgb and led_brightness_3 == self.led_brightness_2:
                        if led_brightness_3 == 0: led_cur_width = 0.2
                        elif 0.09 <= led_brightness_3 <= 0.15: led_cur_width = i / 10.0
                        else: led_cur_width = i / 30.0
                        self.unicornhatmini.set_brightness(led_cur_width)
                        self.unicornhatmini.set_all(led_rgb[0], led_rgb[1], led_rgb[2])
                        self.unicornhatmini.show()
                        time.sleep(led_brightness_3)
                    else:
                        # buttonshim.set_pixel(0, 0, 0)
                        # buttonshim.set_brightness(0)
                        led_rgb = self.the_rgb
                        led_brightness_3 = self.led_brightness_2
                        break
                else:
                    while len(self.the_rgb) == 3 and i >= 1: # for i in range(10, 0, -1):
                        i -= 0.50
                        if led_brightness_3 == 0: led_cur_width = 0.2
                        elif 0.09 <= led_brightness_3 <= 0.15: led_cur_width = i / 10.0
                        else: led_cur_width = i / 30.0
                        self.unicornhatmini.set_brightness(led_cur_width)
                        self.unicornhatmini.set_all(led_rgb[0], led_rgb[1], led_rgb[2])
                        self.unicornhatmini.show()
                        time.sleep(led_brightness_3)
                    else: pass
            elif len(self.the_rgb) == 2:
                print("****** fn_led_1 ELSE")
                for c_1 in range(0, 2, 1):
                    if len(self.the_rgb) == 2 and self.led_act == 0:
                        __next_colour((self.the_rgb[c_1][0], self.the_rgb[c_1][1], self.the_rgb[c_1][2]))
                    else: pass
                for c_2 in reversed(range(0, 2, 1)):
                    if len(self.the_rgb) == 2 and self.led_act == 0:
                        __next_colour((self.the_rgb[c_2][0], self.the_rgb[c_2][1], self.the_rgb[c_2][2]))
                    else: pass
            else: pass

    def fn_button_pressed(self):
        while True:

            if self.burn_in_mode == 2:

                if self.button_a.is_pressed:
                    self.button_a.wait_for_release(timeout = 1)
                    self.press_act = 1
                    self.button_mode -= 1

                elif self.button_b.is_pressed:
                    self.button_b.wait_for_release(timeout = 1)
                    self.press_act = 1
                    self.button_mode += 1

                elif self.button_x.is_pressed:
                    self.button_x.wait_for_release(timeout = 1)
                    self.press_act = 0
                    self.unicornhatmini.set_brightness(0)
                    self.unicornhatmini.clear()
                    self.the_rgb = (0, 0, 0)

                elif self.button_y.is_pressed:
                    self.button_y.wait_for_release(timeout = 1)
                    self.press_act = 0
                    self.unicornhatmini.set_brightness(0)
                    self.unicornhatmini.clear()
                    self.the_rgb = (0, 0, 0)
                    call("sudo shutdown -P -t 0.3", shell=True) # call("sudo shutdown -P -t 1", shell=True)
                    sys.exit(0)

                else: pass

                self.button_mode %= len(self.the_elements)

            else:
                self.press_act = 1
                self.button_mode = 0

            if self.button_mode == 0 and self.press_act == 1: self.fn_current_value(str("{0:02d}".format(self.rtc_now.day) + "." + "{0:02d}".format(self.rtc_now.month) + "." + "{0:02d}".format(self.rtc_now.year)[-2:]), int("{0:02d}".format(self.rtc_now.hour) + "{0:02d}".format(self.rtc_now.minute)), "")

            elif self.button_mode == 1 and self.press_act == 1: self.fn_current_value("TEMP", int(self.bme680_temperature), "C")  # self.fn_current_value("TEMP", round(self.bme680_temperature, 1), "C")

            elif self.button_mode == 2 and self.press_act == 1: self.fn_current_value("RH", int(self.bme680_humidity), "%")

            elif self.button_mode == 3 and self.press_act == 1: self.fn_current_value("eCO2", int(self.data_sgp30_equivalent_co2), "ppm")

            elif self.button_mode == 4 and self.press_act == 1: self.fn_current_value("TVOC", int(self.data_sgp30_total_voc), "ppb")

            elif self.button_mode == 5 and self.press_act == 1: self.fn_current_value("VOC IAQ", int(self.bme680_aqs), "%")

            else: pass

            time.sleep(0.1)

    def fn_thread_go(self): # non-random ordering
        t0 = Thread(target = self.fn_rv3028)
        t0.setDaemon(True)
        t0.start()

        t1 = Thread(target = self.fn_bme680)
        t1.setDaemon(True)
        t1.start()

        t2 = Thread(target = self.fn_sgp30)
        t2.setDaemon(True)
        t2.start()

        t3 = Thread(target = self.fn_led_1)
        t3.setDaemon(True)
        t3.start()

        t4 = Thread(target = self.fn_button_pressed)
        t4.setDaemon(False) # BUTTON FN NO DAEMON!
        t4.start()

if __name__ == "__main__":
    try: DIYzenIAQ()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
    except Exception as e:
        print("*** ERROR: {0} ***".format(str(e)))
        print("*** RELOAD ...")
        os.execl(sys.executable, "python3", __file__, *sys.argv[1:])
        sys.exit(0)
