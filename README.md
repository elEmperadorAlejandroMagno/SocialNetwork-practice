# 📚 Tareas

### Acciones con Javascript y sincronización de servidor

- Follow / Unfollow request
  - Fetch "follow/" (user no puedo hacer follow a sí mismo, si user ya tiene follow a user quitar user)
  - Fetch "unfollow/" (quitar follow de user) [OPCIONAL]
- Like / quitar like request
  - Fetch "like/" (si user ya dio like quitar like)
- edit post
  - Remplazar contenido por textarea y agregar boton de envio

### Templates

- Profile template
  - username
  - number of followers and follows
  - post of user
  - follow or unfollow btn for other users

- All posts
  - username
  - timestamp
  - content
  - likes

- New post
  - within the all post template or in separate template
  - textarea and button to write an create new post

### Pagination with django

- Paginator
  - Server side  (django.core.paginator -> Paginator )
  - Client side (bootstrap pagination)

### Notifications

- Client side:
  - Dropdown with Bootstrap
  - Agregar contador de notificaciones no leídas
  - Update is_read de las notificaciones al hacer :hover sobre la tarjeta de la notificacion
  - Agregar condicionales y estilos manejando el update de is_read
- Server side: 
  - Context Processor: Un context processor es una función que se ejecuta en cada request y agrega datos al contexto de todos los templates.
  - Configuar context processor en settings.py: Templates -> Options -> contest-proccessors
  - Agregar {% url 'post_detail' n.post.id %} post_detail url and template to show post and comments
