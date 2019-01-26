#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Luftkissentisch

import pygame
import time
import sys
import struct
import os.path
import glob
import platform
import math
from math import sqrt, sin, cos
import matplotlib
import signal
matplotlib.use('Agg')
import matplotlib.backends.backend_agg as agg
import matplotlib.pyplot as plt
from scipy.optimize import minimize, OptimizeResult

# define input file

path = os.listdir("/dev/input/by-id/")

pvar = -1
for i in range(len(path)):
    if (path[i].startswith("usb-Multi_touch_Multi_touch_overlay_device")): #usb-Multi_touch_Multi_touch_overlay_device
        pvar = i
        break
if (pvar == -1):
    print("No device connected.")
    quit()

device = "/dev/input/by-id/" + path[pvar]

# pocessor architecture
if (platform.architecture()[0] == "64bit"):
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
    DISPLAY = pygame.display.set_mode(size)
    Scrn = pygame.Rect(Btnx[0],0,width,height)
    Cnvs = pygame.Rect(BtnXlen+25, 5, height-10,  height-10)
    BtnFile = pygame.Rect(Btnx[1],Btny[1], BtnXlen,BtnYlen)
    BtnStart = pygame.Rect(Btnx[2],Btny[2], BtnXlen,BtnYlen)
    BtnSave = pygame.Rect(Btnx[3],Btny[3], BtnXlen,BtnYlen)
    BtnXY = pygame.Rect(Btnx[4],Btny[4], BtnXlen,BtnYlen)
    BtnS = pygame.Rect(Btnx[5],Btny[5], BtnXlen,BtnYlen)
    BtnV = pygame.Rect(Btnx[6],Btny[6], BtnXlen,BtnYlen)
    BtnQuit = pygame.Rect(Btnx[7],Btny[7], BtnXlen,BtnYlen)


    #initial state colors for indicators
    state_color1 = cyan
    state_color2 = cyan
    state_color3 = cyan
    state_color4 = cyan
    run = 0
    datfile = newfile("sg*.csv")


    #define font
    FONT = pygame.font.Font(None, 25)
  
    label_File = FONT.render("File", 1, black)
  
    #Background Screen
    pygame.draw.rect(DISPLAY, grey , Scrn)
    #drawing area Canvas
    pygame.draw.rect(DISPLAY, black , Cnvs)
  
    devopen()
    frame = open(device,"rb")
    
    #define data container
    global dispList1, dispList2
    dispList1 = []
    dispList2 = []
    
    x1lst = [] # x-pos from 1 in mm
    y1lst = [] # y-pos from 1 in mm 
    t1lst = [] # t from 1 in s
    x2lst = [] # x-pos from 2 in mm
    y2lst = [] # y-pos from 2 in mm
    t2lst = [] # t from 2 in s
    tl1 = [] # t for velocities in 1 
    vl1 = [] # v from 1 in mm/s
    tl2 = [] # t for velocities in 2
    vl2 = [] # v from 2 in mm/s

    running = True
    lock = False
    selecting = True
    changed = False
    isCnvsVisible = True
    alreadySaved = False
    firstTimeSaved = False
    
    label_Anlge1 = FONT.render("Angle 1: --.-- degree",1,black) # "°.".decode('utf8').encode(local_encoding)    WITH    local_encoding = 'cp850'
    label_Anlge2 = FONT.render("Angle 2: --.-- degree",1,black)
  
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
                if BtnFile.collidepoint(pos):
                    alreadySaved = False
                    firstTimeSaved = False
                    # Create new file
                    pygame.draw.rect(DISPLAY, red , BtnFile)
                    pygame.display.update()
                    datfile = newfile("sg*.csv")
                    pygame.draw.rect(DISPLAY, cyan , BtnFile)
                    labelfile = FONT.render (datfile, 1, blue)
                    DISPLAY.blit(label_File, (Btnx[1], Btny[1]))
                    DISPLAY.blit(labelfile, (Btnx[1], Btny[1]+30))
                    run = 0
                    pygame.display.update()
                elif BtnStart.collidepoint(pos):
                    if not isCnvsVisible:
                        #Switch to current measurement
                        pygame.draw.rect(DISPLAY, grey, Scrn)
                        pygame.draw.rect(DISPLAY, black, Cnvs)
                        for i in range(len(dispList1)):
                            color = blue
                            if dispList1[i][2]:
                                color = cyan
                            pygame.draw.circle(DISPLAY, color, (dispList1[i][0], dispList1[i][1]), 2)
                        for i in range(len(dispList2)):
                            color = red
                            if dispList2[i][2]:
                                color = cyan
                            pygame.draw.circle(DISPLAY, color, (dispList2[i][0], dispList2[i][1]), 2)
                        isCnvsVisible = True
                        break;
                    # Start measurement
                    run += 1
                    alreadySaved = False
                    pygame.draw.rect(DISPLAY, grey, Scrn)
                    pygame.draw.rect(DISPLAY, black, Cnvs)
                    pygame.draw.rect(DISPLAY, green, BtnStart)
                    x1lst = [] # x-pos from 1 in mm
                    y1lst = [] # y-pos from 1 in mm 
                    t1lst = [] # t from 1 in s
                    dispList1 = []
                    x2lst = [] # x-pos from 2 in mm
                    y2lst = [] # y-pos from 2 in mm
                    t2lst = [] # t from 2 in s
                    dispList2 = []
                    stime =  atime = 0
                    label5 = FONT.render ('Run '+str(run), 1, blue)
                    DISPLAY.blit(label5, (Btnx[2], Btny[2]+30))
                    pygame.display.update()
                    frame.close()
                    devopen()
                    frame = open(device,"rb")
                    while (atime < 6e6):
                        try:
                            (etime,x1,y1,x2,y2) = kugelpos()
                        except IOError:
                            break
                        if (etime == 0): break
                        if (stime == 0): stime = etime
                        atime = etime - stime
                        # Condition for slot changing
                        if not dispList1 == [] and not dispList2 == []:
                            current1 = (x1*fmm,y1*fmm)
                            current2 = (x2*fmm,y2*fmm)
                            before1 = (x1lst[len(x1lst)-1], y1lst[len(y1lst)-1])
                            before2 = (x2lst[len(x2lst)-1], y2lst[len(y2lst)-1])
                            alreadyChanged = False
                            if x1>0 and y1>0 and distance(current1, before1) > distance(current1, before2):
                                x1, y1, x2, y2 = x2, y2, x1, y1
                                alreadyChanged = True
                            if not alreadyChanged and x2>0 and y2>0 and distance(current2, before2) > distance(current2, before1):
                                x1, y1, x2, y2 = x2, y2, x1, y1
                        # Perparation for Drawing an storing data
                        x1d = int(BtnXlen+25+480./32768*x1)
                        y1d = int(480./32768*y1)
                        x2d = int(BtnXlen+25+480./32768*x2)
                        y2d = int(480./32768*y2)
                        if (x1>1000 and y1>1000 and x1<32000 and y2<32000): 
                            pygame.draw.circle(DISPLAY, blue, (x1d, y1d), 2)
                            pygame.display.update()
                            x1lst.append(x1*fmm)
                            y1lst.append(y1*fmm)
                            t1lst.append(1e-6*atime)
                            dispList1.append((x1d, y1d, False))
                        if (x2>1000 and y2>1000 and x2<32000 and y2<32000): 
                            pygame.draw.circle(DISPLAY, red, (x2d, y2d), 2)
                            pygame.display.update()
                            x2lst.append(x2*fmm)
                            y2lst.append(y2*fmm)
                            t2lst.append(1e-6*atime)
                            dispList2.append((x2d, y2d, False))
                    # Geschwindigkeit berechnen
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
                    # lfd. Nr anzeigen, Koordinaten abspeichern
                    state_color2 = cyan
                    pygame.display.update()
                    print("Positionen",len(x1lst),len(x2lst))
                elif BtnSave.collidepoint(pos):
                    if alreadySaved:
                        break
                    if not firstTimeSaved:
                        fd = open(datfile,"a")
                        fd.write('%3s,%4s,%4s,%1s,%1s,%1s\n' % ("run","slot","time","x","y","v"))
                        fd.close
                        firstTimeSaved = True
                    # Save measurement
                    pygame.draw.rect(DISPLAY, red , BtnSave)
                    pygame.display.update()
                    fd = open(datfile,"a")
                    if not t1lst == []:
                        z = '%4i,%4i,%9.6f,%6.1f,%6.1f\n' % (run,1,t1lst[0],x1lst[0],y1lst[0])
                        fd.write(z)
                        for i in range(1,len(x1lst)-1):
                            z = '%4i,%4i,%9.6f,%6.1f,%6.1f,%6.1f\n' % (run,1,t1lst[i],x1lst[i],y1lst[i],vl1[i-1])
                            fd.write(z)
                        z = '%4i,%4i,%9.6f,%6.1f,%6.1f\n' % (run,1,t1lst[len(x1lst)-1],x1lst[len(x1lst)-1],y1lst[len(x1lst)-1])
                        fd.write(z)
                    if not t2lst == []:
                        z = '%4i,%4i,%9.6f,%6.1f,%6.1f\n' % (run,2,t2lst[1],x2lst[1],y2lst[1])
                        fd.write(z)
                        for i in range(1,len(x2lst)-1):
                            z = '%4i,%4i,%9.6f,%6.1f,%6.1f,%6.1f\n' % (run,2,t2lst[i],x2lst[i],y2lst[i],vl2[i-1])
                            fd.write(z)
                        z = '%4i,%4i,%9.6f,%6.1f,%6.1f\n' % (run,2,t2lst[len(x2lst)-1],x2lst[len(x2lst)-1],y2lst[len(x2lst)-1])
                        fd.write(z)
                    fd.close()
                    alreadySaved = True
                    pygame.draw.rect(DISPLAY, state_color3 , BtnSave)
                    pygame.display.update()
                elif BtnXY.collidepoint(pos):
                    isCnvsVisible = False
                    # Show positions
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

                elif BtnS.collidepoint(pos):
                    isCnvsVisible = False
                    # Show s
                    fig = plt.figure(figsize=[11.5, 8],dpi=60,)
                    sl1 = [0]
                    for i in range(len(x1lst)-1):
                        sl1.append(sl1[i]+sqrt((x1lst[i+1]-x1lst[i])**2+(y1lst[i+1]-y1lst[i])**2))
                    sl2 = [0]
                    for i in range(len(x2lst)-1):
                        sl2.append(sl2[i]+sqrt((x2lst[i+1]-x2lst[i])**2+(y2lst[i+1]-y2lst[i])**2))
                    if len(x1lst) == 0 or len(x2lst) == 0:
                        sl2 = sl1 = []
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
                elif BtnV.collidepoint(pos):
                    isCnvsVisible = False
                    # Show velocity
                    fig = plt.figure(figsize=[11.5, 8],dpi=60,)
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
                elif BtnQuit.collidepoint(pos):
                    # Close frame
                    pygame.quit()
                    sys.exit()
                elif Cnvs.collidepoint(pos):
                    if not isCnvsVisible:
                        break
                    # Mark points on Cnvs
                    lock = True
                    collisionAt = getCollitionIndex(dispList1, pos, True)
                    if not collisionAt == []:
                        selecting = not dispList1[collisionAt][2]
                        break
                    collisionAt = getCollitionIndex(dispList2, pos, True)
                    if not collisionAt == []:
                        selecting = not dispList2[collisionAt][2]
            if event.type == pygame.MOUSEBUTTONUP:
                if not isCnvsVisible:
                    break
                lock = False
                selecting = True
                if changed:
                    print("changed")
                    points1 =[]
                    points2 =[]
                    for i in range(len(dispList1)):
                        if not dispList1[i][2]: continue
                        points1.append((x1lst[i],y1lst[i]))
                    res = getLineOfBestFit(points1)
                    if res.success:
                        angle1 = res.x[0]*360/(2*math.pi) %180
                        angleStr1 = "Angle 1: " + str(round(angle1, 2)) + " degree"
                        print("angle 1:",angle1, res.x[1]) #90 - (res.x[0]*360/2*math.pi %180)
                    else: angleStr1 = "Angle 1: ---.-- degree" 
                    for i in range(len(dispList2)):
                        if not dispList2[i][2]: continue
                        points2.append((x2lst[i],y2lst[i]))
                    res = getLineOfBestFit(points2)
                    if res.success:
                        angle2 = res.x[0]*360/(2*math.pi) %180
                        angleStr2 = "Angle 2: " + str(round(angle2, 2)) + " degree"
                        print("angle 2:",angle2, res.x[1]) # 90 - (res.x[0]*360/2*math.pi %180)
                    else: angleStr2 = "Angle 2: ---.-- degree"
                    label_Anlge1 = FONT.render(angleStr1,1,black)
                    label_Anlge2 = FONT.render(angleStr2,1,black)
                changed = False
            if event.type == pygame.MOUSEMOTION:
                if not lock:
                    break
                pos = pygame.mouse.get_pos()
                changed = markPositions(dispList1, pos, (blue, cyan), selecting) or changed
                changed = markPositions(dispList2, pos, (red, cyan), selecting) or changed
    #lets draw the buttons and indicators
            pygame.draw.rect(DISPLAY, state_color1 , BtnFile)
            pygame.draw.rect(DISPLAY, state_color2 , BtnStart)
            pygame.draw.rect(DISPLAY, state_color3 , BtnSave)
            pygame.draw.rect(DISPLAY, state_color4 , BtnXY)
            pygame.draw.rect(DISPLAY, state_color4 , BtnS)
            pygame.draw.rect(DISPLAY, state_color4 , BtnV)
            pygame.draw.rect(DISPLAY, red , BtnQuit)
     
            label_Start = FONT.render ("Start", 1, black)
            label_Save = FONT.render ("Save", 1, black)
        
            labelxy = FONT.render ("x(t), y(t)", 1, black)
            labels = FONT.render ("s(t)", 1, black)
            labelv = FONT.render ("v(t)", 1, black)
            labelquit = FONT.render ("Quit", 1, white)
            labelfile = FONT.render (datfile, 1, blue)
            if label_Anlge1.get_width() > label_Anlge2.get_width(): sizeLabelAnlge = label_Anlge1.get_width()
            else: sizeLabelAnlge = label_Anlge2.get_width()
            if label_Anlge1.get_height() > label_Anlge2.get_height(): sizeLabelAnlge = (sizeLabelAnlge, label_Anlge1.get_height())
            else: sizeLabelAnlge = (sizeLabelAnlge, label_Anlge2.get_height())
            posAngle1 = (Cnvs.x + Cnvs.width + 10, size[1] - 2*sizeLabelAnlge[1]-25)
            posAngle2 = (Cnvs.x + Cnvs.width + 10, size[1] - sizeLabelAnlge[1]-20)
      
            DISPLAY.blit(label_File, (Btnx[1], Btny[1]))
            DISPLAY.blit(labelfile, (Btnx[1], Btny[1]+20))
            DISPLAY.blit(label_Start, (Btnx[2], Btny[2]))
            DISPLAY.blit(label_Save, (Btnx[3], Btny[3]))
            DISPLAY.blit(labelxy,(Btnx[4], Btny[4]))
            DISPLAY.blit(labels, (Btnx[5], Btny[5]))
            DISPLAY.blit(labelv, (Btnx[6], Btny[6]))
            DISPLAY.blit(labelquit, (Btnx[7], Btny[7]))
            if run>0: DISPLAY.blit(label5, (Btnx[2], Btny[2]+20))
            if isCnvsVisible:
                re = pygame.Rect(posAngle1[0], posAngle1[1], posAngle2[0] + sizeLabelAnlge[0], posAngle2[1] + sizeLabelAnlge[1])
                pygame.draw.rect(DISPLAY, grey, re)
                DISPLAY.blit(label_Anlge1, posAngle1)
                DISPLAY.blit(label_Anlge2, posAngle2)
      
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
# mtk multitouchkey
    time = 0
    slot = 0
    x1 = 0
    x2 = 0
    y1 = 0
    y2 = 0
    while True:
        signal.signal(signal.SIGALRM, handler)
        signal.alarm(5)
        buff = frame.read(bstr.size)
        signal.alarm(0)
        if (len(buff)<bstr.size): 
            break
        sec, usec, syn, mtk, val = bstr.unpack(buff)
        time = 1e6*sec+usec
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
    nextfile = "sg"+nr+".csv"
    return nextfile

