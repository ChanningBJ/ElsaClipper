# import smtpd
# import asyncore

# class CustomSMTPServer(smtpd.SMTPServer):
    
#     def process_message(self, peer, mailfrom, rcpttos, data):
#         print 'Receiving message from:', peer
#         print 'Message addressed from:', mailfrom
#         print 'Message addressed to  :', rcpttos
#         print 'Message length        :', len(data)
#         return

# server = CustomSMTPServer(('127.0.0.1', 1025), None)

# asyncore.loop()


from inbox import Inbox

inbox = Inbox()

@inbox.collate
def handle(to, sender, subject, body):
    print sender
    print to
    print subject
    print body

# Bind directly.
inbox.serve(address='0.0.0.0', port=465)
