"""Original, code-drawn 2D Endurance history short. Pillow rigs + procedural foley."""
from PIL import Image,ImageDraw,ImageFont
import numpy as np, math, subprocess, wave,json,os
import imageio_ffmpeg
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FF=imageio_ffmpeg.get_ffmpeg_exe();W,H=960,540;FPS=30;SR=48000
INK='#263d49';SNOW='#edfaff';BLUE='#9bd5e6';rnd=np.random.default_rng(17)
FONT='assets/fonts/archivo-black-latin-400-normal.ttf'
def f(s):return ImageFont.truetype(FONT,s)
def text(d,x,y,s,size=22,color=INK,anchor='mm'):d.text((x,y),s,font=f(size),fill=color,anchor=anchor)
def poly(d,p,fill,outline=INK,width=2):d.polygon(p,fill=fill);d.line(p+[p[0]],fill=outline,width=width,joint='curve')
def label(d,x,y,s,color='#224c73',size=21):
 box=d.textbbox((0,0),s,font=f(size));ww=box[2]+30;d.rounded_rectangle((x-ww/2,y-21,x+ww/2,y+21),12,fill=color,outline='#ffffff',width=2);text(d,x,y,s,size,'white')
def person(im,x,y,scale=1,phase=0,captain=False,wavehand=False):
 layer=Image.new('RGBA',(200,330));d=ImageDraw.Draw(layer);skin='#e3b58b';coat='#2b6785' if captain else '#dd873b';a=math.sin(phase)*9
 d.line((76,245,72+a,307),fill='#283d51',width=25);d.line((120,245,125-a,307),fill='#283d51',width=25)
 d.rounded_rectangle((49+a,298,87+a,321),6,fill='#26363d');d.rounded_rectangle((111-a,298,149-a,321),6,fill='#26363d')
 d.rounded_rectangle((43,133,150,265),22,fill=coat,outline=INK,width=3)
 d.line((51,156,32,240),fill=coat,width=27);d.ellipse((21,229,43,256),fill=skin,outline=INK,width=2)
 if wavehand:
  d.line((143,157,169,120,173+math.sin(phase)*8,73),fill=coat,width=24);d.ellipse((162+math.sin(phase)*8,53,184+math.sin(phase)*8,81),fill=skin,outline=INK,width=2)
 else:
  d.line((143,156,165,239),fill=coat,width=26);d.ellipse((154,229,176,256),fill=skin,outline=INK,width=2)
 d.line((98,144,98,263),fill=INK,width=2)
 for by in [170,194,219,242]:d.ellipse((104,by,110,by+6),fill='#e6d396')
 d.polygon([(46,138),(69,122),(99,150),(125,123),(148,138),(132,174),(99,152),(64,174)],fill='#d7c5a1',outline=INK)
 d.ellipse((51,31,144,145),fill=skin,outline=INK,width=3)
 d.polygon([(53,83),(46,49),(69,22),(118,22),(147,48),(144,85),(127,59),(112,63),(85,49),(66,74)],fill='#47372e')
 # eyebrows and blinking eyes
 blink=abs(math.sin(phase*.29))<.055
 for ex in [78,119]:
  d.arc((ex-10,78,ex+9,87),180,350,fill=INK,width=3)
  if blink:d.line((ex-7,93,ex+7,93),fill=INK,width=2)
  else:
   d.ellipse((ex-8,88,ex+8,103),fill='white',outline=INK,width=1);d.ellipse((ex-2,91,ex+4,101),fill=INK)
 d.line((99,94,95,111,103,112),fill='#ac7959',width=2)
 if captain:
  d.polygon([(54,102),(72,119),(89,115),(101,122),(115,114),(140,101),(136,137),(114,158),(91,164),(66,145)],fill='#3a3434',outline=INK)
  d.arc((86,120,111,137),0,180,fill='#e2ad86',width=3)
  d.polygon([(47,50),(55,25),(139,25),(151,51)],fill='#20556f',outline=INK)
  d.rectangle((51,47,145,59),fill='#e1bc56',outline=INK);d.ellipse((89,30,107,48),outline='#e1bc56',width=3)
 else:d.arc((87,116,112,132),0,170,fill=INK,width=2)
 layer=layer.resize((int(200*scale),int(330*scale)),Image.Resampling.LANCZOS);im.alpha_composite(layer,(int(x-layer.width/2),int(y-layer.height)))
