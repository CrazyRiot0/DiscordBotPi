from __future__ import unicode_literals
import discord
from discord.ext import commands
from discord import Embed
from discord.voice_client import VoiceClient
import urllib
from bs4 import BeautifulSoup
import requests
import youtube_dl
import string
from random import randint
import random
import time
import datetime
import base64
import asyncio
import os
import shutil
import sys
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import yt_search
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
import pysrt
from pytube import YouTube
from google_images_download import google_images_download
import statistics

intents = discord.Intents.all()
client = discord.Client(intents=intents)

platform = ""
if sys.platform.startswith("win32"):
    platform = "Windows"
elif sys.platform.startswith("linux"):
    platform = "Linux"
else:
    platform = "None"

PATH = os.path.dirname(os.path.abspath(__file__))

Q = []
SR = []
Timer = None
player_flag = True
isRepeating = False
RepeatCounter = 0
Counter = 1
YTS_Title = None
YTS_VideoID = None
YTS_VideoURL = None
YTS_ChannelName = None
YTS_ChannelID = None

class VideoInfo:
    title = ""
    path = ""
    id = ""
    channel = ""
    channel_id = ""
    def __init__(self, title, path, id, channel, channel_id):
        self.title = title
        self.path = path
        self.id = id
        self.channel = channel
        self.channel_id = channel_id

class SearchResult:
    title = ""
    link = ""
    def __init__(self, title, link):
        self.title = title
        self.link = link

def ClearYoutubeDL():
    path = os.path.join(PATH, "youtubedl")
    if os.path.isdir(path):
        shutil.rmtree(path)
    os.mkdir(path)
    print("Cleared youtubedl folder.")

class _Timer():
    start = None
    tmp = None
    isRunning = True
    def start(self):
        self.start = time.time()
    def time(self):
        if self.isRunning is False:
            return self.tmp
        now = time.time()
        return now - self.start
    def pause(self):
        if self.isRunning is False:
            return -1
        self.isRunning = False
        now = time.time()
        self.tmp = now - self.start
    def resume(self):
        if self.isRunning is True:
            return -1
        self.isRunning = True
        now = time.time()
        self.start = now - self.tmp

async def AsyncPlayer():
    vc = client.voice_clients[0]
    if vc is None:
        print("VoiceClient Error.")
        pass
    print("AsyncPlayer Started.")
    global player_flag
    global isRepeating
    global RepeatCounter
    global Counter
    global Timer
    while len(client.voice_clients) != 0:
        if vc.is_playing() is False and len(Q) > 0:
            if player_flag:
                player_flag = False
            else:
                if isRepeating is True:
                    Counter = Counter + 1
                    if Counter > RepeatCounter:
                        isRepeating = False
                        Counter = 1
                        Q.pop(0)
                else:
                    Q.pop(0)
                if len(Q) == 0:
                    continue
            Timer = _Timer()
            Timer.start()
            print("Playing " + Q[0].title + " ...")
            vc.play(discord.FFmpegPCMAudio(Q[0].path))
            song = Q[0].title
            # activity = discord.Activity(type=discord.ActivityType.listening, name=song)
            # await client.change_presence(status=discord.Status.online, activity=activity)
        # elif vc.is_playing() is False and len(Q) == 0:
            # await client.change_presence(status=discord.Status.online, activity=discord.Game(""))
        await asyncio.sleep(2)
    isRepeating = False
    print("VoiceClient Not Found. Shutting Down...")
    # await client.change_presence(status=discord.Status.online, activity=discord.Game(""))

def CheckAlreadyUsed(n, list):
    if len(list) == 0:
        return False
    for X in list:
        if n == X:
            return True
    return False

async def AsyncSubtitle(srtpath, channel):
    global Q
    global Timer
    vc = client.voice_clients[0]
    title = Q[0].title
    embed = discord.Embed(title=title+" 자막", colour=discord.Colour.green())
    message = await channel.send(embed=embed)

    subs = pysrt.open(srtpath)
    index = 0
    current = -1
    while len(Q) != 0:
        sub = subs[index]
        X = sub.start
        Y = sub.end
        sub_time = X.hours*3600 + X.minutes*60 + X.seconds + X.milliseconds/1000
        sub_time_end = Y.hours*3600 + Y.minutes*60 + Y.seconds + Y.milliseconds/1000

        if Timer.time() >= sub_time and Timer.time() <= sub_time_end:
            if current == index:
                await asyncio.sleep(0.5)
                continue
            current = index
            embed = discord.Embed(title=title+" 자막", description=sub.text, colour=discord.Colour.green())
            await message.edit(embed=embed)
        elif Timer.time() >= sub_time_end:
            index = index + 1
            if index > len(subs):
                return
        await asyncio.sleep(0.5)

    print("Song Ended. AsyncSubtitle Shutting Down...")

isOmokPlaying = False
isOmokHosting = False
OmokPlayer_White = None
OmokPlayer_White_Name = None
OmokPlayer_Black = None
OmokPlayer_Black_Name = None
Omok_Turn = None
OmokBoard_Len = 19
OmokBoard = None
NumberInCircle = ["⓪", "①", "②", "③", "④", "⑤", "⑥", "⑦", "⑧", "⑨", "⑩",
                  "⑪", "⑫", "⑬", "⑭", "⑮", "⑯", "⑰", "⑱", "⑲", "⑳",
                  "㉑", "㉒", "㉓", "㉔", "㉕", "㉖", "㉗", "㉘", "㉙", "㉚",
                  "㉛", "㉜", "㉝", "㉞", "㉟", "㊱", "㊲", "㊳", "㊴", "㊵",
                  "㊶", "㊷", "㊸", "㊹", "㊺", "㊻", "㊼", "㊽", "㊾", "㊿", ]
WhiteC = "○"
BlackC = "●"
EmptySpace = "ㅤ"

def Omok_MakeBoard():
    len = OmokBoard_Len
    global OmokBoard
    OmokBoard = [[0 for x in range(len)] for y in range(len)]
    for i in range(0, len):
        for j in range(0, len):
            OmokBoard[i][j] = "┼"

    for i in range(0, len):
        OmokBoard[0][i] = "┬"
        OmokBoard[len - 1][i] = "┴"
        OmokBoard[i][0] = "├"
        OmokBoard[i][len - 1] = "┤"

    OmokBoard[0][0] = "┌"
    OmokBoard[0][len - 1] = "┐"
    OmokBoard[len - 1][0] = "└"
    OmokBoard[len - 1][len - 1] = "┘"

def Omok_PlaceInCoord(x, y, color):  # color True = White, False = Black
    global OmokBoard
    global OmokBoard_Len

    if x > OmokBoard_Len or y > OmokBoard_Len or x < 0 or y < 0:
        return -1

    x = x - 1
    y = y - 1

    if OmokBoard[y][x] == 1 or OmokBoard[y][x] == 0:
        return 0

    if color is True:
        OmokBoard[y][x] = 1
    else:
        OmokBoard[y][x] = 0

    return True

def OmokBoardInStr():
    global OmokBoard
    global OmokBoard_Len
    global NumberInCircle
    global EmptySpace
    S = ""
    S += EmptySpace
    for i in range(1, OmokBoard_Len + 1):
        S += NumberInCircle[i]
    S += "\n"

    for i in range(0, OmokBoard_Len):
        S += NumberInCircle[i + 1]
        for j in range(0, OmokBoard_Len):
            if OmokBoard[i][j] == 1:
                S += WhiteC
            elif OmokBoard[i][j] == 0:
                S += BlackC
            else:
                S += OmokBoard[i][j]
        S += "\n"
    return S

def Omok_CheckBoard():
    global OmokBoard
    global OmokBoard_Len
    for i in range(0, OmokBoard_Len):  # 가로를 보아라.
        count_w = 0
        count_b = 0
        prev = None
        for j in range(0, OmokBoard_Len):
            if OmokBoard[i][j] == 1:  # White
                if prev != 1:
                    count_w = 1
                else:
                    count_w = count_w + 1
            elif OmokBoard[i][j] == 0:  # Black
                if prev != 0:
                    count_b = 1
                else:
                    count_b = count_b + 1

            if count_w >= 5:
                return 1
            if count_b >= 5:
                return 0
            prev = OmokBoard[i][j]

    for i in range(0, OmokBoard_Len):  # 세로를 보아라.
        count_w = 0
        count_b = 0
        prev = None
        for j in range(0, OmokBoard_Len):
            if OmokBoard[j][i] == 1:  # White
                if prev != 1:
                    count_w = 1
                else:
                    count_w = count_w + 1
            elif OmokBoard[j][i] == 0:  # Black
                if prev != 0:
                    count_b = 1
                else:
                    count_b = count_b + 1

            if count_w >= 5:
                return 1
            if count_b >= 5:
                return 0
            prev = OmokBoard[i][j]

    # 대각선의 시작...
    len = OmokBoard_Len

    for i in range(0, len):
        X, Y = i, 0

        count_w = 0
        count_b = 0
        prev = None

        while True:
            if X > len - 1 or Y > len - 1 or X < 0 or Y < 0:
                break

            if OmokBoard[X][Y] == 1:  # White
                if prev != 1:
                    count_w = 1
                else:
                    count_w = count_w + 1
            elif OmokBoard[X][Y] == 0:  # Black
                if prev != 0:
                    count_b = 1
                else:
                    count_b = count_b + 1

            if count_w >= 5:
                return 1
            if count_b >= 5:
                return 0
            prev = OmokBoard[X][Y]

            X = X - 1
            Y = Y + 1

    for i in range(0, len):
        X, Y = len - 1, i

        count_w = 0
        count_b = 0
        prev = None

        while True:
            if X > len - 1 or Y > len - 1 or X < 0 or Y < 0:
                break

            if OmokBoard[X][Y] == 1:  # White
                if prev != 1:
                    count_w = 1
                else:
                    count_w = count_w + 1
            elif OmokBoard[X][Y] == 0:  # Black
                if prev != 0:
                    count_b = 1
                else:
                    count_b = count_b + 1

            if count_w >= 5:
                return 1
            if count_b >= 5:
                return 0
            prev = OmokBoard[X][Y]

            X = X - 1
            Y = Y + 1

    for i in range(0, len):
        X, Y = len - 1 - i, 0

        count_w = 0
        count_b = 0
        prev = None

        while True:
            if X > len - 1 or Y > len - 1 or X < 0 or Y < 0:
                break

            if OmokBoard[X][Y] == 1:  # White
                if prev != 1:
                    count_w = 1
                else:
                    count_w = count_w + 1
            elif OmokBoard[X][Y] == 0:  # Black
                if prev != 0:
                    count_b = 1
                else:
                    count_b = count_b + 1

            if count_w >= 5:
                return 1
            if count_b >= 5:
                return 0
            prev = OmokBoard[X][Y]

            X = X + 1
            Y = Y + 1

    for i in range(0, len):
        X, Y = 0, i - 1

        count_w = 0
        count_b = 0
        prev = None

        while True:
            if X > len - 1 or Y > len - 1 or X < 0 or Y < 0:
                break

            if OmokBoard[X][Y] == 1:  # White
                if prev != 1:
                    count_w = 1
                else:
                    count_w = count_w + 1
            elif OmokBoard[X][Y] == 0:  # Black
                if prev != 0:
                    count_b = 1
                else:
                    count_b = count_b + 1

            if count_w >= 5:
                return 1
            if count_b >= 5:
                return 0
            prev = OmokBoard[X][Y]

            X = X + 1
            Y = Y + 1

    return -1

