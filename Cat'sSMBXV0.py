#!/usr/bin/env python3
"""
SUPER MARIO BROS X2 - COMPLETE v2.0
(C) 2025 Samsoft/Team Flames
Full: Menu, Episodes, Editor, 5 Characters, Physics
"""
import pygame,json,os,math,sys
from enum import IntEnum
pygame.init()

SW,SH,GRID,FPS=800,600,32,64

class St(IntEnum):
    MENU=0;EPISODE=1;CHAR=2;PLAY=3;PAUSE=4;EDITOR=5;CREDITS=6;CLEAR=7;OVER=8

class Tl(IntEnum):
    SEL=0;ERA=1;BLK=2;NPC=3;BGO=4

class Pw(IntEnum):
    SM=0;BIG=1;FIRE=2;LEAF=3

class Ch(IntEnum):
    MARIO=0;LUIGI=1;PEACH=2;TOAD=3;LINK=4

class C:
    W=(255,255,255);K=(0,0,0);R=(255,0,0);G=(0,255,0);B=(0,0,255);Y=(255,255,0);GR=(128,128,128)
    SKY=(92,148,252);MB=(0,0,64);SEL=(255,220,64);EP=(45,45,48);EB=(67,67,70);ET=(220,220,220);AC=(0,122,204)

BLK={
    1:{"n":"Brick","c":(165,82,41),"g":"SMB1"},
    2:{"n":"Stone","c":(128,128,128),"g":"SMB1"},
    4:{"n":"?Block","c":(255,200,64),"g":"SMB1","q":1},
    44:{"n":"Note","c":(255,128,160),"g":"SMB3","note":1},
    141:{"n":"PipeTL","c":(0,200,0),"g":"Pipe"},
    142:{"n":"PipeTR","c":(0,200,0),"g":"Pipe"},
    143:{"n":"PipeBL","c":(0,160,0),"g":"Pipe"},
    144:{"n":"PipeBR","c":(0,160,0),"g":"Pipe"},
    181:{"n":"Grass","c":(64,192,64),"g":"Size","semi":1},
    182:{"n":"Dirt","c":(139,90,43),"g":"Size"},
}

NPC={
    1:{"n":"Goomba","c":(139,69,19),"w":32,"h":32,"g":"Enemy","st":1},
    11:{"n":"Koopa","c":(0,128,0),"w":32,"h":54,"g":"Enemy","st":1},
    106:{"n":"Boo","c":(255,255,255),"w":32,"h":32,"g":"Enemy","ghost":1},
    151:{"n":"Mushroom","c":(255,64,64),"w":32,"h":32,"g":"Pwr","pwr":Pw.BIG},
    152:{"n":"Fire","c":(255,128,0),"w":32,"h":32,"g":"Pwr","pwr":Pw.FIRE},
    171:{"n":"Coin","c":(255,215,0),"w":32,"h":32,"g":"Coin","coin":1},
    174:{"n":"StarCoin","c":(255,215,0),"w":48,"h":48,"g":"Coin","stcoin":1},
    181:{"n":"Yoshi","c":(64,200,64),"w":40,"h":48,"g":"Yoshi"},
    203:{"n":"Flag","c":(0,255,0),"w":16,"h":160,"g":"Goal","goal":1},
}

BGO={
    1:{"n":"Bush","c":(64,192,64),"w":96,"h":32},
    3:{"n":"Cloud","c":(255,255,255),"w":96,"h":48},
    5:{"n":"Hill","c":(64,128,64),"w":160,"h":80},
}

screen=pygame.display.set_mode((SW,SH),pygame.RESIZABLE)
pygame.display.set_caption("Super Mario Bros X2 v2.0")
clock=pygame.time.Clock()

try:
    fs=pygame.font.SysFont("segoeui",11)
    fm=pygame.font.SysFont("segoeui",14)
    fb=pygame.font.SysFont("segoeui",14,True)
    fl=pygame.font.SysFont("segoeui",24,True)
    fx=pygame.font.SysFont("segoeui",36,True)
except:
    fs=fm=fb=pygame.font.Font(None,16)
    fl=pygame.font.Font(None,28)
    fx=pygame.font.Font(None,40)

def clamp(v,a,b):
    return max(a,min(b,v))

def lerp(a,b,t):
    return a+(b-a)*t

def txt(s,t,p,f=None,c=C.W):
    s.blit((f or fm).render(str(t),1,c),p)

