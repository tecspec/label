from flask import Flask, current_app, request, render_template, url_for
import sys
import sys
import argparse
import json
import pymysql
import xml.etree.ElementTree as ET

app = Flask(__name__, static_url_path='')

#parser = argparse.ArgumentParser()
#parser.add_argument("--unit_tag")
#args = parser.parse_args()
#unit_tag = args.unit_tag


#ET.register_namespace('', 'http://www.bradycorp.com/printers/bpl')

def get_xml(filename, unit_tag, unit_type):
    tree = ET.parse('schema.xml')
    root = tree.getroot()
    text_node = root[1][0][0][0][0]
    node_value = unit_tag + ":" + unit_type
    text_node.set('value', node_value)
    print(text_node.attrib)
    tree.write('output.xml')


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

@app.route("/")
def index():
    return app.send_static_file('index.html')

@app.route("/get-unit-tag-list")
def get_unit_tag_list():
    return get_units()
