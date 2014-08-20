#! /usr/bin/env python
# -*- coding: utf-8 -*-

import irc.bot
import json
import textwrap
import threading
import urllib
import urllib2
import time
import sys
import os
import ConfigParser
import logging
from urllib2 import HTTPError, URLError
import HTMLParser

irc_bot = None 
vk_bot = None
vk_api = "5.24"

class IrcBot(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nickname, server, port=6667, server_pass = '', deliver_to_irc=True):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port, server_pass)], nickname, nickname)
        self.channel = channel
        self.deliver_to_irc = deliver_to_irc
        logging.info("Initializing irc_bot, parameters: channel = %s, nickname = %s, server = %s, port = %s, deliver_to_irc = %s" % 
                     (channel, nickname, server, str(port), deliver_to_irc))

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.join(self.channel)

    def on_pubmsg(self, c, e):
        if self.deliver_to_irc == True:
            vk_bot.invoke_vk('messages.send', {
                'chat_id' : vk_bot.chat_id,
                'message' : ("%s: %s" % (e.source.nick, e.arguments[0])).encode('utf-8')})

    def send(self, msg):
        self.connection.privmsg(self.channel, msg)

class VkBot(threading.Thread):
    def __init__(self, access_token, chat_id, deliver_to_vk=True):
        super(VkBot, self).__init__()
        self.access_token = access_token
        self.chat_id = chat_id
        self.deliver_to_vk = deliver_to_vk
        logging.info("Initializing vk_bot, parameters: access_token = *****, chat_id = %s, deliver_to_vk = %s" % (chat_id, deliver_to_vk))

    def invoke_vk(self, method, params=dict()):
        #logging.info("invoke_vk. method=%s, params=%s", method, params)
        time.sleep(0.4)
        url = 'https://api.vk.com/method/%s' % method
        constparams = {'v' : vk_api,
                       'access_token' : self.access_token}
        data = urllib.urlencode(dict(constparams.items() + params.items()))
        request = urllib2.Request(url, data)
        response = urllib2.urlopen(request)
        resJson = json.loads(response.read())

        if resJson.get('error') is not None:
            logging.error("Response to VK returned error: %s", resJson['error']['error_msg'])
            logging.info("result=%s", resJson);
            return ""
        return resJson

    def clear_url(self, url):
        result = url
        if '?' in result:
            result = result.split('?')[0]
        return result    
        
    def get_message_details(self, msg_id):
        response = self.invoke_vk('messages.getById', {'message_ids' : msg_id })
        if response['response']['count'] == 0:
            return None
        attachments = list()
        if 'attachments' in response['response']['items'][0]:
            for attach in response['response']['items'][0]['attachments']:
                if attach['type'] == 'photo':
                    for size in (2560, 1280, 807, 604, 130, 75):
                        if "photo_%s" % size in attach['photo']:
                            attachments.append({'url' : attach['photo']["photo_%s" % size]})
                            break
                if attach['type'] == 'audio':
                    attachments.append({'title' : "%s - %s" % (attach['audio']['artist'], attach['audio']['title']),
                                  'url' : self.clear_url(attach['audio']['url'])})
                if attach['type'] == 'wall':
                    attachments.append({'url' : "https://vk.com/wall%s_%s" % (attach['wall']['to_id'], attach['wall']['id'])})
                if attach['type'] == 'video':
                    video_id = "%s_%s" % (attach['video']['owner_id'], attach['video']['id'])
                    video_details = self.invoke_vk('video.get', {'videos' : video_id})
                    if video_details['response']['count'] > 0:
                        attachments.append({'title' : video_details['response']['items'][0]['title']})
                        attachments.append({'url' : video_details['response']['items'][0]['player']})
        return {'user_id' : response['response']['items'][0]['user_id'],
                'attachments' : attachments}

    def get_user_names(self, user_ids):
        response = self.invoke_vk('users.get', {'user_ids' : ','.join(str(x) for x in user_ids), 'name_case' : 'Nom'}) #
        result = dict()
        for user in response['response']:
            result[user['id']] = "%s %s" % (user['first_name'], user['last_name'])
        return result if len(result.items()) > 0 else None

    def load_users(self):
        response = self.invoke_vk('messages.getChat' , {'chat_id' : self.chat_id})
        return self.get_user_names(response['response']['users']) if 'users' in response['response'] else None

    def is_app_user(self, user_id):
        if self.app_user_id is None:
            response = self.invoke_vk('users.isAppUser' , {'user_id' : user_id})
            if int(response['response']) == 1:
                self.app_user_id = user_id
        return user_id == self.app_user_id

    def process_updates(self, updates):
        if len(updates) == 0:
            return
        for update in updates:
            if update[0] == 4 and (int(update[2]) & 0b10 == False):
                details = self.get_message_details(update[1])
                if details is None:
                    return
                user_id = details['user_id']
                if self.is_app_user(user_id):
                    return
                if user_id in self.users:
                    user_name = self.users[user_id]
                    
                    #remove/replace special symbols
                    msg = HTMLParser.HTMLParser().unescape(update[6])
                    msg = msg.replace("<br>", "<br />")
                    name_sent = False
                    for paragraph in msg.split("<br />"):
                        for line in textwrap.wrap(paragraph, 200):
                            if name_sent:
                                irc_bot.send("%s" % line)
                            else:
                                irc_bot.send("%s: %s" % (user_name, line))
                                name_sent = True
                    if 'attachments' in details:
                        for attach in details['attachments']:
                            for key, value in attach.items():
                                if name_sent:
                                    irc_bot.send("[%s] %s" % (key, value))
                                else:
                                    irc_bot.send("%s: [%s] %s" % (user_name, key, value))
                                    name_sent = True


    def get_long_poll_server(self, ts):
        response = self.invoke_vk('messages.getLongPollServer')
        return ("http://%s?act=a_check&key=%s&wait=25&mode=0&ts=%s" % 
                (response['response']['server'],
                 response['response']['key'],
                 response['response']['ts'] if ts == 0 else ts))

    def run(self):
        long_poll_server = None
        self.users = None
        self.app_user_id = None
        while True:
            if self.users is None:
                try:
                    self.users = self.load_users()
                except (HTTPError, URLError):
                    pass
                continue
            
            if long_poll_server is None:
                try:
                    long_poll_server = self.get_long_poll_server(0)
                except (HTTPError, URLError):
                    pass
                continue
            
            try:
                request = urllib2.Request(long_poll_server)
                jsonResponse = urllib2.urlopen(request)
                response = json.loads(jsonResponse.read())
            except (HTTPError, URLError):
                long_poll_server = None
                self.users = None
                continue
            
            if 'failed' in response:
                long_poll_server = None
                continue

            if 'ts' in response:
                ts = response['ts']
                try:
                    if self.deliver_to_vk == True:
                        self.process_updates(response['updates'])
                except (HTTPError, URLError):
                    long_poll_server = None
                    self.users = None
                    continue
                try:
                    long_poll_server = self.get_long_poll_server(ts)
                except (HTTPError, URLError):
                    long_poll_server = None
                    self.users = None

def main():
    global irc_bot, vk_bot, vk_api
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
    config = ConfigParser.SafeConfigParser()
    config_location = "%s/.vk2irc" % os.environ['HOME'] if (len(sys.argv) == 1) else sys.argv[1]
    logging.info("Loading config from %s", config_location)
    config.read(config_location)
    irc_bot = IrcBot("#%s" % config.get('irc_bot', 'channel'),
                    config.get('irc_bot', 'nickname'),
                    config.get('irc_bot', 'server'),
                    config.getint('irc_bot', 'port'),
                    config.get('irc_bot', 'serverpass'),
                    config.getboolean('irc_bot', 'deliver_to_vk'))
    vk_bot = VkBot(config.get('vk_bot', 'access_token'),
                   config.get('vk_bot', 'chat_id'),
                   config.getboolean('vk_bot', 'deliver_to_irc'))
    vk_bot.daemon = True
    vk_bot.start()
    irc_bot.start()

if __name__ == "__main__":
    main()
