import logging, signal, sys, time
import json, sleekxmpp

class MapperXMPP(sleekxmpp.ClientXMPP):

  def __init__(self, jid, password):
    sleekxmpp.ClientXMPP.__init__(self, jid, password)
    self.register_plugin('xep_0004') # Data forms
    self.register_plugin('xep_0030') # Service discovery
    self.register_plugin('xep_0045') # Multi-user chat
    self.register_plugin('xep_0060') # Publish subscribe
    self.register_plugin('xep_0199') # XMPP ping
    self.register_plugin('xep_0203') # Delayed delivery
    self.add_event_handler("session_start", self.handle_start)
    self.add_event_handler("message", self.handle_message)

    self.sources = {}
    self.groups = {}

  def handle_start(self, event):
    logging.info("connected")
    print "connected"
    self.get_roster()
    self.send_presence(pstatus="")

  def handle_message(self, message):
    logging.info(message)
    print message
    delay = message["delay"].get_stamp()
    if delay is None: # process only if it isn't an offline message
      try:
        jbody = json.loads(message["body"])
        func = getattr(self, "hnd_" + jbody["func"]) # gets reference for the application function
        args = jbody["args"] # application arguments
        head = {'from':str(message["from"]), 'to':str(message["to"])} # header arguments
        func(head, args)
      except:
        logging.warning("message error")
    # self.make_message(mto=message["from"], mbody=message["body"]).send()

  '''
  LISTENERS 
  '''
 
  def hnd_stream_init(self, head, args):
    logging.info("stream_init")
    print "hnd_called"
    print args
    print args["hashtags"]
    try:
      if args["group_jid"] is not None:
        source = head['from'].split("@")[0]
        group = args['group_jid']
        print "if" , source
        if self.sources.has_key(source):
          self.sources[source] = {}
        print "endif"
        self.sources[source]['latlng'] = None
        self.sources[source]['hashtags'] = args['hashtags']
        self.sources[source]['group'] = args['group_jid']
        print source , " initiated"
      
        if self.groups.has_key(group):
          self.groups[group] = {}
        self.groups[group]['members'] = []
        self.groups[group]['members'].append(source)
        print group , " created"
    except:
      print sys.exc_info()

  def hnd_stream_pause(self, head, args):
    logging.info("stream_pause")

  def hnd_stream_resume(self, head, args):
    logging.info("stream_resume")

  def hnd_stream_close(self, head, args):
    logging.info("stream_close")
    # leave current group

  def hnd_stream_exists(self, head, args):
    logging.info("stream_exists")

  def hnd_group_join(self, head, args):
    logging.info("group_join")
    # leave current group and join selected/existing group

  def hnd_group_leave(self, head, args):
    logging.info("group_leave")
    # leave current group and create group

  def hnd_group_match(self, head, args):
    logging.info("group_match")
    # find groups matching geolocation + hashtags

  def hnd_update_context(self, head, args):
    logging.info("update_context")
    # publish current geolocation + sensor data + battery level

  def hnd_update_hashtags(self, head, args):
    logging.info("update_hashtags")
    # publish hashtag update

  '''
  MESSAGES
  '''
  
'''
CONSOLE
'''

def signal_handler(signal, frame):
  client.disconnect(wait=True)
  sys.exit(0)

client = None

def main(argv):
  signal.signal(signal.SIGINT, signal_handler)
  
  logging.basicConfig(filename='mapper_xmpp.log',level=logging.DEBUG)
  logging.info("mapper started")
  
  global client

  jid = "comp-mapper@localhost"
  pwd = "123"

  client = MapperXMPP(jid, pwd)
  client.connect()
  client.process()

  while True:
    pass

if __name__ == '__main__':
  main(sys.argv[1:])
