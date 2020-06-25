import json
import pprint
import sys

from common.guider import GuiderInstance, RequestManager
from influxdb import InfluxDBClient


def get_data_by_command(target_addr, request_id, cmd):
    result = dict(result=0, data=dict(), errMsg='')
    pipe = None
    if cmd is None or cmd is '' or target_addr is None or target_addr is '':
        result['result'] = -1
        result['errorMsg'] = 'Required data missing'
        sys.exit(0)
    try:
        RequestManager.add_request(request_id)
        GuiderInstance.set_network_manager(target_addr)
        pipe = GuiderInstance.get_command_pipe(target_addr, cmd)
        while RequestManager.get_request_status(request_id):
            str_pipe = pipe.getData()
            if not str_pipe:
                break
            result['data'] = str_pipe
            try:
                result['data'] = json.loads(result['data'])
                pprint.pprint(result)
                insert_db(result['data'])
            except Exception as error:
                print(error)
                continue
        pipe.close()
        stop_command_run(request_id)
    except Exception as err:
        print(err)
        if pipe:
            pipe.close()
        stop_command_run(request_id)


def stop_command_run(request_id):
    result = dict(result=0, data='stop success', errMsg='')
    if RequestManager.get_request_status(request_id):
        RequestManager.stop_request(request_id)
    else:
        result['result'] = -1
        result['errMsg'] = 'stop failed'


def setup_db(host, port):
    user = config['influxDBClientConfig']['user']
    password = config['influxDBClientConfig']['password']
    db_name = config['influxDBClientConfig']['database']
    db_user = config['influxDBClientConfig']['db_user']
    db_user_password = config['influxDBClientConfig']['db_password']

    client = InfluxDBClient(host, port, user, password, db_name)

    if not {'name': db_name} in client.get_list_database():
        client.create_database(db_name)
        client.create_retention_policy('awesome_policy', config['influxDBClientConfig']['retention_policy'], 1,
                                       default=True)
    client.switch_user(db_user, db_user_password)

    return client


def insert_db(guider_data):
    influx_data = list()
    for super_key in guider_data.keys():
        json_body = dict()
        json_body['tags'] = dict()
        json_body['tags']['host'] = config['tags']['host']
        json_body['tags']['region'] = config['tags']['region']
        json_body['time'] = guider_data['utctime']
        json_body['measurement'] = super_key
        json_body['fields'] = dict()
        if super_key == "cpu":
            json_body['fields']['idle'] = guider_data[super_key]['idle']
            json_body['fields']['iowait'] = guider_data[super_key]['iowait']
            json_body['fields']['irq'] = guider_data[super_key]['irq']
            json_body['fields']['kernel'] = guider_data[super_key]['kernel']
        elif super_key == "mem":
            json_body['fields']['anon'] = guider_data[super_key]['anon']
            json_body['fields']['available'] = guider_data[super_key]['available']
            json_body['fields']['cache'] = guider_data[super_key]['cache']
            json_body['fields']['kernel'] = guider_data[super_key]['kernel']
        elif super_key == "net":
            json_body['fields']['inbound'] = guider_data[super_key]['inbound']
            json_body['fields']['outbound'] = guider_data[super_key]['outbound']
        elif super_key == "storage":
            json_body['fields']['free'] = guider_data[super_key]['total']['free']
            json_body['fields']['usage'] = guider_data[super_key]['total']['usage']
        # TODO parsing each process and saving to influxdb
        elif super_key == "process":
            pass
        else:
            continue
        if len(json_body["fields"]) > 0:
            influx_data.append(json_body)
    client.write_points(influx_data)


if __name__ == '__main__':
    global config
    global client
    with open('./visualization.conf', 'r') as config_file:
        config = json.load(config_file)
    try:
        client = setup_db(config['influxDBClientConfig']['host'], config['influxDBClientConfig']['port'])
        get_data_by_command(sys.argv[1], 1, 'GUIDER reptop -Q')
    except Exception as e:
        print(e)