async def AsyncOmokCounter():
    pass
    global isOmokPlaying
    while True:
        if isOmokPlaying:
            pass

def AdminListToArr():
    file = os.path.join(PATH, "admin.list")
    f = open(file, "r")
    str = f.read()
    f.close()
    list = str.split('\n')
    list = [line for line in list if line.strip() != ""]
    return list

def SetAdminList(list):
    str = '\n'.join(list)
    file = os.path.join(PATH, "admin.list")
    f = open(file, "w")
    f.write(str)
    f.close()

def MentionToId(mention):
    id = mention[3:-1]
    return id

def IdToMention(id):
    mention = "<@!"+id+">"
    return mention


ignore = False

namuwikiNum = -1
namuwikiPrevLink = None

isNumGamePlaying = False
NumGamePlayer = None
NumGame_start_time = None
NumGame_end_time = None
NumGameAnswer = None
NumGameRange_S = None
NumGameRange_E = None
NumGameEstRange_S = None
NumGameEstRange_E = None
NumGameAttempt = None

AdminID = 351677960270381058
AdminList = AdminListToArr()

async def ServerStatusManager():
    Guild = client.get_guild(698722442033496195)
    DateCh = client.get_channel(783552826189152257)
    MemberCountCh = client.get_channel(783529681072685086)
    UserCountCh = client.get_channel(783551100803743804)
    BotCountCh = client.get_channel(783551141866373121)
    # RefreshTimeCh = client.get_channel(798719197822976011)
    # OnlineCountCh = client.get_channel(783529729906180107)
    # OfflineCountCh = client.get_channel(783529755924234261)
    while True:
        now = datetime.datetime.now()
        Date = str(now.year) + "년 " + str(now.month) + "월 " + str(now.day) + "일"
        MemberCount = Guild.member_count
        UserCount = len([m for m in Guild.members if not m.bot])
        BotCount = len([m for m in Guild.members if m.bot])
        # RefreshTime =
        # OnlineCount = sum(m.status!=discord.Status.offline and not m.bot for m in Guild.members)
        # OfflineCount = sum(m.status==discord.Status.offline and not m.bot for m in Guild.members)
        await DateCh.edit(name="| 📅 " + Date + " |")
        await MemberCountCh.edit(name="| 👥 전체 멤버 : " + str(MemberCount) + " |")
        await UserCountCh.edit(name="| 👤 유저 : " + str(UserCount) + " |")
        await BotCountCh.edit(name="| 🤖 봇 : " + str(BotCount) + " |")
        # await RefreshTimeCh.edit(name="| 🔄 새로고침 : " + RefreshTime + " |")
        # await OnlineCountCh.edit(name="| 🟢 온라인 : " + str(OnlineCount) + " |")
        # await OfflineCountCh.edit(name="| 🔴 오프라인 : " + str(OfflineCount) + " |")

        print("Server Status Updated.")
        await asyncio.sleep(600)


@client.event
async def on_ready():
    now = datetime.datetime.now()
    Time = "[" + str(now.year) + "-" + str(now.month) + "-" + str(now.day) + " " + \
           str(now.hour) + ":" + str(now.minute) + ":" + str(now.second) + "]"
    print("\n================="+Time+"=================\n")
    print(client.user.id)
    print("ready")
    game = discord.Game("𝓟𝔂𝓽𝓱𝓸𝓷")
    await client.change_presence(status=discord.Status.online, activity=game)
    ClearYoutubeDL()
    client.loop.create_task(ServerStatusManager())

#########################

