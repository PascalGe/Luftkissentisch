#!/usr/bin/env python

# Luftkissentisch

import pygame
from pygame.locals import *
import time
import sys
import struct
import ctypes
import os.path
import glob
import platform
import math
from math import sqrt
import matplotlib
matplotlib.use('Agg')
import matplotlib.backends.backend_agg as agg
import matplotlib.pyplot as plt

# define input file
device = "kugelstoss.log"
# device = "/dev/input/by-id/usb-Multi_touch_Multi_touch_overlay_device_6F66FA721233-event-if01"


if (platform.machine() == "x86_64"):
    bstr = struct.Struct("I 4x I 4x 2H i")
    print("64 bit architecture")
else:
    bstr = struct.Struct("I I 2H i")
    print("32 bit architecture")


#define some colors
#color    R    G    B
white = (255, 255, 255)
red   = (255,   0,   0)
green = (  0, 255,   0)
blue  = (  0,   0, 255)
black = (  0,   0,   0)
cyan  = (  0, 255, 255)
magenta = (255, 0, 255)
yellow = (255 , 255, 0)
grey = (128,128,128)

#screen size
width = 800
height = 480
size = (width, height)

# frame calibration
fmm = 401./32768.  # factor to resize points -> mm

#Definitions
BtnXlen=100
BtnYlen=60
Btnx = [0,5,5,5,5,5,5,5]
Btny = [0,5,70,135,200,265,330,415]

def main():
    global DISPLAY, FONT, frame, device
    size = (width, height)
    fig = plt.figure(figsize=[11.5, 8], # Inches
                   dpi=60,        # 50 dots per inch, so the resulting buffer is 700x480 pixels
                   )

    pygame.init()
#     DISPLAY = pygame.display.set_mode(size,NOFRAME)
    DISPLAY = pygame.display.set_mode(size)
    Scrn = pygame.Rect(Btnx[0],0,width,height)
    Cnvs = pygame.Rect(BtnXlen+25, 5, height-10,  height-10)
    Btn1 = pygame.Rect(Btnx[1],Btny[1], BtnXlen,BtnYlen)
    Btn2 = pygame.Rect(Btnx[2],Btny[2], BtnXlen,BtnYlen)
    Btn3 = pygame.Rect(Btnx[3],Btny[3], BtnXlen,BtnYlen)
    Btn4 = pygame.Rect(Btnx[4],Btny[4], BtnXlen,BtnYlen)
    Btn5 = pygame.Rect(Btnx[5],Btny[5], BtnXlen,BtnYlen)
    Btn6 = pygame.Rect(Btnx[6],Btny[6], BtnXlen,BtnYlen)
    Btn7 = pygame.Rect(Btnx[7],Btny[7], BtnXlen,BtnYlen)


    #initial state colors for indicators
    state_color1 = cyan
    state_color2 = cyan
    state_color3 = cyan
    state_color4 = cyan
    run = 0
    datfile = newfile("sg*.dat")


    #define font
    FONT = pygame.font.Font(None, 25)
  
    #TODO: Define Labels here
    label_File = FONT.render("Datei", 1, black)
  
    #Background Screen
    pygame.draw.rect(DISPLAY, grey , Scrn)
    #drawing area Canvas
    pygame.draw.rect(DISPLAY, black , Cnvs)
    #shape = pygame.surface.Surface ( ( width, height ) )
  
    #handler.loadFromFile ( "./BtnNorm.png", "Btn" )
    #handler.loadFromFile ( "./BtnPressed.png", "Btn" )
    devopen()
    frame = open(device,"rb")              

    running = True
  
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = 0
        
            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
              
            #if touchscreen pressed
            if event.type == pygame.MOUSEBUTTONDOWN:
                #get position
                pos = pygame.mouse.get_pos()
                state_color1 = state_color2 = state_color3 =cyan
                if Btn1.collidepoint(pos):
                    pygame.draw.rect(DISPLAY, red , Btn1)
                    pygame.display.update()
                    datfile = newfile("sg*.dat")
                    pygame.draw.rect(DISPLAY, cyan , Btn1)
                    labelfile = FONT.render (datfile, 1, blue)
                    #TODO: label_File is defined later!
                    DISPLAY.blit(label_File, (Btnx[1], Btny[1]))
                    DISPLAY.blit(labelfile, (Btnx[1], Btny[1]+30))
                    run = 0
                    pygame.display.update()
                elif Btn2.collidepoint(pos):
                    run += 1
                    pygame.draw.rect(DISPLAY, black, Cnvs)
                    pygame.draw.rect(DISPLAY, green, Btn2)
                    x1lst = []
                    y1lst = []
                    t1lst = []
                    x2lst = []
                    y2lst = []
                    t2lst = []
                    stime =  atime = 0
                    label5 = FONT.render ('Lauf '+str(run), 1, blue)
                    DISPLAY.blit(label5, (Btnx[2], Btny[2]+30))
                    pygame.display.update()
                    frame.close()
                    devopen()
                    frame = open(device,"rb")
                    while (atime < 6e6):
                        (etime,x1,y1,x2,y2) = kugelpos()
                        if (etime == 0): break
                        if (stime == 0): stime = etime
                        atime = etime - stime
                        x1d = int(BtnXlen+25+480./32768*x1)
                        y1d = int(480./32768*y1)
                        x2d = int(BtnXlen+25+480./32768*x2)
                        y2d = int(480./32768*y2)
