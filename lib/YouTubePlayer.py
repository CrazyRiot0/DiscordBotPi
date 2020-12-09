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
