import pygame, sys
from pygame.locals import *
from RGB import *
import time,os,math,copy
import numpy as np

mapWidth,mapHeight  = 24,24#地图宽度
screenWidth,screenHeight= 640,480#窗口大小（屏幕大小）
texWidth,texHeight = 64,64
posX,posY = 3,10#玩家位置   表示含义：实际地图上位置，方格地图上的位置，方格地图上这个位置所在墙的材质
dirX,dirY = -1,0#光线方向
planeX,planeY = 0,0.66#相机平面   与dir相比使得视角FOV小于90度 2atan(0.66/1)=66°

#纹理demo
#dt = np.dtype(np.uint32)
#buffer = np.empty([screenHeight,screenWidth] , dtype = dt)
#texture = np.empty([8,5000] , dtype = dt)#4096
#colorm = np.empty([5000] , dtype = dt)#4096
#for i in range(8) : texture[i]=texWidth*texHeight

dt = np.dtype(np.int32)

#方格地图24*24
worldMap = np.array([
    [4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,7,7,7,7,7,7,7,7],
    [4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,0,0,0,0,0,0,7],
    [4,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7],
    [4,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7],
    [4,0,3,0,0,0,0,0,0,0,0,0,0,0,0,0,7,0,0,0,0,0,0,7],
    [4,0,4,0,0,0,0,5,5,5,5,5,5,5,5,5,7,7,0,7,7,7,7,7],
    [4,0,5,0,0,0,0,5,0,5,0,5,0,5,0,5,7,0,0,0,7,7,7,1],
    [4,0,6,0,0,0,0,5,0,0,0,0,0,0,0,5,7,0,0,0,0,0,0,8],
    [4,0,7,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,7,7,1],
    [4,0,8,0,0,0,0,5,0,0,0,0,0,0,0,5,7,0,0,0,0,0,0,8],
    [4,0,0,0,0,0,0,5,0,0,0,0,0,0,0,5,7,0,0,0,7,7,7,1],
    [4,0,0,0,0,0,0,5,5,5,5,0,5,5,5,5,7,7,7,7,7,7,7,1],
    [6,6,6,6,6,6,6,6,6,6,6,0,6,6,6,6,6,6,6,6,6,6,6,6],
    [8,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4],
    [6,6,6,6,6,6,0,6,6,6,6,0,6,6,6,6,6,6,6,6,6,6,6,6],
    [4,4,4,4,4,4,0,4,4,4,6,0,6,2,2,2,2,2,2,2,3,3,3,3],
    [4,0,0,0,0,0,0,0,0,4,6,0,6,2,0,0,0,0,0,2,0,0,0,2],
    [4,0,0,0,0,0,0,0,0,0,0,0,6,2,0,0,5,0,0,2,0,0,0,2],
    [4,0,0,0,0,0,0,0,0,4,6,0,6,2,0,0,0,0,0,2,2,0,2,2],
    [4,0,6,0,6,0,0,0,0,4,6,0,0,0,0,0,5,0,0,0,0,0,0,2],
    [4,0,0,5,0,0,0,0,0,4,6,0,6,2,0,0,0,0,0,2,2,0,2,2],
    [4,0,6,0,6,0,0,0,0,4,6,0,6,2,0,0,5,0,0,2,0,0,0,2],
    [4,0,0,0,0,0,0,0,0,4,6,0,6,2,0,0,0,0,0,2,0,0,0,2],
    [4,4,4,4,4,4,4,4,4,4,1,1,1,2,2,2,2,2,2,3,3,3,3,3]],dtype = dt)

w = screenWidth
h = screenHeight
mapX,mapY = 0,0
pygame.init()
screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption('rayCaster')
txt = pygame.font.SysFont("微软黑",40)#字体大小

def dLMap(map,posX,posY):
    nmap = copy.deepcopy(map)
    nmap[int(posX)][int(posY)] = 99
    for x0 in range(mapWidth):
        for y0 in range(mapHeight):
            if nmap[x0][y0]==99:
                print(printColors.RED + "▇▇" + printColors.END,end='')
            elif nmap[x0][y0]>0:
                print("▇▇",end='')
            else:
                print("  ",end='')
        print(end='\n')
    nmap=copy.deepcopy(map) 

def t_d(num,t):
    t1 = list(t)
    for i in t1:
        t2 = i/num
        t1.append(t2)
        t1.pop(0)
    return tuple(t1)

os.system("cls")
dLMap(worldMap,posX,posY)

