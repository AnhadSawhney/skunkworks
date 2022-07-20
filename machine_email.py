import imaplib
from settings import Settings
from transactions import make_transaction

s = Settings()

mail = imaplib.IMAP4_SSL(s.imap_server)
mail.login(s.email_address, s.email_password)

run = True
refresh_rate = 5

def parse_header(data):
    data = data.replace('\r\n ', ' ')
    out = [x.split(':', 1) for x in data.split('\r\n') if x]
    return dict(out)


# write a function to check all the emails in the inbox and print them
def check_inbox():
    mail.select('inbox')
    _, ids = mail.search(None, '(UNSEEN)')
    ids = ids[0].split()
    for id in ids:
        _, data = mail.fetch(id, '(BODY[HEADER])')
        data = data[0][1].decode('utf-8')
        h = parse_header(data)
        #print(h)
        print(h['Subject'])
        print(h['From'])
        print(h['Date'])
        print("-----------------------------------------------------")
        #print(h['Message-ID'])
        #print(h['In-Reply-To'])
        #print(h['References'])
        #print(h['Content-Type'])
        #print(h['Mime-Version'])
        #print(h['Content-Transfer-Encoding'])


def check_venmos():
    mail.select('inbox')
    # _, ids = mail.search(None, '(;[p-?  \\|OM venmo@venmo.com FROM grantmduffy@gmail.com '
    #                            f'SUBJECT "paid you" BODY "{s.user_phrase}" UNSEEN)')
    # this formatted as an IMAP search command
    _, ids = mail.search(None, '(OR FROM venmo@venmo.com OR FROM sawhney.anhad@gmail.com FROM anhad@mit.edu '
                               f'SUBJECT "paid you" UNSEEN)')
    ids = ids[0].split()
    venmos = []
    for id in ids:
        _, data = mail.fetch(id, '(BODY[HEADER])')
        data = data[0][1].decode('utf-8')
        h = parse_header(data)
        actor, amount = h['Subject'].split(' paid you $')
        actor = actor.replace('Fwd: ', '').strip()
        print(actor, amount)
        venmos.append(make_transaction(actor.strip(), float(amount)))
    return venmos

if __name__ == '__main__':
    print("Venmo Payments:")
    check_venmos()
    print("-------------------ALL EMAIL-----------------------------")
    check_inbox()