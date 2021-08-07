# encoding: utf-8
import logging

DEFAULT_RESPONSE = u"Disculpa, no entendi ¿Deseas volver a empezar?"
DEFAULT_POSIBLES_RESPUESTAS = [u"SI",u"NO"]

class Bot(object):
    """docstring for Bot."""

    def __init__(self, send_callback, users_dao, arbol):
        self.send_callback = send_callback
        #dao data acces object
        self.users_dao = users_dao
        self.arbol = arbol

    def gestionar(self,user_id, message, admin=False):
        logging.info("Método handel")

        if self.users_dao.existe_mensaje_admin(user_id):
            return

        if admin:
            self.users_dao.evento_agregar_usuarios(user_id,"admin",message)
            return
        # historial en forma de tuplas
        self.users_dao.evento_agregar_usuarios(user_id,"user",message)
        historial = self.users_dao.listar_eventos_usuarios(user_id)
#        historial = [
#            (u"Hola! Por favor selecciona una opción para poder ayudarte.","bot"),
#            (u"Cursos disponibles","user"),
#            (u"Tenemos varios cursos! Todos ellos son muy interesantes y totalmente prácticos. Por favor selecciona la opción que te resulte más interesante.","bot"),
#            (message,"user")
#        ]


        arbol = self.arbol
        nueva_conversacion = True
        reiniciar_bot = False

        for texto, autor in historial:
            bot_resp = True
            logging.info("text %s",texto)
            logging.info("autor %s",autor)
            if autor == 'bot':
                nueva_conversacion = False
                reiniciar_bot = False

                if texto == DEFAULT_RESPONSE:
                    reiniciar_bot = True
                elif 'say' in arbol and texto == arbol['say'] and 'answers' in arbol:
                    arbol = arbol['answers']

            elif autor == 'user':
                if nueva_conversacion:
                    respuesta_bot = arbol['say']
                    posibles_respuestas = arbol['answers'].keys()
                    posibles_respuestas.sort()
                else:
                    if reiniciar_bot:
                        if texto == u'SI':
                            arbol = self.arbol
                            respuesta_bot = arbol['say']
                            posibles_respuestas = arbol['answers'].keys()
                            posibles_respuestas.sort()
                            self.users_dao.eliminar_evento_usuario(user_id)
                            break
                        elif texto == u'NO':
                            bot_resp = False
                            self.users_dao.eliminar_evento_usuario(user_id)
                            continue

                    key = validar_key(texto,arbol)
                    if key is None:
                        respuesta_bot = DEFAULT_RESPONSE
                        posibles_respuestas = DEFAULT_POSIBLES_RESPUESTAS
                    else:
                        arbol = arbol[key]
                        if 'say' in arbol:
                            respuesta_bot = arbol['say']
                        if 'answers' in arbol:
                            posibles_respuestas = arbol['answers'].keys()
                            posibles_respuestas.sort()
                        else:
                            posibles_respuestas = None

        if bot_resp:
            self.send_callback(user_id, respuesta_bot, posibles_respuestas)
            self.users_dao.evento_agregar_usuarios(user_id,"bot",respuesta_bot)

def validar_key(texto, diccionario):
    for clave in diccionario:
        if clave.lower() == texto.lower():
            return clave
    return None
