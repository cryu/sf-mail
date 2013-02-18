from starflyer import Module
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

    def __init__(self, printout=True, *args, **kwargs):
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
        print "SENDING", m
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
        self.port = port

    def __call__(self):
        return smtplib.SMTP(self.host, self.port)

class DummyServerFactory(object):
    """a factory for creating smtp servers"""

    def __call__(self):
        return DummyServer()


class Mail(Module):
    """a mail module for starflyer which supports txt and html mailing
    """

    name = "mail"

    defaults = {
        'dummy'             : False,                # use dummy mailer?
        'host'              : "localhost",          # host to connect to
        'port'              : 25,                   # port to use
        'encoding'          : "utf-8",
        'from_addr'         : "noreply@example.org",
        'from_name'         : "System",
    }

    config_types = {
        'debug' : bool,
        'port' : int,
    }

    def finalize(self):
        """finalize the setup"""
        cfg = self.config
        if cfg.has_key("server_factory"):
            self.server_factory = cfg.server_factory
        elif cfg.debug:
            self.server_factory = DummyServerFactory()
        else:
            self.server_factory = SMTPServerFactory(cfg.host, cfg.port)

    def mail(self, to, subject, msg_txt, from_addr=None, from_name = None, encoding = None, 
                headers = {}, cc = [], bcc = [], **kw):
        """send a plain text email

        :param to: a simple string in RFC 822 format
        :param subject: The subject of the email
        :param msg_txt: The actual text of the message 
        :param tmplname: template name to be used
        :param encoding: optional encoding to use (if None it will default to configured encoding which defaults to utf-8)
        :param cc: list of email addresses to CC the mail to
        :param bcc: list of email addresses to BCC the mail to
        :param **kw: parameters to be used in the template
        """

        # render template
        # now create the message
        msg = Message()
        enc = self.config.encoding
        if encoding is not None:
            enc = encoding
        msg.set_payload(msg_txt.encode(enc))
        msg.set_charset(enc)
        msg['Subject'] = Header(subject, enc)
        if from_name is None:
            from_name = self.config.from_name
        if from_addr is None:
            fa = msg['From'] = "%s <%s>" %(from_name, self.config.from_addr)
        else:
            fa = msg['From'] = "%s <%s>" %(from_name, from_addr)
        msg['To'] = to
        if len(cc)>0:
            msg['CC'] = ",".join(cc)
        # set additional headers
        for k,v in headers.items():
            if k in msg:
                del msg[k]
            msg[k] = v

        server = self.server_factory()
        server.sendmail(fa, [to] + cc + bcc, msg.as_string())
        server.quit()


    def mail_html(self, to, subject, msg_txt, msg_html, from_addr=None, from_name = None, **kw):
        """send a HTML and plain text email

        :param to: a simple string in RFC 822 format
        :param subject: The subject of the email
        :param tmplname_txt: template name to be used for the plain text version (not used if None)
        :param tmplname_html: template name to be used for the HTML version (not used if None)
        :param **kw: parameters to be used in the templates
        """

        # now create the message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = Header(subject, self.config.encoding)
        if from_name is None:
            from_name = self.config.from_name
        if from_addr is None:
            fa = msg['From'] = "%s <%s>" %(from_name, self.config.from_addr)
        else:
            fa = msg['From'] = "%s <%s>" %(from_name, from_addr)
        msg['To'] = to
        
        part1 = MIMEText(msg_txt.encode(self.config.encoding), 'plain', self.config.encoding)
        part2 = MIMEText(msg_html.encode(self.config.encoding), 'html', self.config.encoding)
        
        msg.attach(part1)
        msg.attach(part2)
       
        server = self.server_factory()
        server.sendmail(fa, [to], msg.as_string())
        server.quit()

mail_module = Mail(__name__)


