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


log = logging.getLogger("bulkzones")
log.setLevel(logging.INFO)
fh = logging.FileHandler("bulkzones.log")
ch = logging.StreamHandler()

ch.setLevel(logging.ERROR)
fh.setLevel(logging.INFO)

log.addHandler(fh)
log.addHandler(ch)
log.info("START:")
log.error("Starting bulk add of zones.")

def rand_ipv4():
  first = random.randint(1, 255)
  second = random.randint(0, 255)
  third = random.randint(0, 255)
  fourth = random.randint(0, 255)
  return f"{first}.{second}.{third}.{fourth}"

def rand_string(num=8):
  letters = string.ascii_lowercase
  return ''.join(random.choice(letters) for i in range(num))

def add_rand_zone(api):
  tlds = ["com", "org", "net", "se"]
  tld = random.choice(tlds)
  domain = rand_string()
  full_name = f"{domain}.{tld}."

  serial = str(date.today().strftime("%Y%m%d00"))
  soa = f"ns0.{full_name} admin.{full_name} {serial} 28800 7200 604800 86400"
  soa_name = f"test.python-powerdns.{full_name}"
  soa_r = powerdns.RRSet(name=full_name,
                        rtype="SOA",
                        records=[(soa, False)],
                        ttl=86400)
  try:                        
    zone = api.servers[0].create_zone(name=full_name, kind="Native", rrsets=[soa_r], nameservers=[f"ns1.{full_name}", f"ns2.{full_name}"])
  except:
    log.error("Error in api connection")
    log.error(sys.exc_info()[0])

  log.info(f"{zone},{str(zone.details)}")

@click.command()
@click.option('--num', '-n', 'numzones', required=True, help="number of random zones to add", type=int)
@click.option('--workers', '-w', 'numworkers', required=False, help="Number of workers", show_default=True, default=4, type=int)
def main(numzones, numworkers):
  PDNS_API = "http://172.20.0.4:8081/api/v1"
  PDNS_KEY = "foobar"

  api_client = powerdns.PDNSApiClient(api_endpoint=PDNS_API, api_key=PDNS_KEY)
  api = powerdns.PDNSEndpoint(api_client)
  with concurrent.futures.ThreadPoolExecutor(max_workers=numworkers) as executor:
    for i in range(numzones):
      executor.submit(add_rand_zone, api)

if __name__ == "__main__":
  main()
