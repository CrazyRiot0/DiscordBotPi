from __future__ import unicode_literals
import discord
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
import asyncio
import os
import shutil
import sys
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from requests_html import HTMLSession
from requests_html import AsyncHTMLSession

client = discord.Client()

PATH = os.path.dirname(os.path.abspath(__file__))

class VideoInfo:
    title = ""
    path = ""

    def __init__(self, title, path):
        self.title = title
        self.path = path

class SearchResult:
    title = ""
    link = ""

    def __init__(self, title, link):
        self.title = title
        self.link = link

Q = []
SR = []

ignore = False

def ClearYoutubeDL():
    path = os.path.join(PATH, "youtubedl")
    if os.path.isdir(path):
        shutil.rmtree(path)
    os.mkdir(path)
    print("Cleared folder [youtubedl]")


flag = True

async def AsyncPlayer():
    vc = client.voice_clients[0]
    if vc is None:
        print("VoiceClient Error.")
        pass
    print("AsyncPlayer Started.")
    global flag
    while len(client.voice_clients) != 0:
        if vc.is_playing() is False and len(Q) > 0:
            if flag:
                flag = False
            else:
                Q.pop(0)
                if len(Q) == 0:
                    continue
            print("Playing " + Q[0].title + " ...")
            vc.play(discord.FFmpegPCMAudio(Q[0].path))
        await asyncio.sleep(1)
    print("VoiceClient Not Found. Shutting Down...")


def CheckAlreadyUsed(n, list):
    if len(list) == 0:
        return False
    for X in list:
        if n == X:
            return True
    return False

# 숫자맞추기 변수
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

# 오목 변수
isOmokPlaying = False
isOmokHosting = False
OmokPlayer_White = None
OmokPlayer_White_Name = None
OmokPlayer_Black = None
OmokPlayer_Black_Name = None
Omok_Turn = None
OmokBoard_Len = 20
OmokBoard = None
NumberInCircle = ["⓪", "①", "②", "③", "④", "⑤", "⑥", "⑦", "⑧", "⑨", "⑩",
                  "⑪", "⑫", "⑬", "⑭", "⑮", "⑯", "⑰", "⑱", "⑲", "⑳",
                  "㉑", "㉒", "㉓", "㉔", "㉕", "㉖", "㉗", "㉘", "㉙", "㉚",
                  "㉛", "㉜", "㉝", "㉞", "㉟", "㊱", "㊲", "㊳", "㊴", "㊵",
                  "㊶", "㊷", "㊸", "㊹", "㊺", "㊻", "㊼", "㊽", "㊾", "㊿",]
WhiteC = "○"
BlackC = "●"
EmptySpace = "ㅤ"
'''
ㅤ①②③④⑤
①┌┬┬┬┐
②├┼┼┼┤
③├┼┼┼┤
④└┴┴┴┘'''

def Omok_MakeBoard():
    len = OmokBoard_Len
    global OmokBoard
    OmokBoard = [[0 for x in range(len)] for y in range(len)]
    for i in range(0, len):
        for j in range(0, len):
            OmokBoard[i][j] = "┼"

    for i in range(0, len):
        OmokBoard[0][i] = "┬"
        OmokBoard[len-1][i] = "┴"
        OmokBoard[i][0] = "├"
        OmokBoard[i][len-1] = "┤"

    OmokBoard[0][0] = "┌"
    OmokBoard[0][len-1] = "┐"
    OmokBoard[len-1][0] = "└"
    OmokBoard[len-1][len-1] = "┘"

def Omok_PlaceInCoord(x, y, color): # color True = White, False = Black
    global OmokBoard
    x = x-1
    y = y-1
    if color is True:
        OmokBoard[y][x] = 1
    else:
        OmokBoard[y][x] = 0

