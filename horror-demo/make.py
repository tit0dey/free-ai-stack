from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np, math, subprocess, wave, os
import imageio_ffmpeg
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));os.chdir(ROOT)
FF=imageio_ffmpeg.get_ffmpeg_exe(); W,H=540,960; FPS=30; DUR=34; SR=48000
fontpath='assets/fonts/archivo-black-latin-400-normal.ttf'
def font(s):return ImageFont.truetype(fontpath,s)
def txt(d,xy,s,size=24,fill='white',anchor='mm'):d.text(xy,s,font=font(size),fill=fill,anchor=anchor,stroke_width=0)
def boy(im,x,y,scale=1,walk=0,scared=False):
 l=Image.new('RGBA',(180,320));d=ImageDraw.Draw(l); ink='#101424';skin='#dba486'
 # limbs, pajama and hair
 a=math.sin(walk)*12
 d.line((72,230,65+a,291),fill=ink,width=24);d.line((108,230,118-a,291),fill=ink,width=24)
 d.line((57+a,294,79+a,294),fill='#8994aa',width=15);d.line((108-a,294,131-a,294),fill='#8994aa',width=15)
 d.rounded_rectangle((48,143,130,245),20,fill='#55889c',outline=ink,width=5)
 d.line((50,160,32,215),fill=skin,width=16);d.line((129,160,150,202),fill=skin,width=16)
 d.ellipse((33,30,146,157),fill=skin,outline=ink,width=5)
 d.polygon([(35,90),(29,44),(57,20),(112,20),(151,48),(144,98),(128,62),(107,76),(92,52),(69,75),(58,62)],fill='#242333')
 for ex in [68,115]:
  d.ellipse((ex-11,88,ex+10,113),fill='white');d.ellipse((ex-3,93,ex+5,110),fill='#18202c')
 if scared:d.ellipse((85,122,100,142),fill='#32212a')
 else:d.arc((78,120,105,136),0,160,fill=ink,width=3)
 d.rectangle((143,193,162,220),fill='#e4c769',outline=ink,width=3)
 l=l.resize((int(180*scale),int(320*scale)),Image.Resampling.LANCZOS);im.alpha_composite(l,(int(x-l.width/2),int(y-l.height)))

def scene(t):
 im=Image.new('RGB',(W,H),'#0b1020');d=ImageDraw.Draw(im)
 flick=1 if not (int(t*19)%39==0 and t>7) else .45
 # hallway perspective
 d.polygon([(0,100),(190,260),(190,660),(0,900)],fill='#20283c');d.polygon([(540,100),(350,260),(350,660),(540,900)],fill='#182034')
 d.rectangle((190,260,350,665),fill='#252a39');d.polygon([(0,900),(190,660),(350,660),(540,900),(540,960),(0,960)],fill='#292a38')
 for y in [690,735,795,880]:d.line((0,y,540,y),fill='#42404a',width=2)
 for xx in [-600,-200,150,390,740,1140]:d.line((270,660,xx,960),fill='#101523',width=3)
 for xx in [45,430]:
  d.polygon([(xx,260),(xx+53,300),(xx+53,635),(xx,700)],fill='#0b1020',outline='#535166')
 # ceiling light
 d.polygon([(245,170),(295,170),(308,185),(232,185)],fill='#aaa485')
 d.ellipse((245,175,295,189),fill='#e9dfae' if flick==1 else '#756c51')
 # end door and animated hinge
 d.rectangle((208,370,334,665),fill='#090c16',outline='#8a7766',width=7)
 opening=max(0,min(1,(t-18)/3));right=330-100*opening
 d.polygon([(214,376),(right,376+20*opening),(right,660-10*opening),(214,660)],fill='#5b4c4f',outline='#aa8270')
 if opening<.9:d.ellipse((right-19,514,right-10,525),fill='#dcc080')
 if t<18:
  txt(d,(270,430),'017',16,'#cdbd9a')
 if t>20:
  # stairs into darkness
  for j in range(7):d.line((230+j*4,590+j*9,329,590+j*9),fill='#373646',width=3)
 if t>24:
  u=min(1,(t-24)/2);cx=292;cy=474
  d.ellipse((cx-22*u,cy-44*u,cx+22*u,cy+20*u),fill='#070910')
  d.polygon([(cx-18*u,cy),(cx+18*u,cy),(cx+38*u,635),(cx-38*u,635)],fill='#070910')
  if t>25:
   d.ellipse((281,466,286,471),fill='#f1c08b');d.ellipse((300,466,305,471),fill='#f1c08b')
 im=im.convert('RGBA')
 if t<7:
  boy(im,260+math.sin(t*1.1)*5,870,.83,t*5,False)
 elif t<18:
  boy(im,145+min(1,(t-7)/9)*24,906,.96,t*6,t>11)
 else:boy(im,126,930,1.05,0,True)
 # flashlight cone soft layer
 light=Image.new('RGBA',(W,H));ld=ImageDraw.Draw(light);ld.polygon([(181,818),(233,426),(327,573)],fill=(255,222,145,17));light=light.filter(ImageFilter.GaussianBlur(10));im=Image.alpha_composite(im,light)
 d=ImageDraw.Draw(im)
 d.rectangle((0,0,W,105),fill='#080c16');txt(d,(270,38),'THE DOOR AT 3:17',28,'#e8dfcb');txt(d,(270,78),'AN ORIGINAL ANIMATED HORROR SHORT',10,'#8d9aaa')
 if t<6:
  d.rounded_rectangle((339,694,505,759),9,fill='#101522',outline='#596171',width=2);txt(d,(422,727),'3:17 AM',25,'#de705e')
 captions=[(1,5.5,['Three seventeen a.m.','I heard it again.']),(7,11.5,['Scratching.','Coming from the hallway.']),(12.2,17.8,['There was a door','I had never seen before.']),(18.4,21.5,['So I opened it.']),(24,28,['We don’t have a basement.']),(30,33,['Sleep well.'])]
 for a,b,lines in captions:
  if a<=t<b:
   yy=824;d.rounded_rectangle((24,yy,516,yy+48+27*(len(lines)-1)),10,fill=(5,9,18,240),outline='#566071',width=1)
   for j,line in enumerate(lines):txt(d,(270,yy+25+j*27),line,20,'#ffe4c5')
 # end blackout
 if t>=29:
  im=Image.new('RGBA',(W,H),'#070910');d=ImageDraw.Draw(im)
  txt(d,(270,405),'WE DON’T HAVE',30,'#eee2cc');txt(d,(270,453),'A BASEMENT.',38,'#d46b5b')
  if t>=30:txt(d,(270,560),'Sleep well.',22,'#9ba1ad')
  txt(d,(270,893),'2D HORROR • STYLE DEMO',13,'#676c7b')
 # subtle handheld
 if 21<t<22 or 26<t<26.5:
  im=im.transform(im.size,Image.Transform.AFFINE,(1,0,int(math.sin(t*105)*5),0,1,int(math.cos(t*94)*5)))
 return im.convert('RGB')

