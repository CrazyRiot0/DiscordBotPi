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
