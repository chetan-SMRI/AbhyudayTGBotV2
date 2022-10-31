import string
import re
from telegram.update import Update
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters
from telegram import *
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext,PicklePersistence,ConversationHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply
from database_work import *

from BASIC_FUNCTIONS import *
from SECRETS import *

updater = Updater(BOT_TOKEN,use_context=True)

from CACHE_FUNCTIONS import *


    


#  ____    _                    _       _____                        
# / ___|  | |_    __ _   _ __  | |_    |  ___|  _   _   _ __     ___ 
# \___ \  | __|  / _` | | '__| | __|   | |_    | | | | | '_ \   / __|
#  ___) | | |_  | (_| | | |    | |_    |  _|   | |_| | | | | | | (__ 
# |____/   \__|  \__,_| |_|     \__|   |_|      \__,_| |_| |_|  \___|

def start(update: Update, context: CallbackContext):
    isUser = checkUserRegistered(str(update.effective_chat.id))
    if isUser:
        update.message.reply_text("Hello , Thanks for choosing Abhyuday Unicorp.",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("Add Print Job")]],one_time_keyboard=True,resize_keyboard=True))
    else:    
        update.message.reply_text("Hello , Thanks for choosing Abhyuday Unicorp.",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton('Do Registration', request_contact=True)]],resize_keyboard=True))
def contact_client_registration_callback(update: Update, context: CallbackContext):
    contact = update.effective_message.contact
    phone = contact.phone_number
    #Sending admin user registration request
    context.bot.send_message(chat_id=PrintAdmin[0],
            text=f'New Registration Request.\nContact No. - {phone} \n To Approve Click-\n `/approve '+str(update.effective_chat.id)+'  `',
            parse_mode=ParseMode.MARKDOWN,
            )
    register_user_contact(str(update.effective_chat.id),str(phone))

def help(update: Update, context: CallbackContext):
	update.message.reply_text("Admins - \n@arvindnahar\n@chetannahar\n+91 7000284933\n+91 9425307870")

def Approve(update: Update, context: CallbackContext):
    if (str(update.effective_chat.id) == PrintAdmin[0]):
        input_mex = update.message.text
        input_args = input_mex.split('/approve ')[1]
        ##This Registers User With Approval Status
        register_user(input_args.split(" ")[0],input_args.split(input_args.split(" ")[0])[1])
        context.bot.send_message(chat_id=input_args.split(" ")[0],text="Your registration has been completed. Now you can send print jobs.",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("Add Print Job")]],one_time_keyboard=True,resize_keyboard=True))

def getDB(update: Update, context: CallbackContext):
    if (str(update.effective_chat.id) == PrintAdmin[0]):
        context.bot.send_document(PrintAdmin[0],open('db.db','rb'))


#   ___               _                    ____                         _          
#  / _ \   _ __    __| |   ___   _ __     / ___|  _ __    ___    __ _  | |_    ___ 
# | | | | | '__|  / _` |  / _ \ | '__|   | |     | '__|  / _ \  / _` | | __|  / _ \
# | |_| | | |    | (_| | |  __/ | |      | |___  | |    |  __/ | (_| | | |_  |  __/
#  \___/  |_|     \__,_|  \___| |_|       \____| |_|     \___|  \__,_|  \__|  \___|