def floe(d,x,y,w=170):
 d.ellipse((x-w/2,y-12,x+w/2,y+24),fill='#76bace',outline=INK,width=2);d.ellipse((x-w/2,y-19,x+w/2,y+12),fill=SNOW,outline=INK,width=2)
def ship(im,x,y,scale=1,tilt=0,broken=False):
 l=Image.new('RGBA',(600,410));d=ImageDraw.Draw(l)
 # rigging behind canvas
 for mx,top in [(175,100),(300,33),(420,65)]:
  d.line((mx,top,65,300),fill=INK,width=2);d.line((mx,top,535,297),fill=INK,width=2)
  for dx in [-23,23]:d.line((mx,top+50,mx+dx,298),fill=INK,width=2)
  for yy in range(top+80,295,15):d.line((mx-18,yy,mx+18,yy),fill=INK,width=1)
  d.line((mx,top,mx,307),fill='#875d2e',width=8)
  for sy,sw in [(top+55,100),(top+119,125)]:
   poly(d,[(mx-sw/2,sy),(mx+sw/2,sy),(mx+sw/2-14,sy+43),(mx,sy+57),(mx-sw/2+12,sy+43)],'#f5e5b9')
   d.line((mx-sw/2-7,sy,mx+sw/2+7,sy),fill='#77542d',width=5)
 d.line((480,290,572,210),fill='#78512d',width=9)
 poly(d,[(44,286),(150,305),(447,290),(522,260),(501,334),(441,366),(143,382),(74,348)],'#995e2e',width=4)
 poly(d,[(55,292),(153,316),(445,302),(514,274),(507,297),(448,323),(149,336),(67,311)],'#e1b965',width=3)
 d.line((90,350,147,367,444,349,488,329),fill='#dca65b',width=5)
 for xx in range(137,458,51):d.ellipse((xx,328,xx+16,343),fill='#132f3b',outline='#e3c48b',width=3)
 d.rectangle((88,268,159,301),fill='#ba8a48',outline=INK,width=3)
 for xx in range(93,156,13):d.line((xx,270,xx,298),fill=INK,width=2)
 if broken:poly(d,[(277,309),(292,323),(275,339),(303,357),(288,374),(327,365),(309,343),(326,325),(307,309)],'#34576a')
 l=l.resize((int(600*scale),int(410*scale)),Image.Resampling.LANCZOS).rotate(tilt,resample=Image.Resampling.BICUBIC)
 im.alpha_composite(l,(int(x-l.width/2),int(y-l.height)))
def boat(im,x,y,scale=1,tilt=0):
 l=Image.new('RGBA',(360,220));d=ImageDraw.Draw(l)
 for xx in [80,120,160,200,240,280]:
  d.ellipse((xx-9,95,xx+9,116),fill='#d6ae8c',outline=INK);d.rectangle((xx-12,115,xx+12,151),fill='#314e69')
 d.line((190,20,190,167),fill='#6d543d',width=5)
 poly(d,[(185,26),(185,138),(101,132)],'#f1dfaf')
 poly(d,[(28,143),(331,143),(294,194),(91,199),(52,179)],'#a56939',width=3)
 d.line((52,156,307,156),fill='#ebc176',width=4)
 l=l.resize((int(360*scale),int(220*scale)),Image.Resampling.LANCZOS).rotate(tilt,resample=Image.Resampling.BICUBIC);im.alpha_composite(l,(int(x-l.width/2),int(y-l.height)))
