from flask import Flask, current_app, request, render_template, url_for, jsonify
from subprocess import call
import sys
import math
import time
import argparse
import json
import pymysql
import xml.etree.ElementTree as ET

app = Flask(__name__, static_url_path='')

def create_xml_file(data):
    ET.register_namespace('', 'http://www.bradycorp.com/printers/bpl')
    serial_number_string = str(data['serial_number'])
    return_piping_string = str(data['return_piping_type'])
    supply_piping_string = str(data['supply_piping_type'])
    passthrough_string = get_pass_value(data)
    air_value = get_air_value(data)
    address_value = get_address_value(data)
    tree = ET.parse('test.xml')
    root = tree.getroot()
    labels = root[1][0]
    unit_tag = labels[2][1][0]
    bay_risers = labels[4][1][0]
    return_pipe = labels[6][1][0]
    supply_pipe = labels[8][1][0]
    air = labels[10][1][0]
    passthrough = labels[12][1][0]
    address = labels[14][1][0]
    serial_number = labels[15][0][0]
    binaryaddr = '{0:08b}'.format(int(address_value))
    if binaryaddr[7] == '0':
       labels[16].set('fill', "solid")
       #print(labels[16].nodeValue)
    else:
       labels[17].set('fill', "solid")
    if binaryaddr[6] == '0':
       labels[18].set('fill', "solid")
    else:
       labels[19].set('fill', "solid")
    if binaryaddr[5] == '0':
       labels[20].set('fill', "solid")
    else:
       labels[21].set('fill', "solid")
    if binaryaddr[4] == '0':
       labels[22].set('fill', "solid")
    else:
       labels[23].set('fill', "solid")
    if binaryaddr[3] == '0':
       labels[24].set('fill', "solid")
    else:
       labels[25].set('fill', "solid")
    if binaryaddr[2] == '0':
       labels[26].set('fill', "solid")
    else:
       labels[27].set('fill', "solid")
    if binaryaddr[1] == '0':
       labels[28].set('fill', "solid")
    else:
       labels[29].set('fill', "solid")
    if binaryaddr[0] == '0':
       labels[30].set('fill', "solid")
    else:
       labels[31].set('fill', "solid")
    unit_tag.set('value', data['unit_tag'])
    bay_risers.set('value', data['bay'])
    return_pipe.set('value', return_piping_string)
    supply_pipe.set('value', supply_piping_string)
    air.set('value', air_value)
    passthrough.set('value', passthrough_string)
    address.set('value', address_value)
    serial_number.set('value', serial_number_string)
    filename = './xml_files/output-{}.xml'.format(serial_number_string)
    tree.write(filename)
    return filename

def get_address_value(data):
    return str(int(data['unit_tag'][5:7]))

def get_air_value(data):
    if data["air_l_?"] == "L":
        return "LEFT"
    else:
        return "RIGHT"

def get_pass_value(data):
    if data["pass_through?"] == "P":
        return "YES"
    else:
        return "NO"


def getConfigFromFile(file):
    db_config_json = open(file)
    db_config_string = db_config_json.read()
    db_config = json.loads(db_config_string)
    db_config['cursorclass'] = pymysql.cursors.DictCursor
    return db_config

def connect_to_database():
    db_config = getConfigFromFile('db-config.json')
    return pymysql.connect(**db_config)

def get_unit_tag():
    connection = connect_to_database()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM units WHERE unit_tag=\"" + unit_tag + "\""
            cursor.execute(sql)
            result = cursor.fetchone()
            return result
    finally:
        connection.close()

def set_unit_tag_timestamp(serial_number, unit_tag):
    connection = connect_to_database()
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE `units` SET `serial_number`='{}' WHERE `unit_tag` = '{}'".format(serial_number, unit_tag)
            print(sql)
            cursor.execute(sql)
        connection.commit()
    finally:
        connection.close()

def get_units():
    connection = connect_to_database()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM units" 
            cursor.execute(sql)
            result = cursor.fetchall()
            return json.dumps(result)
    finally:
        connection.close()

def format_data(data):
    if data:
        data["serial_number"] = math.floor(time.time())
        return data

@app.route("/")
def index():
    return app.send_static_file('index.html')

@app.route("/get-unit-tag-list")
def get_unit_tag_list():
    return get_units()

@app.route("/save-unit-tag-order", methods=["POST"])
def save_unit_tag_list():
    data_json = request.get_json()
    data = format_data(data_json)
    serial_number = str(data['serial_number'])
    unit_tag = str(data['unit_tag'])
    set_unit_tag_timestamp(serial_number, unit_tag)
    filename = create_xml_file(data)
    shell_command_to_print = "cat {} | nc 192.168.2.156 9100".format(filename)
    call([shell_command_to_print], shell=True)
    call([shell_command_to_print], shell=True)
    return "THIS WORKED"