def OrderStartHandler(update: Update, context: CallbackContext):
    ######FIRST CLEAR CACHE AT START
    ClearCache(context)
    ###IF CONV IS STARTED WITH A DOCUMENT ITSELF THEN WE DONT ASK FOR 'Send Files'
    if(update.message.document):
        File = update.message.document
        if(File.mime_type=='video/mp4'):
            context.bot.delete_message(chat_id=update.effective_chat.id,message_id=update.message.message_id)
            ConversationHandler.END
        elif("image" in File.mime_type.lower() or "pdf" in File.mime_type.lower() or ".cdr" in File.file_text.lower()):
            #Adding Image Message ID to our file list
            AppendToCache(context,"FileChatID",str(update.message.message_id))
            AppendToCache(context,"FileActualName",str(File.file_name))
            AppendToCache(context,"FileTGIDList",File['file_id'])
            AppendToCache(context,"COUNTER",1,True)#BECOZ WE KNOW ITS FIRST FILE
            for OrderQueue in range(0,int(LoadFromCache(context,"COUNTER"))):
                if OrderQueue==0:  ##FOR VERY FIRST ORDER WE HAVE TO PROCESS DATA AT START
                    ProcessFileData(context,update.effective_chat.id)#DO AFTER SINGLE ORDER COMPLETION
                message=GetOrderStatus(context,update.effective_chat.id)#IT RETURN WHAT TO ASK OR IF EVERYTHING OK THEN CREATE ORDER
            
                if message[1] == "EXPECT_MEDIA_SELECT":
                    return EXPECT_MEDIA_SELECT
                elif message[1] == "EXPECT_TEXT":
                    return EXPECT_TEXT
                elif message[1] == "ORDER_DETAILS_COMPLETE":
                    print("Processing Next Order")
                    ProcessFileData(context,update.effective_chat.id)
                if AllOrdersProcessed(context):
                    return ConversationHandler.END
    else:
        isUser = checkUserRegistered(str(update.effective_chat.id))
        if not isUser:
            update.message.reply_text('Sorry, You Are Not A Registered User')
            return ConversationHandler.END
        update.message.reply_text('Send Files',reply_markup=ReplyKeyboardMarkup([['Continue']],resize_keyboard=True))
        
    return EXPECT_FILE

def GetFiles(update: Update, context: CallbackContext):
    #SEND "Send As File" IF PHOTO RECIEVED.
    if(update.message.photo):
        context.bot.send_message(chat_id=update.effective_chat.id,
            text='SEND AS A "FILE".\nThis file is compressed.',reply_markup=ReplyKeyboardMarkup([[KeyboardButton("Continue")]],one_time_keyboard=True,resize_keyboard=True))
        context.bot.delete_message(chat_id=update.effective_chat.id,message_id=update.message.message_id)
    if update.message.text ==None:
        File = update.message.document
        if(File.mime_type=='video/mp4'):
            context.bot.delete_message(chat_id=update.effective_chat.id,message_id=update.message.message_id)
            ConversationHandler.END
        elif("image" in File.mime_type.lower() or "pdf" in File.mime_type.lower() or ".cdr" in File.file_text.lower()):
            #Adding Image Message ID to our file list
            AppendToCache(context,"FileChatID",str(update.message.message_id))
            AppendToCache(context,"FileActualName",str(File.file_name))
            AppendToCache(context,"FileTGIDList",File['file_id'])
            AppendToCache(context,"COUNTER",int(LoadFromCache(context,"COUNTER"))+1,True)#BECOZ WE KNOW ITS FIRST FILE
    elif update.message.text == "Continue":
        if LoadFromCache(context,"COUNTER") == '0':
            update.message.reply_text("Please send file.")
            return EXPECT_FILE
        print("Start Processing file")
        print("Total Files Loaded : "+str(LoadFromCache(context,"COUNTER")))
        ####################################################################
        ####################################################################
        #ALL FILES LOADED TO CACHE NOW WE ONLY HAVE TO USE LOOP TO ITERATE FOR EVERY ORDER,
        #IF AI COULDNT DETECT ANYTHING IN BTW ORDERS THEN WE JUST GET WHATS LEFT AND WE DO PROCESS IT AFTERWARDS
        ####################################################################
        ####################################################################
        for OrderQueue in range(0,int(LoadFromCache(context,"COUNTER"))):
            if OrderQueue==0:  ##FOR VERY FIRST ORDER WE HAVE TO PROCESS DATA AT START
                ProcessFileData(context,update.effective_chat.id)#DO AFTER SINGLE ORDER COMPLETION
            message=GetOrderStatus(context,update.effective_chat.id)#IT RETURN WHAT TO ASK OR IF EVERYTHING OK THEN CREATE ORDER
            
            if message[1] == "EXPECT_MEDIA_SELECT":
                return EXPECT_MEDIA_SELECT
            elif message[1] == "EXPECT_TEXT":
                return EXPECT_TEXT
            elif message[1] == "ORDER_DETAILS_COMPLETE":
                print("Processing Next Order")
                ProcessFileData(context,update.effective_chat.id)
                if AllOrdersProcessed(context):
                    return ConversationHandler.END

