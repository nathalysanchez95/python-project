# encoding: utf-8
import webapp2
import json
import logging
from google.appengine.api import urlfetch
from bot import Bot
import yaml
from userevent import UserEventDao

VERIFY_TOKEN = "facebook_verification_tocken_chatboot"
ACCES_TOKEN = "EAAHUF9XNYqQBAD33tvjsUyOGV6oIDpxRLchZADTND3Dpjs5KRy4WpRF9APFw7qSLT3kxxtlVeCSOShWiC0oZA2ZBdsjR4sm0ZC0b8Ff6ZBhzs8eV8BZB0arwTfJ48SZAip2iMwNkYIPjww71zZBoQU8qVyCkRLIXKGXiRFRpseA9ippc4NFThZCZA2"
class MainPage(webapp2.RequestHandler):
    def __init__(self, request=None, response=None):
        super(MainPage, self).__init__(request,response)
        logging.info("Instanciando Bot")
        arbol = yaml.load(open('tree.yaml'))
        logging.info("Arbol: %r",arbol)
        self.bot = Bot(enviar_mensaje, UserEventDao(), arbol)

    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        mode = self.request.get("hub.mode")
        if mode == "subscribe":
            challenge = self.request.get("hub.challenge")
            verify_token = self.request.get("hub.verify_token")
            if verify_token == VERIFY_TOKEN:
                self.response.write(challenge)
        else:
            self.response.write("OK")
            #self.bot.gestionar(0,"message_text")


    def post(self):
        data = json.loads(self.request.body)
        logging.info("Data obtenida desde Messenger: %r",data)

        if data["object"] == "page":

            for entry in data["entry"]:
                for messaging_event in entry["messaging"]:
                    sender_id = messaging_event["sender"]["id"]
                    recipient_id = messaging_event["recipient"]["id"]

                    if messaging_event.get("message"):
                        admin =False
                        message = messaging_event['message']
                        if message.get("is_echo"):
                            if message.get('app_id'): #bot
                                continue
                            else:
                                admin = True

                        message_text = messaging_event['message'].get('text','')
                        logging.info("Mensaje obtenido %s",message_text)
                        #enviar_mensaje(sender_id,"Hola soy un Bot en que te puedo ayudar")

                        if admin:
                            user_id = recipient_id
                        else:
                            user_id = sender_id

                        self.bot.gestionar(user_id,message_text,admin)

                    if messaging_event.get("postback"):
                        message_text = messaging_event['postback']['payload']
                        #enviar_mensaje(sender_id,"Hola soy un Bot en que te puedo ayudar")
                        self.bot.gestionar(sender_id,message_text)
                        logging.info("Post-back: %s",message_text)

def enviar_mensaje(id_recip, text_mensaje, posibles_respuestas):
   logging.info("Enviando mensaje a %r: %s",id_recip,text_mensaje)
   headers = {
       "Content-Type": "application/json"
   }
   #message = {"text": text_mensaje}
   #posibles_respuestas = ["Opcion A", "Opcion B", "Opcion C"]
   message = get_postback_buttons_mensaje(text_mensaje, posibles_respuestas)
   if message is None:
       message = {"text": text_mensaje}

   raw_data = {
       "recipient":{
           "id": id_recip
       },
       "message": message
   }
   data = json.dumps(raw_data)

   logging.info("Enviando mensaje a %r: %s",id_recip,text_mensaje)
   r = urlfetch.fetch("https://graph.facebook.com/v11.0/me/messages?access_token=%s" % ACCES_TOKEN,
                       method=urlfetch.POST, headers = headers, payload = data)
   if r.status_code != 200:
       logging.error("Error %r al enviar el mensaje: %s", r.status_code, r.content)

def get_postback_buttons_mensaje(text_mensaje,posibles_respuestas):
    if posibles_respuestas is None or len(posibles_respuestas) > 3:
        return None

    botones = []
    for respuesta in posibles_respuestas:
        botones.append({
           "type": "postback",
           "title": respuesta,
           "payload": respuesta
        })

    return {
             "attachment":{
                 "type": "template",
                 "payload": {
                     "template_type": "button",
                     "text": text_mensaje,
                     "buttons": botones
                 }
             }
       }

#Class de politica de privacidad requerimiento de facebook
class PagPoliticaPrivacidad(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        htmlCont = open('politica_privacidad.html').read()
        self.response.write(htmlCont)
            #self.bot.gestionar(0,"message_text")



app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/politica_privacidad',PagPoliticaPrivacidad)
], debug=True)