def background(t,storm=False,land=False):
 im=Image.new('RGBA',(W,H),'#badfe9' if not storm else '#466b83');d=ImageDraw.Draw(im)
 # layered snowy mountain silhouettes
 for j,(x,hh) in enumerate([(-100,190),(110,130),(300,205),(540,140),(760,240),(970,170)]):
  p=[(x-160,278),(x-70,hh+50),(x-35,hh),(x,hh+10),(x+40,hh-40),(x+87,hh+65),(x+180,278)]
  poly(d,p,'#a1d3e1',width=2)
  poly(d,[(x-70,hh+50),(x-35,hh),(x,hh+10),(x+40,hh-40),(x+63,hh+33),(x+35,hh+15),(x+10,hh+75),(x-19,hh+42),(x-40,hh+71)],'#e4f6f7',outline='#e4f6f7',width=1)
 d.rectangle((0,276,W,H),fill='#51a2c4' if not storm else '#2b607f')
 for j in range(20):
  xx=(j*137+t*(14 if storm else 5))%1100-80;yy=290+(j*47)%240
  d.arc((xx,yy,xx+105,yy+12),0,170,fill='#88cee1' if not storm else '#5e8fa7',width=2)
 if land:poly(d,[(0,391),(180,355),(322,387),(449,355),(647,395),(819,364),(960,386),(960,540),(0,540)],'#e6f4f3')
 return im
# decode sped narration, build timeline
clips=[];starts=[];at=.45
for i in range(1,7):
 raw=subprocess.run([FF,'-v','error','-i',f'history-demo/v{i}.mp3','-af','atempo=1.14','-f','f32le','-ac','1','-ar',str(SR),'-'],capture_output=True,check=True).stdout
 v=np.frombuffer(raw,dtype='float32');clips.append(v);starts.append(at);at+=len(v)/SR+.20
DUR=at+.7;N=math.ceil(DUR*SR);out=np.zeros(N);tt=np.arange(N)/SR
# original soft plucked ostinato and wind
out+=.018*np.sin(tt*2*np.pi*55)+.009*np.sin(tt*2*np.pi*82.4)
noise=rnd.normal(0,1,N);wind=np.convolve(noise,np.ones(110)/110,mode='same');out+=wind*.23

def add(v,at,g=1):
 s=int(at*SR);n=min(len(v),N-s)
 if n>0:out[s:s+n]+=v[:n]*g
for k in np.arange(0,DUR,.43):
 x=np.arange(int(.7*SR))/SR;hz=[220,261.63,329.63,293.66][int(k/.43)%4];sig=(np.sin(2*np.pi*hz*x)+.25*np.sin(2*np.pi*hz*2*x))*np.exp(-x*8);add(sig,k,.022)
for s in starts:
 x=np.arange(int(.35*SR))/SR;add(rnd.normal(0,1,len(x))*np.sin(np.pi*x/.35)**2,s-.2,.025)
# wood cracking at ship loss; wave hits during boat crossing
for s in [starts[2]+1.1,starts[2]+2.1,starts[2]+3.2]:
 x=np.arange(int(.5*SR))/SR;add(rnd.normal(0,1,len(x))*np.exp(-x*15)+np.sin(x*2*np.pi*76)*np.exp(-x*10),s,.10)
for s in np.arange(starts[3],starts[4],1.5):
 x=np.arange(SR)/SR;add(rnd.normal(0,1,len(x))*np.sin(np.pi*x)**2,s,.024)
for s,v in zip(starts,clips):
 a=int(s*SR);out[a:a+len(v)]*=.36;add(v,s,.92)
