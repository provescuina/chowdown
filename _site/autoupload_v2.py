'''import imaplib
import base64
import os
import email
import time'''

import imaplib
import email
import re

# experiment desesperat, nomé provar si la resta falla
#import codecs
#    file = codecs.open("textUTF", "w", "utf-8")
#    file.write(str(subject, "utf-8"))
#    file.close()

#import urllib
#import urllib2
from unicodedata import normalize
from email.header import decode_header
from email.header import make_header


changes = False
new_image = False
image_name = ''
recepta = ''
gmail_username = 'carminaruizllaurado@gmail.com'
gmail_password = 'ribes2005'


def generateRecipeFile(email_content, fileName):
    global recepta
    content = email_content.splitlines()
    recipe_name = content[0][19:]
    recepta = recipe_name
    tags = content[1][11:]
    author = content[2][7:]
    path = os.path.join("/home/pi/receptari/_recipes/", recipe_name + ".md")
    if os.path.isfile(path):
        open(path, 'w').close()
    f = open(path, "w+")
    f.write("---\n\n")
    f.write("layout: recipe\n")
    f.write('title: "' + recipe_name + '"\n')
    f.write("image: " + fileName + "\n")
    f.write("tags: " + tags + "\n\n")
    f.write("ingredients:\n")
    i = 5
    while content[i] != '':
        f.write(content[i]+'\n')
        i += 1
    f.write("\n")
    f.write("directions:\n")
    for j in range(i+2,len(content)):
        f.write(content[j]+'\n')
    f.write("\n")
    f.write("---\n\n")
    f.write("From " + author + "\n")
    f.close()
    os.chmod("/home/pi/receptari/_recipes/" + recipe_name + ".md", 0o777)


def connect_to_gmail(username, password):
    imap = imaplib.IMAP4_SSL('imap.gmail.com')
    imap.login(username, password)
    imap.select("inbox")
    return imap

def get_subject(email):
    h = decode_header(email.get('subject'))
    return str(make_header(h)).encode('utf-8')

def get_decoded_email_body(message_body):
    """ Decode email body.
    Detect character set if the header is not set.
    We try to get text/plain, but if there is not one then fallback to text/html.
    :param message_body: Raw 7-bit message body input e.g. from imaplib. Double encoded in quoted-printable and latin-1
    :return: Message body as unicode string
    """

    msg = email.message_from_string(message_body)

    text = ""
    if msg.is_multipart():
        html = None
        for part in msg.get_payload():

            #print "%s, %s" % (part.get_content_type(), part.get_content_charset())

            if part.get_content_charset() is None:
                # We cannot know the character set, so return decoded "something"
                text = part.get_payload(decode=True)
                continue

            charset = part.get_content_charset()

            if part.get_content_type() == 'text/plain':
                text = unicode(part.get_payload(decode=True), str(charset), "ignore").encode('utf8', 'replace')

            if part.get_content_type() == 'text/html':
                html = unicode(part.get_payload(decode=True), str(charset), "ignore").encode('utf8', 'replace')

        if text is not None:
            return text.strip()
        else:
            return html.strip()
    else:
        text = unicode(msg.get_payload(decode=True), msg.get_content_charset(), 'ignore').encode('utf8', 'replace')
        return text.strip()


# MAIN
#print("connectant")
imap = connect_to_gmail(gmail_username, gmail_password)
#print("filtrant")
result, mails_data = imap.search(None, "(UNSEEN)") # SUBJECT "Recepta de cuina")')
#print("merdejant les dades")
mails_ids = mails_data[0]
mails_id_list = mails_ids.split()

for i in reversed(mails_id_list):
    #print("més merdes")
    result, mail_data = imap.fetch(i, "(RFC822)")
    #print("decodificant")
    raw_email = mail_data[0][1]
    raw_email_string = raw_email.decode('utf-8')
    #print("llegint el correu")
    this_email = email.message_from_string(raw_email_string)
    #print("obtenint el concepte")
    subject = str(get_subject(this_email), "utf-8")
    #print(subject)
    if subject == "Recepta de cuina":
    	print (get_decoded_email_body(raw_email))



'''
while True:
    mail = imaplib.IMAP4_SSL('imap.gmail.com',993)
    mail.login(email_user, email_pass)
    mail.select('Inbox')
    type, data = mail.search(None, '(UNSEEN SUBJECT "Recepta de cuina")')
    #type, data = mail.search(None, '(SUBJECT "Recepta de cuina")')
    mail_ids = data[0]
    id_list = mail_ids.split()

    for num in data[0].split():
        typ, data = mail.fetch(num, '(RFC822)' )
        raw_email = data[0][1]# converts byte literal to string removing b''
        raw_email_string = raw_email.decode('utf-8')
        email_message = email.message_from_string(raw_email_string)

        # downloading attachments
        fileName = ''
        for part in email_message.walk():
            # this part comes from the snipped I don't understand yet... 
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue
            fileName = part.get_filename()        
            if bool(fileName):
                filePath = os.path.join('/home/pi/receptari/images/', fileName)
                if not os.path.isfile(filePath) :
                    fp = open(filePath, 'wb')
                    fp.write(part.get_payload(decode=True))
                    fp.close( )
                    os.chmod("/home/pi/receptari/images/" + fileName, 0o777)
                    new_image = True
                    image_name = fileName
                subject = str(email_message).split("Subject: ", 1)[1].split("\nTo:", 1)[0]

        for response_part in data:
            if isinstance(response_part, tuple):
                msg = email.message_from_string(response_part[1].decode('utf-8'))
                for part in msg.walk():
                    if part.get_content_type() == 'text/plain':
                        email_content = part.get_payload()
                        generateRecipeFile(email_content, fileName)
                        changes = True

    if changes:
        os.system("sudo chown -R pi:pi /home/pi/receptari/")
        if new_image:
            print("mv /home/pi/receptari/images/'" + image_name + "' /home/pi/receptari/images/'" + recepta + image_name[-4:]+ "'")
            os.system("mv /home/pi/receptari/images/'" + image_name + "' /home/pi/receptari/images/'" + recepta + image_name[-4:]+ "'")
        os.system("/usr/bin/make -C /home/pi/receptari/")
    time.sleep(60) '''