from PIL import Image,ImageFont,ImageDraw
from aip import AipSpeech
import os
import sys
import cv2
import eyed3
from moviepy.editor import VideoFileClip,AudioFileClip,CompositeAudioClip,concatenate_videoclips

num=0

APP_ID = '15918384'
API_KEY = 'gmq87YZIXIXqhagikbwMYCtS'
SECRET_KEY = 'TtjVz4GnjPIt1PpdoEey30pDhPRzAMYM'
client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

def _read(index):
    try:
        f=open(index,"r",encoding="utf-8")
        x=f.read()
        f.close()
        return x
    except:
        return "error"

def create_frame(player_name,text):
    global num,font_bg,client
    try:
        player= Image.open("img/players/"+player_name+".png")
    except:
        if(player_name=="kp"):
            player= Image.open("zc/kp.png")
        else:
            player= Image.open("zc/pc.png")

    try:
        bg= Image.open("img/bg.jpg")
    except:
        bg= Image.open("zc/bg.jpg")

    soundjdg=0
    for i in range(len(sound)):
        if(sound[i][0]==player_name):
            spd=sound[i][1]
            per=sound[i][2]
            pit=sound[i][3]
            soundjdg=1
            break
    if(soundjdg==0):
        spd=6
        per=1
        pit=7

    result  = client.synthesis(text, 'zh', 1, {'vol': 5,'spd':spd,'per':per,'pit':pit})
    if not isinstance(result, dict):
        with open(r'sound/'+str(num)+'.mp3', 'wb') as f:
            f.write(result)
    else:
        print("语音合成出错")
        sys.exit()
        
    dhk= Image.open("zc/dhk.png")
    bgx,bgy=bg.size
    dhkx,dhky=dhk.size
    dhk=dhk.resize((bgx,int(bgx/dhkx*dhky/5*4)),Image.BILINEAR)
    dhkx,dhky=dhk.size
    _font=ImageFont.truetype('simhei.ttf',int(bgy/20))

    hk=bg
    playerx,playery=player.size
    player=player.resize((int((bgy/6*5)/playery*playerx),int(bgy/6*5)),Image.BILINEAR)
    playerx,playery=player.size
    try:
        hk.paste(player,(int(bgx/30),int(bgy-playery-(bgy/6))),mask=player.split()[3])
    except:
        hk.paste(player,(int(bgx/30),int(bgy-playery-(bgy/6))))
    hk.paste(dhk,(0,bgy-dhky),mask=dhk.split()[3])
    draw=ImageDraw.Draw(hk)
    draw.text((int(bgx/30),int(bgy/60*font_bg)),player_name,(255,255,255),font=_font)
    if(len(text)>=23):
        text0=[]
        numn=int(len(text)/23)+1
        for i in range(numn):
            if((i+1)*23>len(text)-1):
                text0.append(text[i*23:])
            else:
                text0.append(text[i*23:(i+1)*23])
        text=text0
    else:
        text=[text]

    for i in range(len(text)):
        draw.text((int(bgx/30),int(bgy/60*(font_bg+8+i*4))),text[i],(255,255,255),font=_font)
    hk.save("frame/"+str(num)+".jpg")

    num+=1
def create_video(lenlist):
    fourcc=cv2.VideoWriter_fourcc("D","I","V","X")
    img=cv2.imread("frame/0.jpg")
    imgInfo = img.shape
    size = (imgInfo[1],imgInfo[0])
    video=cv2.VideoWriter("video/video.mp4",fourcc,1,size)
    for i in range(num):
        img=cv2.imread("frame/"+str(i)+".jpg")
        for j in range(lenlist[i]):
            video.write(img)
    video.release()

def audio_add():
    video = VideoFileClip('video/video.mp4')
    for i in range(len(lenlist)):
        if(i!=0):
            video_=video.subclip(sum(lenlist[0:i]),sum(lenlist[0:i])+lenlist[i])
            print([sum(lenlist[0:i]),sum(lenlist[0:i])+lenlist[i]])
        else:
            video_=video.subclip(0,lenlist[i])
        audio=AudioFileClip("sound/"+str(i)+".mp3")
        video_=video_.set_audio(audio)
        if(i==0):
            subvideo=video_
        else:
            subvideo=concatenate_videoclips([subvideo,video_])

    subvideo.write_videofile("video/result.mp4")

msg=_read("text/text.txt")

if(msg=="error"):
    print("打开text.txt出错")
    sys.exit()
sound=_read("text/sound.txt")
if(sound=="error"):
    print("打开sound.txt出错")
    sys.exit()
try:
    font_bg=_read("position.txt")
    if(font_bg=="error"):
        print("打开position.txt出错")
        sys.exit()
    font_bg=int(font_bg)
except:
    font_bg=36

try:
    msg=msg.split("\n\n")
    for i in range(len(msg)):
        msg[i]=msg[i].split("\n")
except:
    print("text.txt格式错误")
    sys.exit()
try:
    sound=sound.split("\n")
    for i in range(len(sound)):
        sound[i]=sound[i].split(" ")
    for i in range(len(sound)):
        for j in range(1,len(sound[i])):
            sound[i][j]=int(sound[i][j])
except:
    print("sound.txt格式错误")
    sys.exit()

for i in os.listdir("frame"):
    os.remove("frame/"+i)

for i in os.listdir("sound"):
    os.remove("sound/"+i)

print("开始合成，一共有"+str(len(msg))+"帧")
for i in range(len(msg)):
    print("开始合成第"+str(i+1)+"帧")
    create_frame(msg[i][0],msg[i][1])
lenlist=[]
for i in range(num):
    voice_file = eyed3.load("sound/"+str(i)+".mp3")
    secs = voice_file.info.time_secs
    secs=int(secs)+1
    lenlist.append(secs)
print(lenlist)
create_video(lenlist)
print("视频合成完成，开始添加音轨")
audio_add()
print("合成成功")
