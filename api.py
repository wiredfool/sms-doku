import web
import so
import twilio.rest

from config import *

urls = (
    '/', 'ping', 
    '/solve', 'solve',
    '/solve_sms', 'solve_sms',
#    '/hint', 'hint'
)

app = web.application(urls, globals())

class ping(object):
    def GET(self):
        return self.usage

    def POST(self):
        return self.usage

    usage = """<pre>Soduku solver: POST your board to /solve:
....3....
2.......3
..52.86..
...4.1...
.946.753.
..6...8..
.57.2.46.
..3...7..
.825.439.

returns

841936257
269745183
735218649
328451976
194687532
576392814
957123468
413869725
682574391

"""

client = twilio.rest.TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)

class solve (object):
    def POST(self):
        data = web.data()
        #print data
        b = so.board(data)
        if b.solve(10):
            return b.dump()
        return "Sorry No Solution Found"


class solve_sms(object):
    def POST(self):
        replyto = None
        try:
            data = web.input()
            replyto = data.From
            if data.Body:
                data = data.Body
            else:
                return "Sorry, no body"
        except:
            return "Sorry, Couldn't find the data"
        print data
        b = so.board(data)
        if b.solve(10):
            print b.dump()
            if replyto:
                msg = client.messages.create(from_=PHONE_NUM, to=replyto, body=b.dump())
                print "sent message: %s" % msg.sid
        else:
            msg = client.messages.create(from_=PHONE_NUM, to=replyto, body="Sorry, no solution found")
            print "sent message: %s" % msg.sid
        return "Sorry No Solution Found"



if __name__=='__main__':
    web.config.debug = False
    app.run()
