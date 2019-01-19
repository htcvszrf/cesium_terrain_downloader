#!/usr/bin/env python
# coding:utf-8

import os
import urllib
import json
import gzip
from cStringIO import StringIO
import Queue
import threading
import logging
import time

global access_token, assert_url

def get_access_token():
  global access_token, assert_url
  user_access_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJiMGRjM2QxYi04ODM2LTQzMDEtOGJmOS1mNDlkY2Q2NjE4MjciLCJpZCI6MjU5LCJpYXQiOjE1MjU5NjYyMDd9.xW9loNLo68KE3ReAHd-Lp73M8qJKhI9vA0wYL-qJX_I'
  endpoint_url = 'https://api.cesium.com/v1/assets/1/endpoint'

  jsonStr = urllib.urlopen(endpoint_url + '?access_token=' + user_access_token).read()
  jsonObj = json.loads(jsonStr)
  access_token = 'access_token=' + jsonObj['accessToken']
  assert_url = jsonObj['url']

def print_requests():
  global access_token, assert_url
  layerStr = urllib.urlopen(assert_url + 'layer.json?' + access_token).read()
  layerObj = json.loads(gzdecode(layerStr))

  maxzoom = int(layerObj['maxzoom'])
  minzoom = int(layerObj['minzoom'])
  # maxzoom = 1
  # minzoom = 9
  for i in range(minzoom, maxzoom + 1):
    # print 'zoom:', i, 'len:', len(layerObj['available'][i])
    count = 0
    for j in range(0, len(layerObj['available'][i])):
      startX = int(layerObj['available'][i][j]['startX'])
      startY = int(layerObj['available'][i][j]['startY'])
      endX = int(layerObj['available'][i][j]['endX'])
      endY = int(layerObj['available'][i][j]['endY'])
      # print '\trange:', j, 'start_x:', startX, 'start_y:', startY, 'end_x:', endX, 'end_y:', endY
      count += download_terrain_tiles(i, startX, endX, startY, endY)
    print 'zoom: [%s], nrange: [%s], count: [%s]'%(i, len(layerObj['available'][i]), count)

def download_terrain_tiles(zoom, startX, endX, startY, endY):
  # print 'zoom:', zoom, 'start_x:', startX, 'start_y:', startY, 'end_x:', endX, 'end_y:', endY
  count = (endX-startX+1)*(endY-startY+1)
  # print 'zoom: [%s], xrange: [%s-%s], yrange: [%s_%s], count: [%s]'%(zoom, startX, endX, startY, endY, count)
  return count

def gzdecode(data):
  compressedStream = StringIO(data)
  gziper = gzip.GzipFile(fileobj=compressedStream)
  data2 = gziper.read()

  return data2

def main():
  global access_token, assert_url, exitFlag
  exitFlag = 0
  get_access_token()

  try:
    print_requests()
  except BaseException as e:
    logging.exception(e)

main()
