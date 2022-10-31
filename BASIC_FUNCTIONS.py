import re
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

#   ____                         _      __     __               
#  / ___|   ___    _ __    ___  | |_    \ \   / /   __ _   _ __ 
# | |      / _ \  | '_ \  / __| | __|    \ \ / /   / _` | | '__|
# | |___  | (_) | | | | | \__ \ | |_      \ V /   | (_| | | |   
#  \____|  \___/  |_| |_| |___/  \__|      \_/     \__,_| |_|   


MediaCategory = ["Gloss Vinyl","Matte Vinyl","BL Vinyl","OneWay Vision","Gloss Canvas","Matt Canvas","Banner Media","Translit","Other"]
EXPECT_TEXT, EXPECT_MEDIA_SELECT, EXPECT_FILE = range(3)
#ALIAS FOR MEDIAS
VINYL = ['vinyl','binyl','vnyl','vinayal','vinl']
BL = ['bl flex','backlit','baklit','backlitt']
ONEWAY_VISION = ['onewayvision','oneway','onway','1way']
CANVAS = ['canvas','cnvas','canvs']
BANNER_MEDIA = ['bannar media','banner media','bannermedia']
TRANSLIT = ["translit","tranlit",'translitt']

MATT = ['matt','matte','mett','met','mat']
GLOSS = ['glossy','gloss','glos']



#  ____                  _            _____                          _     _                 
# | __ )    __ _   ___  (_)   ___    |  ___|  _   _   _ __     ___  | |_  (_)   ___    _ __  
# |  _ \   / _` | / __| | |  / __|   | |_    | | | | | '_ \   / __| | __| | |  / _ \  | '_ \ 
# | |_) | | (_| | \__ \ | | | (__    |  _|   | |_| | | | | | | (__  | |_  | | | (_) | | | | |
# |____/   \__,_| |___/ |_|  \___|   |_|      \__,_| |_| |_|  \___|  \__| |_|  \___/  |_| |_|

def findWholeWord(w):
    return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search
def detectMedia(file_name):
    for alias in VINYL:
        if findWholeWord(alias)(file_name) != None:
            for alias2 in GLOSS:
                if findWholeWord(alias2)(file_name) != None:
                    return "Gloss Vinyl"
            for alias2 in MATT:
                if findWholeWord(alias2)(file_name) != None:
                    return "Matt Vinyl"
            for alias2 in BL:
                if findWholeWord(alias2)(file_name) != None:
                    return "BL Vinyl"
            #DEFAULT
            return "Gloss Vinyl"
    for alias in ONEWAY_VISION:
        if findWholeWord(alias)(file_name) != None:
            return "OneWay Vision"
    for alias in CANVAS:
        if findWholeWord(alias)(file_name) != None:
            for alias2 in GLOSS:
                if findWholeWord(alias2)(file_name) != None:
                    return "Gloss Canvas"
            for alias2 in MATT:
                if findWholeWord(alias2)(file_name) != None:
                    return "Matt Canvas"
            #DEFAULT
            return "Gloss Canvas"
    for alias in BANNER_MEDIA:
        if findWholeWord(alias)(file_name) != None:
            return "Banner Media"
    for alias in TRANSLIT:
        if findWholeWord(alias)(file_name) != None:
            return "Translit"
    print('Failed To Detect Media')
    return None
    
def detectWidthHeight(file_name):
    #EXAMPLE - re.search(WidthHeightRegex, str("    123.45x123.45")).groups()

    #matches digit at end of str
    #we have to remove extension first
    file_name = file_name.rsplit('.',1)[0]
    file_name = file_name.replace(' ','')
    try:
        WH = []
        if 'x' in file_name:
            WH = list(re.search("([\d.]+)x([\d.]+).*", file_name).groups())
        elif 'X' in file_name:
            WH = list(re.search("([\d.]+)X([\d.]+).*", file_name).groups())
        elif '*' in file_name:
            WH = list(re.search("([\d.]+)*([\d.]+).*", file_name).groups())
        if WH == []:
            return None
        if re.search('ft', file_name, re.IGNORECASE) or re.search('feet', file_name, re.IGNORECASE) or re.search('foot', file_name, re.IGNORECASE):
            return str(int(WH[0])*12)+'x'+str(int(WH[1])*12)
        return WH[0]+'x'+WH[1]
    except:
        return None

def detectQuantity(file_name):
    QuantityRegex='.*?([0-9]+)$'
    #matches digit at end of str
    #we have to remove extension first
    file_namesplit = file_name.rsplit('.',1)[0]
    try:
        Quantity = re.search(QuantityRegex, file_namesplit).group(1)
        ##WE USE THIS TO CHECK IF IT IS GIVING SAME QUANTITY AS IN HEIGTH OF SIZE
        ##IF SAME THEN WE USE QUANTITY = 1
        try:
            height = detectWidthHeight(file_name).split('x')[1]
            print(Quantity)
            print(height)
            if(height == str(Quantity)):
                return 1
        except:
            print("here")
        return Quantity
    except:
        return 1

def LoadMediaCategories():
	MediaSelection = []
	for Media in range(0,len(MediaCategory)):
		MediaSelection.append(InlineKeyboardButton(MediaCategory[Media],callback_data=MediaCategory[Media]))
	#Create section changer
	return InlineKeyboardMarkup([MediaSelection[i:i+3] for i in range(0, len(MediaSelection), 3)])

def ConvertToInlineMarkup(ButtonText):
    Markups = []
    for Text in range(0,len(ButtonText)):
        Markups.append(InlineKeyboardButton(ButtonText[Text],callback_data=ButtonText[Text]))
    #Create section changer
    return [Markups[i:i+3] for i in range(0, len(Markups), 3)]


#IT RETURNS SIZE CONVERTED TO CORRECT FORM(IF EXISTING) ELSE FALSE
def GetCorrectSizeFormat(text):
    SizeTemp = text.replace('X','x')
    SizeTemp = SizeTemp.replace('*',"x")
    try:
        WH = []
        WH = list(re.search("([\d.]+)x([\d.]+).*", SizeTemp).groups())
        if WH == []:
            return None
        return WH[0]+'x'+WH[1]
    except:
        return False
