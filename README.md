# rpi-resc

# 利用 LoRa-WiFi 自適應雙模式山區搜救定位資料傳輸

本項目是論文的實作程式碼，待救者與搜救者設備根據距離不同更改傳輸模式。

## 硬體需求
LoRa: SX1276
GPS: Neo6M

## 軟體/套件需求
請使用Raspberry pi OS，且需要安裝 `Rpi.GPIO` 和 `spidev`

## 前置作業
1. 確保樹梅派已經開啟 SPI 和 Serial(GPS模組)。
2. 搜救者設備必須啟動為 wifi AP 模式，並且從設定本項目中`resc-wifi.conf`、`targ-wifi.conf`中設定 WiFi 內部 IP位址，提供待救者連上。

## 版本
python 3.9.7
## 套件
[pySX127x](https://github.com/mayeranalytics/pySX127x)
## 使用方法
### 待救者
`python ./Target_test.py`
### 搜救者
`python ./Rescuer_test.py`

程式一律從LoRa模式啟動。另外可以依照需求使用`cron`排程或是`systemd`作為機器啟動的服務。

## 參數
`-d` 強制從雙模啟動
`-w` 強制從WiFi模式啟動
`-t` 不會竊換模式

## 開源授權
本項目的 pySX127x 是採用 GNU AGPL 授權。
