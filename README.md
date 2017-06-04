# Python automation for motorized curtains

## Sun events calculator
Tool allows to calculate sun events like sunrise, sunset, twilight in a specified location on the earth on a specified date. Here is used equation from [wikipedia](https://en.wikipedia.org/wiki/Sunrise_equation).

## Curtain planner
Tool is used to open/close curtains at some specified time of the day. It may be fixed time or time provided by the sun events calculator. This script should be executed at the begining of every day. For example at 2:00 am. I use "cron" to execute it. Script creates planned tasks using "at" utility. A task is a MQTT message. I use mosquitto server in my smart home system as a communication layer.

## 433RF-mqtt binding
Tool serves for translation of MQTT messages into RC signals. To send RC signals it calles RFCodeSender utility from [RF433Mhz](https://github.com/denmatfoton/RF433Mhz). Devices are described in the XML file.