#                         print "Pos: ",atime,x1,y1,x2,y2,x1d,y1d,x2d,y2d
                        if (x1>0 and y1>0): 
                            pygame.draw.circle(DISPLAY, blue, (x1d, y1d), 2)
                            pygame.display.update()
                            x1lst.append(x1*fmm)
                            y1lst.append(y1*fmm)
                            t1lst.append(1e-6*atime)
                        if (x2>0 and y2>0): 
                            pygame.draw.circle(DISPLAY, red, (x2d, y2d), 2)
                            pygame.display.update()
                            x2lst.append(x2*fmm)
                            y2lst.append(y2*fmm)
                            t2lst.append(1e-6*atime)
                    # hier geht es dann weiter: Koordinaten anzeigen, evtl. ok Button
                    # lfd. Nr anzeigen, Koordinaten abspeichern
                    state_color2 = cyan
                    pygame.display.update()
                    print("Positionen",len(x1lst),len(x2lst))
                elif Btn3.collidepoint(pos):
                    pygame.draw.rect(DISPLAY, red , Btn3)
                    pygame.display.update()
                    fd = open(datfile,"a")
                    for i in range(len(x1lst)):
                        z = '%4i%4i%9.6f%6.1f%6.1f\n' % (run,1,t1lst[i],x1lst[i],y1lst[i])
                        fd.write(z)
                    for i in range(len(x2lst)):
                        z = '%4i%4i%9.6f%6.1f%6.1f\n' % (run,1,t2lst[i],x2lst[i],y2lst[i])
                        fd.write(z)
                    fd.close()
                    pygame.draw.rect(DISPLAY, state_color3 , Btn3)
                    pygame.display.update()
                elif Btn4.collidepoint(pos):
                    fig = plt.figure(figsize=[11.5, 8],dpi=60,)
                    plt.plot(t1lst,x1lst,'.',label='x1(t)')
                    plt.plot(t1lst,y1lst,'.',label='y1(t)')
                    plt.plot(t2lst,x2lst,'.',label='x2(t)')
                    plt.plot(t2lst,y2lst,'.',label='y2(t)')
                    plt.xlabel('t/s')
                    plt.ylabel('pos/mm')
                    plt.title("Ebener Stoss: Position")
                    plt.legend()
                    canvas = agg.FigureCanvasAgg(fig)
                    canvas.draw()
                    renderer = canvas.get_renderer()
                    raw_data = renderer.tostring_rgb()
                    size = canvas.get_width_height()
                    surf = pygame.image.fromstring(raw_data, size, "RGB")
                    DISPLAY.blit(surf, (BtnXlen+10,0))
                    pygame.display.flip()

                elif Btn5.collidepoint(pos):
                    fig = plt.figure(figsize=[11.5, 8],dpi=60,)
                    sl1 = [0]
                    for i in range(len(x1lst)-1):
                        sl1.append(sl1[i]+sqrt((x1lst[i+1]-x1lst[i])**2+(y1lst[i+1]-y1lst[i])**2))
                    sl2 = [0]
                    for i in range(len(x2lst)-1):
                        sl2.append(sl2[i]+sqrt((x2lst[i+1]-x2lst[i])**2+(y2lst[i+1]-y2lst[i])**2))
                    plt.plot(t1lst,sl1,'.',label='s1(t)')
                    plt.plot(t2lst,sl2,'.',label='s2(t)')
                    plt.xlabel('t/s')
                    plt.ylabel('s/mm')
                    plt.title("Ebener Stoss: Weg")
                    plt.legend()
                    canvas = agg.FigureCanvasAgg(fig)
                    canvas.draw()
                    renderer = canvas.get_renderer()
                    raw_data = renderer.tostring_rgb()
                    size = canvas.get_width_height()

                    surf = pygame.image.fromstring(raw_data, size, "RGB")
                    DISPLAY.blit(surf, (BtnXlen+10,0))
                    pygame.display.flip()
                elif Btn6.collidepoint(pos):
                    fig = plt.figure(figsize=[11.5, 8],dpi=60,)
                    tl1 = []
                    vl1 = []
                    for i in range(len(x1lst)-2):
                        dll1 = sqrt((x1lst[i+1]-x1lst[i])**2+(y1lst[i+1]-y1lst[i])**2)
                        dlr1 = sqrt((x1lst[i+2]-x1lst[i+1])**2+(y1lst[i+2]-y1lst[i+1])**2)
                        tl1.append(t1lst[i+1])
                        vl1.append((dll1+dlr1)/(t1lst[i+2]-t1lst[i]))
                    tl2 = []
                    vl2 = []
                    for i in range(len(x2lst)-2):
                        dll2 = sqrt((x2lst[i+1]-x2lst[i])**2+(y2lst[i+1]-y2lst[i])**2)
                        dlr2 = sqrt((x2lst[i+2]-x2lst[i+1])**2+(y2lst[i+2]-y2lst[i+1])**2)
                        tl2.append(t2lst[i+1])
                        vl2.append((dll2+dlr2)/(t2lst[i+2]-t2lst[i]))
                    plt.plot(tl1,vl1,'.',label='v1(t)')
                    plt.plot(tl2,vl2,'.',label='v2(t)')
                    plt.xlabel('t/s')
                    plt.ylabel('v in mm/s')
                    plt.title("Ebener Stoss: Geschwindigkeit")
                    plt.legend()
                    canvas = agg.FigureCanvasAgg(fig)
                    canvas.draw()
                    renderer = canvas.get_renderer()
                    raw_data = renderer.tostring_rgb()
                    size = canvas.get_width_height()
                    surf = pygame.image.fromstring(raw_data, size, "RGB")
                    DISPLAY.blit(surf, (BtnXlen+10,0))
                    pygame.display.flip()
                elif Btn7.collidepoint(pos):
                    pygame.quit()
                    sys.exit()

    #lets draw the buttons and indicators
      
            pygame.draw.rect(DISPLAY, state_color1 , Btn1)
            pygame.draw.rect(DISPLAY, state_color2 , Btn2)
            pygame.draw.rect(DISPLAY, state_color3 , Btn3)
            pygame.draw.rect(DISPLAY, state_color4 , Btn4)
            pygame.draw.rect(DISPLAY, state_color4 , Btn5)
            pygame.draw.rect(DISPLAY, state_color4 , Btn6)
            pygame.draw.rect(DISPLAY, red , Btn7)
     