while True:
    screen.fill(RGB_Black)
    oldTime = time.time()#开始计数
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():#退出游戏
        if event.type == QUIT:
            pygame.quit() 
            sys.exit()

    for x in range(w):
        cameraX = 2 * x / float(w) - 1#计算实际屏幕上的光线位置
        rayDirX = dirX + planeX * cameraX#代入计算光线方向矢量  
        rayDirY = dirY + planeY * cameraX

        mapX = int(posX)#地图上射线位置
        mapY = int(posY)
        sideDistX:float#光线的开头段长度（第一次遇到x侧）
        sideDistY:float
        # rayDirX 或 rayDirY 为 0，则通过将其设置为非常高的值 1e30 来避免被零除。
        deltaDistX = 1.0*10**30 if rayDirX == 0 else abs(1 / rayDirX)#光线的中间段长度（从x侧到另一个x侧长度）
        deltaDistY = 1.0*10**30 if rayDirY == 0 else abs(1 / rayDirY)#用相似证出deltaDistX=sqrt(1+(rayDirY*rayDirY)/(rayDirX*rayDirX))

        perpWallDis:float#用于计算射线的长度

        stepX:int#方格所在x或y轴的正负方向，stepx或y只有+1或-1
        stepY:int

        hit = 0#用于检测是否击中（控制循环是否继续进行）
        side = 0#用于检测击中类型（如果击中了 x 侧，则 side 设置为 0，如果击中了 y 侧，则 side 将为 1）


        #如果光线有负分量，则 stepX 为 -1，如果射线方向具有正 x 分量，则为 +1。如果 x 分量为 0，则 stepX 的值无关紧要，因为它将未被使用。
        if rayDirX < 0:
            stepX = -1#对应地图上，光线迈步
            sideDistX = (posX - mapX) * deltaDistX#计算开头段的长度,通过相似三角形证得sideDistX = (posX - mapX) * deltaDistX
        else:
            stepX = 1
            sideDistX = (mapX + 1.0 - posX) * deltaDistX
        if rayDirY < 0:
            stepY = -1
            sideDistY = (posY - mapY) * deltaDistY
        else:
            stepY = 1
            sideDistY = (mapY + 1.0 - posY) * deltaDistY

        #DDA算法
        while hit == 0:
            if sideDistX < sideDistY:
                  sideDistX += deltaDistX;#从“开头段”开始，一直加“中间段”
                  mapX += stepX;#对应地图上
                  side = 0;#x-side 0, y-side 1.
            else:
                sideDistY += deltaDistY;
                mapY += stepY;
                side = 1;
            if worldMap[mapX][mapY] > 0: hit = 1#射线不断在地图上迈步，当迈步到非0时，说明撞到墙壁，此时要停止迈步（退出循环）

        if side == 0 :#计算垂直距离，避免“圆圈效应”
            perpWallDist = sideDistX - deltaDistX
        else:
            perpWallDist = sideDistY - deltaDistY

        lineHeight = int(h / perpWallDist)
        drawStart = -lineHeight / 2 + h / 3
        if drawStart < 0 : drawStart = 0
        drawEnd = lineHeight / 2 + h / 3
        if drawEnd >= h : drawEnd = h - 1
        
        if worldMap[mapX][mapY] == 1 : color = RGB_Red
        elif worldMap[mapX][mapY] == 2 : color = RGB_Green
        elif worldMap[mapX][mapY] == 3 : color = RGB_Blue
        elif worldMap[mapX][mapY] == 4 : color = RGB_White
        else: color =  RGB_Yellow

        if side == 1 : color = t_d(2,color)

      #verLine(x, drawStart, drawEnd, color);
        pygame.draw.line(screen,color,(x,drawStart),(x,drawEnd),width=1)

    timeNow = time.time()#计数完成
    frameTime = timeNow - oldTime
    fps = 1 / frameTime
    txt2 = txt.render("FPS:"+str(int(fps)),True,RGB_Red)
    screen.blit(txt2,(0,0))#计算并打印帧数 目前问题：帧数跳动太厉害
    #print(fps)# 打印帧率

    moveSpeed = frameTime * 8.0#移动速度
    rotSpeed = frameTime * 3#旋转速度
    if keys[pygame.K_UP]:
        if worldMap[int(posX + dirX * moveSpeed)][int(posY)] == False : posX += dirX * moveSpeed
        if worldMap[int(posX)][int(posY + dirY * moveSpeed)] == False : posY += dirY * moveSpeed

    if keys[pygame.K_DOWN]:
        if worldMap[int(posX - dirX * moveSpeed)][int(posY)] == False : posX -= dirX * moveSpeed
        if worldMap[int(posX)][int(posY - dirY * moveSpeed)] == False :  posY -= dirY * moveSpeed

    #if keys[pygame.K_DOWN] or keys[pygame.K_UP]:  #启用小地图，目前问题：刷新过慢，延迟太高
    #    os.system("cls") 
    #    dLMap(worldMap,posX,posY)

    if keys[pygame.K_RIGHT]:
      oldDirX = dirX;
      dirX = dirX * math.cos(-rotSpeed) - dirY * math.sin(-rotSpeed)
      dirY = oldDirX * math.sin(-rotSpeed) + dirY * math.cos(-rotSpeed)
      oldPlaneX = planeX
      planeX = planeX * math.cos(-rotSpeed) - planeY * math.sin(-rotSpeed)
      planeY = oldPlaneX * math.sin(-rotSpeed) + planeY * math.cos(-rotSpeed)

    if keys[pygame.K_LEFT]:
      oldDirX = dirX
      dirX = dirX * math.cos(rotSpeed) - dirY * math.sin(rotSpeed)
      dirY = oldDirX * math.sin(rotSpeed) + dirY * math.cos(rotSpeed)
      oldPlaneX = planeX
      planeX = planeX * math.cos(rotSpeed) - planeY * math.sin(rotSpeed)
      planeY = oldPlaneX * math.sin(rotSpeed) + planeY * math.cos(rotSpeed)
    pygame.display.update()