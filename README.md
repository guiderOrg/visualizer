# Guider Visualizer
Visualizer using Grafana & InfluxDB for Guider

<img width="2498" alt="result_sample" src="https://user-images.githubusercontent.com/38535571/83333366-245f8a00-a2db-11ea-8278-9660828e0902.png">

## Container Run 
#### Version
```
Docker Image: 2.3.0
Ubuntu: 18.04
InfluxDB: 1.7.10
Grafana: 6.6.2
```

#### Run
* Start container
  * Method 1: Use DockerHub
  ```sh
  $ docker pull yoonje/guider-influxdb-grafana
  ```
  ```sh  
  $ docker run --ulimit nofile=66000:66000 \
    -d \
    --name guider-visualization \
    -p 3003:3003 \
    -p 8086:8086 \
  yoonje/guider-influxdb-grafana
  ```
  * Method 2: Build in local environment
  ```sh
  $ git clone https://github.com/guiderOrg/visualizer.git
  ```
  ```sh
  $ docker build -t guider-influxdb-grafana .
  ```
  ```sh  
  $ docker run --ulimit nofile=66000:66000 \
    -d \
    --name guider-visualization \
    -p 3003:3003 \
    -p 8086:8086 \
  guider-influxdb-grafana
  ```
  
* Stop container
```sh
$ docker stop guider-visualization
```
* Restart container
```sh
$ docker start guider-visualization
```

#### Port Forwarding
|Host|Container|Service|
|:---:|:---:|:---:|
|3003|3003|grafana|
|8086|8086|influxdb|

#### Grafana
Open <http://localhost:3003>
```
Username: root
Password: root
```

#### Add data source on Grafana
1. Using the wizard click on `Configuration` -> `Add data source`
2. Select `InfluxDB`
3. Fill remaining fields as follows and click on `Add` without altering other fields
  ```yml
  Url: http://localhost:8086
  Database: guider
  User: guider
  Password: guider
  ```
4. Click Save & Test

#### Import dashboard
1. Using the wizard click on `Create` -> `Import`
2. Upload [Dashbaord](dashboard/Guider_Dashbaord.json) and Click Import

## Guider Visualizer Run
#### Requirements
```
Python >= 3.0
```

#### Install Python Dependencies
It is recommended to use virtualenv.
```shell script
$ pip3 install virtualenv
```
```shell script
$ virtualenv venv 
```
```shell script
$ source ./venv/bin/activate
```
If you don't want to use virtualenv, just run this command.
```sh
$ pip3 install -r requirements.txt
```


#### Run
* First, Run the guider server on the PC to measure performance. Only ports between 50 and 999 are available.
    ```sh
    $ python3 guider.py server -x {PORT}
    ```
* Run visualization client. Only ports between 50 and 999 are available.
    ```sh
    $ python3 visualize.py {guider server IP:PORT}
    ```
