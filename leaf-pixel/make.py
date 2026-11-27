"""Original pixel-art photosynthesis visual study. Deliberately simplified, not molecular scale."""
from PIL import Image, ImageDraw,ImageFont
import numpy as np, math,subprocess,wave,os
import imageio_ffmpeg
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FF=imageio_ffmpeg.get_ffmpeg_exe();W,H=270,480;FPS=30;DUR=12;SR=48000;rng=np.random.default_rng(79)
F='/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf';B='/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'
def tx(d,p,s,n=8,c='#d8f6bd',a=None):d.text(p,s,font=ImageFont.truetype(B,n),fill=c,anchor=a)
def pill(d,box,s):d.rectangle(box,fill='#0c211c',outline='#5a8f6a');tx(d,((box[0]+box[2])//2,(box[1]+box[3])//2),s,8,a='mm')
def chloro(d,x,y,s=1,t=0):
 x=int(x);y=int(y);rw=int(23*s);rh=int(12*s)
 d.ellipse((x-rw-2,y-rh-2,x+rw+2,y+rh+2),fill='#173e29',outline='#a4cd6b',width=max(1,int(s)))
 d.ellipse((x-rw,y-rh,x+rw,y+rh),fill='#629b44');d.arc((x-rw,y-rh,x+rw,y+rh),190,320,fill='#bdd77e',width=max(1,int(s)))
 for j in [-1,0,1]:
  xx=x+int(j*12*s)
  for k in range(3):
   yy=y+int((k*3-3)*s);d.rectangle((xx-int(4*s),yy,xx+int(4*s),yy+max(1,int(s))),fill=['#193d27','#a9cb67','#305e33'][k])
  if j<1:d.line((xx,y,xx+int(11*s),y),fill='#b6d376',width=max(1,int(s)))
# prebuild organic plant cell lattice
base=Image.new('RGB',(W,H),'#1c3528');d=ImageDraw.Draw(base)
centres=[]
for row in range(-1,7):
 for col in range(-1,4):
  x=col*99+(row%2)*48;y=row*89
  p=[(x-46,y-30),(x-5,y-45),(x+44,y-24),(x+48,y+21),(x+9,y+44),(x-45,y+25)]
  d.polygon(p,fill=['#405e37','#4c693d','#3b5935'][(row+col)%3]);d.line(p+[p[0]],fill='#aec58a',width=5);d.line(p+[p[0]],fill='#385131',width=1)
  d.ellipse((x-26,y-25,x+26,y+23),fill='#75905a',outline='#8eaa6c',width=2)
  d.ellipse((x-21,y-21,x+25,y+21),fill='#6f8955')
  d.ellipse((x+20,y+13,x+33,y+26),fill='#a19b72',outline='#cfcb8f');d.ellipse((x+25,y+17,x+29,y+21),fill='#555d3d')
  centres.extend([(x-23,y-27),(x+23,y-17),(x-22,y+24)])
for j in range(2000):
 x=int(rng.integers(W));y=int(rng.integers(H));d.point((x,y),fill=['#557443','#5e7d4b','#344c30'][j%3])
for x,y in centres:chloro(d,x,y,.56)
# subtle base pixel grain
arr=np.asarray(base).astype('int16');noise=rng.integers(-4,5,(H,W,1));base=Image.fromarray(np.uint8(np.clip(arr+noise,0,255)))

def frame(t):
 if t<3.6:
  # leaf macro drawn at pixel resolution, vein branches, shaded serrated body
  im=Image.new('RGB',(W,H),'#0d1c1c');d=ImageDraw.Draw(im)
  for x in range(0,W,20):d.line((x,0,x,H),fill='#142825')
  for y in range(0,H,20):d.line((0,y,W,y),fill='#142825')
  # sun rays
  for j in range(8):
   x=int((j*51+t*37)%400)-70;y=int((j*67+t*61)%320)-30
   d.line((x,y,x+22,y+38),fill='#e5d183',width=2)
  mask=Image.new('L',(W,H));md=ImageDraw.Draw(mask)
  outline=[(193,105),(195,151),(208,183),(200,214),(204,241),(189,260),(183,289),(162,303),(145,328),(119,338),(89,364),(72,336),(55,318),(55,288),(44,263),(53,236),(51,210),(66,192),(72,168),(96,159),(111,140),(137,136),(159,118)]
  md.polygon(outline,fill=255)
  yy,xx=np.mgrid[:H,:W];v=28+22*np.sin(xx*.017)+12*np.cos(yy*.023)+rng.integers(-3,4,(H,W))
  a=np.zeros((H,W,3),dtype=np.uint8);a[:,:,0]=np.clip(v*.65,0,255);a[:,:,1]=np.clip(v*2.25,0,255);a[:,:,2]=np.clip(v*.8,0,255)
  im.paste(Image.fromarray(a),(0,0),mask);d=ImageDraw.Draw(im);d.line(outline+[outline[0]],fill='#99bd66',width=1)
  d.line((73,394,90,352,127,270,161,193,193,105),fill='#abc67a',width=3)
  for j in range(8):
   y=166+j*23;x=166-j*9
   d.line((x,y,x-34,y-10,x-58,y-26),fill='#7ca857',width=1);d.line((x,y,x+20,y-2,x+36,y-17),fill='#7ca857',width=1)
  # zoom targeting box
  if t>1.8:
   d.rectangle((104,213,157,266),outline='#e5e4ae',width=1);d.line((158,239,224,239,224,281),fill='#e5e4ae');tx(d,(164,287),'ZOOM IN',8)
  pill(d,(16,47,168,67),'01 / THE SOLAR FACTORY')
  tx(d,(22,414),'SUNLIGHT IN.',15);tx(d,(22,437),'LIFE OUT.',15,'#e9d993')
 elif t<7.3:
  # slow tracking through mesophyll cells
  q=(t-3.6)/3.7;zoom=1+q*.18
  big=base.resize((int(W*zoom),int(H*zoom)),Image.Resampling.NEAREST)
  im=big.crop((int(10*q),int(30*q),int(10*q)+W,int(30*q)+H));d=ImageDraw.Draw(im)
  for j in range(13):
   x=int((j*59+t*12)%W);y=int((j*43+t*8)%H);d.rectangle((x,y,x+1,y+1),fill='#d2d397')
  pill(d,(15,47,160,67),'02 / INSIDE A LEAF')
  d.line((167,250,224,215,254,215),fill='#f1e7b7');pill(d,(169,189,257,208),'CHLOROPLAST')
  d.rectangle((12,407,258,467),fill='#10271f');tx(d,(23,418),'Millions of tiny',10);tx(d,(23,435),'light-powered workshops.',10,'#dfde9f')
 else:
  im=Image.new('RGB',(W,H),'#10291f');d=ImageDraw.Draw(im)
  # stroma pixel texture
  for j in range(380):
   x=(j*71)%W;y=(j*137)%H;d.rectangle((x,y,x+1,y+1),fill=['#163724','#1b3e29','#24452c'][j%3])
  d.ellipse((-89,98,359,422),fill='#385f34',outline='#aed184',width=4)
  d.ellipse((-80,107,350,412),outline='#729b52',width=3)
  # granum stacks with strong rim lighting, shadows and connectors
  for cx,cy in [(48,240),(135,280),(222,220)]:
   d.line((cx,cy,cx+80,cy+29),fill='#b3be68',width=3)
   for k in range(7):
    y=cy-42+k*12
    d.rectangle((cx-29,y,cx+28,y+7),fill='#1c3823',outline='#8daf58');d.ellipse((cx-30,y-5,cx+29,y+4),fill='#739f49',outline='#b7d17b');d.line((cx-20,y-2,cx+14,y-2),fill='#91b65b')
  # photons arrive, energy pulses around stacks, oxygen bubbles leave
  for j in range(7):
   x=int((j*47+t*30)%330)-30;y=int((j*62+t*59)%260)-20
   d.line((x,y,x+13,y+23),fill='#f2d778',width=2)
   if 160<y<210:d.rectangle((x-3,y-3,x+3,y+3),outline='#fff1b5')
  for j in range(11):
   x=int((j*47+math.sin(t+j)*5)%W);y=int(380-((t-7.3)*32+j*41)%245)
   d.ellipse((x-3,y-3,x+3,y+3),outline='#d6efcf');d.point((x-1,y-1),fill='#ffffff')
  pill(d,(15,47,222,67),'03 / POWERED BY SUNLIGHT')
  d.rectangle((12,405,258,467),fill='#0b2019')
  tx(d,(22,415),'LIGHT + WATER + CO2',11,'#f0d981');tx(d,(22,438),'SUGAR + OXYGEN',13,'#c2e6a1')
  if t>10.4:pill(d,(59,365,211,385),'O2 RELEASED',)
 d=ImageDraw.Draw(im);d.rectangle((0,0,W,33),fill='#0b1918');tx(d,(14,11),'THE HIDDEN GREEN WORLD',10)
 d.rectangle((0,473,W,480),fill='#0b1918');tx(d,(12,474),'SIMPLIFIED SCIENCE / PIXEL STUDY',6,'#95ad96')
 return im
N=SR*DUR;out=np.zeros(N);rng=np.random.default_rng(8)
def add(v,at):
 s=int(at*SR);n=min(len(v),N-s)
 if n>0:out[s:s+n]+=v[:n]
for at in np.arange(0,DUR,.42):
 x=np.arange(int(.7*SR))/SR;hz=[196,246.94,293.66,369.99][int(at/.42)%4];add(np.sin(2*np.pi*hz*x)*np.exp(-x*8)*.035,at)
for at in [3.6,7.3]:
 x=np.arange(int(.5*SR))/SR;add(rng.normal(0,1,len(x))*np.sin(np.pi*x/.5)**2*.025,at-.2)
for at in np.arange(7.5,11.8,.37):
 x=np.arange(int(.16*SR))/SR;add(np.sin(2*np.pi*(900*x-1400*x*x))*np.exp(-x*25)*.075,at)
with wave.open('leaf-pixel/sfx.wav','wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes((np.tanh(out)*28000).astype('int16').tobytes())
p=subprocess.Popen([FF,'-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','270x480','-r','30','-i','-','-i','leaf-pixel/sfx.wav','-vf','scale=2160:3840:flags=neighbor','-c:v','libx264','-preset','ultrafast','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart','-shortest','LEAF_PIXEL_4K_TEST.mp4'],stdin=subprocess.PIPE)
for n in range(DUR*FPS):
 p.stdin.write(frame(n/FPS).tobytes())
p.stdin.close();assert p.wait()==0
sh=Image.new('RGB',(810,480))
for j,t in enumerate([2.8,5.5,10]):sh.paste(frame(t),(j*270,0))
sh.save('leaf-pixel/preview.png');print('DONE')