@client.event
async def on_message(message):
    global AdminID
    global AdminList
    global ignore
    global player_flag
    global YTS_Title
    global YTS_VideoID
    global YTS_VideoURL
    global YTS_ChannelName
    global YTS_ChannelID
    global Timer

    if isinstance(message.channel, discord.channel.DMChannel):
        return

    if ignore == True and str(message.author.id) not in AdminList:
        return

    if message.content.startswith("!") or message.content.startswith(";"):
        now = datetime.datetime.now()
        Time = "[" + str(now.year) + "-" + str(now.month) + "-" + str(now.day) + " " + \
               str(now.hour) + ":" + str(now.minute) + ":" + str(now.second) + "]"
        S = Time + " [" + str(message.guild) + "] [" + str(message.author) + "] " + message.content
        print(S)
        log_path = os.path.join(PATH, "log.txt")
        with open(log_path, mode="r", encoding="utf-8") as f:
            data = f.read()
        with open(log_path, mode="w", encoding="utf-8") as f:
            f.write(S + "\n" + data)


        if message.content == "!명령어":
            embed = discord.Embed(title="𝓓𝓲𝓼𝓒𝓸𝓻𝓭𝓑𝓞𝓣 명령어", colour=discord.Colour.green())
            inline = False
            embed.add_field(name="**!명령어**", value="봇의 명령어를 보여줍니다.", inline=inline)
            embed.add_field(name="**!관리자 명령어**", value="관리자만 사용할 수 있어요.", inline=inline)
            embed.add_field(name="**!코드**", value="GitHub에서 봇 코드를 보여줍니다.", inline=inline)
            embed.add_field(name="**!안녕**", value="봇에게 인사합니다.", inline=inline)
            embed.add_field(name="**!말해라 [말]**", value="봇이 하고 싶은 말을 해줍니다.", inline=inline)
            embed.add_field(name="**!레식전적 [닉네임]**", value="레식 전적을 보여줍니다.", inline=inline)
            embed.add_field(name="**!롤전적 [닉네임]**", value="롤 전적을 보여줍니다.", inline=inline)
            embed.add_field(name="**!롤체전적 [닉네임]**", value="롤체 전적을 보여줍니다.", inline=inline)
            embed.add_field(name="**!나무위키 [검색]**", value="나무위키 검색 결과를 보여줍니다.", inline=inline)
            embed.add_field(name="**!영어사전 [검색]**", value="영어사전 검색 결과를 보여줍니다.", inline=inline)
            embed.add_field(name="**!번역 [한/영] [문장]**", value="번역 결과를 보여줍니다.", inline=inline)
            embed.add_field(name="**!날씨 [지역이름]**", value="오늘 날씨를 검색합니다.", inline=inline)
            embed.add_field(name="**!전화번호 [지역이름]**", value="전화번호를 검색합니다.", inline=inline)
            embed.add_field(name="**!가사 [노래]**", value="노래 가사를 검색합니다.", inline=inline)
            embed.add_field(name="**!상태메시지 [상태메시지]**", value="봇의 상태메시지를 바꿉니다.", inline=inline)
            embed.add_field(name="**!텍스트 [텍스트]**", value="텍스트를 멋있게 바꿔줍니다.", inline=inline)
            embed.add_field(name="**!사진 [검색어]**", value="구글에서 사진을 검색합니다.", inline=inline)
            embed.add_field(name="**!다나와 [제품]**", value="다나와에서 제품 가격을 보여줍니다.", inline=inline)
            embed.add_field(name="**!구글 [검색어]**", value="구글에서 검색 결과를 보여줍니다.", inline=inline)
            embed.add_field(name="**!링크 [검색어]**", value="링크를 보여줍니다.", inline=inline)
            embed.add_field(name="**!미니게임**", value="미니게임 명령어를 보여줍니다.", inline=inline)
            embed.add_field(name="**!자가진단 [학교] [이름] [생년월일]**", value="자가진단을 대신 해줍니다! (경기도만)", inline=inline)
            embed.add_field(name="**!명령어 노래봇**", value="노래봇 명령어를 보여줍니다.", inline=inline)
            embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
            await message.channel.send(embed=embed)
        elif message.content.startswith("!명령어 노래봇"):
            embed = discord.Embed(title="𝓓𝓲𝓼𝓒𝓸𝓻𝓭𝓑𝓞𝓣 노래봇 명령어", colour=discord.Colour.green())
            inline = False
            embed.add_field(name="**!명령어 노래봇**", value="노래봇 명령어를 보여줍니다.", inline=inline)
            embed.add_field(name="**!참가**", value="봇이 음성 채널에 참여합니다.", inline=inline)
            embed.add_field(name="**!나가**", value="봇이 음성 채널에서 나갑니다.", inline=inline)
            embed.add_field(name="**!재생 [URL]**", value="유튜브에서 노래를 재생합니다.", inline=inline)
            embed.add_field(name="**!검색 [제목]**", value="유튜브에서 영상을 검색해 결과를 보여줍니다.", inline=inline)
            embed.add_field(name="**!선택 [번호]**", value="검색 결과 중에서 선택합니다.", inline=inline)
            embed.add_field(name="**!반복 [횟수]**", value="현재 재생중인 노래를 지정한 횟수만큼 반복합니다.", inline=inline)
            embed.add_field(name="**!반복 중지**", value="현재 재생중인 노래의 반복을 중지합니다.", inline=inline)
            embed.add_field(name="**!일시정지**", value="노래를 일시정지합니다.", inline=inline)
            embed.add_field(name="**!다시재생**", value="노래를 다시 재생합니다.", inline=inline)
            embed.add_field(name="**!스킵**", value="노래를 스킵합니다.", inline=inline)
            embed.add_field(name="**!정지**", value="재생목록을 초기화합니다.", inline=inline)
            embed.add_field(name="**!재생목록**", value="재생목록을 보여줍니다.", inline=inline)
            embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
            await message.channel.send(embed=embed)
        elif message.content.startswith("!관리자"):
            if str(message.author.id) not in AdminList:
                embed = discord.Embed(title="실패!", description="관리자가 아니에요.", colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                return
            msg = message.content.split(" ")
            if len(msg) <= 1:
                embed = discord.Embed(title="실패!", description="명령어를 입력해주세요.", colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                return
            query = msg[1]
            if query == "명령어":
                embed = discord.Embed(title="𝓓𝓲𝓼𝓒𝓸𝓻𝓭𝓑𝓞𝓣 관리자 명령어", colour=discord.Colour.green())
                inline = False
                embed.add_field(name="**!관리자 명령어**", value="관리자 툴의 명령어를 보여줍니다.", inline=inline)
                embed.add_field(name="**!관리자 추가 [@멘션]**", value="봇 관리자를 추가합니다.", inline=inline)
                embed.add_field(name="**!관리자 제거 [@멘션]**", value="봇 관리자를 제거합니다.", inline=inline)
                embed.add_field(name="**!관리자 목록**", value="봇 관리자 목록을 보여줍니다.", inline=inline)
                embed.add_field(name="**!관리자 잠금**", value="봇이 작동하지 않게 합니다.", inline=inline)
                embed.add_field(name="**!관리자 잠금해제**", value="봇을 다시 작동합니다.", inline=inline)
                embed.add_field(name="**!관리자 종료**", value="봇을 종료합니다.", inline=inline)
                embed.add_field(name="**!관리자 온도**", value="𝓡𝓟𝓲4의 온도를 보여줍니다.", inline=inline)
                embed.add_field(name="**!관리자 실행 [명령어]**", value="𝓡𝓟𝓲4 𝓢𝓱𝓮𝓵𝓵 명령어를 실행합니다.", inline=inline)
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
            elif query == "잠금":
                ignore = True
                embed = discord.Embed(title="성공!", description="봇이 대답하지 않습니다.", colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
            elif query == "잠금해제":
                ignore = False
                embed = discord.Embed(title="성공!", description="봇이 대답합니다.", colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
            elif query == "종료":
                if message.author.id != AdminID:
                    embed = discord.Embed(title="실패!", description="권한이 없습니다.", colour=discord.Colour.green())
                    embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                    await message.channel.send(embed=embed)
                    return
                await client.change_presence(status=discord.Status.offline)
                embed = discord.Embed(title="종료 중...", description="봇을 종료합니다...", colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                exit()
            elif query == "온도":
                if platform == "Windows":
                    embed = discord.Embed(title="실패!", description="Windows 운영체제에서는 사용할 수 없습니다!",
                                          colour=discord.Colour.green())
                    embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                    await message.channel.send(embed=embed)
                    return
                command = "vcgencmd measure_temp"
                command = command.split(" ")
                # result = subprocess.run(['vcgencmd', 'measure_temp'], stdout=subprocess.PIPE)
                result = subprocess.run(command, stdout=subprocess.PIPE)
                R = result.stdout.decode('utf-8')
                embed = discord.Embed(title="𝓡𝓟𝓲4 온도", description=R, colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
            elif query == "추가":
                if message.author.id != AdminID:
                    embed = discord.Embed(title="실패!", description="권한이 없습니다.", colour=discord.Colour.green())
                    embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                    await message.channel.send(embed=embed)
                    return
                mention = msg[2]
                id = MentionToId(mention)
                if id in AdminList:
                    embed = discord.Embed(title="실패!", description="해당 유저는 이미 관리자입니다.", colour=discord.Colour.green())
                    embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                    await message.channel.send(embed=embed)
                    return
                AdminList.append(id)
                SetAdminList(AdminList)
                embed = discord.Embed(title="성공!", description=mention + " 을 관리자 목록에 추가했습니다.", colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
            elif query == "제거":
                if message.author.id != AdminID:
                    embed = discord.Embed(title="실패!", description="권한이 없습니다.", colour=discord.Colour.green())
                    embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                    await message.channel.send(embed=embed)
                    return
                mention = msg[2]
                id = MentionToId(mention)
                if id not in AdminList:
                    embed = discord.Embed(title="실패!", description="해당 유저는 관리자가 아닙니다.", colour=discord.Colour.green())
                    embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                    await message.channel.send(embed=embed)
                    return
                if id == str(AdminID):
                    embed = discord.Embed(title="실패!", description="해당 유저는 제거할 수 없습니다.", colour=discord.Colour.green())
                    embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                    await message.channel.send(embed=embed)
                    return
                AdminList.remove(id)
                SetAdminList(AdminList)
                embed = discord.Embed(title="성공!", description=mention+" 은 더 이상 관리자가 아닙니다.", colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
            elif query == "목록":
                AdminList = AdminListToArr()
                S = ""
                for id in AdminList:
                    mention = IdToMention(id)
                    S += mention+"\n"
                embed = discord.Embed(title="𝓓𝓲𝓼𝓒𝓸𝓻𝓭𝓑𝓞𝓣 관리자 목록", description=S, colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
        elif message.content.startswith("!exec"):
            if message.author.id != AdminID:
                embed = discord.Embed(title="실패!", description="관리자가 아니에요.", colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                return
            msg = message.content
            cmd = msg[6:]
            if cmd is None:
                embed = discord.Embed(title="실패!", description="명령어를 입력해주세요.", colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                return

            sp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
            output = sp.stdout.read()
            output = output.decode("utf-8")

            embed = discord.Embed(title=cmd, description="```"+output+"```", colour=discord.Colour.green())
            embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
            await message.channel.send(embed=embed)

        elif message.content.startswith("!코드"):
            link = "https://github.com/CrazyRiot0/DiscordBotPi/blob/master/main.py"
            await message.channel.send(link)
        elif message.content.startswith("!안녕"):
            await message.channel.send("안녕하세요!")
        elif message.content.startswith("!아침"):
            await message.channel.send("좋은 아침이에요!")
        elif message.content.startswith("!노예야"):
            await message.channel.send("예 주인님!")
        elif message.content.startswith("!말해라"):
            msg = message.content
            if len(msg) == 0:
                await message.channel.send("말을 입력해주세요.")
            else:
                await message.channel.send(msg[5:])
        elif message.content.startswith("!레식전적"):
            msg = message.content
            username = msg[6:]
            if len(username) == 0:
                embed = discord.Embed(title="실패!", description="닉네임을 입력해주세요.", colour=discord.Colour.green())
                await message.channel.send(embed=embed)
                return

            link = "https://r6.tracker.network/profile/pc/" + urllib.parse.quote(username)
            reqUrl = urllib.request.Request(link, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(urllib.request.urlopen(reqUrl).read(), 'html.parser')

            embed = discord.Embed(title=username + "'s R6S Stats", colour=discord.Colour.green())

            code = soup.find_all(True, class_="trn-card")
            index = 1
            for X in code:
                title = X.find(True, {'class': ['trn-card__header-tab',
                                                 'trn-card__header-title']})
                if title is None:
                    continue
                title = title.text.strip()

                C = X.find_all("div", {'class': ['trn-defstat mb0', 'trn-defstat']})
                S = ""
                for T in C:
                    name = T.find("div", class_="trn-defstat__name").text.strip()
                    value = T.find("div", class_="trn-defstat__value").text.strip()
                    S += "**• " + name + "** : " + value + "\n"

                if len(S) == 0:
                    continue

                inline = True
                if index == 1:
                    inline = False
                elif index == 5:
                    inline = False
                embed.add_field(name="["+title+"]", value=S, inline=inline)
                index = index + 1


            embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
            await message.channel.send(embed=embed)
        elif message.content.startswith("!롤전적"):
            msg = message.content
            username = msg[5:]
            if len(username) == 0:
                embed = discord.Embed(title="실패!", description="닉네임을 입력해주세요.", colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                return
            link = "https://www.op.gg/summoner/userName=" + urllib.parse.quote(username)

            reqUrl = urllib.request.Request(link, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(urllib.request.urlopen(reqUrl).read(), 'html.parser')
            code = soup.find("img", {"class": "ProfileImage"})
            ProfileImageURL = "https:" + code["src"]
            RankingCode = soup.find("div", {"class": "SummonerRatingMedium"})
            # code = RankingCode.find("div", {"class": "Medal tip"})
            # code = code.find("img", {"class": "Image"})
            # RankingLogoURL = "https:" + code["src"]
            code = soup.find("span", {"class": "Level tip"})
            Level = code.text
            code = soup.find("div", {"class": "TierRank"})
            SoloRank = ""
            SoloRankWins = ""
            SoloRankLosses = ""
            SoloRankWinLose = ""
            SoloRankWinRatio = ""
            FreeRank = ""
            FreeRankWinLose = ""
            FreeRankWinRatio = ""

            if code is not None:
                SoloRank = code.text
            code = soup.find("span", {"class": "WinLose"})
            if code is not None:
                code2 = code.find("span", {"class": "wins"})
                if code2 is not None:
                    SoloRankWins = code2.text
                code2 = code.find("span", {"class": "losses"})
                if code2 is not None:
                    SoloRankLosses = code2.text
                SoloRankWinLose = SoloRankWins + " " + SoloRankLosses
                code2 = code.find("span", {"class": "winratio"})
                if code2 is not None:
                    SoloRankWinRatio = code2.text

            FreeRankCode = soup.find("div", {"class": "sub-tier__info"})
            code = FreeRankCode.find("div", {"class": "sub-tier__rank-tier"})
            if code is not None:
                FreeRank = code.text.strip()
            code = FreeRankCode.find("span", {"class": "sub-tier__gray-text"})
            if code is not None:
                FreeRankWinLose = code.text[2:]
            code = FreeRankCode.find("div", {"class": "sub-tier__gray-text"})
            if code is not None:
                FreeRankWinRatio = code.text.strip()

            embed = discord.Embed(title="", description="", colour=discord.Colour.green())
            iconurl = "https://opgg-com-image.akamaized.net/attach/images/20190416173507.228538.png"
            embed.set_author(name=username, url=link, icon_url=iconurl)
            embed.set_thumbnail(url=ProfileImageURL)
            inline = True
            embed.add_field(name="레벨", value=Level, inline=inline)
            embed.add_field(name="솔로랭크", value=SoloRank + "\n" + SoloRankWinLose + "\n" + SoloRankWinRatio, inline=inline)
            embed.add_field(name="자유랭크", value=FreeRank + "\n" + FreeRankWinLose + "\n" + FreeRankWinRatio, inline=inline)
            embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
            await message.channel.send(embed=embed)
        elif message.content.startswith("!롤체전적"):
            msg = message.content
            username = msg[6:]
            if len(username) == 0:
                embed = discord.Embed(title="실패!", description="닉네임을 입력해주세요.", colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                return

            link = "https://lolchess.gg/profile/kr/" + urllib.parse.quote(username)
            reqUrl = urllib.request.Request(link, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(urllib.request.urlopen(reqUrl).read(), 'html.parser')

            profile_icon = soup.find("div", {"class": "profile__icon"}).find("img")["src"]
            profile_icon = "https:" + profile_icon
            code = soup.find("div", {"class": "profile__tier"})
            tier = code.find("span", {"class": "profile__tier__summary__tier text-diamond"}).text
            tier_icon = code.find("div", {"class": "profile__tier__icon"}).find("img")["src"]
            lp = code.find("span", {"class": "profile__tier__summary__lp"}).text
            winratio = code.find("div", {"class": "col-6 profile__tier__winrate_10"})\
                .find("span", {"class": "profile__tier__stat__value float-right"}).text.strip()
            wins = code.find("div", {"class": "col-6 profile__tier__wins"})\
                .find("span", {"class": "profile__tier__stat__value float-right"}).text.strip()
            top4ratio = code.find("div", {"class": "col-6 profile__tier__toprate"})\
                .find("span", {"class": "profile__tier__stat__value float-right"}).text.strip()

            embed = discord.Embed(title="", description="", colour=discord.Colour.green())
            favicon = "https://cdn.lolchess.gg/images/favicon/ms-icon-144x144.png"
            embed.set_author(name=username, url=link, icon_url=favicon)
            embed.set_thumbnail(url=profile_icon)
            inline = False
            embed.add_field(name="티어", value=tier+" "+lp, inline=inline)
            embed.add_field(name="승률", value=winratio, inline=inline)
            embed.add_field(name="승리", value=wins, inline=inline)
            embed.add_field(name="TOP 4 비율", value=top4ratio, inline=inline)
            embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)

            await message.channel.send(embed=embed)
        elif message.content.startswith("!나무위키"):
            global namuwikiNum
            global namuwikiPrevLink
            global namuwikiPrevTitle
            msg = message.content
            list = msg.split(" ")
            if list[1] == "다음":
                if namuwikiNum == -1:
                    embed = discord.Embed(title="실패!", description="먼저 **[!나무위키]**를 통해 검색해 주세요.",
                                          colour=discord.Colour.green())
                    embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                    await message.channel.send(embed=embed)
                namuwikiNum = namuwikiNum + 1
                reqUrl = urllib.request.Request(namuwikiPrevLink, headers={'User-Agent': 'Mozilla/5.0'})
                soup = BeautifulSoup(urllib.request.urlopen(reqUrl).read(), 'html.parser')
                code = soup.find_all("div", {"class": "wiki-heading-content"})
                result = code[namuwikiNum].getText(' ', strip=True)
                code = soup.find_all("h2", {"class": "wiki-heading"})
                title = code[namuwikiNum].getText(' ', strip=True)
                if len(result) > 2000:
                    result = result[:2000]
                    result += " ..."
                S = "(페이지 " + str(namuwikiNum + 1) + ")"
                embed = discord.Embed(title="**" + namuwikiPrevTitle + "** 검색 결과 " + S, description=result,
                                      colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                return
            query = msg[6:]
            original = query
            query = urllib.parse.quote(query)
            if len(query) == 0:
                await message.channel.send("https://namu.wiki/w/")
            else:
                link = "https://namu.wiki/w/" + query
            namuwikiPrevLink = link
            namuwikiNum = 0
            namuwikiPrevTitle = original
            reqUrl = urllib.request.Request(link, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(urllib.request.urlopen(reqUrl).read(), 'html.parser')
            code = soup.find_all("div", {"class": "wiki-heading-content"})
            result = code[0].getText(' ', strip=True)
            code = soup.find_all("h2", {"class": "wiki-heading"})
            title = code[0].getText(' ', strip=True)
            if len(result) > 2000:
                result = result[:2000]
                result += " ..."
            embed = discord.Embed(title="**" + original + "** 검색 결과", description=result,
                                  colour=discord.Colour.green())
            embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
            await message.channel.send(embed=embed)
        elif message.content.startswith("!영어사전"):
            msg = message.content
            q = msg[6:]
            if len(q) == 0:
                embed = discord.Embed(title="실패!", description="검색어를 입력해주세요.", colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                return
            link = "https://small.dic.daum.net/search.do?dic=eng&q=" + urllib.parse.quote(q)
            reqUrl = urllib.request.Request(link, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(urllib.request.urlopen(reqUrl).read(), 'html.parser')
            code = soup.find("meta", {"property": "og:description"})
            result = code["content"]

            embed = discord.Embed(title=q, description=result, colour=discord.Colour.green())
            embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
            await message.channel.send(embed=embed)
        elif message.content.startswith("!번역"):
            msg = message.content
            check = msg.split(" ")
            lang = check[1]
            # link = "https://translate.google.com/#view=home&op=translate"
            link = "https://papago.naver.com/"
            if lang == "한":
                # link += "&sl=ko&tl=en&text="
                link += "?sk=ko&tk=en&st="
            elif lang == "영":
                # link += "?&sl=en&tl=ko&text="
                link += "?sk=en&tk=ko&st="
            else:
                embed = discord.Embed(title="실패!", description="언어를 제대로 입력해주세요.", colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                return
            query = msg[6:]
            link += urllib.parse.quote(query)

            embed = discord.Embed(title="번역 중...", description="번역 중입니다...", colour=discord.Colour.green())
            embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
            await message.channel.send(embed=embed)

            start_time = time.time()

            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument("headless")
            chrome_options.add_argument("disable-gpu")
            wd = None
            if platform == "Windows":
                chromedriver_path = os.path.join(PATH, "executables", "chromedriver.exe")
                wd = webdriver.Chrome(executable_path=chromedriver_path, options=chrome_options)
            elif platform == "Linux":
                wd = webdriver.Chrome(options=chrome_options)
            wd.get(link)
            wait = WebDriverWait(wd, 10)
            element = wait.until(EC.presence_of_element_located((By.ID, "txtTarget")))
            result = element.text
            wd.quit()

            if len(result) == 0:
                embed = discord.Embed(title="실패!", description="번역에 실패했어요.", colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                return

            end_time = time.time()
            duration = round(end_time - start_time, 2)
            duration = str(duration)
            S = " (" + duration + "s)"
            embed = discord.Embed(title=query + " 번역 결과", description=result + S, colour=discord.Colour.green())
            embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
            await message.channel.send(embed=embed)
        elif message.content.startswith("!날씨"):
            location = message.content[4:]
            if len(location) == 0:
                embed = discord.Embed(title="실패!", description="지역을 입력해주세요.", colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                return
            query = location + " 날씨"
            query = urllib.parse.quote(query)
            link = "https://search.naver.com/search.naver?query=" + query
            reqUrl = urllib.request.Request(link, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(urllib.request.urlopen(reqUrl).read(), 'html.parser')
            code1 = soup.find("span", class_="todaytemp")  # 온도
            if code1 is None:
                embed = discord.Embed(title="실패!", description="지역을 찾을 수 없어요.", colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                return
            temp = code1.text
            temp += "℃"
            code2 = soup.find("span", class_="btn_select")  # 지역명
            if code2 is None:
                code3 = soup.find("a", class_="btn_select _selectLayerTrigger")  # 해외 날씨
                tloc = code3.text
            else:
                tloc = code2.text  # 국내 날씨
            code4 = soup.find("span", class_="min")  # 최저기온
            if code4 is None:
                code4 = "Null"
            else:
                code4 = code4.text
            min = code4
            code5 = soup.find("span", class_="max")  # 최고기온
            if code5 is None:
                code5 = "Null"
            else:
                code5 = code5.text
            max = code5
            code6 = soup.find("span", class_="sensible")  # 체감온도
            if code6 is None:
                code6 = "Null"
            else:
                code6 = code6.text
            code6 = code6.split(" ")
            sensible = code6[1]
            code7 = soup.find("span", class_="rainfall")  # 시간당 강수량
            if code7 is None:
                code7 = "Null"
            else:
                code7 = code7.text
            rainfall = code7
            code8 = soup.find("div", class_="detail_box")  # 미세먼지, 초미세먼지, 오존지수
            if code8 is None:
                code8 = "Null"
            else:
                code8 = code8.text
            detail = code8
            detail = detail[2:]
            t = detail.split(" ")
            detail = t[0] + " " + t[1] + "\n"
            detail += t[2] + " " + t[3] + "\n"
            detail += t[4] + " " + t[5] + "\n"
            embed = discord.Embed(title=tloc + " 날씨", colour=discord.Colour.green())
            embed.add_field(name="온도", value=temp)
            embed.add_field(name="최저기온", value=min)
            embed.add_field(name="최고기온", value=max)
            embed.add_field(name="체감온도", value=sensible)
            embed.add_field(name="시간당 강수량", value=rainfall)
            embed.add_field(name="미세먼지", value=detail)

            embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
            await message.channel.send(embed=embed)
        elif message.content.startswith("!계산기"):
            msg = message.content
            query = msg[5:]
            command = ["qalc", query]
            result = subprocess.run(command, stdout=subprocess.PIPE)
            R = result.stdout.decode('utf-8')
            embed = discord.Embed(title="계산 결과", description=R, colour=discord.Colour.green())
            embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
            await message.channel.send(embed=embed)
        elif message.content.startswith("!전화번호"):
            query = message.content[6:]
            if len(query) == 0:
                embed = discord.Embed(title="실패!", description="검색 대상을 입력해주세요.", colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                return
            query = query + " 전화번호"
            query = urllib.parse.quote(query)
            link = "https://search.naver.com/search.naver?query=" + query
            reqUrl = urllib.request.Request(link, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(urllib.request.urlopen(reqUrl).read(), 'html.parser')
            code1 = soup.find("a", class_="tit _title _sp_each_url _sp_each_title")
            if code1 is None:
                await message.channel.send("지역을 찾을 수 없어요.")
            place = code1.text
            code2 = soup.find("span", class_="tell")
            tell = code2.text
            embed = discord.Embed(title=place, description=tell, colour=discord.Colour.green())
            embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
            await message.channel.send(embed=embed)
        elif message.content.startswith("!가사"):
            query = message.content[4:]
            query = query + " 가사"
            query = urllib.parse.quote(query)
            link = "https://search.naver.com/search.naver?query=" + query
            reqUrl = urllib.request.Request(link, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(urllib.request.urlopen(reqUrl).read(), 'html.parser')
            code1 = soup.find("div", class_="lyrics_area")
            if code1 is None:
                embed = discord.Embed(title="실패!", description="노래 가사를 찾을 수 없습니다.", colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                return
            lyrics = code1.getText('\n', strip=True)
            lyrics = lyrics[:lyrics.rfind('\n')]
            lyrics = lyrics[:lyrics.rfind('\n')]
            code2 = soup.find("h3", class_="api_title")
            title = code2.text
            embed = discord.Embed(title=title, description=lyrics, colour=discord.Colour.green())
            embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
            await message.channel.send(embed=embed)
        elif message.content.startswith("!상태메시지"):
            msg = message.content
            q = msg[7:]
            if len(q) != 0:
                game = discord.Game(q)
                await client.change_presence(status=discord.Status.online, activity=game)
                embed = discord.Embed(title="성공!", description="상태메시지를 **" + q + "** 로 바꿨어요.",
                                      colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
            else:
                embed = discord.Embed(title="실패!", description="상태메시지를 입력해주세요.", colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
        elif message.content.startswith("!텍스트"):
            msg = message.content
            q = msg[5:]
            if len(q) == 0:
                embed = discord.Embed(title="실패!", description="텍스트를 입력해주세요.", colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                return
            org = q
            q = urllib.parse.quote(q)
            link = "http://qaz.wtf/u/convert.cgi?text=" + q
            reqUrl = urllib.request.Request(link, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(urllib.request.urlopen(reqUrl).read(), 'html.parser')
            code = soup.find_all("td")
            type = ""
            text = ""
            embed = discord.Embed(title=org, colour=discord.Colour.green())
            flag = False
            for X in code:
                if flag is True:
                    text = X.text
                    text = text[:text.rfind('\n')]
                    embed.add_field(name=type, value=text, inline=True)
                    flag = False
                else:
                    type = X.text
                    flag = True
            embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
            await message.channel.send(embed=embed)
        elif message.content.startswith("!사진") or message.content.startswith(";"):
            if message.content.startswith("!사진"):
                q = message.content[4:]
            elif message.content.startswith(";"):
                q = message.content[1:]

            link = "https://www.google.com/search?tbm=isch&q=" + urllib.parse.quote(q)
            reqUrl = urllib.request.Request(link, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(urllib.request.urlopen(reqUrl).read(), 'html.parser')
            code = soup.find("table", {"class": "GpQGbf"})
            code = code.find("td", {"class": "e3goi"})
            code = code.find("img")
            src = code["src"]

            embed = discord.Embed(title=q + " 검색 결과", colour=discord.Colour.green())
            embed.set_image(url=src)
            embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
            await message.channel.send(embed=embed)

            """
            if len(q) == 0:
                embed = discord.Embed(title="실패!", description="검색할 말을 입력해주세요.", colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                return
            response = google_images_download.googleimagesdownload()
            args = {"keywords": q, "limit": 1, "print_urls": True, "no_directory": True}
            try:
                paths = response.download(args)
            except:
                embed = discord.Embed(title="실패!", description="검색 결과가 없습니다.", colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                return

            path = next(iter(paths[0].values()))[0]

            embed = discord.Embed(title=q+" 검색 결과", colour=discord.Colour.green())
            file = discord.File(path, filename="image.png")
            embed.set_image(url="attachment://image.png")
            embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
            await message.channel.send(file=file, embed=embed)

            os.remove(path)
            """
        elif message.content.startswith("!다나와"):
            msg = message.content
            query = msg[5:]
            if len(query) == 0:
                embed = discord.Embed(title="실패!", description="제품 이름을 입력해주세요.", colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                return
            link = "http://search.danawa.com/dsearch.php?query=" + urllib.parse.quote(query)

            embed = discord.Embed(title="검색 중...", description="**" + query + "** 를 검색하는 중...",
                                  colour=discord.Colour.green())
            embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
            await message.channel.send(embed=embed)

            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument("headless")
            chrome_options.add_argument("disable-gpu")
            wd = None
            if platform == "Windows":
                chromedriver_path = os.path.join(PATH, "executables", "chromedriver.exe")
                wd = webdriver.Chrome(executable_path=chromedriver_path, options=chrome_options)
            elif platform == "Linux":
                wd = webdriver.Chrome(options=chrome_options)
            wd.get(link)
            wait = WebDriverWait(wd, 10)

            element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "prod_name")))
            prd_name = element.text
            element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "click_log_product_standard_price_")))
            prd_price = element.text
            element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "click_log_product_standard_img_")))
            prd_image_src = element.get_attribute("src")
            element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "click_log_product_standard_title_")))
            prd_link = element.get_attribute("href")
            # prd_name = wd.find_elements_by_class_name("prod_name")
            # prd_price = wd.find_elements_by_class_name("price_sect")
            wd.quit()

            embed = discord.Embed(title=prd_name, description="**" + prd_price + "**", colour=discord.Colour.green())
            embed.set_image(url=prd_image_src)
            embed.set_author(name="Danawa (링크)", url=prd_link,
                             icon_url="http://img.danawa.com/new/tour/img/logo/sns_danawa.jpg")
            embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
            await message.channel.send(embed=embed)
        elif message.content.startswith("!구글"):
            msg = message.content
            query = msg[4:]
            link = "https://www.google.com/search?q=" + urllib.parse.quote(query)
            reqUrl = urllib.request.Request(link, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(urllib.request.urlopen(reqUrl).read(), 'html.parser')
            code = soup.find_all("div", {"class": "BNeawe"})
            result = code[0].text

            embed = discord.Embed(title=query, description=result, colour=discord.Colour.green())
            embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
            await message.channel.send(embed=embed)
        elif message.content.startswith("!링크"):
            msg = message.content
            query = msg[4:]
            link = "http://www.google.com/search?btnI&q=" + urllib.parse.quote(query)
            reqUrl = urllib.request.Request(link, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(urllib.request.urlopen(reqUrl).read(), 'html.parser')
            code = soup.find("div", class_="fTk7vd")
            code = code.find("a")
            url = code['href']

            # S = "[" + query + "](" + url + ")"
            embed = discord.Embed(title=query, description=url, colour=discord.Colour.green())
            embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
            await message.channel.send(embed=embed)

        elif message.content.startswith("!미니게임"):
            embed = discord.Embed(title="𝓓𝓲𝓼𝓒𝓸𝓻𝓭𝓑𝓞𝓣 미니게임 명령어", colour=discord.Colour.green())
            inline = False
            embed.add_field(name="**!미니게임**", value="미니게임 명령어를 보여줍니다.", inline=inline)
            embed.add_field(name="**!사다리게임 [목록(띄어쓰기 구분)] / [목록(띄어쓰기 구분)]**", value="사다리게임 결과를 보여줍니다.", inline=inline)
            embed.add_field(name="**!숫자맞추기 명령어**", value="숫자 맞추기 게임 명령어를 보여줍니다.", inline=inline)
            embed.add_field(name="**!오목 명령어**", value="오목 명령어를 보여줍니다.", inline=inline)
            embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
            await message.channel.send(embed=embed)

        elif message.content.startswith("!사다리게임"):
            msg = message.content
            list = msg.split(" ")
            if len(list) == 1:
                embed = discord.Embed(title="실패!", description="목록을 입력해주세요.", colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                return
            list.pop(0)
            isFirst = True
            first = []
            end = []
            for X in list:
                if X == "/":
                    isFirst = False
                    continue
                if isFirst:
                    first.append(X)
                else:
                    end.append(X)
            if len(first) != len(end):
                embed = discord.Embed(title="실패!", description="두 목록의 길이가 일치하지 않습니다.", colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                return

            L = len(first)
            result = []

            for i in range(0, L):
                while True:
                    n = randint(0, L - 1)
                    if CheckAlreadyUsed(n, result) == False:
                        break
                result.append(n)

            S = ""
            for i in range(0, L):
                S += first[i] + " -> " + end[result[i]] + "\n"
            embed = discord.Embed(title="사다리게임 결과", description=S, colour=discord.Colour.green())
            embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
            await message.channel.send(embed=embed)
        elif message.content.startswith("!숫자맞추기"):
            global isNumGamePlaying
            global NumGamePlayer
            global NumGame_start_time
            global NumGame_end_time
            global NumGameAnswer
            global NumGameRange_S
            global NumGameRange_E
            global NumGameEstRange_S
            global NumGameEstRange_E
            global NumGameAttempt

            if isNumGamePlaying and message.author.id != NumGamePlayer:
                embed = discord.Embed(title="실패!", description="게임이 이미 다른 플레이어에 의해 실행 중이에요.",
                                      colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                return
            msg = message.content
            list = msg.split(" ")
            if len(list) == 1:
                embed = discord.Embed(title="실패!", description="명령어를 제대로 입력해주세요.\n"
                                                               "**[!숫자맞추기 명령어]** 로 명령어를 확인하세요.",
                                      colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                return
            list.pop(0)
            query = list[0]
            if query == "명령어":
                embed = discord.Embed(title="𝓓𝓲𝓼𝓒𝓸𝓻𝓭𝓑𝓞𝓣 미니게임 숫자맞추기 명령어", colour=discord.Colour.green())
                inline = False
                embed.add_field(name="**!숫자맟추기 명령어**", value="숫자맞추기 게임 명령어를 보여줍니다.", inline=inline)
                embed.add_field(name="**!숫자맟추기 시작 [시작 숫자] [끝 숫자]**", value="숫자맞추기 게임을 시작합니다.", inline=inline)
                embed.add_field(name="**!숫자 [숫자]**", value="숫자를 선택합니다.", inline=inline)
                embed.add_field(name="**!숫자맟추기 종료**", value="숫자맞추기 게임을 종료합니다.", inline=inline)
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                return
            elif query == "시작":
                if isNumGamePlaying:
                    embed = discord.Embed(title="실패!", description="게임이 이미 플레이 중입니다.", colour=discord.Colour.green())
                    embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                    await message.channel.send(embed=embed)
                    return
                list.pop(0)
                if len(list) != 2:
                    embed = discord.Embed(title="실패!", description="숫자 범위를 정확히 입력해주세요.", colour=discord.Colour.green())
                    embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                    await message.channel.send(embed=embed)
                    return
                NumGameRange_S = int(list[0])
                NumGameRange_E = int(list[1])
                NumGameAnswer = randint(NumGameRange_S, NumGameRange_E)
                NumGameEstRange_S = NumGameRange_S
                NumGameEstRange_E = NumGameRange_E
                NumGame_start_time = time.time()
                isNumGamePlaying = True
                NumGamePlayer = message.author.id
                NumGameAttempt = 0
                RangeInStr = "[" + str(NumGameRange_S) + " ~ " + str(NumGameRange_E) + "]"
                embed = discord.Embed(title="숫자맞추기 게임 시작! " + RangeInStr, description="숫자맞추기 게임을 시작했습니다.\n"
                                                                                      "**[!숫자 [숫자]]** 로 숫자를 맞춰보세요.\n"
                                                                                      "**[!숫자맞추기 종료]** 로 게임을 종료합니다.\n",
                                      colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
            elif query == "종료":
                if message.author.id != NumGamePlayer:
                    if message.author.id == AdminID:
                        isNumGamePlaying = False
                        embed = discord.Embed(title="숫자맞추기 게임 종료", description="관리자의 권한으로 숫자맞추기 게임을 종료했습니다.",
                                              colour=discord.Colour.green())
                        embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                        await message.channel.send(embed=embed)
                        return
                    embed = discord.Embed(title="실패!", description="플레이어가 아닙니다.", colour=discord.Colour.green())
                    embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                    await message.channel.send(embed=embed)
                    return
                isNumGamePlaying = False
                embed = discord.Embed(title="숫자맞추기 게임 종료", description="숫자맞추기 게임을 종료했습니다.",
                                      colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                return
        elif message.content.startswith("!숫자"):
            if message.author.id != NumGamePlayer:
                embed = discord.Embed(title="실패!", description="플레이어가 아닙니다.", colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                return
            msg = message.content
            list = msg.split(" ")
            if len(list) != 2:
                embed = discord.Embed(title="실패!", description="숫자를 제대로 입력해주세요.", colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                return
            num = list[1]
            num = int(num)
            if num < NumGameEstRange_S or num > NumGameEstRange_E:
                embed = discord.Embed(title="실패!", description="범위 안에 있는 숫자를 입력해주세요.", colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                return
            S = "**" + str(num)
            if num > NumGameAnswer:  # 5 입력 : 답 2      범위 1 <= 정답 <= 100
                NumGameEstRange_E = num
                S += " [미만]**\n"
            elif num < NumGameAnswer:  # 5 입력 : 답 10    범위 1 <= 정답 <= 100
                NumGameEstRange_S = num
                S += " [초과]**\n"
            else:  # 숫자 맞춤
                isNumGamePlaying = False
                NumGameAttempt += 1
                S = "숫자를 맞췄어요! (**" + str(NumGameAttempt) + "**번 시도)"
                embed = discord.Embed(title="성공!", description=S, colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                return
            NumGameAttempt += 1
            AttemptInStr = "[" + str(NumGameAttempt) + "번째 시도]"
            S += "**[" + str(NumGameEstRange_S) + " < 정답 < " + str(NumGameEstRange_E) + "]**"
            embed = discord.Embed(title="숫자맞추기 " + AttemptInStr, description=S, colour=discord.Colour.green())
            embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
            await message.channel.send(embed=embed)
        elif message.content.startswith("!오목"):
            global isOmokPlaying
            global isOmokHosting
            global OmokPlayer_White
            global OmokPlayer_White_Name
            global OmokPlayer_Black
            global OmokPlayer_Black_Name
            global Omok_Turn  # True = White, False = Black
            global OmokBoard_Len
            global OmokBoard

            msg = message.content
            list = msg.split(" ")
            if len(list) == 1:
                embed = discord.Embed(title="실패!", description="명령어를 제대로 입력해주세요.\n"
                                                               "**[!오목 명령어]** 로 명령어를 확인하세요.",
                                      colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                return
            list.pop(0)
            query = list[0]
            if query == "명령어":
                embed = discord.Embed(title="𝓓𝓲𝓼𝓒𝓸𝓻𝓭𝓑𝓞𝓣 미니게임 오목 명령어", colour=discord.Colour.green())
                inline = False
                embed.add_field(name="**!오목 명령어**", value="오목 명령어를 보여줍니다.", inline=inline)
                embed.add_field(name="**!오목 시작**", value="오목 게임을 호스트로 시작합니다.", inline=inline)
                embed.add_field(name="**!오목 참가**", value="실행 중인 오목 게임에 참가합니다.", inline=inline)
                embed.add_field(name="**!오목 두기 [x좌표] [y좌표]**", value="해당 좌표에 돌을 놓습니다.", inline=inline)
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                return
            elif query == "시작":
                isOmokHosting = True
                OmokPlayer_White = message.author.id
                OmokPlayer_White_Name = message.author.name
                # client.loop.create_task(AsyncOmokCounter())
                embed = discord.Embed(title="성공!", description="오목 게임을 시작했습니다.\n"
                                                               "**[!오목 참가]** 를 통해 참가하세요.\n"
                                                               "**[!오목 종료]** 를 통해 게임을 취소합니다.\n",
                                      colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
            elif query == "종료":
                if message.author.id != AdminID:
                    if message.author.id != OmokPlayer_White or message.author.id != OmokPlayer_Black:
                        embed = discord.Embed(title="실패!", description="플레이어가 아니에요.", colour=discord.Colour.green())
                        embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                        await message.channel.send(embed=embed)
                        return
                isOmokHosting = False
                isOmokPlaying = False
                embed = discord.Embed(title="성공!", description="오목 게임을 종료했습니다.", colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
            elif query == "참가":
                if isOmokHosting is False:
                    embed = discord.Embed(title="실패!", description="참가할 게임이 없습니다.", colour=discord.Colour.green())
                    embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                    await message.channel.send(embed=embed)
                    return
                '''if message.author.id == OmokPlayer_White:
                    embed = discord.Embed(title="실패!", description="호스트는 자기 자신의 게임에 참가할 수 없어요.", colour=discord.Colour.green())
                    embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                    await message.channel.send(embed=embed)
                    return'''
                OmokPlayer_Black = message.author.id
                OmokPlayer_Black_Name = message.author.name
                isOmokPlaying = True
                Omok_MakeBoard()

                S = "**" + OmokPlayer_White_Name + "** 님의 게임에 참가했습니다."
                embed = discord.Embed(title="성공!", description=S, colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)

                Omok_Turn = True  # 하얀 돌 먼저 시작

                S = "하얀 돌 : **" + OmokPlayer_White_Name + "**\n"
                S += "검은 돌 : **" + OmokPlayer_Black_Name + "**"
                embed = discord.Embed(title="게임을 시작합니다!", description=S, colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)

                embed = discord.Embed(title="오목", description=OmokBoardInStr(), colour=discord.Colour.green())
                await message.channel.send(embed=embed)

                S = ""
                if Omok_Turn is True:
                    S += "하얀 돌 [" + OmokPlayer_White_Name + "]"
                else:
                    S += "검은 돌 [" + OmokPlayer_Black_Name + "]"
                embed = discord.Embed(title=S + " 차례입니다.", colour=discord.Colour.green())
                await message.channel.send(embed=embed)
            elif query == "두기":
                if isOmokPlaying is False:
                    embed = discord.Embed(title="실패!", description="참가할 게임이 없습니다.", colour=discord.Colour.green())
                    embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                    await message.channel.send(embed=embed)
                    return
                if message.author.id != OmokPlayer_White and message.author.id != OmokPlayer_Black:
                    embed = discord.Embed(title="실패!", description="플레이어가 아닙니다.", colour=discord.Colour.green())
                    embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                    await message.channel.send(embed=embed)
                    return
                if Omok_Turn is True:
                    if message.author.id != OmokPlayer_White:
                        embed = discord.Embed(title="실패!", description="차례가 아니에요.", colour=discord.Colour.green())
                        embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                        await message.channel.send(embed=embed)
                        return
                if Omok_Turn is False:
                    if message.author.id != OmokPlayer_Black:
                        embed = discord.Embed(title="실패!", description="차례가 아니에요.", colour=discord.Colour.green())
                        embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                        await message.channel.send(embed=embed)
                        return

                msg = message.content
                list = msg.split(" ")
                list.pop(0)
                list.pop(0)
                if len(list) != 2:
                    embed = discord.Embed(title="실패!", description="좌표를 제대로 입력해주세요.", colour=discord.Colour.green())
                    embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                    await message.channel.send(embed=embed)
                    return
                x = int(list[0])
                y = int(list[1])
                result = Omok_PlaceInCoord(x, y, Omok_Turn)

                if result == -1:
                    embed = discord.Embed(title="실패!", description="좌표가 범위를 벗어났습니다.", colour=discord.Colour.green())
                    embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                    await message.channel.send(embed=embed)
                    return
                elif result == 0:
                    embed = discord.Embed(title="실패!", description="좌표에 이미 돌이 놓아져 있어요.", colour=discord.Colour.green())
                    embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                    await message.channel.send(embed=embed)
                    return

                embed = discord.Embed(title="오목", description=OmokBoardInStr(), colour=discord.Colour.green())
                await message.channel.send(embed=embed)

                result = Omok_CheckBoard()
                if result == 1:
                    S = "하얀 돌 [" + OmokPlayer_White_Name + "] 님이 이겼습니다!"
                    embed = discord.Embed(title=S, colour=discord.Colour.green())
                    await message.channel.send(embed=embed)
                    return
                elif result == 0:
                    S = "검은 돌 [" + OmokPlayer_Black_Name + "] 님이 이겼습니다!"
                    embed = discord.Embed(title=S, colour=discord.Colour.green())
                    await message.channel.send(embed=embed)
                    return
                elif result == -1:
                    S = ""
                    Omok_Turn = not Omok_Turn
                    if Omok_Turn is True:
                        S += "하얀 돌 [" + OmokPlayer_White_Name + "]"
                    else:
                        S += "검은 돌 [" + OmokPlayer_Black_Name + "]"
                    embed = discord.Embed(title=S + " 차례입니다.", colour=discord.Colour.green())
                    await message.channel.send(embed=embed)
        ## MINIGAME
        elif message.content.startswith("!끝말잇기"):
            global isWordGamePlaying
            global isWordGameHosting
            global WordGamePlayerID_List
            global WordGamePlayerName_List
            global WordGame_Turn
            global WordGameHistory

            msg = message.content

        elif message.content.startswith("!자가진단"):
            msg = message.content
            list = msg.split(" ")
            if len(list) != 4:
                embed = discord.Embed(title="실패!", description="**[!자가진단 [학교] [이름] [생년월일]]** 형식으로 입력해주세요.\n"
                                                               "ex) **!자가진단 동암중학교 김민재 050718**",
                                      colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                return
            school = list[1]
            name = list[2]
            birth = list[3]

            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument("headless")
            chrome_options.add_argument("disable-gpu")
            wd = None
            if platform == "Windows":
                chromedriver_path = os.path.join(PATH, "executables", "chromedriver.exe")
                wd = webdriver.Chrome(executable_path=chromedriver_path, options=chrome_options)
            elif platform == "Linux":
                wd = webdriver.Chrome(options=chrome_options)
            wd.get("https://eduro.goe.go.kr/stv_cvd_co00_002.do")

            wait = WebDriverWait(wd, 5)
            Main_Page = wd.current_window_handle
            try:
                SchoolSearchButton = wait.until(EC.element_to_be_clickable((By.ID, "btnSrchSchul")))
                SchoolSearchButton.click()
                for handle in wd.window_handles:
                    if handle != Main_Page:
                        SearchSchool_Page = handle
                wd.switch_to.window(SearchSchool_Page)
                # In School Search Window
                InsertSchool = wait.until(EC.presence_of_element_located((By.ID, "schulNm")))
                InsertSchool.send_keys(school)
                SearchButton = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "btn_sm.btn_gray")))
                SearchButton.click()
                ConfirmButton = wait.until(EC.element_to_be_clickable((By.ID, "btnConfirm")))
                ConfirmButton.click()
                # End of Search Window
                wd.switch_to.window(Main_Page)
                # Back to Main Page

                InsertName = wait.until(EC.presence_of_element_located((By.ID, "pName")))
                InsertName.send_keys(name)
                InsertBirth = wait.until(EC.presence_of_element_located((By.ID, "frnoRidno")))
                InsertBirth.send_keys(birth)
                ConfirmButton = wait.until(EC.element_to_be_clickable((By.ID, "btnConfirm")))
                ConfirmButton.click()
            except TimeoutException:
                embed = discord.Embed(title="실패!", description="서버가 응답하지 않습니다.", colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                wd.quit()
                return

            # Info Delivered

            try:
                CheckBox1 = wait.until(EC.presence_of_element_located((By.ID, "rspns011")))
                CheckBox1.click()
                CheckBox2 = wait.until(EC.presence_of_element_located((By.ID, "rspns02")))
                CheckBox2.click()
                CheckBox3 = wait.until(EC.presence_of_element_located((By.ID, "rspns070")))
                CheckBox3.click()
                CheckBox4 = wait.until(EC.presence_of_element_located((By.ID, "rspns080")))
                CheckBox4.click()
                CheckBox5 = wait.until(EC.presence_of_element_located((By.ID, "rspns090")))
                CheckBox5.click()
                ConfirmButton = wait.until(EC.element_to_be_clickable((By.ID, "btnConfirm")))
                ConfirmButton.click()
                embed = discord.Embed(title="성공!", description="자가진단을 완료했습니다.", colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
            except TimeoutException:
                embed = discord.Embed(title="실패!", description="서버가 응답하지 않습니다.", colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)

            # Info Delivered

            wd.quit()

        elif message.content.startswith("!사과"):
            src = "http://www.rpi4.kro.kr/repo/APPLE.gif"
            embed = discord.Embed(title="APPLE!", colour=discord.Colour.green())
            embed.set_image(url=src)
            embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
            await message.channel.send(embed=embed)
        # ==============================================
        # ==============================================
        # ==============================================
        elif message.content == "!참가":
            if message.author.voice is None:
                embed = discord.Embed(title="실패!", description="먼저 음성 채널에 들어와 주세요.", colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                return
            channel = message.author.voice.channel
            vc = await channel.connect()
            print("Joined Channel ID " + str(channel.id))

            client.loop.create_task(AsyncPlayer())

            embed = discord.Embed(title="성공!", description="음성 채널에 참가했어요.", colour=discord.Colour.green())
            embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
            await message.channel.send(embed=embed)
        elif message.content == "!나가":
            vc = message.guild.voice_client
            if vc is None:
                embed = discord.Embed(title="실패!", description="봇이 음성 채널에 들어와 있지 않아요.", colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                return
            await vc.disconnect()

            embed = discord.Embed(title="성공!", description="음성 채널을 나갔어요.", colour=discord.Colour.green())
            embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
            await message.channel.send(embed=embed)
            ClearYoutubeDL()
        elif (message.content.startswith("!재생") or message.content.startswith("!선택")) and message.content != "!재생목록" and message.content != "!재생중":
            msg = message.content
            Searched = False
            if msg.startswith("!재생"):
                url = msg[4:]
                if len(url) == 0:
                    embed = discord.Embed(title="실패!", description="URL을 입력해 주세요.", colour=discord.Colour.green())
                    embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                    await message.channel.send(embed=embed)
                    return
            elif msg.startswith("!선택"):
                if len(YTS_Title) == 0:
                    embed = discord.Embed(title="실패!", description="먼저 **!검색** 을 통해 검색해 주세요.",
                                          colour=discord.Colour.green())
                    embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                    await message.channel.send(embed=embed)
                Searched = True
                choice = int(msg[4:])
                choice -= 1
                # url = SR[choice].link
                url = "https://www.youtube.com/watch?v=" + YTS_VideoID[choice]
                # title = SR[choice].title
                title = YTS_Title[choice]
                id = YTS_VideoID[choice]
                channel_name = YTS_ChannelName[choice]
                channel_id = YTS_ChannelID[choice]
                YTS_Title.clear()
                YTS_VideoID.clear()
                YTS_VideoURL = ""
                YTS_ChannelName.clear()
                YTS_ChannelID.clear()

            channel = message.author.voice.channel
            server = message.guild
            vc = message.guild.voice_client

            if vc is None:
                embed = discord.Embed(title="실패!", description="봇이 음성 채널에 들어와 있지 않아요.", colour=discord.Colour.green())
                await message.channel.send(embed=embed)
                return

            if Searched is False:
                reqUrl = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                soup = BeautifulSoup(urllib.request.urlopen(reqUrl).read(), 'html.parser')
                title = soup.find("span", id="eow-title").text
                title = title.strip()

            """filename = ""
            string_pool = string.ascii_letters
            _LENGTH = 10
            for i in range(_LENGTH):
                filename += random.choice(string_pool)
            filename += ".mp3"""
            filename = id + ".mp3"

            download_path = os.path.join(PATH, "youtubedl", filename)

            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': download_path,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '128',
                }],
            }
            embed = discord.Embed(title="다운로드 중...", description="**" + title + "** 을 다운로드 중...",
                                  colour=discord.Colour.green())
            embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
            await message.channel.send(embed=embed)

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            # download_path, title
            if len(Q) == 0:
                player_flag = True
            Q.append(VideoInfo(title, download_path, id, channel_name, channel_id))
            # AsyncPlayer() will perceive this

            embed = discord.Embed(title="성공!", description="**" + Q[-1].title + "** 을 재생 목록에 추가했습니다.",
                                  colour=discord.Colour.green())
            embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
            await message.channel.send(embed=embed)
        elif message.content.startswith("!반복"):
            global isRepeating
            global RepeatCounter
            global Counter

            msg = message.content
            query = msg[4:]
            if len(query) == 0:
                embed = discord.Embed(title="실패!", description="**[!반복 [횟수]]** 를 통해 지정된 횟수만큼 현재 노래를 반복하거나,\n"
                                                               "**[!반복 중지]** 를 통해 반복을 중지하세요.", colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                return
            if query == "중지":
                isRepeating = False
                embed = discord.Embed(title="성공!", description="현재 재생중인 노래의 반복을 중지합니다.", colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                return
            else:
                if query.isnumeric() is False or query == 0:
                    embed = discord.Embed(title="실패!", description="반복할 횟수를 입력해 주세요.", colour=discord.Colour.green())
                    embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                    await message.channel.send(embed=embed)
                    return
                n = int(query)
                limit = 20
                if n > limit:
                    embed = discord.Embed(title="실패!", description=limit+" 을 초과할 수 없습니다.", colour=discord.Colour.green())
                    embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                    await message.channel.send(embed=embed)
                    return
                isRepeating = True
                RepeatCounter = n
                Counter = 1

                embed = discord.Embed(title="성공!", description="현재 재생중인 노래를 **["+str(n)+"번]** 반복합니다.", colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)

        elif message.content.startswith("!검색"):
            msg = message.content
            query = msg[4:]
            if len(query) == 0:
                embed = discord.Embed(title="실패!", description="검색할 영상 제목을 입력해주세요.", colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                return
            embed = discord.Embed(title="검색 중...", description="**" + query + "** 을 검색하는 중...",
                                  colour=discord.Colour.green())
            embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
            await message.channel.send(embed=embed)
            
            yt = yt_search.build("AIzaSyAkAkcxaJvTBVOr07Ax-KaKM56mcwFxouw")
            res = yt.search(query, sMax=5, sType=["video"])

            YTS_Title = res.title
            YTS_VideoID = res.videoId
            YTS_ChannelName = res.channelTitle
            YTS_ChannelID = res.channelId

            List = ""
            i = 1
            for X in YTS_Title:
                List += "**[ "
                List += str(i) + " ] " + X
                List += "**\n"
                i += 1
            embed = discord.Embed(title="**!선택 [1-5]** 로 선택해주세요.\n", description=List, colour=discord.Colour.green())
            embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
            await message.channel.send(embed=embed)
        elif message.content == "!재생중":
            if len(Q) == 0:
                embed = discord.Embed(title="실패!", description="재생 중인 노래가 없습니다.", colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                return

            Title = Q[0].title
            VideoURL = "https://www.youtube.com/watch?v=" + Q[0].id
            ThumbnailURL = "https://i.ytimg.com/vi/" + Q[0].id + "/hqdefault.jpg"
            ChannelName = Q[0].channel
            ChannelID = Q[0].channel_id
            ChannelURL = "https://www.youtube.com/channel/" + ChannelID
            embed = discord.Embed(title=Title, url=VideoURL, colour=discord.Colour.green())
            embed.set_author(name=ChannelName, url=ChannelURL)
            embed.set_thumbnail(url=ThumbnailURL)
            await message.channel.send(embed=embed)

        elif message.content == "!일시정지":
            vc = message.guild.voice_client
            if vc is None:
                embed = discord.Embed(title="실패!", description="먼저 음악을 재생해주세요.", colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                return
            Timer.pause()
            vc.pause()
            embed = discord.Embed(title="성공!", description="음악을 일시정지했어요.", colour=discord.Colour.green())
            embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
            await message.channel.send(embed=embed)
        elif message.content == "!다시재생":
            vc = message.guild.voice_client
            if vc is None:
                embed = discord.Embed(title="실패!", description="먼저 음악을 재생해주세요.", colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                return
            Timer.resume()
            vc.resume()
            embed = discord.Embed(title="성공!", description="음악을 다시 재생합니다.", colour=discord.Colour.green())
            embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
            await message.channel.send(embed=embed)
        elif message.content == "!스킵":
            vc = message.guild.voice_client
            if vc is None:
                embed = discord.Embed(title="실패!", description="먼저 음악을 재생해주세요.", colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                return
            vc.stop()
            isRepeating = False
            Counter = 1
            embed = discord.Embed(title="성공!", description="음악을 스킵합니다.", colour=discord.Colour.green())
            embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
            await message.channel.send(embed=embed)
        elif message.content == "!초기화":
            vc = message.guild.voice_client
            if vc is None:
                embed = discord.Embed(title="실패!", description="먼저 음악을 재생해주세요.", colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                return

            Q.clear()
            vc.stop()
            player_flag = True

            embed = discord.Embed(title="성공!", description="재생목록을 초기화했어요.", colour=discord.Colour.green())
            embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
            await message.channel.send(embed=embed)
        elif message.content == "!재생목록":
            vc = message.guild.voice_client
            if vc is None:
                embed = discord.Embed(title="실패!", description="먼저 음악을 재생해주세요.", colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                return
            l = len(Q)
            if l == 0:
                embed = discord.Embed(title="실패!", description="재생목록이 비어 있어요.", colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                return
            i = 1
            List = "**"
            for X in Q:
                List += "[ " + str(i) + " ] " + X.title + "\n"
                i += 1
            List += "**"

            embed = discord.Embed(title="재생목록", description=List, colour=discord.Colour.green())
            embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
            await message.channel.send(embed=embed)
        elif message.content == "!자막":
            if len(Q) == 0:
                embed = discord.Embed(title="실패!", description="재생 중인 노래가 없어요.", colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                return
            id = Q[0].id
            url = "https://www.youtube.com/watch?v=" + id
            yt = YouTube(url)
            caption = yt.captions.get_by_language_code("ko")
            if caption == None:
                caption = yt.captions.all()[0]
            srt = caption.generate_srt_captions()
            filename = id + ".srt"
            path = os.path.join(PATH, "youtubesrt", filename)
            with open(path, "w") as file:
                file.write(srt)

            client.loop.create_task(AsyncSubtitle(path, message.channel))

        elif message.content.startswith("!타르코프"):
            tags = ["weapon", "ammo", "magazines", "tactical_devices", "weapon_parts", "special_equipment", "maps",
                    "ammo_boxes", "currency", "keys", "barter", "containers", "provisions", "gear", "meds", "sights", "suppressors"]
            query = message.content[6:]
            if len(query) == 0 or query == "명령어":
                embed = discord.Embed(title="𝓓𝓲𝓼𝓒𝓸𝓻𝓭𝓑𝓞𝓣 타르코프 명령어", colour=discord.Colour.green())
                inline = False
                embed.add_field(name="!타르코프 명령어", value="명령어를 보여줍니다.")
                embed.add_field(name="!타르코프 [물건]", value="타르코프 상점에서 물건을 검색합니다.\nex) !타르코프 AS VAL", inline=inline)
                embed.add_field(name="!타르코프 [물건] --[태그]", value="지정된 태그를 이용해 검색합니다.\nex) !타르코프 Mosin --weapon", inline=inline)
                embed.add_field(name="사용 가능한 태그", value=", ".join(tags))
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                return

            link = "https://tarkov-market.com/"

            t = query.find("--")
            if t != -1:
                tag = query[t+2:]
                tag = tag.lower()
                tag = tag.replace(" ", "_")
                if tag not in tags:
                    embed = discord.Embed(title="실패!", description="사용 가능한 태그를 입력해 주세요.", colour=discord.Colour.green())
                    embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                    await message.channel.send(embed=embed)
                    return
                link += "tag/" + tag
                query = query[:t-1]

            embed = discord.Embed(title="검색 중...", description="**" + query + "** 를 검색하는 중...",
                                  colour=discord.Colour.green())
            embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
            await message.channel.send(embed=embed)

            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument("headless")
            chrome_options.add_argument("disable-gpu")
            wd = None
            if platform == "Windows":
                chromedriver_path = os.path.join(PATH, "executables", "chromedriver.exe")
                wd = webdriver.Chrome(executable_path=chromedriver_path, options=chrome_options)
            elif platform == "Linux":
                wd = webdriver.Chrome(options=chrome_options)
            wd.get(link)
            wait = WebDriverWait(wd, 2)

            element = wait.until(EC.presence_of_element_located((By.TAG_NAME, "input")))
            element.send_keys(query)
            await asyncio.sleep(2)
            element = wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
            table = element
            tbody = table.find_element_by_tag_name("tbody")

            length = len(tbody.find_elements_by_tag_name("tr"))
            if length == 0:
                embed = discord.Embed(title="실패!", description="검색 결과가 없습니다.", colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                return

            tr = tbody.find_elements_by_tag_name("tr")[0]
            _icon = tr.find_elements_by_tag_name("td")[0]
            _icon = _icon.find_element_by_tag_name("img")
            item_icon = _icon.get_attribute("src")
            _title = tr.find_elements_by_tag_name("td")[1]
            _title = _title.find_element_by_tag_name("a")
            item_url = _title.get_attribute("href")
            item_title = _title.text
            _price = tr.find_elements_by_tag_name("td")[2]
            _price = _price.find_element_by_tag_name("span")
            item_price = _price.text

            embed = discord.Embed(title=item_title, url=item_url, description="**"+item_price+"**\n", colour=discord.Colour.green())
            embed.set_thumbnail(url=item_icon)
            embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)

            limit = 5
            if length < 5:
                limit = length
            if length > 1:
                for X in range(1, limit):
                    tr = tbody.find_elements_by_tag_name("tr")[X]
                    _icon = tr.find_elements_by_tag_name("td")[0]
                    _icon = _icon.find_element_by_tag_name("img")
                    item_icon = _icon.get_attribute("src")

                    _title = tr.find_elements_by_tag_name("td")[1]
                    _title = _title.find_element_by_tag_name("a")
                    item_url = _title.get_attribute("href")
                    item_title = _title.text

                    _price = tr.find_elements_by_tag_name("td")[2]
                    _price = _price.find_element_by_tag_name("span")
                    item_price = _price.text

                    embed.add_field(name="ㅤ", value="**["+item_title+"]("+item_url+")\n"+item_price+"**", inline=False)

            await message.channel.send(embed=embed)

        elif message.content.startswith("!메타크리틱"):
            query = message.content[7:]
            if len(query) == 0:
                embed = discord.Embed(title="실패!", description="검색할 게임 이름을 입력해주세요.", colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                return
            link = "https://www.metacritic.com/search/all/"+urllib.parse.quote(query)+"/results"
            reqUrl = urllib.request.Request(link, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(urllib.request.urlopen(reqUrl).read(), 'html.parser')
            code = soup.find("li", class_="result first_result")
            title_code = code.find("h3", class_="product_title")
            title_code = title_code.find("a")
            title = title_code.text
            item_url = "https://www.metacritic.com" + title_code['href']
            score = code.find("span", class_="metascore_w").text
            img_code = code.find("div", class_="result_thumbnail")
            img_code = img_code.find("img")
            img_url = img_code['src']

            embed = discord.Embed(title=title, url=item_url, description="**"+score+" 점**", colour=discord.Colour.green())
            embed.set_author(name="metacritic", url="https://www.metacritic.com/", icon_url="https://www.metacritic.com/MC_favicon.png")
            embed.set_image(url=img_url)
            embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
            await message.channel.send(embed=embed)
        elif message.content.startswith("!멤버정보"):
            query = message.content[6:]
            if query == "준서":
                file = os.path.join(PATH, "userinfo", "준서.txt")
                f = open(file, "r")
                text = f.read()
                f.close()
                await message.channel.send(text)
            elif query == "민재":
                file = os.path.join(PATH, "userinfo", "민재.txt")
                f = open(file, "r")
                text = f.read()
                f.close()
                await message.channel.send(text)
            elif query == "제일":
                file = os.path.join(PATH, "userinfo", "제일.txt")
                f = open(file, "r")
                text = f.read()
                f.close()
                await message.channel.send(text)
        elif message.content.startswith("!통계"):
            list = message.content.split(" ")
            list.pop(0)
            if len(list) == 0:
                embed = discord.Embed(title="실패!", description="변량을 입력해주세요.", colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                return
            list = [float(x) for x in list]
            avg = statistics.mean(list)
            median = statistics.median(list)
            try: mode = statistics.mode(list)
            except statistics.StatisticsError:
                mode = "None"
            variance = statistics.pvariance(list)
            stdev = statistics.pstdev(list)

            embed = discord.Embed(title="통계", colour=discord.Colour.green())
            inline = False
            embed.add_field(name="평균", value=str(avg), inline=inline)
            embed.add_field(name="중앙값", value=str(median), inline=inline)
            embed.add_field(name="최빈값", value=str(mode), inline=inline)
            embed.add_field(name="분산", value=str(variance), inline=inline)
            embed.add_field(name="표준편차", value=str(stdev), inline=inline)
            embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)

            await message.channel.send(embed=embed)
        elif message.content.startswith("!GTA통계"):
            username = message.content.split(" ")[1]
            link = "https://socialclub.rockstargames.com/member/" + username + "/games/gtav/pc/career/overview/gtaonline"

            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument("headless")
            chrome_options.add_argument("disable-gpu")
            wd = None
            if platform == "Windows":
                chromedriver_path = os.path.join(PATH, "executables", "chromedriver.exe")
                wd = webdriver.Chrome(executable_path=chromedriver_path, options=chrome_options)
            elif platform == "Linux":
                wd = webdriver.Chrome(options=chrome_options)

            signinUrl = "https://signin.rockstargames.com/signin/user-form?cid=socialclub"
            wd.get(signinUrl)
            wait = WebDriverWait(wd, 10)
            webdriver.save_screenshot(os.path.join(PATH, "plz.png"))
            InsertEmail = wait.until(EC.presence_of_element_located((By.ID, "textInput__11")))
            InsertPw = wait.until(EC.presence_of_element_located((By.ID, "textInput__12")))
            ConfirmButton = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "UI__Button-socialclub__btn.UI__Button-socialclub__primary.UI__Button-socialclub__medium.loginform__submit")))
            InsertEmail.send_keys("jjaenae@naver.com")
            InsertPw.send_keys("Admin*9248")
            ConfirmButton.click()
            wait.until(lambda wd: wd.current_url != signinUrl)

            wd.get(link)

            level = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "rankHex.right-grad.bronze"))).text
            playtime = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "rankBar")))\
                .find_element_by_tag_name("h4").text
            cash = wait.until(EC.presence_of_element_located((By.ID, "cash-value"))).text
            bank = wait.until(EC.presence_of_element_located((By.ID, "bank-value"))).text
            cashEarned = wait.until(EC.presence_of_element_located((By.ID, "cashEarned")))\
                .find_element_by_tag_name("p").text
            cashSpent = wait.until(EC.presence_of_element_located((By.ID, "cashSpent")))\
                .find_element_by_tag_name("p").text
            wd.quit()

            S = "level "+level+"\n"+\
                "playtime "+playtime+"\n"+\
                "cash "+cash+"\n"+\
                "bank "+bank+"\n"+\
                "cashEarned "+cashEarned+"\n"+\
                "cashSpent "+cashSpent
            await message.channel.send(S)
        else:
            None
            #await message.channel.send("무슨 말인지 모르겠어요.")
    elif message.content == "홀리쓋":
        await message.channel.send("보여주는부분이네")
    elif message.content == "사발":
        await message.channel.send("면")


file = os.path.join(PATH, "token")
f = open(file, "r")
TOKEN = f.readline()
f.close()
client.run(TOKEN)
