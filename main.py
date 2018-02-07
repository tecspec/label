import sys
import argparse
import json
import pymysql
import xml.etree.ElementTree as ET

parser = argparse.ArgumentParser()
parser.add_argument("--unit_tag")
args = parser.parse_args()
unit_tag = args.unit_tag


ET.register_namespace('', 'http://www.bradycorp.com/printers/bpl')

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

db_config = getConfigFromFile('db-config.json')

connection = pymysql.connect(**db_config)

try:
    with connection.cursor() as cursor:
        sql = "SELECT * FROM units WHERE unit_tag=\"" + unit_tag + "\""
        cursor.execute(sql)
        result = cursor.fetchone()
        get_xml('schema.xml', result['unit_tag'], result['unit_type'])
finally:
    connection.close()
