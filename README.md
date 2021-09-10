# A Do It Yourself zen Indoor Air Quality monitor

`#DIYzenIAQ` is a DIY Carbon Dioxide (CO2) and Volatile Organic Compounds (VOC) meter, an accurate indoor air quality monitor that helps to focus on breathing.

> The idea is to encourage to live in healthy environments, and as soon as possible, stop, relax and focus on breathing.

[Learn more about #DIYzenIAQ](https://work.saraceni.org/airquality/?lang=en)

![#DIYzenIAQ a Do It Yourself zen Indoor Air Quality monitor](https://work.saraceni.org/airquality/img/gallery/diyzeniaq-unicorn-hat-mini-github.jpg)

## Measurement values

- [x] Date and time
- [x] Temperature
- [x] Humidity
- [ ] Apparent temperature (Heat Index)
- [x] eCO2
- [x] TVOC
- [x] VOC IAQ (% Indoor Air Quality)
- [ ] Total index (comfort and pollutants for zen mode)

## Components

* [Raspberry Pi 1 Model A+](https://www.raspberrypi.org/products/raspberry-pi-1-model-a-plus/)
* [Pimoroni HAT Hacker HAT](https://shop.pimoroni.com/products/hat-hacker-hat)
* [Pimoroni Unicorn HAT Mini](https://shop.pimoroni.com/products/unicorn-hat-mini)
* [Pimoroni Breakout Garden Mini (I2C)](https://shop.pimoroni.com/products/breakout-garden-mini-i2c)
* [Pimoroni BME680 Breakout](https://shop.pimoroni.com/products/bme680-breakout) / [Pimoroni BME688 4-in-1 Air Quality Breakout](https://shop.pimoroni.com/products/bme688-breakout)
* [Pimoroni SGP30 Air Quality Sensor Breakout](https://shop.pimoroni.com/products/sgp30-air-quality-sensor-breakout)
* [Pimoroni RV3028 Real-Time Clock](https://shop.pimoroni.com/products/rv3028-real-time-clock-rtc-breakout)
* [3 Totem L-twisted bracket](https://totemmaker.net/product/l-twisted-bracket-20-pack/)
* [3 Totem L-twisted mirror bracket](https://totemmaker.net/product/l-twisted-mirror-bracket-20-pack/)
* [2 Totem Plastic boards 30 x 100 mm](https://totemmaker.net/product/boards-10-pack/)
* Flat copper heatsink and modified Suptronics Cooling Fan Expansion Board X728-A1
* GPIO Booster Header
* Nylon nut, bolt and spacer M2.5 / M3
* Right angle microUSB cable

## Dependencies & installation

* Raspberry Pi OS Buster
* Python 3.7 or later

```shell
sudo apt-get install python3-pip
sudo pip3 install setuptools
sudo pip3 install smbus
sudo pip3 install smbus2
sudo pip3 install unicornhatmini
sudo pip3 install bme680
sudo pip3 install pimoroni-sgp30
sudo pip3 install rv3028
```

## Use & button commands

```shell
sudo python3 diyzeniaq.py
```

After **6 minutes** of sensors burn-in (in a healthy environment, previously ventilated) it is possible to interact with the buttons:

* **A**: LEDs _ON_ and scroll _UP_ the list of values
* **B**: LEDs _ON_ and scroll _DOWN_ the list of values
* **X**: LEDs _OFF_
* **Y**: safe shutdown

## References

* [Bosch Sensortec BME680](https://www.bosch-sensortec.com/products/environmental-sensors/gas-sensors/bme680/) / [BME688](https://www.bosch-sensortec.com/products/environmental-sensors/gas-sensors/bme688/) has been developed to detect exhaled human breath. It measures the concentration of Volatile Organic Compoundss (VOCs) and outputs an index of air quality (IAQ).
* [Sensirion SGP30](https://www.sensirion.com/en/environmental-sensors/gas-sensors/sgp30/) is a gas sensor that can detect a wide range of Volatile Organic Compoundss (VOCs) and an equivalent carbon dioxide (CO2eq)
* [Micro Crystal RV-3028](https://www.microcrystal.com/en/products/real-time-clock-rtc-modules/rv-3028-c7/) is an extreme low power and highly accurate real-time clock / calendar module.
* [Air quality, COVID-19 and sensing solutions](https://www.bosch-sensortec.com/news/how-sensing-solutions-help-to-fight-against-covid-19.html)
* [Correct ventilation helps to prevent virus transmission](https://www.sensirion.com/en/environmental-sensors/indoor-air-quality/correct-ventilation-helps-to-reduce-the-risk-of-virus-transmission/)
