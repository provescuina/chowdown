import imaplib
import base64
import os
import email


def generateRecipeFile(email_content, fileName):
    global recepta
    content = email_content.splitlines()
    recipe_name = content[0][19:]
    recepta = recipe_name
    tags = content[1][11:]
    author = content[2][7:]
    path = os.path.join("/home/pi/receptari/_recipes/", recipe_name+".md")
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

changes = False
new_image = False
image_name = ''
recepta = ''
email_user = 'carminaruizllaurado@gmail.com'
email_pass = 'ribes2005'
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
    if new_image:
        os.system("mv /home/pi/receptari/images/" + image_name + " /home/pi/receptari/images/" + recepta + image_name[-4:])
    os.system("make")