# final hopeful chord
x=np.arange(int(2.6*SR))/SR
for hz in [220,277.18,329.63]:add(np.sin(2*np.pi*hz*x)*np.exp(-x*1.4),starts[5]+2,.024)
out=np.tanh(out)*.93
with wave.open('history-demo/mix.wav','wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes((out*32767).astype('int16').tobytes())
# short English on-screen captions; narration Hindi
CAPS=[['SHIP LOST. ALL 28 SURVIVED.','ERNEST SHACKLETON'],['1914: THE EXPEDITION BEGINS','ENDURANCE TRAPPED IN SEA ICE'],['THE ICE CRUSHED THEIR SHIP','THREE LIFEBOATS. ONE CHANCE.'],['ELEPHANT ISLAND TO SOUTH GEORGIA','6 MEN • ABOUT 1,300 KM'],['A MOUNTAIN CROSSING FOR HELP','THEN HE WENT BACK FOR HIS CREW'],['AUGUST 1916: RESCUED','ALL 28 ENDURANCE MEN SURVIVED']]
def frame(t):
 idx=max(0,min(5,next((i-1 for i,s in enumerate(starts) if s>t),5))) if t<starts[-1] else 5
 # robust timeline lookup
 idx=sum(t>=s for s in starts)-1;idx=max(0,min(5,idx));lt=t-starts[idx];dur=(starts[idx+1] if idx<5 else DUR)-starts[idx];q=max(0,min(1,lt/dur))
 im=background(t,storm=idx in [2,3],land=idx in [0,4,5]);d=ImageDraw.Draw(im)
 if idx==0:
  ship(im,730,370,.65,tilt=-13,broken=True)
  d=ImageDraw.Draw(im);floe(d,259,459,340)
  person(im,230,464,1.08,t*5,captain=True)
  label(d,555,86,'A SHIPWRECK. AN IMPOSSIBLE RESCUE.',size=20)
  label(d,584,400,'28 / 28 SURVIVED',color='#2b775d',size=25)
 elif idx==1:
  ship(im,480+math.sin(t)*5,407,.96,tilt=math.sin(t)*2)
  d=ImageDraw.Draw(im)
  for xx,yy,ww in [(140,411,195),(810,430,225),(430,482,220)]:floe(d,xx+math.sin(t)*2,yy,ww)
  label(d,145,87,'1914',size=30);label(d,730,100,'DESTINATION: ANTARCTICA',size=18)
  if q>.48:label(d,490,186,'1915: LOCKED IN THE ICE',color='#bd6245',size=21)
 elif idx==2:
  ship(im,645,397+q*70,.75,tilt=-q*25,broken=True)
  d=ImageDraw.Draw(im);floe(d,243,446,460)
  for xx in [112,188,270]:person(im,xx,437,.52,t*2,captain=xx==188)
  for xx in [82,210,342]:boat(im,xx,499,.35)
  d=ImageDraw.Draw(im);label(d,480,85,'THE SHIP WAS GONE. NOT THE CREW.',color='#954e43',size=22)
 elif idx==3:
  # island silhouette, rising animated waves, small boat on enormous sea
  d=ImageDraw.Draw(im);poly(d,[(0,332),(30,278),(84,256),(135,335),(165,389),(0,393)],'#3b5260')
  boat(im,390+q*140,425+math.sin(t*2.8)*12,.95,tilt=math.sin(t*2.8)*7)
  d=ImageDraw.Draw(im)
  for j in range(5):
   yy=455+j*18;pts=[(x,yy+math.sin(x*.018+t*2+j)*10) for x in range(-10,980,10)];d.line(pts,fill=['#3e89a8','#9ed4e2'][j%2],width=7)
  label(d,482,84,'~1,300 KM OF SOUTHERN OCEAN',color='#24455f',size=23)
  label(d,735,187,'6 MEN. ONE SMALL BOAT.',size=18)
 elif idx==4:
  d=ImageDraw.Draw(im)
  poly(d,[(0,490),(153,205),(272,326),(429,123),(578,277),(745,170),(960,489),(960,540),(0,540)],'#a6c4ce',width=3)
  for xx,yy in [(153,205),(429,123),(745,170)]:poly(d,[(xx-67,yy+105),(xx,yy),(xx+70,yy+100),(xx+21,yy+64),(xx-5,yy+82),(xx-21,yy+57)],'#f3fbfb',outline='#f3fbfb')
  for j in range(3):person(im,350+j*75+q*55,444-j*29,.43,t*7,captain=j==0)
  d=ImageDraw.Draw(im);label(d,494,77,'SOUTH GEORGIA: CROSS THE MOUNTAINS',size=21)
  if q>.58:label(d,716,399,'HELP WAS FINALLY WITHIN REACH',color='#2c705e',size=16)
 else:
  d=ImageDraw.Draw(im)
  # Yelcho rescue tug (not the sunken Endurance)
  by=350+math.sin(t)*2
  poly(d,[(575,by),(911,by),(875,by+47),(621,by+47)],'#344752',width=3)
  d.rectangle((624,by-59,832,by),fill='#eee7cf',outline=INK,width=3)
  d.rectangle((655,by-91,749,by-58),fill='#d9e4dd',outline=INK,width=3)
  d.rectangle((773,by-109,798,by-59),fill='#a0523d',outline=INK,width=3)
  for xx in [635,674,713,752,791]:d.rectangle((xx,by-43,xx+21,by-23),fill='#5594a6',outline=INK,width=2)
  for j in range(3):d.ellipse((778+j*13,by-140-j*18,817+j*13,by-108-j*18),fill='#9bb4bf')
  text(d,753,by+21,'YELCHO',16,'#ffffff')
  d=ImageDraw.Draw(im);floe(d,286,465,520)
  for j in range(6):person(im,102+j*73,458,.56,t*5+j,captain=j==2,wavehand=True)
  d=ImageDraw.Draw(im);label(d,485,83,'30 AUGUST 1916 • RESCUE',color='#2b775d',size=25)
  label(d,700,443,'28 LIVES SAVED',color='#2b775d',size=23)
 # snow across layers
 d=ImageDraw.Draw(im)
 for j in range(52):
  xx=(j*137-t*(27 if idx in [2,3] else 11))%980-10;yy=(j*71+t*26)%540;d.ellipse((xx,yy,xx+2,yy+2),fill='#effaff')
 # readable consistent captions in lower safe band
 line=CAPS[idx][0 if q<.50 else 1]
 d.rounded_rectangle((58,486,902,528),10,fill='#17364c',outline='#d0f1f4',width=2);text(d,480,507,line,23,'#ffffff')
 # progress, small source branding
 d.rectangle((0,0,960,6),fill='#d6eef3');d.rectangle((0,0,int(W*t/DUR),6),fill='#e7a33a')
 text(d,18,23,'HISTORY / ENDURANCE',11,INK,anchor='lm')
 text(d,942,23,'ORIGINAL 2D RECONSTRUCTION',10,INK,anchor='rm')
 return im.convert('RGB')
json.dump({'duration':DUR,'starts':starts},open('history-demo/timing.json','w'),indent=2)
p=subprocess.Popen([FF,'-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','960x540','-r',str(FPS),'-i','-','-i','history-demo/mix.wav','-vf','scale=1920:1080:flags=lanczos','-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart','-shortest','SHACKLETON_2D_HISTORY.mp4'],stdin=subprocess.PIPE)
for n in range(math.ceil(DUR*FPS)):
 p.stdin.write(frame(n/FPS).tobytes())
 if n%300==0:print(n,'/',math.ceil(DUR*FPS),flush=True)
p.stdin.close();assert p.wait()==0
sheet=Image.new('RGB',(960,810))
for i,s in enumerate(starts):sheet.paste(frame(s+2).resize((480,270)),((i%2)*480,(i//2)*270))
sheet.save('history-demo/contact.jpg');print('DONE',DUR,flush=True)
