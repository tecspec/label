import sys
import json
import pymysql
import xml.etree.ElementTree as ET

def get_xml(filename):
    tree = ET.parse('schema.xml')
    root = tree.getroot()
    text_node = root[1][0][0][0][0]
    text_node.set('value', "This is a test")
    print(text_node.attrib)
    tree.write('output.xml')

get_xml('schema.xml')

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
        sql = "SELECT * FROM units"
        print(sql) 
        cursor.execute(sql)
        result = cursor.fetchone()
        print(result)
	
finally:
    connection.close()
