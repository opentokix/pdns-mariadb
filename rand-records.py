#!/usr/bin/env python3 

import powerdns 
import logging 
import random
import string
from datetime import date
from time import sleep
import sys
import concurrent.futures 
import click
import mysql.connector


log = logging.getLogger("bulkrecords")
log.setLevel(logging.INFO)
fh = logging.FileHandler("bulkrecords.log")
ch = logging.StreamHandler()

ch.setLevel(logging.ERROR)
fh.setLevel(logging.INFO)

log.addHandler(fh)
log.addHandler(ch)
log.info("START:")
log.error("Starting bulk add of records")

def create_connection(host_name, user_name, user_password):
  connection = None
  try:
    connection = mysql.connector.connect(host=host_name, user=user_name, passwd=user_password, database='pdns')
  except: 
    print("Unable to connect to db.")
  return connection


def rand_ipv4():
  first = random.randint(1, 255)
  second = random.randint(0, 255)
  third = random.randint(0, 255)
  fourth = random.randint(0, 255)
  return f"{first}.{second}.{third}.{fourth}"

def rand_string(num=8):
  letters = string.ascii_lowercase
  return ''.join(random.choice(letters) for i in range(num))

def add_rand_records(api, zonename, num_records):
  logging.error("Entering add rand records!")
  zone = api.servers[0].get_zone(zonename)
  logging.error(zone.details)
  records = []
  for i in range(num_records):
    r = rand_string()
    ip = rand_ipv4()
    zone.create_records([powerdns.RRSet(r, 'A', [(ip, False)])])

def add_rand_record_db(cur, num_records=1):
  cursor = con.cursor()
  domain_id = get_random_zone_from_api(con)
  for i in range(num_records):
    r = rand_string()
    ip = rand_ipv4()

    query = f"""
    INSERT INTO 'records' ('domain_id', 'name', 'type', 'content', 'ttl', 'prio', 'disabled', 'ordername', 'auth')
    VALUES
      ({domain_id}, {r}, 'A', {ip}, '3600', '0', '0', 'NULL', '1');"""
    cursor.execute(query)
  

def get_random_zone_from_db(con):
  cursor = con.cursor()
  query = 'SELECT id FROM domains ORDER BY RAND() LIMIT 1'
  cursor.execute(query)
  return cursor.fetchone()[0]
  
def get_random_zone_from_api(api):
  pass
 
@click.command()
@click.option('--num', '-n', 'numrecords', required=True, help="How many records to add per zone", type=int)
@click.option('--workers', '-w', 'numworkers', required=False, help="Number of workers", show_default=True, default=4, type=int)
@click.option('--zones', '-z', 'zones', required=False, help="How many zones to iter thru.", show_default=True, default=1, type=int)
def main(numrecords, numworkers, zones):
  PDNS_API = "http://172.20.0.3:8081/api/v1"
  PDNS_KEY = "foobar"
  con = create_connection("172.20.0.2", "pdns", "P2RNxOUz" )
  print(get_random_zone_from_db(con))

  # api_client = powerdns.PDNSApiClient(api_endpoint=PDNS_API, api_key=PDNS_KEY)
  # api = powerdns.PDNSEndpoint(api_client)
  # add_rand_records(api, "lombfgoy.com.", 10)
  # with concurrent.futures.ThreadPoolExecutor(max_workers=numworkers) as executor:
  #   for i in range(zones):
  #     executor.submit(add_rand_records, api, "lombfgoy.com.", 10)

if __name__ == "__main__":
  main()