def MediaSelectHandler(update: Update, context: CallbackContext):
    MSG = update.callback_query.data
    if (MSG=="EDIT"):
        update.callback_query.answer(text="You Can't Edit This Before Generating All Orders.")
        return EXPECT_BUTTON_CLICK
    if (MSG=="Other"):
        context.bot.editMessageText(
            chat_id=update.effective_chat.id,
            message_id=LoadFromCache(context,"WORKING_ORDERID"), 
            text='***Enter Media Name: ***'
            ,parse_mode=ParseMode.MARKDOWN)
        AppendToCache(context,"CURRENT_USER_INPUT","OtherMedia")
        return EXPECT_TEXT
    if MSG in MediaCategory:
        update.callback_query.answer(f'{MSG} selected.')
        AppendToCache(context,"DetectedMedia",MSG,True)
        for OrderQueue in range(0,int(LoadFromCache(context,"COUNTER"))):
            if AllOrdersProcessed(context):
                return ConversationHandler.END
            message=GetOrderStatus(context,update.effective_chat.id)#IT RETURN WHAT TO ASK OR IF EVERYTHING OK THEN CREATE ORDER
            print(message[0])
            print(message[1])
            if message[1] == "EXPECT_MEDIA_SELECT":
                return EXPECT_MEDIA_SELECT
            elif message[1] == "EXPECT_TEXT":
                return EXPECT_TEXT
            elif message[1] == "ORDER_DETAILS_COMPLETE":
                print("Processing Next Order")
                ProcessFileData(context,update.effective_chat.id)#DO AFTER SINGLE ORDER COMPLETION
                if AllOrdersProcessed(context):
                    return ConversationHandler.END

    

def TextHandler(update: Update, context: CallbackContext):
    TEXT = update.message.text
    if LoadFromCache(context,"CURRENT_USER_INPUT") == "SIZE":
        if GetCorrectSizeFormat(TEXT):
            Size = GetCorrectSizeFormat(TEXT)
            AppendToCache(context,"DetectedWidthHeight",Size,True)
            context.bot.deleteMessage(update.effective_chat.id,update.message.message_id)
            for OrderQueue in range(0,int(LoadFromCache(context,"COUNTER"))):
                if AllOrdersProcessed(context):
                    return ConversationHandler.END
                message=GetOrderStatus(context,update.effective_chat.id)#IT RETURN WHAT TO ASK OR IF EVERYTHING OK THEN CREATE ORDER
                print(message[0])
                print(message[1])
                if message[1] == "EXPECT_MEDIA_SELECT":
                    return EXPECT_MEDIA_SELECT
                elif message[1] == "EXPECT_TEXT":
                    return EXPECT_TEXT
                elif message[1] == "ORDER_DETAILS_COMPLETE":
                    print("Processing Next Order")
                    ProcessFileData(context,update.effective_chat.id)#DO AFTER SINGLE ORDER COMPLETION
                    if AllOrdersProcessed(context):
                        return ConversationHandler.END
        else:
            update.message.reply_text("Enter In Correct Format")
            context.bot.deleteMessage(update.effective_chat.id,update.message.message_id)
    if LoadFromCache(context,"CURRENT_USER_INPUT") == "OtherMedia":
        AppendToCache(context,"DetectedMedia",TEXT,True)
        context.bot.deleteMessage(update.effective_chat.id,update.message.message_id)
        for OrderQueue in range(0,int(LoadFromCache(context,"COUNTER"))):
            if AllOrdersProcessed(context):
                return ConversationHandler.END
            message=GetOrderStatus(context,update.effective_chat.id)#IT RETURN WHAT TO ASK OR IF EVERYTHING OK THEN CREATE ORDER
            print(message[0])
            print(message[1])
            if message[1] == "EXPECT_MEDIA_SELECT":
                return EXPECT_MEDIA_SELECT
            elif message[1] == "EXPECT_TEXT":
                return EXPECT_TEXT
            elif message[1] == "ORDER_DETAILS_COMPLETE":
                print("Processing Next Order")
                ProcessFileData(context,update.effective_chat.id)#DO AFTER SINGLE ORDER COMPLETION
                if AllOrdersProcessed(context):
                    return ConversationHandler.END
    
    
