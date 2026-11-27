"""Object Witness: original fictional phone POV opening; generated Hindi narrator."""
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import numpy as np, subprocess,math,wave,json,os
import imageio_ffmpeg
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FF=imageio_ffmpeg.get_ffmpeg_exe();W,H=1280,720;FPS=30;DUR=22.;SR=48000
CREAM='#f2efdf';INK='#182b2b';GREEN='#bee86b';RED='#ee7359';GRAY='#64736a'
B='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf';R='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def font(n,b=True):return ImageFont.truetype(B if b else R,n)
def text(d,xy,s,n=24,c=INK,anchor=None,b=True):d.text(xy,s,font=font(n,b),fill=c,anchor=anchor)
def clamp(x):return max(0,min(1,x))
def ease(x):return 1-(1-clamp(x))**3
def pill(d,box,s,fill=GREEN,c=INK,n=18):d.rounded_rectangle(box,(box[3]-box[1])//2,fill=fill);text(d,((box[0]+box[2])/2,(box[1]+box[3])/2),s,n,c,'mm')
def phone(t,mode='face'):
 im=Image.new('RGBA',(340,520));d=ImageDraw.Draw(im)
 d.rounded_rectangle((23,10,322,507),43,fill='#536262');d.rounded_rectangle((17,5,316,501),43,fill='#142626',outline='#6c8174',width=3)
 d.rounded_rectangle((28,17,305,489),32,fill='#d8e4b9' if mode=='face' else '#203a37')
 d.rounded_rectangle((120,23,210,38),8,fill='#142626');text(d,(48,51),'09:41',12);text(d,(248,51),'1%',12,RED)
 # worn glass cracks
 d.line([(288,79),(271,114),(287,146),(260,170)],fill='#9eaf92',width=2);d.line([(271,114),(246,124)],fill='#9eaf92',width=2)
 if mode=='face':
  blink=abs(math.sin(t*1.2))<.1
  for x in [111,219]:
   if blink:d.rounded_rectangle((x-19,198,x+19,204),3,fill=INK)
   else:
    d.rounded_rectangle((x-20,174,x+20,218),16,fill=INK);d.ellipse((x-9,181,x,190),fill=CREAM)
  d.arc((126,227,206,268),0,180,fill=INK,width=7)
  # voice-activated mouth varies across time
  if t%1>.3:d.ellipse((151,244,181,256+int(6*math.sin(t*28)**2)),fill=INK)
  d.line((86,155,132,149),fill=INK,width=5);d.line((200,149,245,156),fill=INK,width=5)
  pill(d,(60,351,274,388),'PRE-LOVED. VERY TIRED.',INK,CREAM,12)
  text(d,(166,420),'4 YEARS OF SERVICE',13,GRAY,'mm')
 elif mode=='record':
  text(d,(166,107),'VOICE MEMOS',23,CREAM,'mm');d.ellipse((137,154,195,212),fill=RED);d.rounded_rectangle((157,167,175,193),8,fill=CREAM)
  text(d,(166,254),'one_day.m4a',21,CREAM,'mm');text(d,(166,286),'LAST PLAYED: NEVER',12,'#96b5a4','mm')
  for j in range(31):
   xx=55+j*7;hh=4+int(abs(math.sin(j*2.1+t*5))*29);d.line((xx,350-hh,xx,350+hh),fill=GREEN,width=3)
  pill(d,(76,412,260,451),'PLAY RECORDING',GREEN,INK,13)
 im=im.rotate(math.sin(t*.8)*2,Image.Resampling.BICUBIC,expand=False)
 return im
CAP=[(.35,2.3,'Kal mera maalik mujhe bech dega.'),(2.75,4.25,'Aath hazaar maange hain.'),(4.5,7.05,'Jis phone se isne teen lakh ki shopping ki...'),(7.4,9.5,'Uski apni keemat aath hazaar!'),(9.85,12.9,'Waah beta. Kya izzat hai.'),(13.5,16.7,'Lekin jaane se pehle, ise ek recording sunaani hai.'),(17,18.55,'Dikkat bas itni hai...'),(18.7,20.7,'Meri battery ek percent hai.')]
def frame(t):
 im=Image.new('RGB',(W,H),CREAM);d=ImageDraw.Draw(im)
 for x in range(34,W,32):
  for y in range(80,635,32):d.point((x,y),fill='#d1d8c6')
 text(d,(54,37),'OBJECT WITNESS',20);text(d,(1226,37),'01 / THE LAST BACKUP',15,GRAY,'ra')
 d.line((54,70,1226,70),fill='#b9c4b1',width=1)
 if t<13.35:
  # phone on pedestal, levitating at 2px breath
  d.ellipse((112,567,452,609),fill='#d0d5bd');d.rounded_rectangle((106,579,454,629),14,fill='#c4ceb2');d.ellipse((106,559,454,604),fill='#e3e7ce')
  p=phone(t);im.paste(p,(108,int(85+math.sin(t*1.3)*4)),p);d=ImageDraw.Draw(im)
  if t<2.55:
   text(d,(542,146),'TOMORROW,',25,GRAY);text(d,(537,185),'I GET SOLD.',69)
   pill(d,(545,300,765,340),'OWNER LISTING',INK,CREAM)
   text(d,(545,374),'"Minor scratches."',30);text(d,(545,425),'Major emotional damage.',23,GRAY,b=False)
  elif t<4.5:
   pill(d,(545,139,794,176),'RESALE VALUE',INK,CREAM)
   text(d,(538,192),'Rs 8,000',91)
   d.line((548,314,1125,314),fill=RED,width=9);text(d,(545,365),'Battery: weak.',25,GRAY);text(d,(545,410),'Self-respect: weaker.',25,GRAY)
  elif t<7.35:
   text(d,(544,130),'OWNER\'S SHOPPING TOTAL',22,GRAY)
   for j,(name,price) in enumerate([('SNEAKERS','Rs 18,000'),('FOOD AT 2 AM','Rs 42,000'),('"ESSENTIALS"','Rs 2,40,000')]):
    y=200+j*85;off=int((1-ease((t-4.5-j*.13)*3))*80)
    d.rounded_rectangle((540+off,y,1180+off,y+67),12,fill='#ffffff',outline='#c7cdbd');text(d,(563+off,y+23),name,17);text(d,(1154+off,y+21),price,23,anchor='ra')
   pill(d,(754,477,1178,532),'TOTAL: Rs 3,00,000',GREEN,INK,29)
  elif t<9.7:
   text(d,(542,132),'HIS PURCHASES',21,GRAY);text(d,(538,170),'Rs 3,00,000',70)
   text(d,(544,291),'MY ENTIRE EXISTENCE',21,GRAY);text(d,(538,329),'Rs 8,000',80,RED)
   text(d,(545,462),'THE MATH IS MATHING.',21)
  else:
   pill(d,(545,149,905,190),'PERFORMANCE REVIEW',INK,CREAM)
   text(d,(540,224),'WAAH BETA.',61);text(d,(540,305),'KYA IZZAT HAI.',53,RED)
   # dry comedic 5-star review
   text(d,(546,417),'SERVICE: 4 YEARS',24,GRAY);text(d,(546,462),'APPRECIATION: 0',24,GRAY)
 elif t<17:
  im=Image.new('RGB',(W,H),INK);d=ImageDraw.Draw(im)
  text(d,(54,37),'OBJECT WITNESS',20,CREAM);text(d,(1226,37),'ONE FILE LEFT UNOPENED',15,'#91a99a','ra')
  p=phone(t,'record');im.paste(p,(130,88),p);d=ImageDraw.Draw(im)
  pill(d,(565,152,850,190),'BEFORE I GO...',GREEN,INK)
  text(d,(559,244),'ONE RECORDING.',53,CREAM);text(d,(565,325),'He needs to hear it.',28,'#b5c6b5',b=False)
  for j in range(49):
   x=567+j*12;v=int((5+abs(math.sin(j*.85+t*3))*34)*(0.4+0.6*math.sin(j*.1)**2));d.line((x,447-v,x,447+v),fill=GREEN,width=5)
 elif t<18.75:
  im=Image.new('RGB',(W,H),INK);d=ImageDraw.Draw(im)
  text(d,(640,250),'ONE SMALL PROBLEM.',49,CREAM,'mm')
  q=ease((t-17.3)*1.5);d.rounded_rectangle((490,332,790,423),14,outline='#7e9988',width=4);d.rectangle((791,358,805,396),fill='#7e9988');d.rectangle((503,346,503+int(270*(1-q)+10),409),fill=RED)
 else:
  im=Image.new('RGB',(W,H),'#172523');d=ImageDraw.Draw(im)
  # huge battery glyph and stark visual pause
  pulse=.75+.25*math.sin(t*6)**2
  d.rounded_rectangle((123,219,478,420),29,outline='#71847a',width=8);d.rounded_rectangle((481,278,504,361),7,fill='#71847a');d.rounded_rectangle((139,235,163,404),7,fill=RED)
  text(d,(581,153),'BATTERY REMAINING',23,'#aebda8');text(d,(565,171),'1%',194,RED)
  text(d,(588,421),'ONE CHANCE TO PRESS PLAY.',21,CREAM)
  if t>20.7:
   pill(d,(586,483,1161,536),'THE LAST BACKUP  /  COMING NEXT',GREEN,INK,18)
 d=ImageDraw.Draw(im)
 for a,b,s in CAP:
  if a<=t<b:
   tw=d.textbbox((0,0),s,font=font(22))[2];d.rounded_rectangle(((W-tw)/2-25,642,(W+tw)/2+25,694),12,fill='#0d1d1c');text(d,(640,669),s,22,'#f7f1dc','mm')
 d.rectangle((0,714,int(W*t/DUR),719),fill=RED if t>18.75 else GREEN)
 return im
raw=subprocess.run([FF,'-v','error','-i','object-witness/demo-vo.mp3','-f','f32le','-ac','1','-ar',str(SR),'-'],capture_output=True,check=True).stdout
vo=np.frombuffer(raw,dtype=np.float32);N=int(SR*DUR);out=np.zeros(N);rng=np.random.default_rng(44)
def add(v,at,g=1):
 s=int(at*SR);n=min(N-s,len(v))
 if n>0:out[s:s+n]+=v[:n]*g
# quiet original plucked groove that drops away for the battery reveal
for j,a in enumerate(np.arange(.0,16.9,.375)):
 x=np.arange(int(.5*SR))/SR;hz=[164.81,196,246.94,220][j%4];add((np.sin(2*np.pi*hz*x)+.25*np.sin(2*np.pi*hz*2*x))*np.exp(-x*10),a,.025)
for at in [2.55,4.5,7.35,9.7,13.35]:
 x=np.arange(int(.15*SR))/SR;add(rng.normal(0,1,len(x))*np.sin(np.pi*x/.15)**2,at,.017)
for at in [4.6,4.9,5.2]:
 x=np.arange(int(.15*SR))/SR;add(np.sin(2*np.pi*1000*x)*np.exp(-x*30),at,.035)
for at in [18.85,19.18]:
 x=np.arange(int(.14*SR))/SR;add(np.sin(2*np.pi*660*x)*np.sin(np.pi*x/.14),at,.08)
add(vo,.35,.95);out=np.tanh(out*1.08)*.92
with wave.open('object-witness/mix.wav','wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes((out*32767).astype('int16').tobytes())
p=subprocess.Popen([FF,'-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','1280x720','-r','30','-i','-','-i','object-witness/mix.wav','-vf','scale=1920:1080:flags=lanczos','-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart','-shortest','OBJECT_WITNESS_DEMO.mp4'],stdin=subprocess.PIPE)
for n in range(int(DUR*FPS)):
 p.stdin.write(frame(n/FPS).tobytes())
 if n%150==0:print(n,flush=True)
p.stdin.close();assert p.wait()==0
sheet=Image.new('RGB',(960,540))
for i,t in enumerate([1,3,6,10,15,19.5]):sheet.paste(frame(t).resize((320,180)),((i%3)*320,(i//3)*180))
sheet.save('object-witness/preview.jpg')
json.dump({'narrator_voice_id':'voice-02','language':'hi','note':'Automatically assigned audition; not explicitly approved by user. Voice service persistence not guaranteed.','format':'Original fictional object POV; this file records demo settings, not commercial licensing.'},open('object-witness/voice.json','w'),indent=2)
print('DONE')