#             label_File = FONT.render ("File", 1, black)
            label_Start = FONT.render ("Start", 1, black)
            label_Save = FONT.render ("Save", 1, black)
        
#             labelp = FONT.render ("Plot", 1, black)
            labelxy = FONT.render ("x(t), y(t)", 1, black)
            labels = FONT.render ("s(t)", 1, black)
            labelv = FONT.render ("v(t)", 1, black)
            labelquit = FONT.render ("Quit", 1, white)
            labelfile = FONT.render (datfile, 1, blue)
      
            DISPLAY.blit(label_File, (Btnx[1], Btny[1]))
            DISPLAY.blit(labelfile, (Btnx[1], Btny[1]+20))
            DISPLAY.blit(label_Start, (Btnx[2], Btny[2]))
            DISPLAY.blit(label_Save, (Btnx[3], Btny[3]))
#             DISPLAY.blit(labelp, (Btnx[4], Btny[4]-20))
            DISPLAY.blit(labelxy,(Btnx[4], Btny[4]))
            DISPLAY.blit(labels, (Btnx[5], Btny[5]))
            DISPLAY.blit(labelv, (Btnx[6], Btny[6]))
            DISPLAY.blit(labelquit, (Btnx[7], Btny[7]))
            if run>0: DISPLAY.blit(label5, (Btnx[2], Btny[2]+20))
      
            #pygame.draw.circle ( DISPLAY, green, ( 450, 250 ), 200, 5 )
            #pygame.draw.line ( DISPLAY, red, ( 200, 100 ), ( 500, 400 ), 5 )
      
        #refresh screen        
        pygame.display.update()
        time.sleep(0.01)

