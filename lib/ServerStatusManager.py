async def ServerStatusManager():
    Guild = client.get_guild(698722442033496195)
    DateCh = client.get_channel(783552826189152257)
    MemberCountCh = client.get_channel(783529681072685086)
    UserCountCh = client.get_channel(783551100803743804)
    BotCountCh = client.get_channel(783551141866373121)
    OnlineCountCh = client.get_channel(783529729906180107)
    OfflineCountCh = client.get_channel(783529755924234261)
    while True:
        now = datetime.datetime.now()
        Date = "📅 " + str(now.year) + "년 " + str(now.month) + "월 " + str(now.day) + "일 "
        MemberCount = Guild.member_count
        UserCount = len([m for m in Guild.members if not m.bot])
        BotCount = len([m for m in Guild.members if m.bot])
        OnlineCount = sum(m.status!=discord.Status.offline and not m.bot for m in Guild.members)
        OfflineCount = sum(m.status==discord.Status.offline and not m.bot for m in Guild.members)
        await DateCh.edit(name="| " + Date + " |")
        await MemberCountCh.edit(name="| 👥 전체 멤버 : " + str(MemberCount) + " |")
        await UserCountCh.edit(name="| 👤 유저 : " + str(UserCount) + " |")
        await BotCountCh.edit(name="| 🤖 봇 : " + str(BotCount) + " |")
        await OnlineCountCh.edit(name="| 🟢 온라인 : " + str(OnlineCount) + " |")
        await OfflineCountCh.edit(name="| 🔴 오프라인 : " + str(OfflineCount) + " |")

        await asyncio.sleep(600)
