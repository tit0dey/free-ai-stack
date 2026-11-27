from PIL import Image,ImageDraw,ImageFont
import math,numpy as np,subprocess,wave,os
import imageio_ffmpeg
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
W,H=320,180;FPS=30;DUR=26;SR=48000;FF=imageio_ffmpeg.get_ffmpeg_exe();rng=np.random.default_rng(8)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf',8)
small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf',7)
P={'ink':'#242331','skin':'#f5bf86','hair':'#332b3d','blue':'#5288dc','pants':'#353960','shoe':'#f2e9cb'}
def text(d,xy,s,col='#fff1cc',f=font):d.text(xy,s,font=f,fill=col)
def box(d,x,y,lines,who=''):
 width=max(d.textbbox((0,0),s,font=font)[2] for s in lines)+12;width=min(width,310);x=max(4,min(316-width,int(x)));h=12*len(lines)+8
 d.rectangle((x+2,y+2,x+width+2,y+h+2),fill='#242331');d.rectangle((x,y,x+width,y+h),fill='#fff1cc',outline='#242331',width=2)
 for i,s in enumerate(lines):text(d,(x+6,y+5+i*12),s,'#242331')
 d.polygon([(x+16,y+h-1),(x+23,y+h+6),(x+25,y+h-1)],fill='#fff1cc')
def kid(d,x,y,t,run=False,shock=False,pose=False):
 x=int(x);y=int(y);a=int(math.sin(t*(22 if run else 10))*4) if run else 0
 # shadow
 d.ellipse((x-10,y-2,x+12,y+2),fill='#695c69')
 d.rectangle((x-6,y-14,x-1,y-4),fill=P['pants']);d.rectangle((x+3,y-14,x+8,y-4),fill=P['pants'])
 d.rectangle((x-8+a,y-5,x-1+a,y),fill=P['shoe']);d.rectangle((x+3-a,y-5,x+10-a,y),fill=P['shoe'])
 d.rectangle((x-9,y-32,x+10,y-15),fill=P['ink']);d.rectangle((x-7,y-31,x+8,y-16),fill=P['blue']);d.rectangle((x-2,y-30,x+2,y-18),fill='#8dc5f5')
 if pose:
  d.rectangle((x-13,y-31,x-9,y-24),fill=P['skin']);d.rectangle((x+10,y-37,x+14,y-25),fill=P['skin'])
 else:
  d.rectangle((x-12,y-29+a,x-8,y-17+a),fill=P['skin']);d.rectangle((x+9,y-29-a,x+13,y-17-a),fill=P['skin'])
 d.rectangle((x-10,y-51,x+10,y-32),fill=P['ink']);d.rectangle((x-8,y-49,x+9,y-34),fill=P['skin'])
 d.rectangle((x-11,y-52,x+8,y-46),fill=P['hair']);d.rectangle((x-8,y-55,x+4,y-50),fill=P['hair']);d.rectangle((x-10,y-47,x-6,y-40),fill=P['hair'])
 for xx in [-3,5]:
  d.rectangle((x+xx,y-43,x+xx+2,y-40),fill=P['ink'])
 if shock:d.rectangle((x,y-37,x+3,y-34),fill=P['ink'])
 else:d.line((x,y-36,x+4,y-36),fill='#a75a57')
def cat(d,x,y,t,food=False):
 x=int(x);y=int(y);a=int(math.sin(t*24)*3)
 d.ellipse((x-11,y-3,x+13,y+2),fill='#695c69');d.rectangle((x-9,y-14,x+8,y-5),fill='#dc9755')
 d.rectangle((x-12,y-18,x-9,y-10),fill='#dc9755');d.rectangle((x-16,y-20,x-9,y-17),fill='#dc9755')
 for xx in [-6,5]:d.rectangle((x+xx+a,y-5,x+xx+3+a,y),fill='#f0c480')
 d.rectangle((x+5,y-24,x+18,y-11),fill='#ecb76c');d.polygon([(x+5,y-23),(x+5,y-29),(x+10,y-23)],fill='#ecb76c');d.polygon([(x+13,y-23),(x+18,y-29),(x+18,y-21)],fill='#ecb76c')
 d.point((x+11,y-18),fill='#242331');d.point((x+17,y-18),fill='#242331');d.rectangle((x+17,y-14,x+20,y-12),fill='#73423d')
 if food:samosa(d,x+25,y-10)
