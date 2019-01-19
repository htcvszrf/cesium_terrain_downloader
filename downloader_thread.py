#!/usr/bin/env python
# coding:utf-8

import sys
import os
import urllib
import json
import gzip
from cStringIO import StringIO
import Queue
import threading
import logging

global access_token, assert_url, exitFlag, passNum, processNum, index
queueLock = threading.Lock()
workQueue = Queue.Queue(5000)
threadList = {}
threads = []

def get_access_token():
  global access_token, assert_url
  user_access_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJiMGRjM2QxYi04ODM2LTQzMDEtOGJmOS1mNDlkY2Q2NjE4MjciLCJpZCI6MjU5LCJpYXQiOjE1MjU5NjYyMDd9.xW9loNLo68KE3ReAHd-Lp73M8qJKhI9vA0wYL-qJX_I'
  endpoint_url = 'https://api.cesium.com/v1/assets/1/endpoint'

  jsonStr = urllib.urlopen(endpoint_url + '?access_token=' + user_access_token).read()
  jsonObj = json.loads(jsonStr)
  access_token = 'access_token=' + jsonObj['accessToken']
  assert_url = jsonObj['url']

def test_get_layer_and_terrain():
  global access_token, assert_url
  layerStr = urllib.urlopen(assert_url + 'layer.json?' + access_token).read()
  # print gzdecode(layerStr)

  fileObject = open('layer.json', 'w')
  fileObject.write(gzdecode(layerStr))
  fileObject.close()

  terrain = urllib.urlopen('https://assets.cesium.com/1/13/12905/5528.terrain?v=1.1.0&' + access_token).read()
  # print terrain
  fileObject = open('test.terrain', 'wb')
  fileObject.write(gzdecode(terrain))
  fileObject.close()

def print_requests():
  global access_token, assert_url, index
  layerStr = urllib.urlopen(assert_url + 'layer.json?' + access_token).read()
  layerObj = json.loads(gzdecode(layerStr))

  # maxzoom = int(layerObj['maxzoom'])
  # minzoom = int(layerObj['minzoom'])
  maxzoom = 13
  minzoom = 13
  for i in range(minzoom, maxzoom + 1):
    # print 'zoom:', i, 'len:', len(layerObj['available'][i])
    for j in range(0, len(layerObj['available'][i])):
      startX = int(layerObj['available'][i][j]['startX'])
      startY = int(layerObj['available'][i][j]['startY'])
      endX = int(layerObj['available'][i][j]['endX'])
      endY = int(layerObj['available'][i][j]['endY'])
      # print '\trange:', j, 'start_x:', startX, 'start_y:', startY, 'end_x:', endX, 'end_y:', endY
      download_terrain_tiles(i, startX, endX, startY, endY)

def download_terrain_tiles(zoom, startX, endX, startY, endY):
  global index, passNum, processNum
  print 'zoom:', zoom, 'start_x:', startX, 'start_y:', startY, 'end_x:', endX, 'end_y:', endY, 'current: ', index - passNum
  sys.stdout.flush()
  for x in range (startX, endX + 1):
    for y in range (startY, endY + 1):
      index += 1
      if index <= passNum:
        pass
      elif index >= (passNum + processNum):
        return
      else:
        queueLock.acquire()
        while workQueue.full():
          queueLock.release()

          for p in threads:
            if p.is_alive() is False:
              print '%s is DEAD, Now RELOAD it.'
              sys.stdout.flush()
              get_access_token()
              threads.remove(p)
              result = threadList.pop(p.name)
              print result
              sys.stdout.flush()
              thread = myThread(result, p.name, workQueue)
              threadList[p.name] = result
              thread.start()
              threads.append(thread)

          queueLock.acquire()
        workQueue.put([zoom, x, y])
        queueLock.release()

class myThread(threading.Thread):
  global exitFlag
  def __init__(self, threadID, name, q):
    threading.Thread.__init__(self)
    self.threadID = threadID
    self.name = name
    self.q = q
  def run(self):
    print "Starting " + self.name
    sys.stdout.flush()
    try:
      process_data(self.name, self.q)
    except BaseException as e:
      logging.exception(e)
    print "Exiting " + self.name
    sys.stdout.flush()

def process_data(threadName, q):
  global access_token, assert_url, exitFlag, passNum
  while not exitFlag:
    queueLock.acquire()
    if not workQueue.empty():
      data = q.get()
      queueLock.release()
      if not os.path.exists('tiles/%s/%s/%s.terrain'%(data[0], data[1], data[2])):
        terrain_url = "%s%s/%s/%s.terrain?v1.1.0&%s"%(assert_url, data[0], data[1], data[2], access_token)
        terrain = urllib.urlopen(terrain_url).read()

        if not os.path.exists('tiles/%s/%s'%(data[0], data[1])):
          os.makedirs('tiles/%s/%s'%(data[0], data[1]))

        fileObject = open('tiles/%s/%s/%s.terrain'%(data[0], data[1], data[2]), 'wb')
        fileObject.write(gzdecode(terrain))
        fileObject.close()
        # print '%s download: %s_%s_%s.terrain is %s'%(threadName, data[0], data[1], data[2], 'done.')
      # else :
        # print '%s download: %s_%s_%s.terrain is %s'%(threadName, data[0], data[1], data[2], 'exists.')
    else:
      queueLock.release()

def gzdecode(data):
  compressedStream = StringIO(data)
  gziper = gzip.GzipFile(fileobj=compressedStream)
  data2 = gziper.read()

  return data2

def main():
  global access_token, assert_url, exitFlag, passNum, processNum, index
  exitFlag = 0
  passNum = 1800000 
  index = 0
  processNum = 31000
  get_access_token()
  # test_get_layer_and_terrain()

  threadCount = 100
  # threadList = ['Thread-1', 'Thread-2']

  for i in range(threadCount):
    thread = myThread(i, "Thread-%s"%(i), workQueue)
    threadList["Thread-%s"%(i)] = i
    thread.start()
    threads.append(thread)

  try:
    print_requests()
  except BaseException as e:
    logging.exception(e)
    exitFlag = 1

  while not workQueue.empty():
    pass

  exitFlag = 1

  for t in threads:
    t.join()

  print "Exiting Main Thread"
  sys.stdout.flush()

main()
