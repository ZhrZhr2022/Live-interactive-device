# Live-interactive-device

WiFiClient.ino是arduino程序，arduino使用的是带有esp8266的板子，可以进行网络通信。（使用智能配网，可以用微信小程序直接连接网络，连接一次即可，连接成功后会保存到EEPROM）

espclient.py 是电脑上与arduino通信的程序。 （加上了清除WIFI账号密码的功能，方便切换网络）

android_client是用安卓手机与arduino通信的程序。（测试版，功能简单，打开软件后点击屏幕即可作出反应）。

也提供了生成好的exe文件和apk文件。
