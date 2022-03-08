# Ryan Tompkins - PaymentWorks Massachusetts Bay Transportation Authority (MBTA) RESTful client API

## Introduction

> This is a Python3 RESTful client that reports the routes and stops in the MBTA

## Installation

> pip install requests

> pip install argparse

## Usage

usage: client.py [-h] [-s ID] [-f FILTER] [-stats]

optional arguments:
  -h, --help            show this help message and exit
  -s ID, -subway ID, -stops ID, -n ID, -name ID, -i ID, -id ID, --id ID
                        Print all stops for the given route name
  -f FILTER, -filter FILTER, --filter FILTER
                        'Light Rail' (type 0) and 'Heavy Rail' (type 1)
  -stats, --stats       Output stops connecting two or more routes and route
                        with most+least stops

> python3 client.py -id RED

> python3 client.py -stops blue

> python3 client.py -name Green-B

> python3 client.py -f 0,1,4

> python3 client.py -stats

## API Endpoints

> https://api-v3.mbta.com/routes​ - lists all the subway lines, commuter-rail lines, bus-lines and ferry-routes

> https://api-v3.mbta.com/stops?route={STOP_ID}​ - lists all the stops for the given route