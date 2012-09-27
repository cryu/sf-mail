from starflyer import Module, AttributeMapper
import urlparse
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.charset import Charset, QP
from email.message import Message
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import email


__all__ = ['Mail', 'mail_module']

class DummyServer(object):
    """a dummy mailer which does not send but stores mail. Can be used for testing"""

    def __init__(self, printout=False, *args, **kwargs):
        """initialize the dummy mail server"""
        self.mails = []
        self.printout = printout

    def connect(self, *args, **kwargs):
        pass

    def quit(self, *args, **kwargs):
        pass

    def sendmail(self, from_addr, to, msg):
        """send the mail means storing it in the list of mails"""
        m = {
            'from': from_addr,
            'to' : to,
            'msg' : msg
        }
        self.mails.append(m) # msg actually contains everything
        if self.printout:
            print "--------"
            print "To: ", to
            msg = email.message_from_string(msg)
            for part in msg.walk():
                print 1, part.get_payload(decode=True), 2
            print "--------"


class SMTPServerFactory(object):
    """a factory for creating smtp servers"""

    def __init__(self, host, port):
        self.host = host
        self.port

    def __call__(self):
        return smtplib.SMTPServer(self.host, self.port)

class DummyServerFactory(object):
    """a factory for creating smtp servers"""

    def __call__(self):
        return DummyServer()



class Mail(Module):
    """a mail module for starflyer which supports txt and html mailing
    """

    name = "mailer"

    defaults = {
        'dummy'             : False,                # use dummy mailer?
        'host'              : "localhost",          # host to connect to
        'port'              : 22,                   # port to use
    }

    def finalize(self):
        """finalize the setup"""
        cfg = self.config
        if cfg.debug:
            self.mail_factory = DummyServerFactory()
        else:
            self.mail_factory = SMTPServerFactory(cfg.host, cfg.port)

    def mail(self, to, subject, msg, from_addr=None, from_name = None, **kw):
        """send a plain text email

        :param to: a simple string in RFC 822 format
        :param subject: The subject of the email
        :param msg: The actual text of the message 
        :param tmplname: template name to be used
        :param **kw: parameters to be used in the template
        """

        # render template
        # now create the message
        msg = Message()
        msg.set_payload(payload.encode("utf8"))
        msg.set_charset(self.charset)
        msg['Subject'] = Header(subject, "utf8")
        if from_name is None:
            from_name = self.from_name
        if from_addr is None:
            fa = msg['From'] = "%s <%s>" %(from_name, self.from_addr)
        else:
            fa = msg['From'] = "%s <%s>" %(from_name, from_addr)
        msg['To'] = to

        server = self.server_factory()
        server.sendmail(fa, [to], msg.as_string())
        server.quit()


    def mail_html(self, to, subject, tmplname_txt, tmplname_html, from_addr=None, from_name = None, **kw):
        """send a HTML and plain text email

        :param to: a simple string in RFC 822 format
        :param subject: The subject of the email
        :param tmplname_txt: template name to be used for the plain text version (not used if None)
        :param tmplname_html: template name to be used for the HTML version (not used if None)
        :param **kw: parameters to be used in the templates
        """

        # render template
        tmpl_txt = self.templates.get_template(tmplname_txt)
        tmpl_html = self.templates.get_template(tmplname_html)
        payload_txt = tmpl_txt.render(kw)
        payload_html = tmpl_html.render(kw)
        
        # now create the message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = Header(subject, "utf8")
        if from_name is None:
            from_name = self.from_name
        if from_addr is None:
            fa = msg['From'] = "%s <%s>" %(from_name, self.from_addr)
        else:
            fa = msg['From'] = "%s <%s>" %(from_name, from_addr)
        msg['To'] = to
        
        part1 = MIMEText(payload_txt.encode('utf-8'), 'plain', 'utf-8')
        part2 = MIMEText(payload_html.encode('utf-8'), 'html', 'utf-8')
        
        msg.attach(part1)
        msg.attach(part2)
        
        server = self.server_factory()
        server.sendmail(fa, [to], msg.as_string())
        server.quit()

mail_module = Mail(__name__)


