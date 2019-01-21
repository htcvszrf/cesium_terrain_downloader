#!/usr/bin/env python
# coding:utf-8

import json
import logging
from PIL import Image

height = 2048
width  = height*2

def print_requests():
    with open("layer.json", "r") as layerjson:
        layerObj = json.load(layerjson)
        maxzoom = int(layerObj['maxzoom'])
        minzoom = int(layerObj['minzoom'])

    for i in range(minzoom, maxzoom + 1):
        bitmap = [0 for n in range(width * height)]
        for j in range(0, len(layerObj['available'][i])):
            startX = int(layerObj['available'][i][j]['startX'])
            startY = int(layerObj['available'][i][j]['startY'])
            endX = int(layerObj['available'][i][j]['endX'])
            endY = int(layerObj['available'][i][j]['endY'])
            calc_pixel_map(i, startX, endX, startY, endY, bitmap)
            # print 'zoom: [%s], nrange: [%s]'%(i, len(layerObj['available'][i]))
        print_image(i, bitmap)

def print_image(zoom, bitmap):
    img = Image.new("RGBA", (width, height))
    for x in range(width):
        for y in range(height):
            if bitmap[x*height+y] == 1:
              img.putpixel((x, height-y-1),(255, 0, 0, 100))
    # img.save("global_%s.png"%zoom, 'png')

    world = Image.open("world.png")

    Image.blend(world, img, 0.3).save("global_%s.png"%zoom, 'png')

def calc_pixel_map(zoom, startX, endX, startY, endY, bitmap):
    rate = float(height)/2**zoom

    minX = int(startX * rate)
    maxX = int((endX + 1) * rate) - 1
    maxX = max(maxX, minX)

    minY = int(startY * rate)
    maxY = int((endY + 1) * rate) - 1
    maxY = max(maxY, minY)

    print zoom, minX, maxX, minY, maxY

    for x in range(minX, maxX + 1):
        for y in range(minY, maxY + 1):
            bitmap[x*height+y] = 1
def main():

    try:
        print_requests()
    except BaseException as e:
        logging.exception(e)

main()
