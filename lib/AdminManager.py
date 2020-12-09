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
