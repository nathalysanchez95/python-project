from google.appengine.ext import ndb
import logging

class UserEvent(ndb.Model):
    user_id = ndb.StringProperty()
    autor = ndb.StringProperty()
    mensaje = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)

class UserEventDao(object):
    def evento_agregar_usuarios(self,user_id,autor,mensaje):
        evt = UserEvent()
        evt.user_id = user_id
        evt.autor = autor
        evt.mensaje = mensaje
        evt.put()
        logging.info("Evento ingresado %r",evt)

    def listar_eventos_usuarios(self,user_id):
        evts = UserEvent.query(UserEvent.user_id == user_id).order(UserEvent.date)
        return [(evt.mensaje,evt.autor) for evt in evts]

    def eliminar_evento_usuario(self,user_id):
        evts = UserEvent.query(UserEvent.user_id == user_id)
        cant = evts.count()
        for event in evts:
            event.key.delete()
        logging.info("Se eliminaron %r eventos",cant)

    def existe_mensaje_admin(self,user_id):
        evts = UserEvent.query(UserEvent.user_id == user_id, UserEvent.autor == 'admin')
        return evts.count() > 0