def txtc(s,t,r,f=None,c=C.W):
    x=(f or fm).render(str(t),1,c)
    s.blit(x,(r[0]+(r[2]-x.get_width())//2,r[1]+(r[3]-x.get_height())//2))

def grad(s,r,c1,c2):
    for i in range(r[3]):
        t=i/max(1,r[3])
        pygame.draw.line(s,(int(c1[0]+(c2[0]-c1[0])*t),int(c1[1]+(c2[1]-c1[1])*t),int(c1[2]+(c2[2]-c1[2])*t)),(r[0],r[1]+i),(r[0]+r[2],r[1]+i))

def btn(s,r,t,h=0,a=0):
    pygame.draw.rect(s,C.AC if a else(C.GR if h else(60,60,60)),r)
    pygame.draw.rect(s,C.EB,r,1)
    txtc(s,t,r,fs,C.W)

class Cam:
    def __init__(self):
        self.x=self.y=0
        self.z=1.0
    def w2s(self,p,o=(0,0)):
        return(int((p[0]-self.x)*self.z)+o[0],int((p[1]-self.y)*self.z)+o[1])
    def s2w(self,p,o=(0,0)):
        return((p[0]-o[0])/self.z+self.x,(p[1]-o[1])/self.z+self.y)
    def follow(self,x,y):
        self.x=lerp(self.x,x-SW/2/self.z,0.1)
        self.y=lerp(self.y,y-SH/2/self.z,0.1)

class Block:
    def __init__(self,x,y,i):
        self.x,self.y,self.id=x,y,i
        self.w=self.h=GRID
        d=BLK.get(i,{"n":"?","c":C.GR})
        self.n,self.c=d.get("n"),d.get("c")
        self.sel=0
        self.r=pygame.Rect(x,y,self.w,self.h)
    def draw(self,s,cam,o=(0,0)):
        sp=cam.w2s((self.x,self.y),o)
        w,h=int(self.w*cam.z),int(self.h*cam.z)
        r=pygame.Rect(sp[0],sp[1],w,h)
        pygame.draw.rect(s,self.c,r)
        pygame.draw.rect(s,tuple(max(0,x-40)for x in self.c),r,1)
        if BLK.get(self.id,{}).get("q"):
            txtc(s,"?",r,fb,C.W)
        if self.sel:
            pygame.draw.rect(s,(51,153,255),r,2)

class Npc:
    def __init__(self,x,y,i):
        self.x,self.y,self.id=x,y,i
        d=NPC.get(i,{"n":"?","c":C.GR,"w":32,"h":32})
        self.n,self.c=d.get("n"),d.get("c")
        self.w,self.h=d.get("w",32),d.get("h",32)
        self.sel=0
        self.act=1
        self.vx=-1
        self.vy=0
        self.r=pygame.Rect(x,y,self.w,self.h)
    def update(self,blks,plr=None):
        if not self.act:
            return
        d=NPC.get(self.id,{})
        if d.get("coin") or d.get("pwr") or d.get("goal") or d.get("stcoin"):
            return
        if not d.get("ghost"):
            self.vy=min(self.vy+0.4,12)
        if d.get("ghost") and plr:
            dx=plr.x-self.x
            self.vx=1 if dx>0 and plr.dir==0 else(-1 if dx<0 and plr.dir==1 else 0)
        self.x+=self.vx
        self.y+=self.vy
        self.r=pygame.Rect(int(self.x),int(self.y),self.w,self.h)
        for b in blks:
            if not self.r.colliderect(b.r):
                continue
            if self.vy>0 and self.r.bottom>b.r.top and self.r.bottom-self.vy<=b.r.top+8:
                self.r.bottom=b.r.top
                self.y=self.r.y
                self.vy=0
            if self.vx>0 and self.r.right>b.r.left and self.r.left<b.r.left:
                self.vx=-abs(self.vx)
            elif self.vx<0 and self.r.left<b.r.right and self.r.right>b.r.right:
                self.vx=abs(self.vx)
        if self.y>1000:
            self.act=0
    def draw(self,s,cam,o=(0,0)):
        if not self.act:
            return
        sp=cam.w2s((self.x,self.y),o)
        w,h=int(self.w*cam.z),int(self.h*cam.z)
        r=pygame.Rect(sp[0],sp[1],w,h)
        d=NPC.get(self.id,{})
        if d.get("coin") or d.get("stcoin"):
            pygame.draw.ellipse(s,self.c,r)
            pygame.draw.ellipse(s,(200,150,0),r,2)
        elif d.get("pwr"):
            pygame.draw.ellipse(s,self.c,(r.x,r.y,w,int(h*0.6)))
            pygame.draw.rect(s,(255,220,180),(r.centerx-w//4,r.y+int(h*0.5),w//2,h//2))
        elif d.get("goal"):
            pygame.draw.rect(s,C.GR,(r.centerx-2,r.y,4,h))
            pygame.draw.polygon(s,C.G,[(r.centerx,r.y+8),(r.centerx+24,r.y+24),(r.centerx,r.y+40)])
        else:
            pygame.draw.ellipse(s,self.c,r)
        if self.sel:
            pygame.draw.rect(s,(51,153,255),r,2)

class Bgo:
    def __init__(self,x,y,i):
        self.x,self.y,self.id=x,y,i
        d=BGO.get(i,{"n":"?","c":C.GR,"w":32,"h":32})
        self.n,self.c=d.get("n"),d.get("c")
        self.w,self.h=d.get("w",32),d.get("h",32)
        self.sel=0
        self.r=pygame.Rect(x,y,self.w,self.h)
    def draw(self,s,cam,o=(0,0)):
        sp=cam.w2s((self.x,self.y),o)
        w,h=int(self.w*cam.z),int(self.h*cam.z)
        r=pygame.Rect(sp[0],sp[1],w,h)
        if "Cloud" in self.n:
            pygame.draw.ellipse(s,self.c,r)
        elif "Hill" in self.n:
            pygame.draw.polygon(s,self.c,[(r.left,r.bottom),(r.centerx,r.top),(r.right,r.bottom)])
        else:
            pygame.draw.ellipse(s,self.c,r)

class Player:
    def __init__(self,x,y,ch=Ch.MARIO):
        self.x,self.y=float(x),float(y)
        self.w,self.h=24,32
        self.vx=self.vy=0.0
        self.ch=ch
        self.pwr=Pw.SM
        self.dir=1
        self.grnd=0
        self.jh=0
        self.inv=0
        self.dead=0
        self.goal=0
        self.coins=0
        self.lives=5
        self.score=0
        self.cc={
            Ch.MARIO:(C.R,(64,64,200)),
            Ch.LUIGI:(C.G,(64,64,200)),
            Ch.PEACH:((255,192,203),(255,100,150)),
            Ch.TOAD:(C.R,C.W),
            Ch.LINK:((0,128,0),(139,90,43))
        }
        self.r=pygame.Rect(int(x),int(y),self.w,self.h)
    
    def update(self,keys,blks,npcs):
        if self.dead:
            self.vy+=0.4
            self.y+=self.vy
            return
        jp=[-10.5,-11.5,-9.5,-9.5,-10.0][self.ch]
        sm=[1.0,0.92,0.85,1.15,0.95][self.ch]
        mx=6.0*sm
        ac=0.15 if self.grnd else 0.1
        if keys[pygame.K_LEFT]:
            self.vx=max(-mx,self.vx-ac)
            self.dir=0
        elif keys[pygame.K_RIGHT]:
            self.vx=min(mx,self.vx+ac)
            self.dir=1
        else:
            if abs(self.vx)<0.1:
                self.vx=0
            elif self.vx>0:
                self.vx-=0.1
            else:
                self.vx+=0.1
        if keys[pygame.K_z] and self.grnd and not self.jh:
            self.vy=jp
            self.grnd=0
            self.jh=1
        if not keys[pygame.K_z]:
            self.jh=0
        gv=0.2 if keys[pygame.K_z] and self.vy<0 else 0.4
        self.vy=min(self.vy+gv,12)
        self.x+=self.vx
        self.y+=self.vy
        self.r=pygame.Rect(int(self.x),int(self.y),self.w,self.h)
        self.grnd=0
        for b in blks:
            if not self.r.colliderect(b.r):
                continue
            bd=BLK.get(b.id,{})
            if bd.get("semi"):
                if self.vy>0 and self.r.bottom>b.r.top and self.r.bottom-self.vy<=b.r.top+8:
                    self.r.bottom=b.r.top
                    self.y=self.r.y
                    self.vy=0
                    self.grnd=1
                continue
            if self.vy>0 and self.r.bottom>b.r.top and self.r.bottom-self.vy<=b.r.top+8:
                self.r.bottom=b.r.top
                self.y=self.r.y
                self.vy=0
                self.grnd=1
                if bd.get("note"):
                    self.vy=-10
                    self.grnd=0
            elif self.vy<0 and self.r.top<b.r.bottom:
                self.r.top=b.r.bottom
                self.y=self.r.y
                self.vy=0
            if self.vx>0 and self.r.right>b.r.left and self.r.left<b.r.left:
                self.r.right=b.r.left
                self.x=self.r.x
                self.vx=0
            elif self.vx<0 and self.r.left<b.r.right and self.r.right>b.r.right:
                self.r.left=b.r.right
                self.x=self.r.x
                self.vx=0
        for n in npcs:
            if not n.act or not self.r.colliderect(n.r):
                continue
            d=NPC.get(n.id,{})
            if d.get("coin"):
                self.coins+=1
                self.score+=200
                n.act=0
            elif d.get("pwr"):
                if self.pwr==Pw.SM:
                    self.pwr=Pw.BIG
                    self.y-=22
                self.score+=1000
                n.act=0
            elif d.get("goal"):
                self.goal=1
            elif d.get("st"):
                if self.vy>0 and self.r.bottom<n.r.centery+8:
                    self.vy=-6.5
                    self.score+=100
                    n.act=0
                else:
                    self.dmg()
        if self.inv>0:
            self.inv-=1
        if self.y>1000:
            self.dead=1
            self.vy=-8
    
    def dmg(self):
        if self.inv>0:
            return
        if self.pwr==Pw.SM:
            self.dead=1
            self.vy=-8
        else:
            self.pwr=Pw.SM
            self.inv=120
    
    def draw(self,s,cam,o=(0,0)):
        if self.inv>0 and self.inv%6<3:
            return
        sp=cam.w2s((self.x,self.y),o)
        w,h=int(self.w*cam.z),int(self.h*cam.z)
        r=pygame.Rect(sp[0],sp[1],w,h)
        c1,c2=self.cc.get(self.ch,(C.R,C.B))
        pygame.draw.rect(s,c2,(r.x,r.y+h//3,w,h*2//3))
        pygame.draw.ellipse(s,(255,200,150),(r.x,r.y,w,h//2))
        pygame.draw.rect(s,c1,(r.x-2,r.y+2,w+4,h//6))

class Level:
    def __init__(self):
        self.blks=[]
        self.npcs=[]
        self.bgos=[]
        self.p1=(200,400)
    
    def desel(self):
        for o in self.blks+self.npcs+self.bgos:
            o.sel=0
    
    def delsel(self):
        self.blks=[b for b in self.blks if not b.sel]
        self.npcs=[n for n in self.npcs if not n.sel]
        self.bgos=[b for b in self.bgos if not b.sel]
    
    def at(self,p):
        for o in reversed(self.npcs+self.blks+self.bgos):
            if o.r.collidepoint(p):
                return o
        return None
    
    def save(self,f):
        with open(f,"w") as x:
            json.dump({"blks":[{"x":b.x,"y":b.y,"id":b.id}for b in self.blks],"npcs":[{"x":n.x,"y":n.y,"id":n.id}for n in self.npcs]},x)
    
    def load(self,f):
        if not os.path.exists(f):
            return
        with open(f) as x:
            d=json.load(x)
        self.blks=[Block(i["x"],i["y"],i["id"])for i in d.get("blks",[])]
        self.npcs=[Npc(i["x"],i["y"],i["id"])for i in d.get("npcs",[])]

class PalItem:
    def __init__(self,x,y,w,h,i,t,d):
        self.x,self.y,self.w,self.h=x,y,w,h
        self.id,self.t,self.d=i,t,d
        self.r=pygame.Rect(x,y,w,h)
        self.hov=0
        self.sel=0
    
    def draw(self,s):
        pygame.draw.rect(s,C.AC if self.sel else(C.GR if self.hov else(60,60,60)),self.r)
        pygame.draw.rect(s,C.EB,self.r,1)
        pr=pygame.Rect(self.x+4,self.y+4,self.w-8,self.h-14)
        oc=self.d.get("c",C.GR)
        if self.t=="blk":
            pygame.draw.rect(s,oc,pr)
        else:
            pygame.draw.ellipse(s,oc,pr)
        txt(s,str(self.id),(self.x+4,self.y+self.h-11),fs,(180,180,180))

class Game:
    def __init__(self):
        self.st=St.MENU
        self.lvl=Level()
        self.cam=Cam()
        self.p1=None
        self.ch1=Ch.MARIO
        self.msel=0
        self.esel=0
        self.psel=0
        self.crscr=0
        self.tool=Tl.BLK
        self.sblk=1
        self.snpc=1
        self.sbgo=1
        self.scat="All"
        self.pal=[]
        self.pscr=0
        self.grid=1
        self.pan=0
        self.pst=(0,0)
        self.cst=(0,0)
        self.eps=[{"n":"Demo Episode","c":["SMBX2 Recreation","","By Samsoft","","Press ESC"]}]
        self._bpal()
        self._demo()
    
    def _demo(self):
        self.lvl=Level()
        for i in range(60):
            self.lvl.blks.append(Block(i*GRID,480,181))
            self.lvl.blks.append(Block(i*GRID,512,182))
        for i in range(4):
            self.lvl.blks.append(Block(200+i*32,384,1))
        self.lvl.blks.append(Block(264,384,4))
        self.lvl.blks.append(Block(350,400,44))
        self.lvl.blks.append(Block(500,416,141))
        self.lvl.blks.append(Block(532,416,142))
        self.lvl.blks.append(Block(500,448,143))
        self.lvl.blks.append(Block(532,448,144))
        self.lvl.npcs.append(Npc(400,448,1))
        self.lvl.npcs.append(Npc(600,426,11))
        self.lvl.npcs.append(Npc(800,448,106))
        for i in range(6):
            self.lvl.npcs.append(Npc(200+i*32,320,171))
        self.lvl.npcs.append(Npc(1100,300,151))
        self.lvl.npcs.append(Npc(350,250,174))
        self.lvl.npcs.append(Npc(450,432,181))
        self.lvl.bgos.append(Bgo(100,400,1))
        self.lvl.bgos.append(Bgo(300,200,3))
        self.lvl.bgos.append(Bgo(600,150,5))
        self.lvl.npcs.append(Npc(1800,320,203))
    
    def _bpal(self):
        self.pal.clear()
        if self.tool==Tl.BLK:
            d,t=BLK,"blk"
        elif self.tool==Tl.NPC:
            d,t=NPC,"npc"
        elif self.tool==Tl.BGO:
            d,t=BGO,"bgo"
        else:
            return
        if self.scat!="All":
            d={k:v for k,v in d.items() if v.get("g","")==self.scat}
        for i,(oi,od) in enumerate(d.items()):
            x=5+(i%4)*45
            y=85+(i//4)*50-self.pscr
            self.pal.append(PalItem(x,y,42,46,oi,t,od))
    
    def _cats(self):
        if self.tool==Tl.BLK:
            cs=set(v.get("g","") for v in BLK.values())
        elif self.tool==Tl.NPC:
            cs=set(v.get("g","") for v in NPC.values())
        else:
            return ["All"]
        return ["All"]+sorted(cs)
    
    def run(self):
        go=1
        while go:
            for e in pygame.event.get():
                if e.type==pygame.QUIT:
                    go=0
                elif e.type==pygame.KEYDOWN:
                    self._key(e)
                elif e.type==pygame.MOUSEBUTTONDOWN:
                    self._md(e)
                elif e.type==pygame.MOUSEBUTTONUP:
                    self._mu(e)
                elif e.type==pygame.MOUSEMOTION:
                    self._mm(e)
                elif e.type==pygame.MOUSEWHEEL:
                    self._mw(e)
                elif e.type==pygame.VIDEORESIZE:
                    global SW,SH,screen
                    SW,SH=e.w,e.h
                    screen=pygame.display.set_mode((SW,SH),pygame.RESIZABLE)
            self._upd()
            self._drw()
            clock.tick(FPS)
        pygame.quit()
    
    def _key(self,e):
        if self.st==St.MENU:
            if e.key==pygame.K_UP:
                self.msel=(self.msel-1)%5
            elif e.key==pygame.K_DOWN:
                self.msel=(self.msel+1)%5
            elif e.key in [pygame.K_RETURN,pygame.K_z]:
                if self.msel==0:
                    self.st=St.EPISODE
                elif self.msel==1:
                    self.st=St.EPISODE
                elif self.msel==2:
                    self.st=St.EDITOR
                elif self.msel==3:
                    self.st=St.CREDITS
                    self.crscr=0
                elif self.msel==4:
                    pygame.quit()
                    sys.exit()
        elif self.st==St.EPISODE:
            if e.key in [pygame.K_RETURN,pygame.K_z]:
                self.st=St.CHAR
            elif e.key==pygame.K_ESCAPE:
                self.st=St.MENU
        elif self.st==St.CHAR:
            if e.key==pygame.K_LEFT:
                self.ch1=Ch((self.ch1-1)%5)
            elif e.key==pygame.K_RIGHT:
                self.ch1=Ch((self.ch1+1)%5)
            elif e.key in [pygame.K_RETURN,pygame.K_z]:
                self._start()
            elif e.key==pygame.K_ESCAPE:
                self.st=St.EPISODE
        elif self.st==St.PLAY:
            if e.key in [pygame.K_ESCAPE,pygame.K_p]:
                self.st=St.PAUSE
                self.psel=0
        elif self.st==St.PAUSE:
            if e.key==pygame.K_UP:
                self.psel=(self.psel-1)%3
            elif e.key==pygame.K_DOWN:
                self.psel=(self.psel+1)%3
            elif e.key in [pygame.K_RETURN,pygame.K_z]:
                if self.psel==0:
                    self.st=St.PLAY
                elif self.psel==1:
                    self._start()
                elif self.psel==2:
                    self.st=St.MENU
            elif e.key==pygame.K_ESCAPE:
                self.st=St.PLAY
        elif self.st==St.EDITOR:
            if e.key==pygame.K_DELETE:
                self.lvl.delsel()
            elif e.key==pygame.K_ESCAPE:
                self.lvl.desel()
            elif e.key==pygame.K_g:
                self.grid=1-self.grid
            elif e.key==pygame.K_F5:
                self._test()
            elif e.key==pygame.K_s and e.mod&pygame.KMOD_CTRL:
                self.lvl.save("level.json")
            elif e.key==pygame.K_F1:
                self.st=St.MENU
            elif e.key==pygame.K_1:
                self.tool=Tl.SEL
            elif e.key==pygame.K_2:
                self.tool=Tl.BLK
                self._bpal()
            elif e.key==pygame.K_3:
                self.tool=Tl.NPC
                self._bpal()
            elif e.key==pygame.K_4:
                self.tool=Tl.BGO
                self._bpal()
        elif self.st==St.CREDITS:
            if e.key==pygame.K_ESCAPE:
                self.st=St.MENU
        elif self.st in [St.CLEAR,St.OVER]:
            if e.key==pygame.K_RETURN:
                self.st=St.MENU
    
    def _md(self,e):
        if self.st!=St.EDITOR:
            return
        mx,my=e.pos
        PW=185
        if 30<=my<58:
            tools=[("Sel",Tl.SEL),("Era",Tl.ERA),("Blk",Tl.BLK),("NPC",Tl.NPC),("BGO",Tl.BGO)]
            x=10
            for n,t in tools:
                if x<=mx<x+42:
                    self.tool=t
                    if t in [Tl.BLK,Tl.NPC,Tl.BGO]:
                        self._bpal()
                    return
                x+=47
            if SW-65<=mx:
                self._test()
                return
        if mx<PW and my>58:
            self._palc(mx,my,e.button)
            return
        cx,cy=PW,58
        cw,ch=SW-PW,SH-cy-20
        if cx<=mx<cx+cw and cy<=my<cy+ch:
            wp=self.cam.s2w((mx,my),(cx,cy))
            wp=(int(wp[0]//GRID)*GRID,int(wp[1]//GRID)*GRID)
            if e.button==1:
                if self.tool==Tl.SEL:
                    o=self.lvl.at(wp)
                    self.lvl.desel()
                    if o:
                        o.sel=1
                elif self.tool==Tl.BLK:
                    self.lvl.blks.append(Block(int(wp[0]),int(wp[1]),self.sblk))
                elif self.tool==Tl.NPC:
                    self.lvl.npcs.append(Npc(int(wp[0]),int(wp[1]),self.snpc))
                elif self.tool==Tl.BGO:
                    self.lvl.bgos.append(Bgo(int(wp[0]),int(wp[1]),self.sbgo))
                elif self.tool==Tl.ERA:
                    o=self.lvl.at(wp)
                    if o:
                        o.sel=1
                        self.lvl.delsel()
            elif e.button==2:
                self.pan=1
                self.pst=(mx,my)
                self.cst=(self.cam.x,self.cam.y)
            elif e.button==3:
                o=self.lvl.at(wp)
                if o:
                    o.sel=1
                    self.lvl.delsel()
    
    def _mu(self,e):
        if e.button==2:
            self.pan=0
    
    def _mm(self,e):
        if self.st!=St.EDITOR:
            return
        mx,my=e.pos
        for i in self.pal:
            i.hov=i.r.collidepoint(mx,my) and my>85
        if self.pan:
            self.cam.x=self.cst[0]+(self.pst[0]-mx)/self.cam.z
            self.cam.y=self.cst[1]+(self.pst[1]-my)/self.cam.z
    
    def _mw(self,e):
        if self.st!=St.EDITOR:
            return
        mx,my=pygame.mouse.get_pos()
        if mx<185 and my>85:
            self.pscr=max(0,self.pscr-e.y*25)
            self._bpal()
        else:
            self.cam.z=clamp(self.cam.z*(1.1 if e.y>0 else 0.9),0.25,4)
    
    def _palc(self,mx,my,b):
        if b!=1:
            return
        cats=self._cats()
        tw=44
        for i,c in enumerate(cats[:8]):
            tx=5+(i%4)*(tw+2)
            ty=60+(i//4)*18
            if tx<=mx<tx+tw and ty<=my<ty+16:
                self.scat=c
                self.pscr=0
                self._bpal()
                return
        for i in self.pal:
            if i.r.collidepoint(mx,my) and i.r.y>85:
                for x in self.pal:
                    x.sel=0
                i.sel=1
                if i.t=="blk":
                    self.sblk=i.id
                elif i.t=="npc":
                    self.snpc=i.id
                elif i.t=="bgo":
                    self.sbgo=i.id
                return
    
    def _start(self):
        self._demo()
        self.p1=Player(self.lvl.p1[0],self.lvl.p1[1],self.ch1)
        for n in self.lvl.npcs:
            n.act=1
        self.cam.x=self.cam.y=0
        self.st=St.PLAY
    
    def _test(self):
        self.p1=Player(self.lvl.p1[0],self.lvl.p1[1],Ch.MARIO)
        for n in self.lvl.npcs:
            n.act=1
        self.cam.x=self.cam.y=0
        self.st=St.PLAY
    
    def _upd(self):
        if self.st==St.PLAY:
            keys=pygame.key.get_pressed()
            if self.p1 and not self.p1.dead:
                self.p1.update(keys,self.lvl.blks,self.lvl.npcs)
                if self.p1.goal:
                    self.st=St.CLEAR
                elif self.p1.dead:
                    self.p1.lives-=1
            if self.p1 and self.p1.dead and self.p1.y>SH+100:
                if self.p1.lives<=0:
                    self.st=St.OVER
                else:
                    self.p1=Player(self.lvl.p1[0],self.lvl.p1[1],self.ch1)
            for n in self.lvl.npcs:
                n.update(self.lvl.blks,self.p1)
            if self.p1:
                self.cam.follow(self.p1.x+12,self.p1.y+16)
        elif self.st==St.CREDITS:
            self.crscr+=1
    
    def _drw(self):
        if self.st==St.MENU:
            self._dmenu()
        elif self.st==St.EPISODE:
            self._depi()
        elif self.st==St.CHAR:
            self._dchar()
        elif self.st==St.PLAY:
            self._dgame()
        elif self.st==St.PAUSE:
            self._dgame()
            self._dpause()
        elif self.st==St.EDITOR:
            self._dedit()
        elif self.st==St.CREDITS:
            self._dcred()
        elif self.st==St.CLEAR:
            self._dclear()
        elif self.st==St.OVER:
            self._dover()
        pygame.display.flip()
    
    def _dmenu(self):
        grad(screen,(0,0,SW,SH),C.MB,(0,0,96))
        t=pygame.time.get_ticks()
        for i in range(12):
            bri=int(128+127*math.sin(t/300+i))
            pygame.draw.circle(screen,(bri,bri,bri),((i*97+t//50)%SW,(i*53)%(SH-100)+50),2)
        ti=fx.render("Super Mario Bros X2",1,C.W)
        sh=fx.render("Super Mario Bros X2",1,C.K)
        screen.blit(sh,(SW//2-ti.get_width()//2+3,53))
        screen.blit(ti,(SW//2-ti.get_width()//2,50))
        txt(screen,"v2.0",(SW//2+ti.get_width()//2-25,90),fs,(180,180,180))
        items=["1 Player Game","2 Player Game","Level Editor","Credits","Exit"]
        for i,it in enumerate(items):
            r=(SW//2-110,160+i*42,220,34)
            pygame.draw.rect(screen,(32,32,96),r)
            pygame.draw.rect(screen,C.SEL if i==self.msel else(128,128,192),r,2)
            txtc(screen,it,r,fm,C.SEL if i==self.msel else C.W)
        txt(screen,"(C) 2025 Samsoft/Team Flames",(10,SH-20),fs,(150,150,150))
        txt(screen,"Z=Select, Arrows=Navigate",(SW-190,SH-20),fs,(150,150,150))
    
    def _depi(self):
        grad(screen,(0,0,SW,SH),C.MB,(0,0,96))
        ti=fl.render("Select Episode",1,C.W)
        screen.blit(ti,(SW//2-ti.get_width()//2,30))
        for i,ep in enumerate(self.eps):
            r=(SW//2-140,100+i*50,280,40)
            pygame.draw.rect(screen,(32,32,96),r)
            pygame.draw.rect(screen,C.SEL if i==self.esel else(128,128,192),r,2)
            txt(screen,ep["n"],(r[0]+15,r[1]+10),fm,C.SEL if i==self.esel else C.W)
        txt(screen,"Z=Select, ESC=Back",(SW//2-70,SH-35),fs,(150,150,150))
    
    def _dchar(self):
        grad(screen,(0,0,SW,SH),C.MB,(0,0,96))
        ti=fl.render("Select Character",1,C.W)
        screen.blit(ti,(SW//2-ti.get_width()//2,30))
        chs=["Mario","Luigi","Peach","Toad","Link"]
        cols=[C.R,C.G,(255,192,203),C.R,(0,128,0)]
        for i,(n,c) in enumerate(zip(chs,cols)):
            x=50+i*145
            y=130
            r=(x,y,120,150)
            sel=i==self.ch1
            pygame.draw.rect(screen,(32,32,96),r)
            pygame.draw.rect(screen,C.SEL if sel else(128,128,192),r,3 if sel else 1)
            pygame.draw.ellipse(screen,c,(x+35,y+15,50,70))
            pygame.draw.ellipse(screen,(255,200,150),(x+40,y+25,40,30))
            txtc(screen,n,(x,y+110,120,30),fm,C.SEL if sel else C.W)
        txt(screen,"Z=Start, Left/Right=Select, ESC=Back",(SW//2-145,SH-35),fs,(150,150,150))
    
    def _dgame(self):
        screen.fill(C.SKY)
        for b in self.lvl.bgos:
            b.draw(screen,self.cam)
        for b in self.lvl.blks:
            b.draw(screen,self.cam)
        for n in self.lvl.npcs:
            n.draw(screen,self.cam)
        if self.p1:
            self.p1.draw(screen,self.cam)
        pygame.draw.rect(screen,C.K,(0,0,SW,32))
        if self.p1:
            chars=["MARIO","LUIGI","PEACH","TOAD","LINK"]
            txt(screen,chars[self.p1.ch],(15,3),fb,C.W)
            txt(screen,f"x{self.p1.lives}",(15,16),fs,C.W)
            pygame.draw.circle(screen,C.Y,(95,16),6)
            txt(screen,f"x{self.p1.coins:02d}",(105,8),fm,C.W)
            txt(screen,f"{self.p1.score:08d}",(170,8),fm,C.W)
            pwrs=["Small","Big","Fire","Leaf"]
            txt(screen,pwrs[self.p1.pwr],(300,8),fs,(180,180,180))
    
    def _dpause(self):
        s=pygame.Surface((SW,SH),pygame.SRCALPHA)
        s.fill((0,0,0,150))
        screen.blit(s,(0,0))
        ti=fl.render("PAUSED",1,C.W)
        screen.blit(ti,(SW//2-ti.get_width()//2,100))
        items=["Continue","Restart","Quit"]
        for i,it in enumerate(items):
            r=(SW//2-70,180+i*42,140,34)
            pygame.draw.rect(screen,(32,32,96),r)
            pygame.draw.rect(screen,C.SEL if i==self.psel else(128,128,192),r,2)
            txtc(screen,it,r,fm,C.SEL if i==self.psel else C.W)
    
    def _dedit(self):
        screen.fill(C.EP)
        PW=185
        cx,cy=PW,58
        cw,ch=SW-PW,SH-cy-20
        cv=pygame.Surface((cw,ch))
        cv.fill(C.SKY)
        if self.grid:
            for x in range(int(self.cam.x//GRID)*GRID,int(self.cam.x+cw/self.cam.z)+GRID,GRID):
                px=int((x-self.cam.x)*self.cam.z)
                pygame.draw.line(cv,(80,80,85) if x%128==0 else(60,60,65),(px,0),(px,ch))
            for y in range(int(self.cam.y//GRID)*GRID,int(self.cam.y+ch/self.cam.z)+GRID,GRID):
                py=int((y-self.cam.y)*self.cam.z)
                pygame.draw.line(cv,(80,80,85) if y%128==0 else(60,60,65),(0,py),(cw,py))
        for b in self.lvl.bgos:
            b.draw(cv,self.cam)
        for b in self.lvl.blks:
            b.draw(cv,self.cam)
        for n in self.lvl.npcs:
            n.draw(cv,self.cam)
        screen.blit(cv,(cx,cy))
        pygame.draw.rect(screen,(37,37,38),(0,0,SW,28))
        pygame.draw.line(screen,C.EB,(0,27),(SW,27))
        for i,m in enumerate(["File","Edit","View","Test"]):
            txt(screen,m,(10+i*50,6),fs,C.ET)
        pygame.draw.rect(screen,(37,37,38),(0,28,SW,30))
        pygame.draw.line(screen,C.EB,(0,57),(SW,57))
        tools=[("Sel",Tl.SEL),("Era",Tl.ERA),("Blk",Tl.BLK),("NPC",Tl.NPC),("BGO",Tl.BGO)]
        x=10
        for n,t in tools:
            btn(screen,(x,33,42,22),n,0,self.tool==t)
            x+=47
        btn(screen,(SW-65,33,55,22),"▶Play")
        pygame.draw.rect(screen,(37,37,38),(0,58,PW,SH-78))
        pygame.draw.line(screen,C.EB,(PW-1,58),(PW-1,SH-20))
        nms={Tl.BLK:"Blocks",Tl.NPC:"NPCs",Tl.BGO:"BGOs",Tl.SEL:"Select",Tl.ERA:"Erase"}
        txt(screen,nms.get(self.tool,""),(8,60),fb,C.W)
        if self.tool in [Tl.BLK,Tl.NPC,Tl.BGO]:
            cats=self._cats()
            tw=44
            for i,c in enumerate(cats[:8]):
                tx=5+(i%4)*(tw+2)
                ty=78+(i//4)*18
                act=self.scat==c
                pygame.draw.rect(screen,C.AC if act else(60,60,60),(tx,ty,tw,16))
                pygame.draw.rect(screen,C.EB,(tx,ty,tw,16),1)
                txtc(screen,c[:4],(tx,ty,tw,16),fs,C.W if act else(150,150,150))
        cr=pygame.Rect(0,100,PW,SH-120)
        for i in self.pal:
            if cr.colliderect(i.r):
                screen.set_clip(cr)
                i.draw(screen)
                screen.set_clip(None)
        pygame.draw.rect(screen,(37,37,38),(0,SH-20,SW,20))
        pygame.draw.line(screen,C.EB,(0,SH-20),(SW,SH-20))
        mx,my=pygame.mouse.get_pos()
        if mx>cx and 58<my<SH-20:
            wx,wy=self.cam.s2w((mx,my),(cx,cy))
            txt(screen,f"({int(wx)},{int(wy)})",(10,SH-17),fs,C.ET)
        txt(screen,f"Zoom:{int(self.cam.z*100)}%",(110,SH-17),fs,C.ET)
        txt(screen,f"Blk:{len(self.lvl.blks)} NPC:{len(self.lvl.npcs)}",(200,SH-17),fs,C.ET)
        txt(screen,"F5:Test F1:Menu G:Grid",(SW-170,SH-17),fs,(150,150,150))
    
    def _dcred(self):
        grad(screen,(0,0,SW,SH),C.MB,C.K)
        ti=fl.render("CREDITS",1,C.W)
        screen.blit(ti,(SW//2-ti.get_width()//2,30))
        crs=["","SUPER MARIO BROS X2","","Engine by","Samsoft / Team Flames","","Original SMBX by","Redigit","","SMBX2 by","Wohlstand & Team","","Press ESC"]
        y=100-self.crscr//3
        for ln in crs:
            if 50<y<SH-50:
                t=fm.render(ln,1,C.W)
                screen.blit(t,(SW//2-t.get_width()//2,y))
            y+=26
    
    def _dclear(self):
        grad(screen,(0,0,SW,SH),(0,64,0),(0,32,0))
        ti=fx.render("LEVEL CLEAR!",1,C.Y)
        screen.blit(ti,(SW//2-ti.get_width()//2,100))
        if self.p1:
            txt(screen,f"Score: {self.p1.score}",(SW//2-55,200),fl,C.W)
            txt(screen,f"Coins: {self.p1.coins}",(SW//2-55,235),fl,C.W)
        txt(screen,"Press ENTER",(SW//2-50,SH-70),fm,(150,150,150))
    
    def _dover(self):
        grad(screen,(0,0,SW,SH),(64,0,0),(32,0,0))
        ti=fx.render("GAME OVER",1,C.R)
        screen.blit(ti,(SW//2-ti.get_width()//2,SH//2-40))
        txt(screen,"Press ENTER",(SW//2-50,SH-70),fm,(150,150,150))

if __name__=="__main__":
    print("╔════════════════════════════════════════════════╗")
    print("║  Super Mario Bros X2 v2.0                      ║")
    print("║  Complete Recreation with Editor               ║")
    print("║  (C) 2025 Samsoft / Team Flames                ║")
    print("╚════════════════════════════════════════════════╝")
    print("\nFeatures: Menu, Episodes, 5 Characters, Editor")
    print("Controls: Arrows=Move, Z=Jump, P=Pause, F5=Test")
    Game().run()
