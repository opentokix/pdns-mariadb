#!/usr/bin/env python3 

import powerdns 
import logging 
import random
import string
import threading
from datetime import date
from time import sleep
import sys

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

def rand_string(num=8):
  letters = string.ascii_lowercase
  return ''.join(random.choice(letters) for i in range(num))

def add_rand_zone(api):
  tlds = ["com", "org", "net", "se"]
  tld = random.choice(tlds)
  domain = rand_string()
  full_name = domain + "." + tld + "."

  serial = str(date.today().strftime("%Y%m%d00"))
  soa = "ns0." + full_name + " admin." + full_name + " " +  serial + " 28800 7200 604800 86400"
  soa_name = "test.python-powerdns." + full_name + "."
  soa_r = powerdns.RRSet(name=full_name,
                        rtype="SOA",
                        records=[(soa, False)],
                        ttl=86400)
  try:                        
    zone = api.servers[0].create_zone(name=full_name, kind="Native", rrsets=[soa_r], nameservers=["ns1." + full_name, "ns2." + full_name])
  except:
    log.error("Error in api connection")
    log.error(sys.exc_info()[0])

  log.info(str(zone) + "," + str(zone.details))

def main():
  PDNS_API = "http://172.20.0.4:8081/api/v1"
  PDNS_KEY = "foobar"

  api_client = powerdns.PDNSApiClient(api_endpoint=PDNS_API, api_key=PDNS_KEY)
  api = powerdns.PDNSEndpoint(api_client)

  for i in range(200):
    threads = []
    for t in range(20):
      t = threading.Thread(target=add_rand_zone, args=(api,))
      threads.append(t)
      t.start()
    sleep(0.5)

if __name__ == "__main__":
    main()