# Audio: synthesized original ambience / foley + existing narration
rng=np.random.default_rng(917);N=SR*DUR;out=np.zeros(N);tt=np.arange(N)/SR
out+=.026*np.sin(2*np.pi*43*tt)+.013*np.sin(2*np.pi*64.7*tt);out*=.7+.3*np.sin(tt*.4)**2
noise=rng.normal(0,1,N);out+=.006*np.convolve(noise,np.ones(120)/120,mode='same')
def add(v,at,g=1):
 k=int(at*SR);n=min(len(v),N-k)
 if n>0:out[k:k+n]+=v[:n]*g
for k in np.arange(3,18,.72):
 x=np.arange(int(.18*SR))/SR;add((rng.normal(0,1,len(x))*.16+np.sin(x*2*np.pi*85)*.3)*np.exp(-x*29),k,.55)
for k in [7,7.55,8.1,10.3,13.2,14,16.5]:
 x=np.arange(int(.38*SR))/SR;add(rng.normal(0,1,len(x))*.13*(.5+.5*np.sin(x*145))*np.sin(np.pi*x/.38)**2,k)
x=np.arange(3*SR)/SR;add((np.sin(2*np.pi*(180*x+40*x*x))+.3*rng.normal(0,1,len(x)))*np.sin(np.pi*x/3)*.06,18)
for k in np.arange(21.5,29,.68):
 for dt in [0,.16]:
  x=np.arange(int(.16*SR))/SR;add(np.sin(2*np.pi*55*x)*np.exp(-x*35),k+dt,.18)
x=np.arange(int(1.8*SR))/SR;add((np.sin(2*np.pi*(65*x-10*x*x))*.5+rng.normal(0,1,len(x))*.15)*np.exp(-x*3),26,.65)
for i,at in enumerate([1,7,12.2,18.4,24,30],1):
 data=subprocess.run([FF,'-v','error','-i',f'titonomics-video/vo4/h{i}.mp3','-ar',str(SR),'-ac','1','-f','f32le','-'],capture_output=True,check=True).stdout
 v=np.frombuffer(data,dtype=np.float32);start=int(at*SR);end=min(N,start+len(v));out[start:end]*=.32;add(v,at,.95)
out=np.tanh(out*1.15)*.88
with wave.open('horror-demo/mix.wav','wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes((out*32767).astype('int16').tobytes())
p=subprocess.Popen([FF,'-y','-v','error','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s','540x960','-r','30','-i','-','-i','horror-demo/mix.wav','-vf','scale=1080:1920:flags=lanczos','-c:v','libx264','-preset','fast','-crf','21','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart','-shortest','HORROR_2D_DEMO.mp4'],stdin=subprocess.PIPE)
for n in range(int(DUR*FPS)):
 p.stdin.write(scene(n/FPS).tobytes())
 if n%150==0:print('frame',n,flush=True)
p.stdin.close();assert p.wait()==0
scene(25.5).save('horror-demo/preview.png');print('DONE',flush=True)
