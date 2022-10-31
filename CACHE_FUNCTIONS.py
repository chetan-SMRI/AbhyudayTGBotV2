from BASIC_FUNCTIONS import LoadMediaCategories,ConvertToInlineMarkup
from telegram import *
from database_work import create_order,returnClientAlias
from SECRETS import PrintAdmin

def ClearCache(context):
    context.user_data["Media"] = ""               #This Shows Current Media  'Gloss Vinyl'
    context.user_data["WidthHeight"] = ""         #This Shows Current Width/Height '28x89'
    context.user_data["FileTGIDList"] = ""        #[LIST]This is telegram personal document id 'BQACAgUAAxkBAAIKI2NU0YVtH26xMrOuZjqbWsF0hVMwAAIXBgACElCpVgSmdxhLQn_IKgQ' 
    context.user_data["FileActualName"] = ""      #[LIST]Actual Name of file sent by user ' Gloss Vinyl 48*48 Pc-2.jpeg'
    context.user_data["FileChatID"] = ""          #[LIST]File Location In 1to1 chat , for eg 123
    context.user_data["DetectedMedia"] = ""       #Detected Media By Regex
    context.user_data["DetectedWidthHeight"] = "" #Detected WidthHeight By Regex
    context.user_data["DetectedQuantity"] = ""    #Detected Quantity By Regex
    context.user_data["COUNTER"] = "0"            #FILE COUNTER ,eg if user selects 5 files at a time then 5
    context.user_data["PROCESSING_COUNTER"] = "0" #FOR SAVING COUNTER VALUE OF HOW MANY FILES HAVE BEEN PROCESSED TILL YET 
    context.user_data["PROCESSING_STATUS"] = False#Processing status of order helps in telling about is order preprocessed for info or not. 
    context.user_data["WORKING_ORDERID"] = ""     #Current Order ID
    context.user_data["CURRENT_USER_INPUT"] = ""  #Current User Input eg- SIZE OR QUANTITY OR MEDIA
    
def AppendToCache(context,CacheVar,Value,ClearBeforeAppend=False):#ClearBeforeAppend clears cache before writing(used for single var)
    if ClearBeforeAppend==True:
        context.user_data[CacheVar] = ""
    if (context.user_data.get(CacheVar,"") == ""):
        context.user_data[CacheVar] = Value
    else:
        context.user_data[CacheVar] = context.user_data.get(CacheVar)+','+Value

def LoadFromCache(context,CacheVar):
    return context.user_data.get(CacheVar)

def SendJobToAdmin(context,ClientID,OrderID,MEDIA,SIZE,QUANTITY,DOCUMENT_ID):
    context.bot.sendDocument(
        chat_id = PrintAdmin[0],
        caption = 
        f'`#Order No. : {OrderID}`\n'
        f'Client : ***{returnClientAlias(str(ClientID))}***\n'
        f'Media : ***{MEDIA}***\n'
        f'Size(inches) : ***{SIZE}***'                        
        f'\nQuantity : ***{QUANTITY}***',
        parse_mode=ParseMode.MARKDOWN,
        document = DOCUMENT_ID,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Job In Progress",callback_data=f"WIP#{OrderID}")]],resize_keyboard=True),
    )
    
def GetOrderStatus(context,ClientID):
    OrderID = LoadFromCache(context,"WORKING_ORDERID")
    DETECTED_MEDIA = LoadFromCache(context,"DetectedMedia")
    DETECTED_WH= LoadFromCache(context,"DetectedWidthHeight")
    DETECTED_QUANTITY = LoadFromCache(context,"DetectedQuantity")
    
    
    QueueCounter = int(LoadFromCache(context,"PROCESSING_COUNTER"))-1
    FileName = LoadFromCache(context,"FileActualName").split(',')[QueueCounter]
    FileChatID = str(LoadFromCache(context,"FileChatID").split(',')[QueueCounter])
    FileTGID = LoadFromCache(context,"FileTGIDList").split(',')[QueueCounter]
    
    
    NEW_MSG = f'`#Order No. : {OrderID}`\n'
    if DETECTED_MEDIA:
        NEW_MSG+=f'Media : ***{DETECTED_MEDIA}***\n'
    
    if DETECTED_WH:
        NEW_MSG+=f'Size(Inch) : ***{DETECTED_WH}***\n'
    
    NEW_MSG+=f'Quantity : ***{DETECTED_QUANTITY}***\n'
    print(DETECTED_MEDIA)
    print(DETECTED_WH)
    
    if not DETECTED_MEDIA:
        NEW_MSG+='***SELECT MEDIA : ***'
        context.bot.editMessageText(
            chat_id=ClientID,
            message_id=OrderID,
            text=NEW_MSG,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=LoadMediaCategories()
            )
        return [NEW_MSG,"EXPECT_MEDIA_SELECT"]
    
    elif not DETECTED_WH:
        AppendToCache(context,"CURRENT_USER_INPUT","SIZE",True)
        NEW_MSG+='***ENTER SIZE(In Inches) : ***'
        context.bot.editMessageText(
            chat_id=ClientID,
            message_id=OrderID, 
            text=NEW_MSG,
            parse_mode=ParseMode.MARKDOWN
            )
        return [NEW_MSG,"EXPECT_TEXT"]
    else:
        create_order(str(ClientID),FileName+','+FileChatID,FileTGID,DETECTED_MEDIA,str(DETECTED_WH),str(DETECTED_QUANTITY),str(OrderID))
        SendJobToAdmin(context,ClientID,OrderID,DETECTED_MEDIA,DETECTED_WH,DETECTED_QUANTITY,FileTGID)
        NEW_MSG+='\n\u23E9 Job Sent'
        context.bot.editMessageText(
            chat_id=ClientID,
            message_id=OrderID, 
            text=NEW_MSG,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Edit",callback_data="EDIT")]])
            )
            
        return [NEW_MSG,"ORDER_DETAILS_COMPLETE"]

    


def RemoveEditOption(context,ClientID,OrderDetails):
    context.bot.editMessageText(
    chat_id=ClientID,
    message_id=str(OrderDetails[10]), 
    text=
    f'`#Order No. : {str(OrderDetails[10])}`\n'
    f'Media : ***{str(OrderDetails[1])}***\n'
    f'Size(inches) : ***{str(OrderDetails[4])+"x"+str(OrderDetails[5])}***'                        
    f'\nQuantity : ***{str(OrderDetails[6])}***'
    ,parse_mode=ParseMode.MARKDOWN,
    )


def ShowInlineMarkupWithText(context,ClientID,OrderDetails,ExtraMsg,ButtonText,MEDIA=True,SIZE=True,QUANTITY=True):
    MSG = f'`#Order No. : {str(OrderDetails[10])}`\n'
    if MEDIA==True:
        MSG += f'Media : ***{str(OrderDetails[1])}***\n'
    if SIZE==True:
        MSG += f'Size(inches) : ***{str(OrderDetails[4])+"x"+str(OrderDetails[5])}***\n'
    if QUANTITY==True:
        MSG += f'Quantity : ***{str(OrderDetails[6])}***'
    
    context.bot.editMessageText(
    chat_id=ClientID,
    message_id=str(OrderDetails[10]), 
    text=
    f'{MSG}'
    f'{ExtraMsg}',
    parse_mode=ParseMode.MARKDOWN,
    reply_markup=InlineKeyboardMarkup(ConvertToInlineMarkup(ButtonText),resize_keyboard=True)
    )