def samosa(d,x,y):
 x=int(x);y=int(y);d.polygon([(x-6,y+3),(x,y-7),(x+7,y+3)],fill='#ffd36c',outline='#9f5b36');d.point((x,y-2),fill='#b97b43');d.point((x+3,y+1),fill='#b97b43')
def shop(d,t):
 d.rectangle((154,58,298,135),fill='#78536b',outline='#352f49',width=2);d.rectangle((162,72,289,109),fill='#3c384d')
 for x in range(154,300,18):d.rectangle((x,51,x+17,64),fill='#f38d72' if (x//18)%2 else '#ffe1a0');d.rectangle((x,64,x+17,68),fill='#bf5b62' if (x//18)%2 else '#e7b86f')
 d.rectangle((177,35,275,52),fill='#3e3c56',outline='#ffe1a0',width=2);text(d,(185,39),'SAMO-SA GOOD!')
 # vendor
 d.rectangle((237,82,258,111),fill='#f6e2b4');d.rectangle((238,68,254,84),fill='#e9ae7a');d.rectangle((236,65,256,70),fill='#fff1cc');d.rectangle((241,76,243,77),fill='#242331');d.rectangle((250,76,252,77),fill='#242331');d.rectangle((242,80,252,82),fill='#594344')
 d.rectangle((155,110,298,123),fill='#d8a06b',outline='#473447',width=2);d.rectangle((164,124,288,135),fill='#a66d55')
 d.rectangle((167,91,212,108),fill='#fff1cc');text(d,(170,95),'Rs.10','#4b3c52')
 d.ellipse((217,110,237,115),fill='#dce6dd')
def frame(t):
 im=Image.new('RGB',(W,H),'#a0bdd1');d=ImageDraw.Draw(im)
 # distant town
 d.rectangle((0,78,320,141),fill='#798aa2')
 for j in range(9):
  x=j*42-8;top=39+(j*19)%39;d.rectangle((x,top,x+33,121),fill=['#a99daa','#8c95ae','#b3a0aa'][j%3])
  for yy in range(top+8,118,18):
   for xx in [x+6,x+20]:d.rectangle((xx,yy,xx+6,yy+8),fill='#64798c')
 d.rectangle((0,132,320,148),fill='#d4bb9e');d.rectangle((0,149,320,180),fill='#575c78');d.line((0,148,320,148),fill='#fff0c5',width=2)
 for xx in range(0,320,50):d.rectangle((xx,168,xx+26,170),fill='#c6bfae')
 # tree and bench
 d.rectangle((16,90,22,135),fill='#665263');d.rectangle((4,65,35,96),fill='#537e74');d.rectangle((0,74,43,88),fill='#537e74')
 d.rectangle((39,119,86,124),fill='#926853');d.rectangle((43,125,46,139),fill='#594c54');d.rectangle((80,125,83,139),fill='#594c54')
 shop(d,t)
 if t<5:
  x=54+min(t/3,1)*55;kid(d,x,145,t,run=t<3)
  samosa(d,228,107);box(d,17,14,['Bhaiya! Last samosa mera!'])
  if t>3:cat(d,37,145,t)
 elif t<10:
  kid(d,109,145,t,pose=True);cat(d,40+(t-5)*24,145,t);samosa(d,228,107)
  box(d,13,12,['Wallet: 9 rupees.','Confidence: 100 rupees.'])
  if t>7:
   for j in range(3):d.rectangle((127+j*8,125-(j%2)*4,131+j*8,129-(j%2)*4),fill='#f7cf6d')
 elif t<13:
  kid(d,109,145,t,shock=t>11)
  q=(t-10)/3;cx=168+q*61;cy=145-math.sin(q*math.pi)*53;cat(d,cx,cy,t,food=t>11.5)
  if t<=11.5:samosa(d,228,107)
  box(d,12,11,['Processing payment...'])
 elif t<18:
  q=(t-13)/5;cx=230+q*115;kx=109+q*150
  cat(d,cx,145,t,True);kid(d,kx,145,t,run=True,shock=True)
  for j in range(3):d.line((int(kx)-30-j*7,119+j*5,int(kx)-18-j*7,119+j*5),fill='#f8e3b0')
  box(d,14,12,['ARRE! MERA SAMOSAAA!'])
 elif t<22:
  kid(d,138,145,t,shock=True,pose=True);cat(d,283,145,t,True)
  box(d,12,12,['Usne paise bhi nahi diye!'])
  if t>19.4:box(d,168,77,['Woh regular hai.'])
 else:
  kid(d,138,145,t,shock=True);cat(d,280,145,t,False)
  box(d,10,12,['CAT: 1     HUMAN: 0'])
  if t>23:box(d,29,69,['UPI? Nah.','United Paws of India.'])
 # game UI footer
 d.rectangle((0,173,320,179),fill='#302b46');text(d,(5,173),'THE LAST SAMOSA  /  ORIGINAL PIXEL COMEDY',f=small)
 return im
# chiptune background, no sampled audio
N=SR*DUR;out=np.zeros(N)
def add(v,at,g=1):
 k=int(at*SR);n=min(len(v),N-k)
 if n>0:out[k:k+n]+=v[:n]*g

def tone(at,hz,dur=.1,g=.07,kind='square'):
 x=np.arange(int(dur*SR))/SR;ph=2*np.pi*hz*x
 v=(np.sign(np.sin(ph)) if kind=='square' else np.sin(ph));v*=np.minimum(1,x/.006)*np.minimum(1,(dur-x)/.025);add(v,at,g)
notes=[261.63,329.63,392,329.63,293.66,349.23,440,392]
for j,at in enumerate(np.arange(0,DUR,.24)):
 tone(at,notes[j%8],.14,.019);tone(at,notes[(j//4)%8]/2,.18,.021,'sine')
 if j%2==0:
  x=np.arange(int(.07*SR))/SR;add(rng.normal(0,1,len(x))*np.exp(-x*75),at,.018)
# retro dialogue blips
for a,b in [(0,1.5),(5,6.8),(10,11),(13,14.5),(18,19.3),(19.6,20.5),(22,22.8),(23,24.4)]:
 for at in np.arange(a,b,.09):tone(at,float(rng.choice([540,650,730,820])),.035,.028)
for at in [7.2,7.5,7.8]:
 tone(at,987,.08,.065);tone(at+.07,1318,.16,.055)
# jump ascending, landing, chase footsteps
for j in range(9):tone(10+j*.055,300+j*75,.055,.052)
for at in np.arange(13,18,.19):tone(at,110,.045,.065,'sine')
# alarm, meow-like descending glide
for at in [12.2,15.5,22.9]:
 x=np.arange(int(.35*SR))/SR;v=np.sin(2*np.pi*(950*x-750*x*x))*np.sin(np.pi*x/.35);add(v,at,.09)
for j,hz in enumerate([523,659,784,1046]):tone(22+j*.12,hz,.2,.07)
for j,hz in enumerate([392,349,311,196]):tone(24.5+j*.18,hz,.2,.075)
out=np.tanh(out)*.85
with wave.open('pixel-demo/audio.wav','wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes((out*32767).astype('int16').tobytes())
p=subprocess.Popen([FF,'-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','320x180','-r','30','-i','-','-i','pixel-demo/audio.wav','-vf','scale=1920:1080:flags=neighbor','-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart','-shortest','FUNNY_PIXEL_SAMOSA.mp4'],stdin=subprocess.PIPE)
for n in range(FPS*DUR):p.stdin.write(frame(n/FPS).tobytes())
p.stdin.close();assert p.wait()==0
sh=Image.new('RGB',(960,360))
for j,t in enumerate([2,8,11.8,15,20,24]):sh.paste(frame(t),((j%3)*320,(j//3)*180))
sh.resize((1440,540),Image.Resampling.NEAREST).save('pixel-demo/preview.png');print('done')
