import web
import cgi
import so
import twilio.rest

from config import *

urls = (
    '/', 'ping', 
    '/solve', 'solve',
    '/sms', 'sms',
    '/hint', 'hint'
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

or sms to %s:
help, 

solve
....3....
2.......3
..52.86..
...4.1...
.946.753.
..6...8..
.57.2.46.
..3...7..
.825.439.

or 
hint 
....3....
2.......3
..52.86..
...4.1...
.946.753.
..6...8..
.57.2.46.
..3...7..
.825.439.
 
</pre>
""" % PHONE_NUM

client = twilio.rest.TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)

class solve(object):
    def POST(self):
        data = web.data()
        #print data
        b = so.board(data)
        if b.solve():
            return b.dump()
        return "Sorry, No Solution Found"

class hint(object):
    def POST(self): 
        data = web.data()
        b = so.board(data)
        cell = b.hint()
        if cell:
            return self.reply("Try %d at row %d and column %d" % (cell.val, 
                                                                  cell.row +1, 
                                                                  cell.col +1))
        return "Sorry, No Solution Found"


class sms(object):
    
    def reply_old(self, to, body):
        msg = client.messages.create(from_=PHONE_NUM, to=to, body=body)
        print "sent message: %s" % msg.sid

    def reply(self, body):
        web.header('Content-Type', 'text/xml')
        return """<?xml version="1.0" encoding="UTF-8" ?>
<Response>
    <Message>%s</Message>
</Response>""" % cgi.escape(body)


    def help(self):
        return self.reply("""Text for a solution or a hint:
solve|hint
....3....
2.......3
..52.86..
...4.1...
.946.753.
..6...8..
.57.2.46.
..3...7..
.825.439.
Dots or spaces for unknowns""")

    def solve(self, data):
        b = so.board(data)
        if b.solve():
            return self.reply("\n"+b.dump())
        return self.reply("Sorry, no solution found")

    def hint(self, data): 
        b = so.board(data)
        cell = b.hint()
        if cell:
            return self.reply("Try %d at row %d and column %d" % (cell.val, 
                                                                  cell.row +1, 
                                                                  cell.col +1))
        return self.reply("Sorry, didn't find a solution")
                              

    def POST(self):
        try:
            data = web.input()
            replyto = data.From
            if data.Body:
                data = data.Body.lower()
            else:
                return "Sorry, no body"
        except:
            return "Sorry, Couldn't find the data"
        print replyto, data
        
        if 'solve' in data:
            return self.solve(data.replace('solve','').lstrip())
        if 'help' in data or 'usage' in data:
            return self.help()
        if 'hint' in data: 
            return self.hint(data.replace('hint','').lstrip())
        # fall through
        return self.solve(data)

if __name__=='__main__':
    web.config.debug = False
    app.run()
