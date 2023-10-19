from flask import Flask, request, abort
import db_Friends as DB
import re

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError, LineBotApiError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)

line_bot_api = LineBotApi('YOUR_CHANNEL_ACCESS_TOKEN')
handler = WebhookHandler('YOUR_CHANNEL_SECRET')

# List of GroupName Generator
lsGUNAME = ["alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta", "iota", "kappa", "lambda", "mu", "nu", "xi", "omicron", "pi", "rho", "sigma", "tau", "upsilon", "phi", "chi", "psi", "omega"]

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    global body
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)


    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    groupSrc = re.search(r'"groupId":"(.*?)"', body)
    msg_from_user = event.message.text


    # PERSONAL CHAT
    if not groupSrc:
        if "$help" in msg_from_user:
            line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="The bot is always ready and happy to provide assistance!\nAlways use the '$' trigger to use the available features, namely:\n1. $help to ask for help\n2. $register to register your account to be able to use the menfess feature\n3. $pc to send personal chat messages via Bot based on recipient's NIM\n4. $reply to reply to menfess messages based on the sender's UserName\n5. $group to send a message to a group based on the GroupName of the destination group\n\nThis bot is still in early development so there are still many limitations and shortcomings. As a result:\n1. Bots CAN ONLY send TEXT messages\n2. Bots can NOT send messages containing EMOJI\n3. Bots have a DELAY of ~15 - 60 seconds\n\nSo if your message is not responded to, please send it in a few moments ~30 seconds"))
        elif "$register" in msg_from_user:
            msg_from_user = msg_from_user.split(" ")
            lenMSG = len(msg_from_user)
            if lenMSG == 4:
                # Gets the sender ID from the webhook body
                ID = re.search(r'"userId":"(.*?)"', body)
                # If ID is found
                if ID:
                    ID = ID.group(1)
                    # is Registered?
                    isRegistered = DB.findTable("Friends", "NIM", msg_from_user[1])
                    # If the registrant NIM is found in the Friends table (already registered)
                    if isRegistered:
                        line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="NIM has been registered!"))
                    else:
                        # is Waiting?
                        isWaiting = DB.findTable("Registers", "ID", ID)
                        # If the registrant ID is not found in the Registers table (not waiting to be verified)
                        if not isWaiting:
                            # Check if UNAME is duplicate or not?
                            isUNAME = DB.findTable("Friends", "UNAME", msg_from_user[3])
                            # If not found (duplicate)
                            if not isUNAME:
                                # If data entry is successful
                                if DB.insertTable("Registers", ID, msg_from_user[2], msg_from_user[1], msg_from_user[3]) == "Success":
                                    line_bot_api.reply_message(
                                    event.reply_token,
                                    TextSendMessage(text="Success\nNIM: {}\nID Line: {}\nUsername: {}\nPlease wait to be verified by Admin".format(msg_from_user[1], msg_from_user[2], msg_from_user[3])))
                                else:
                                    line_bot_api.reply_message(
                                    event.reply_token,
                                    TextSendMessage(text="An error occurred in the Database"))
                            else:
                                line_bot_api.reply_message(
                                event.reply_token,
                                TextSendMessage(text="USERNAME has been taken!"))
                        else:
                            line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text="This account is waiting to be verified!"))
                else:
                    line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="An error occurred in Messages"))
            else:
                line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="Please type: $register <NIM> <ID Line> <username>\nAttention!\nUsername is used as a pseudonym and is inserted at the end of the menfess message\n\nExample: $register 19622999 john123 WhoAmI"))
        elif "$pc" in msg_from_user:
            if len(msg_from_user)>13:
                # Gets the sender ID from the webhook body
                ID = re.search(r'"userId":"(.*?)"', body)
                # If the sender ID is found
                if ID:
                    ID = ID.group(1)
                    dest = msg_from_user[4:12]
                    pesan = msg_from_user[13::]

                    # Checks whether the sender has become a Friend
                    isFriend = DB.findTable("Friends", "ID", ID)
                    # If Friends
                    if isFriend:
                        sender = isFriend.replace("(","").replace(")","").replace("'","").split(", ")

                        # Check whether the recipient has become a Friend
                        isTargetFriend = DB.findTable("Friends", "NIM", dest)
                        # If Friends
                        if isTargetFriend:
                            dest = isTargetFriend.replace("(","").replace(")","").replace("'","").split(", ")
                            # Mengirimkan pesan menfess ke dest
                            work = "Successfully"
                            try:
                                line_bot_api.push_message(dest[0], TextSendMessage(text="{}\n\nSender: {}\n$reply to reply".format(pesan, sender[3])))
                            except LineBotApiError:
                                work = "Failed"
                            line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text="{} sent message!".format(work)))
                        else:
                            line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text="The destination NIM has not yet been registered"))
                    else:
                        line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="Your account is not registered yet!\Please type: $register"))
            else:
                line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="Please type: $pc <Destination NIM> <Message>\nExample: $pc 19622999 this is the message"))
        elif "$reply" in msg_from_user:
            if len(msg_from_user)>15:
                # Gets the sender ID from the webhook body
                ID = re.search(r'"userId":"(.*?)"', body)
                # If ID is found
                if ID:
                    ID = ID.group(1)
                    msg_from_user = msg_from_user.split(' ')
                    msg_from_user[2:] = [' '.join(msg_from_user[2:])]
                    pesan = msg_from_user[2]

                    # Checks whether the sender has become a Friend
                    isFriend = DB.findTable("Friends", "ID", ID)
                    # If Friends
                    if isFriend:
                        sender = isFriend.replace("(","").replace(")","").replace("'","").split(", ")

                        # Check whether the recipient has become a Friend
                        isTargetFriend = DB.findTable("Friends", "UNAME", msg_from_user[1])
                        # If Friends
                        if isTargetFriend:
                            dest = isTargetFriend.replace("(","").replace(")","").replace("'","").split(", ")
                            
                            # Send a reply message
                            work = "Successfully"
                            try:
                                line_bot_api.push_message(dest[0], TextSendMessage(text="{}\n\nSender: {}\n$reply untuk membalas".format(pesan, sender[3])))
                            except LineBotApiError:
                                work = "Failed"
                            line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text="{} sent message!".format(work)))
                        else:
                            line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text="Invalid destination Username"))
                    else:
                        line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="Your account is not registered yet!\Please type: $register"))
            else:
                line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="Please type: $reply <username sender> <Message>\nExample: $reply WhoAmI this is the message"))
        elif "$group" in msg_from_user:
            if len(msg_from_user)>10:
                # Gets the sender ID from the webhook body
                ID = re.search(r'"userId":"(.*?)"', body)
                # If the sender ID is found
                if ID:
                    ID = ID.group(1)
                    msg_from_user = msg_from_user.split(' ')
                    msg_from_user[2:] = [' '.join(msg_from_user[2:])]

                    # Checks whether the sender has become a Friend
                    isFriend = DB.findTable("Friends", "ID", ID)
                    # If Friends
                    if isFriend:
                        # Checks whether the destination GroupName is registered
                        isTargetGroups = DB.findTable("`Groups`", "GUNAME", msg_from_user[1])
                        # If GroupName is listed
                        if isTargetGroups:
                            dest = isTargetGroups.replace("(","").replace(")","").replace("'","").split(", ")

                            # Initialize var profile to help with try-except scheme
                            profile = None
                            try:
                                # Checks whether the sender is a member of the dest group
                                profile = line_bot_api.get_group_member_profile(dest[0], ID)
                            except LineBotApiError:
                                profile = None
                            
                            Gsummary = None
                            try:
                                # Checking whether the Bot is a member of the dest group (it could be expelled or out)
                                Gsummary = line_bot_api.get_group_summary(dest[0])
                            except LineBotApiError:
                                Gsummary = None

                            # If both the sender and Bot are members of the dest group
                            if (profile is not None) and (Gsummary is not None):
                                # Send messages to groups
                                line_bot_api.push_message(dest[0], TextSendMessage(text="{}".format(msg_from_user[2])))
                                
                                line_bot_api.reply_message(
                                event.reply_token,
                                TextSendMessage(text="Successfully sent the message!"))
                            else:
                                line_bot_api.reply_message(
                                event.reply_token,
                                TextSendMessage(text="The Bot detects that you or the Bot are not/no longer a member of the Group"))
                        else:
                            line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text="Destination GroupName is not Valid"))
            else:
                line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="Please type: $group <GroupName> <Message>\nExample: $group HighTableGroup this is the message"))

        # ADMIN MODE
        elif "$4dm1nInsertRegisters" in msg_from_user:
            msg_from_user = msg_from_user.split(" ")
            lenMSG = len(msg_from_user)
            if lenMSG == 5:
                isExist = DB.findTable("Registers", "NIM", msg_from_user[3])
                if not isExist:
                    line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=DB.insertTable("Registers", msg_from_user[1], msg_from_user[2], msg_from_user[3], msg_from_user[4])))
                else:
                    line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="Failed, NIM has been registered"))
            else:
                line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="Please type: $4dm1nInsertRegisters <ID> <IDL> <NIM> <UNAME>\nExample: $4dm1nInsertFriends 19622999"))
        elif "$4dm1nInsertFriends" in msg_from_user:
            msg_from_user = msg_from_user.split(" ")
            lenMSG = len(msg_from_user)
            if lenMSG == 2:
                isWaiting = DB.findTable("Registers", "NIM", msg_from_user[1])
                if isWaiting:
                    data = isWaiting
                    data = data.replace("(","").replace(")","").replace("'","").split(", ")

                    isRegistered = DB.findTable("Friends", "NIM", data[2])
                    if not isRegistered:
                        # If Insert data is successful
                        if (DB.insertTable("Friends", data[0], data[1], data[2], data[3]) == "Success"):
                            # If the Waiting data deletion is successful
                            if (DB.deleteTable("Registers", "ID", data[0]) == "Success"):
                                line_bot_api.push_message(data[0], TextSendMessage(text="Akun kamu sudah admin VERIF yah UwU"))

                                line_bot_api.reply_message(
                                event.reply_token,
                                TextSendMessage(text="Successfully inserted data"))
                            # If it fails delete in Waiting
                            # cancel previous data insert
                            else:
                                if (DB.deleteTable("Friends", "NIM", data[2]) == "Success"):
                                    line_bot_api.reply_message(
                                    event.reply_token,
                                    TextSendMessage(text="Failed to register"))
                                else:
                                    line_bot_api.reply_message(
                                    event.reply_token,
                                    TextSendMessage(text="Failed to delete registration data (undo)"))
                        else:
                            line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text="Failed to insert data"))
                    else:
                        line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="Failed, NIM has been registered"))
                else:
                    line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="Failed, NIM is not in the queue"))
            else:
                line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="Please type: $4dm1nInsertFriends <NIM>\nExample: $4dm1nInsertFriends 19622999"))
        elif "$4dm1nReadRegisters" in msg_from_user:
            result = DB.readTable("Registers")
            line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=result))
        elif "$4dm1nReadFriends" in msg_from_user:
            result = DB.readTable("Friends")
            line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=result))
        else:
            line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="Sorry, we couldn't understand the message you sent\nType $help"))
    # GROUP CHAT
    else:
        if "$help" in msg_from_user:
            line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="The bot is always ready and happy to provide assistance!\nAlways use the '$' trigger to use the available features, namely:\n1. $help to ask for help\n2. $register to register this Group and get a GroupName so you can use the menfess feature\n\nTo get started, register your account via personal chat to this Bot\n\nTo send a message to this group, do a personal chat to the Bot with the trigger $group and GroupName this group\n\nThis bot is still in early development so there are still many limitations and shortcomings. As a result:\n1. Bots CAN ONLY send TEXT messages\n2. Bots can NOT send messages containing EMOJI\n3. Bots have a DELAY of ~15 -- 60 seconds\n\nSo if your message is not responded to, please send it in a few moments ~30 seconds"))
        if "$register" in msg_from_user:
            ID = re.search(r'"userId":"(.*?)"', body)
            if ID and groupSrc:
                ID = ID.group(1)
                GID = groupSrc.group(1)

                # Checks whether the sender has become a Friend
                isFriend = DB.findTable("Friends", "ID", ID)
                # If Friends
                if isFriend:
                    # Checks whether the group is registered
                    isGroups = DB.findTable("`Groups`", "GID", GID)
                    # If not registered
                    if not isGroups:
                        # Determines the number of rows (groups) that have been registered
                        # and used as the index of the GroupName list
                        GUNAME = lsGUNAME[DB.lengthRow("`Groups`")]
                        # If GUNAME is defined
                        if GUNAME:
                            # Data insertion
                            if (DB.insertGroups(GID, GUNAME, ID) == "Success"):
                                line_bot_api.reply_message(
                                event.reply_token,
                                TextSendMessage(text="Successfully registered the Group!\nGroupName: {}\nUse '{}' as the GroupName when you want to send Menfess to this group".format(GUNAME, GUNAME)))
                            else:
                                line_bot_api.reply_message(
                                event.reply_token,
                                TextSendMessage(text="Failed to insert data"))
                        else:
                            line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text="Failed to Generate GroupName"))
                    # Jika group terlah terdaftar
                    else:
                        GUNAME = DB.findTable("`Groups`", "GID", GID)
                        GUNAME = GUNAME.replace("(","").replace(")","").replace("'","").split(", ")
                        GUNAME = GUNAME[1]
                        line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="This group is registered with GroupName = {}".format(GUNAME)))
                else:
                    line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="Your account is not registered yet!\nPlease DM and send $register"))
            else:
                line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="Terjadi kesalahan pada Pesan"))


if __name__ == "__main__":
    app.run()