def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("Cancelled.\nNote-Processed Orders Aren't Cancelled.")


#  ____                                                ___               _               
# |  _ \   _ __    ___     ___    ___   ___   ___     / _ \   _ __    __| |   ___   _ __ 
# | |_) | | '__|  / _ \   / __|  / _ \ / __| / __|   | | | | | '__|  / _` |  / _ \ | '__|
# |  __/  | |    | (_) | | (__  |  __/ \__ \ \__ \   | |_| | | |    | (_| | |  __/ | |   
# |_|     |_|     \___/   \___|  \___| |___/ |___/    \___/  |_|     \__,_|  \___| |_|   

def AllOrdersProcessed(context):
    if int(LoadFromCache(context,"PROCESSING_COUNTER"))>int(LoadFromCache(context,"COUNTER")):            ##RETURN AFTER ALL ORDERS TAKEN
        return True

def ProcessFileData(context,ClientID):#THIS IS DEFAULT FILE DATA EXTRACTOR
    AppendToCache(context,"PROCESSING_COUNTER",int(LoadFromCache(context,"PROCESSING_COUNTER"))+1,True)#CHANGE ORDER TO NEXT ORDER
    AppendToCache(context,"WORKING_ORDERID","",True)#CLEARING LAST ORDER CACHE
    AppendToCache(context,"DetectedMedia","",True)
    AppendToCache(context,"DetectedWidthHeight","",True)
    AppendToCache(context,"DetectedQuantity","",True)
    
    if LoadFromCache(context,"PROCESSING_COUNTER")>LoadFromCache(context,"COUNTER"):            ##RETURN AFTER ALL ORDERS TAKEN
        context.bot.send_message(chat_id=ClientID,text="Your order will be processed shortly.",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("Add Print Job")]] ,resize_keyboard=True) )
        print("END OF ORDERS")
    else:
        CurrentFileName = LoadFromCache(context,"FileActualName").split(',')[LoadFromCache(context,"PROCESSING_COUNTER")-1]
        FileChatID = LoadFromCache(context,"FileChatID").split(',')[LoadFromCache(context,"PROCESSING_COUNTER")-1]
        DETECTED_MEDIA = detectMedia(CurrentFileName)
        DETECTED_WH = detectWidthHeight(CurrentFileName)
        DETECTED_QUANTITY = detectQuantity(CurrentFileName)
        
        OrderID = context.bot.send_message(chat_id=ClientID,text="`Processing File...`",parse_mode=ParseMode.MARKDOWN,reply_to_message_id = FileChatID).message_id
        if DETECTED_MEDIA != None:
            AppendToCache(context,"DetectedMedia",DETECTED_MEDIA,True)
        
        if DETECTED_WH != None:
            AppendToCache(context,"DetectedWidthHeight",DETECTED_WH,True)
        
        AppendToCache(context,"DetectedQuantity",DETECTED_QUANTITY,True)

        AppendToCache(context,"PROCESSING_STATUS",True,True)
        AppendToCache(context,"WORKING_ORDERID",OrderID,True)


#  _____   ____    ___   _____      ___    ____    ____    _____   ____  
# | ____| |  _ \  |_ _| |_   _|    / _ \  |  _ \  |  _ \  | ____| |  _ \ 
# |  _|   | | | |  | |    | |     | | | | | |_) | | | | | |  _|   | |_) |
# | |___  | |_| |  | |    | |     | |_| | |  _ <  | |_| | | |___  |  _ < 
# |_____| |____/  |___|   |_|      \___/  |_| \_\ |____/  |_____| |_| \_\