def OmokBoardInStr():
    global OmokBoard
    global OmokBoard_Len
    global NumberInCircle
    global EmptySpace
    S = ""
    S += EmptySpace
    for i in range(1, OmokBoard_Len+1):
        S += NumberInCircle[i]
    S += "\n"

    for i in range(0, OmokBoard_Len):
        S += NumberInCircle[i+1]
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
    for i in range(0, OmokBoard_Len): # 가로를 보아라.
        count_w = 0
        count_b = 0
        prev = None
        for j in range(0, OmokBoard_Len):
            if OmokBoard[i][j] == 1: # White
                if prev != 1:
                    count_w = 1
                count_w = count_w + 1
            elif OmokBoard[i][j] == 0: # Black
                if prev != 0:
                    count_b = 1
                count_b = count_b + 1

            if count_w >= 5:
                return 1
            if count_b >= 5:
                return 0
            prev = OmokBoard[i][j]
        
    for i in range(0, OmokBoard_Len): # 세로를 보아라.
        count_w = 0
        count_b = 0
        prev = None
        for j in range(0, OmokBoard_Len):
            if OmokBoard[j][i] == 1: # White
                if prev != 1:
                    count_w = 1
                else:
                    count_w = count_w + 1
            elif OmokBoard[j][i] == 0: # Black
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


AdminID = 351677960270381058

@client.event
async def on_ready():
    print(client.user.id)
    print("ready")
    # game = discord.Game("𝓟𝓻𝓸𝓰𝓻𝓪𝓶𝓪𝓬𝓲ó𝐧")
    game = discord.Game("봇이 𝓡𝓟𝓲4로 이동했습니다!")
    await client.change_presence(status=discord.Status.online, activity=game)
    ClearYoutubeDL()

