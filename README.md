# A Do It Yourself zen Indoor Air Quality monitor

`#DIYzenIAQ` is a DIY Carbon Dioxide (CO2) and Volatile Organic Compounds (VOC) meter, an accurate indoor air quality monitor that helps to focus on breathing.

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
* [Pimoroni BME680 Breakout](https://shop.pimoroni.com/products/bme680-breakout)
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
sudo pip3 install --upgrade setuptools
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

After **6 minutes** of sensors burn-in, it is possible to interact with the buttons:

* **A**: LEDs _ON_ and scroll _UP_ the list of values
* **B**: LEDs _ON_ and scroll _DOWN_ the list of values
* **X**: LEDs _OFF_
* **Y**: safe shutdown

## WIP

- [ ] ...