def EditOrder(update: Update, context: CallbackContext):
    query = update.callback_query
    Order = GetOrderDetails(str(update.callback_query.message.message_id))
    ##REMOVING EDIT BUTTON IF CLICKED AFTER 10 MINUTES

    if(str(update.effective_chat.id) == PrintAdmin[0]):
        if 'WIP#' in query.data:
            OrderID = query.data.replace('WIP#','')
            OrderDetails = GetOrderDetails(OrderID)
            context.bot.editMessageCaption(
                chat_id=PrintAdmin[0],
                message_id=update.callback_query.message.message_id, 
                caption=
                f'`#Order No. : {str(OrderDetails[10])}`\n'
                f'Media : ***{str(OrderDetails[1])}***\n'
                f'Size(inches) : ***{str(OrderDetails[4])+"x"+str(OrderDetails[5])}***'                        
                f'\nQuantity : ***{str(OrderDetails[6])}***'
                '\n\u2699 Job In Progress',
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Job Completed",callback_data=f"DONE#{OrderID}")]],resize_keyboard=True),
            )
            ShowInlineMarkupWithText(context,str(OrderDetails[0]),OrderDetails,"\n\u2699 Job In Progress",[])
            UpdateJobStatus(OrderID,"WIP")
            return
        elif 'DONE#' in query.data:
            OrderID = query.data.replace('DONE#','')
            OrderDetails = GetOrderDetails(OrderID)
            context.bot.editMessageCaption(
                chat_id=PrintAdmin[0],
                message_id=update.callback_query.message.message_id, 
                caption=
                f'`#Order No. : {str(OrderDetails[10])}`\n'
                f'Media : ***{str(OrderDetails[1])}***\n'
                f'Size(inches) : ***{str(OrderDetails[4])+"x"+str(OrderDetails[5])}***'                        
                f'\nQuantity : ***{str(OrderDetails[6])}***'
                '\n\u2705 Job Completed!',
                parse_mode=ParseMode.MARKDOWN,
            )
            ShowInlineMarkupWithText(context,str(OrderDetails[0]),OrderDetails,"\n\u2705 Job Completed!",[])
            context.bot.send_message(chat_id=str(OrderDetails[0]), text=f'`#Order No. : {str(OrderDetails[10])}`\n'f'Completed! You Can Pick It Up Anytime.'
            ,parse_mode=ParseMode.MARKDOWN)
            UpdateJobStatus(OrderID,"DONE")
            return
        

    if not CanEditOrder(str(update.effective_chat.id),str(update.callback_query.message.message_id)):
        RemoveEditOption(context,update.effective_chat.id,Order)
        return
    
    if(query.data=="EDIT"):
        ShowInlineMarkupWithText(context,update.effective_chat.id,Order,"\n\n***Choose what to EDIT?***",['Media','Size','Quantity'])
        
    elif(query.data=="Media"):
        ShowInlineMarkupWithText(context,update.effective_chat.id,Order,"\n\n***Choose Media : ***",MediaCategory,MEDIA=False)
    elif(query.data=="Size"):
        ShowInlineMarkupWithText(context,update.effective_chat.id,Order,"\n\n***Enter Size(In Inches) : ***",[],SIZE=False)
        context.user_data["EDIT_COMMAND"] = "SIZE"
        context.user_data["EDIT_ORDER_ID"] = str(Order[10])
    elif(query.data=="Quantity"):
        ShowInlineMarkupWithText(context,update.effective_chat.id,Order,"\n\n***Enter Quantity : ***",[],QUANTITY=False)
        context.user_data["EDIT_COMMAND"] = "QUANTITY"
        context.user_data["EDIT_ORDER_ID"] = str(Order[10])
    elif(query.data=="Other"):
        ShowInlineMarkupWithText(context,update.effective_chat.id,Order,"\n\n***Enter Media Name : ***",[],MEDIA=False)
        context.user_data["EDIT_COMMAND"] = "OtherMedia"
        context.user_data["EDIT_ORDER_ID"] = str(Order[10])
    elif query.data in MediaCategory:
        context.bot.editMessageText(chat_id=update.effective_chat.id,
            message_id=update.callback_query.message.message_id, 
            text=
            f'`#Order No. : {str(Order[10])}`\n'
            f'Media : ***{query.data}***\n'
            f'Size(inches) : ***{str(Order[4])+"x"+str(Order[5])}***'                        
            f'\nQuantity : ***{str(Order[6])}***'
            ,parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Edit",callback_data="EDIT")]]))
        EditOrderDetails(str(update.effective_chat.id),str(update.callback_query.message.message_id),"Media",query.data)
        context.bot.send_message(
            chat_id=PrintAdmin[0], 
            text=
            f'`***EDITED***\n#Order No. : {str(Order[10])}`\n'
            f'`Media : ***{query.data}***\n`'
            f'Size(inches) : ***{str(Order[4])+"x"+str(Order[5])}***'                        
            f'\nQuantity : ***{str(Order[6])}***'
            ,parse_mode=ParseMode.MARKDOWN,)
        AppendToCache(context,"EDIT_COMMAND","",True)
        AppendToCache(context,"EDIT_ORDER_ID","",True)

def EditOrderSizeOrQuantity(update: Update, context: CallbackContext):
    
    query = update.callback_query
    Order = GetOrderDetails(str(LoadFromCache(context,"EDIT_ORDER_ID")))
    ##REMOVING EDIT BUTTON IF TEXTED AFTER 10 MINUTES

    if not CanEditOrder(str(update.effective_chat.id),str(str(LoadFromCache(context,"EDIT_ORDER_ID")))):
        RemoveEditOption(context,update.effective_chat.id,Order)
        return
    
    TEXT = update.message.text
    
    if(context.user_data.get("EDIT_COMMAND","") == ""):
        update.message.text("I don't recognize this command.")
    
    if LoadFromCache(context,"EDIT_COMMAND") == "SIZE":
        if GetCorrectSizeFormat(TEXT):
            Size = GetCorrectSizeFormat(TEXT)
            context.bot.editMessageText(
                chat_id=update.effective_chat.id,
                message_id=str(LoadFromCache(context,"EDIT_ORDER_ID")), 
                text=
                f'`#Order No. : {str(Order[10])}`\n'
                f'Media : ***{str(Order[1])}***\n'
                f'Size(inches) : ***{Size}***'                        
                f'\nQuantity : ***{str(Order[6])}***',
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Edit",callback_data="EDIT")]])
            )
            EditOrderDetails(str(update.effective_chat.id),str(LoadFromCache(context,"EDIT_ORDER_ID")),"WidthHeight",Size)
            context.bot.deleteMessage (message_id = update.message.message_id,
                chat_id = update.effective_chat.id)
            context.bot.send_message(
            chat_id=PrintAdmin[0], 
            text=
            f'`***EDITED***\n#Order No. : {str(Order[10])}`\n'
            f'Media : ***{str(Order[1])}***\n'
            f'`Size(inches) : ***{Size}***`'                        
            f'\nQuantity : ***{str(Order[6])}***'
            ,parse_mode=ParseMode.MARKDOWN,)
            AppendToCache(context,"EDIT_COMMAND","",True)
            AppendToCache(context,"EDIT_ORDER_ID","",True)
        else:
            update.message.reply_text("Enter In Correct Format")
            context.bot.deleteMessage(update.effective_chat.id,update.message.message_id)
    if LoadFromCache(context,"EDIT_COMMAND") == "QUANTITY":
        if(TEXT.isdigit()):
            context.bot.editMessageText(chat_id=update.effective_chat.id,
                message_id=context.user_data.get("EDIT_ORDER_ID"),
                text=
                f'`#Order No. : {str(Order[10])}`\n'
                f'Media : ***{str(Order[1])}***\n'
                f'Size(inches) : ***{str(Order[4])+"x"+str(Order[5])}***'                        
                f'\nQuantity : ***{str(TEXT)}***'
                ,parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Edit",callback_data="EDIT")]]))
            EditOrderDetails(str(update.effective_chat.id),str(context.user_data.get("EDIT_ORDER_ID")),"Quantity",TEXT)
            context.bot.deleteMessage (message_id = update.message.message_id,
                           chat_id = update.effective_chat.id)
            context.bot.send_message(chat_id=PrintAdmin[0], 
            text=
            f'`***EDITED***\n#Order No. : {str(Order[10])}`\n'
            f'Media : ***{str(Order[1])}***\n'
            f'Size(inches) : ***{str(Order[4])+"x"+str(Order[5])}***'                        
            f'`\nQuantity : ***{update.message.text}***`'
            ,parse_mode=ParseMode.MARKDOWN,)
            AppendToCache(context,"EDIT_COMMAND","",True)
            AppendToCache(context,"EDIT_ORDER_ID","",True)
        else:
            update.message.reply_text("Enter In Digit")
            context.bot.deleteMessage(update.effective_chat.id,update.message.message_id)
    
    if LoadFromCache(context,"EDIT_COMMAND") == "OtherMedia":
        context.bot.editMessageText(chat_id=update.effective_chat.id,
            message_id=context.user_data.get("EDIT_ORDER_ID"),
            text=
            f'`#Order No. : {str(Order[10])}`\n'
            f'Media : ***{TEXT}***\n'
            f'Size(inches) : ***{str(Order[4])+"x"+str(Order[5])}***'                        
            f'\nQuantity : ***{str(Order[6])}***'
            ,parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Edit",callback_data="EDIT")]])
        )
        EditOrderDetails(str(update.effective_chat.id),str(context.user_data.get("EDIT_ORDER_ID")),"Media",TEXT)
        context.bot.deleteMessage (message_id = update.message.message_id,
                       chat_id = update.effective_chat.id)
        context.bot.send_message(chat_id=PrintAdmin[0], 
        text=
        f'`***EDITED***\n#Order No. : {str(Order[10])}`\n'
        f'`Media : ***{TEXT}***`\n'
        f'Size(inches) : ***{str(Order[4])+"x"+str(Order[5])}***'                        
        f'\nQuantity : ***{str(Order[6])}***'
        ,parse_mode=ParseMode.MARKDOWN,)
        AppendToCache(context,"EDIT_COMMAND","",True)
        AppendToCache(context,"EDIT_ORDER_ID","",True)
#  _____    ____     ____    _                                _                   
# |_   _|  / ___|   |  _ \  (_)  ___   _ __     __ _    ___  | |__     ___   _ __ 
#   | |   | |  _    | | | | | | / __| | '_ \   / _` |  / __| | '_ \   / _ \ | '__|
#   | |   | |_| |   | |_| | | | \__ \ | |_) | | (_| | | (__  | | | | |  __/ | |   
#   |_|    \____|   |____/  |_| |___/ | .__/   \__,_|  \___| |_| |_|  \___| |_|   
#                                     |_|                                         

updater.dispatcher.add_handler(CommandHandler('start', start))#BASIC FUNC
updater.dispatcher.add_handler(CommandHandler('help', help))#BASIC FUNC
updater.dispatcher.add_handler(MessageHandler(Filters.contact, contact_client_registration_callback))#BASIC FUNC
updater.dispatcher.add_handler(CommandHandler('approve', Approve))#ADMIN ONLY, BASIC FUNC

updater.dispatcher.add_handler(CommandHandler('getDB', getDB))#ADMIN ONLY

##NEW ORDER RELATED
NEW_ORDER_HANDLER = ConversationHandler(
        #Filter.document directly start order with document
        entry_points=[CommandHandler('add_print', OrderStartHandler) , MessageHandler(Filters.regex(re.compile(r'Add Print Job', re.IGNORECASE)) | Filters.document,OrderStartHandler)],
        states={
            EXPECT_FILE:[MessageHandler(Filters.document | Filters.photo | Filters.regex(re.compile(r'Continue', re.IGNORECASE)), GetFiles)],
            EXPECT_MEDIA_SELECT: [CallbackQueryHandler(MediaSelectHandler)],
            EXPECT_TEXT: [MessageHandler(Filters.text, TextHandler)],
        },
        fallbacks=[CommandHandler('CANCEL', cancel)],
    )
updater.dispatcher.add_handler(NEW_ORDER_HANDLER)

###ORDER EDITING WITHIN 10 MINUTES OF ORDER GENERATION
updater.dispatcher.add_handler(CallbackQueryHandler(EditOrder))
updater.dispatcher.add_handler(MessageHandler(Filters.text,EditOrderSizeOrQuantity))


PORT = int(os.environ.get('PORT', 5000))

updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path='5607987516:AAHosHPGAF9_b7cQgezcxuzhchN1kgir-Vw',
		          webhook_url='https://nameless-journey-34713.herokuapp.com/' + '5607987516:AAHosHPGAF9_b7cQgezcxuzhchN1kgir-Vw')
updater.idle()