@client.event
async def on_message(message):
    global AdminID
    global ignore
    global flag

    if ignore == True and message.author.id != AdminID:
        return
    if message.content.startswith("!") and message.content.startswith("!!") is False:
        print("[", end='')
        print(message.author, end="] ")
        print(message.content)
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
            embed.add_field(name="**!네이버/구글 [검색어]**", value="네이버 또는 구글로부터 사진을 검색합니다.", inline=inline)
            embed.add_field(name="**!미니게임**", value="미니게임 명령어를 보여줍니다.", inline=inline)
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
            embed.add_field(name="**!일시정지**", value="노래를 일시정지합니다.", inline=inline)
            embed.add_field(name="**!다시재생**", value="노래를 다시 재생합니다.", inline=inline)
            embed.add_field(name="**!스킵**", value="노래를 스킵합니다.", inline=inline)
            embed.add_field(name="**!정지**", value="재생목록을 초기화합니다.", inline=inline)
            embed.add_field(name="**!재생목록**", value="재생목록을 보여줍니다.", inline=inline)
            embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
            await message.channel.send(embed=embed)
        elif message.content.startswith("!관리자"):
            if message.author.id != 351677960270381058:
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
                await client.change_presence(status=discord.Status.offline)
                embed = discord.Embed(title="종료 중...", description="봇을 종료합니다...", colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                exit()
            elif query == "온도":
                command = "vcgencmd measure_temp"
                command = command.split(" ")
                # result = subprocess.run(['vcgencmd', 'measure_temp'], stdout=subprocess.PIPE)
                result = subprocess.run(command, stdout=subprocess.PIPE)
                R = result.stdout.decode('utf-8')
                embed = discord.Embed(title="𝓡𝓟𝓲4 온도", description=R, colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
            elif query == "실행": #!관리자 실행 []
                cmd = message.content[8:]
                if cmd is None:
                    embed = discord.Embed(title="실패!", description="명령어를 입력해주세요.", colour=discord.Colour.green())
                    embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                    await message.channel.send(embed=embed)
                    return
                command = cmd.split(" ")
                result = subprocess.run(command, stdout=subprocess.PIPE)
                R = result.stdout.decode('utf-8')
                embed = discord.Embed(title=cmd, description=R, colour=discord.Colour.green())
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
            org = username
            username = urllib.parse.quote(username)
            link = "https://r6.tracker.network/profile/pc/" + username
            link += "\nhttps://r6.op.gg/search?search=" + username
            embed = discord.Embed(title=org + " 님의 레식 전적", description=link, colour=discord.Colour.green())
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
            org = username
            username = urllib.parse.quote(username)
            link = "https://www.op.gg/summoner/userName=" + username
            embed = discord.Embed(title=org + " 님의 롤 전적", description=link, colour=discord.Colour.green())
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
            org = username
            username = urllib.parse.quote(username)
            link = "https://lolchess.gg/profile/kr/" + username
            embed = discord.Embed(title=org + " 님의 롤체 전적", description=link, colour=discord.Colour.green())
            embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
            await message.channel.send(embed=embed)
        elif message.content.startswith("!나무위키"):
            msg = message.content
            query = msg[6:]
            original = query
            query = urllib.parse.quote(query)
            if len(query) == 0:
                await message.channel.send("https://namu.wiki/w/")
            else:
                link = "https://namu.wiki/w/" + query
            reqUrl = urllib.request.Request(link, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(urllib.request.urlopen(reqUrl).read(), 'html.parser')
            code = soup.find_all("div", {"class": "wiki-heading-content"})
            result = code[0].getText(' ', strip=True)
            if len(result) > 2000:
                result = result[:2000]
                result += " ..."
                embed = discord.Embed(title="**" + original + "** 검색 결과", description=result,
                                      colour=discord.Colour.green())
                embed.set_footer(text="2000자 까지만 보여줍니다.")
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
            else:
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
        elif message.content.startswith("!다나와"):
            msg = message.content
            query = msg[5:]
            query = urllib.parse.quote(query)
            if len(query) == 0:
                await message.channel.send("http://danawa.com/")
            else:
                link = "http://search.danawa.com/dsearch.php?query=" + query
                await message.channel.send(link)
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

            wd = webdriver.Chrome(options=chrome_options)
            wd.get(link)
            # wait = WebDriverWait(wd, 10)
            # button = wait.until(EC.element_to_be_clickable((By.ID, "btnTranslate")))
            # button.click()
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
        elif message.content.startswith("!영어사전"):
            msg = message.content
            query = msg[6:]
            query = urllib.parse.quote(query)
            link = "https://en.dict.naver.com/#/search?query=" + query
            reqUrl = urllib.request.Request(link, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(urllib.request.urlopen(reqUrl).read(), 'html.parser')
            code = soup.find("div", class_="row")

            if code is None:
                await message.channel.send("단어를 찾을 수 없습니다.")
            else:
                # result = code.getText('\n', strip=True)
                result = code.text
                await message.channel.send(result)
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
        elif message.content.startswith("!거리"):
            msg = message.content
            query = msg[1:]
            query = urllib.parse.quote(query)
            link = "https://www.google.com/search?q=" + query
            reqUrl = urllib.request.Request(link, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(urllib.request.urlopen(reqUrl).read(), 'html.parser')
            code = soup.find("div", class_="dDoNo vk_bk")  # dDoNo vk_bk
            if code is None:
                await message.channel.send("거리를 찾을 수 없어요.")
            distance = code.text
            await message.channel.send(distance)
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
        elif message.content.startswith("!네이버"):
            msg = message.content
            q = msg[5:]
            if len(q) == 0:
                embed = discord.Embed(title="실패!", description="검색할 말을 입력해주세요.", colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                return
            link = "https://search.naver.com/search.naver?where=image&query=" + urllib.parse.quote(q)
            reqUrl = urllib.request.Request(link, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(urllib.request.urlopen(reqUrl).read(), 'html.parser')
            code = soup.find("div", {"class": "img_area _item"})
            code = code.find("a")
            code = code.find("img")
            src = code['data-source']

            embed = discord.Embed(title=q + " 검색 결과", colour=discord.Colour.green())
            embed.set_image(url=src)
            embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
            await message.channel.send(embed=embed)
        elif message.content.startswith("!구글"):
            msg = message.content
            q = msg[4:]
            if len(q) == 0:
                embed = discord.Embed(title="실패!", description="검색할 말을 입력해주세요.", colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                return
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
                    n = randint(0, L-1)
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
                embed = discord.Embed(title="실패!", description="게임이 이미 다른 플레이어에 의해 실행 중이에요.", colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                return
            msg = message.content
            list = msg.split(" ")
            if len(list) == 1:
                embed = discord.Embed(title="실패!", description="명령어를 제대로 입력해주세요.\n"
                                                               "**[!숫자맞추기 명령어]** 로 명령어를 확인하세요.", colour=discord.Colour.green())
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
                embed = discord.Embed(title="숫자맞추기 게임 종료", description="숫자맞추기 게임을 종료했습니다.", colour=discord.Colour.green())
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
            if num > NumGameAnswer: # 5 입력 : 답 2      범위 1 <= 정답 <= 100
                NumGameEstRange_E = num
                S += " [미만]**\n"
            elif num < NumGameAnswer: # 5 입력 : 답 10    범위 1 <= 정답 <= 100
                NumGameEstRange_S = num
                S += " [초과]**\n"
            else: # 숫자 맞춤
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
            global Omok_Turn # True = White, False = Black
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

                Omok_Turn = True # 하얀 돌 먼저 시작

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
                Omok_PlaceInCoord(x, y, Omok_Turn)

                embed = discord.Embed(title="오목", description=OmokBoardInStr(), colour=discord.Colour.green())
                await message.channel.send(embed=embed)

                result = Omok_CheckBoard()
                if result == 1:
                    S = "하얀 돌 [" + OmokPlayer_White_Name +"] 님이 이겼습니다!"
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
        elif (message.content.startswith("!재생") or message.content.startswith("!선택")) and message.content != "!재생목록":
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
                if len(SR) == 0:
                    embed = discord.Embed(title="실패!", description="먼저 **!검색** 을 통해 검색해 주세요.",
                                          colour=discord.Colour.green())
                    embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                    await message.channel.send(embed=embed)
                Searched = True
                choice = int(msg[4:])
                choice -= 1
                url = SR[choice].link
                title = SR[choice].title
                SR.clear()

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

            filename = ""
            string_pool = string.ascii_letters
            _LENGTH = 10
            for i in range(_LENGTH):
                filename += random.choice(string_pool)
            filename += ".mp3"

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
                flag = True
            Q.append(VideoInfo(title, download_path))
            # AsyncPlayer() will perceive this

            embed = discord.Embed(title="성공!", description="**" + Q[-1].title + "** 을 재생 목록에 추가했습니다.",
                                  colour=discord.Colour.green())
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
            query = urllib.parse.quote(query)

            while True:
                link = "https://www.youtube.com/results?search_query=" + query
                reqUrl = urllib.request.Request(link, headers={'User-Agent': 'Mozilla/5.0'})
                html = urllib.request.urlopen(reqUrl).read()
                soup = BeautifulSoup(html, 'html.parser')
                SR.clear()
                for vid in soup.find_all(attrs={"class": "yt-uix-tile-link"}, limit=5):
                    URL = "https://www.youtube.com"
                    URL += vid['href']
                    Title = vid['title']
                    SR.append(SearchResult(Title, URL))
                if len(SR) != 0:
                    break

            List = ""
            i = 1
            for X in SR:
                List += "**"
                List += str(i) + ". " + X.title
                List += "**\n"
                i += 1
            embed = discord.Embed(title="**!선택 [1-5]** 로 선택해주세요.\n", description=List, colour=discord.Colour.green())
            embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
            await message.channel.send(embed=embed)
        elif message.content == "!일시정지":
            vc = message.guild.voice_client
            if vc is None:
                embed = discord.Embed(title="실패!", description="먼저 음악을 재생해주세요.", colour=discord.Colour.green())
                embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
                return
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
            flag = True

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
                List += str(i)
                List += ": "
                List += X.title
                List += "\n"
                i += 1
            List += "**"

            embed = discord.Embed(title="재생목록", description=List, colour=discord.Colour.green())
            embed.set_footer(text="Requested by " + message.author.name, icon_url=message.author.avatar_url)
            await message.channel.send(embed=embed)
        else:
            await message.channel.send("무슨 말인지 모르겠어요.")

    elif message.content == "홀리쓋":
        await message.channel.send("보여주는부분이네")
    elif message.content == "사발":
        await message.channel.send("면")
    # elif message.content.startswith("ㅋ"):
    #    if message.author.bot is False:
    #        await message.channel.send("ㅋㅋㅋㅋㅋㅋㅋ")


file = os.path.join(PATH, "token")
f = open(file, "r")
TOKEN = f.readline()
f.close()
client.run(TOKEN)