def markPositions(posList, mousePos, colors, selectingFlag):
    """Highlights the selected positions and changes the selection values for those positions to True.
    """
    changed = False
    color = colors[0]
    if selectingFlag:
        color = colors[1]
    indexes = getCollitionIndex(posList, mousePos, False)
    for i in indexes:
        posList[i] = (posList[i][0], posList[i][1], selectingFlag)
        pygame.draw.circle(DISPLAY, color, (posList[i][0], posList[i][1]), 2)
        changed = True
    return changed

def getCollitionIndex(posList, mousePos, getOnlyOne):
    """
    Returns the index of posList that matches with the mouse position.
    
    
    posList = List of the balls position
    
    mousePos = Position of the mouse
    
    getOnlyOne = True if you only want the average index that matches
    """
    
    collisionTol = 5
    indexes = []
    for i in range(len(posList)):
                    if (posList[i][0]-collisionTol) < (mousePos[0]) and (posList[i][0]+collisionTol) > (mousePos[0]):
                        if (posList[i][1]-collisionTol) < (mousePos[1]) and (posList[i][1]+collisionTol) > (mousePos[1]):
                            indexes.append(i)
    if not indexes == [] and getOnlyOne:
        index = 0
        n = len(indexes)
        for i in range(n):
            index += indexes[i]
        average = math.trunc(index/n)
        for i in range(n):
            if average == indexes[i]:
                return average
        return indexes[0]
    return indexes

def getLineOfBestFit(points):
    n = len(points)
    if not n == 0:
        delx = points[n-1][0] - points[0][0]
        dely = points[n-1][1] - points[0][1]
        if not delx == 0:
            phi_start = math.atan2(dely, delx)
            p_start = points[0][1] - dely/delx*points[0][0]
            def fun(x):
                y = 0
                for i in range(n):
                    y+= (points[i][0]*cos(x[0])+points[i][1]*sin(x[0]) - x[1])**2
                return y
            return minimize(fun, [phi_start,p_start], args=(), method='Nelder-Mead', jac=None, hess=None, hessp=None, bounds=None, constraints=(), tol=0.1, callback=None, options=None)
    res = OptimizeResult()
    res.success = False
    return res   

def distance(point1, point2):
    return sqrt((point2[0]-point1[0])**2 +  (point2[1] - point1[1])**2)

def handler(signum, frame):
    raise IOError("TimeException")

if __name__ == '__main__':
    main()                