def kugelpos():
# HID codes
#   0 0x00 => "ack_x",
#   1 0x01 => "ack_y",
#  47 0x2f => "mt_slot",
#  48 0x30 => "touch_major",
#  49 0x31 => "touch_minor",
#  50 0x32 => "width_major",
#  51 0x33 => "width_minor",
#  52 0x34 => "orientation",
#  53 0x35 => "pos_x",
#  54 0x36 => "pos_y",
#  57 0x39 => "tracking_id",
# 330 0x14a => "btn_touch");
    time = 0
    slot = 0
    x1 = 0
    x2 = 0
    y1 = 0
    y2 = 0
    while True:
        buff = frame.read(bstr.size)
        if (len(buff)<bstr.size): 
#             print "Ende! ",len(buff),bstr.size
            break
        sec, usec, syn, mtk, val = bstr.unpack(buff)
        time = 1e6*sec+usec
#         if (mtk == 0x30): print "major: ",401.*val/32768.
#         if (mtk == 0x31): print "minor: ",401.*val/32768.
        if (mtk == 0 and val == 0): break
        if (mtk == 0x2f) : slot = val
        if (mtk == 0x35) :
            if (slot == 0) : x1 = val
            if (slot == 1) : x2 = val
        if (mtk == 0x36) :
            if (slot == 0) : y1 = val
            if (slot == 1) : y2 = val
    return(time,x1,y1,x2,y2)

def devopen():  # Device open?
    if not os.path.exists(device):
        hid = False
#    print "trying to open ",device
        while not hid:
            hid = os.path.exists(device)
        while True:
            st = os.stat(device)
            if (st.st_mode) == 8612:
                break
    return

def newfile(path):
    dfiles = glob.glob(path)
    if len(dfiles)>0:
        last = dfiles[-1]
        nr = str(int(last[3:7])+100001)[1:]
    else:
        nr="00001"
    nextfile = "sg"+nr+".dat"
    return nextfile

if __name__ == '__main__':
    main()                