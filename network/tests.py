from django.test import TestCase, Client

class PostTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_post_creation(self):
        self.client.post("/register", {
            "username": "usuario_a_seguir", 
            "email": "usuario_a@seguir.com", 
            "password": "testpass", 
            "confirmation": "testpass"
            })
        self.client.login(username="usuario_a_seguir", password="testpass")

        response = self.client.post("/post/new_post", {"content": "Hola mundo"})
        self.assertEqual(response.status_code, 200)

    
    def test_post_editing(self):
        # Crear un usuario y loguearse
        self.client.post("/register", {
            "username": "test_user", 
            "email": "test@example.com", 
            "password": "testpass", 
            "confirmation": "testpass"
            })
        self.client.login(username="test_user", password="testpass")
        
        # Crear un post primero
        create_response = self.client.post("/post/new_post", {"content": "Contenido original"})
        post_id = create_response.json().get("post_id")
        
        # Editar el post
        edit_response = self.client.post("/post/edit", {
            "post_id": post_id, 
            "content": "Contenido editado"
            })
        self.assertEqual(edit_response.status_code, 200)
        self.assertEqual(edit_response.json().get("new_content"), "Contenido editado")

    def test_like_unlike_post(self):
        # Crear un usuario y loguearse
        self.client.post("/register", {
            "username": "like_test_user", 
            "email": "liketest@example.com", 
            "password": "testpass", 
            "confirmation": "testpass"
            })
        self.client.login(username="like_test_user", password="testpass")
        
        # Crear un post primero
        create_response = self.client.post("/post/new_post", {"content": "Post para like"})
        post_id = create_response.json().get("post_id")
        
        # Dar like al post
        like_response = self.client.post("/like", {"post_id": post_id})
        self.assertEqual(like_response.status_code, 200)
        self.assertEqual(like_response.json().get("action"), "liked")
        
        # Quitar like al post
        unlike_response = self.client.post("/like", {"post_id": post_id})
        self.assertEqual(unlike_response.status_code, 200)
        self.assertEqual(unlike_response.json().get("action"), "unliked")

    def test_follow_unfollow_user(self):
        # Crear usuario a seguir
        self.client.post("/register", {
            "username": "usuario_a_seguir", 
            "email": "usuario_a@seguir.com", 
            "password": "testpass", 
            "confirmation": "testpass"
            })
        # Crear usuario que va a seguir
        self.client.post("/register", {
            "username": "usuario_follower", 
            "email": "usuario_follower@example.com", 
            "password": "testpass", 
            "confirmation": "testpass"
            })
        self.client.login(username="usuario_follower", password="testpass")
        
        # Seguir a un usuario
        follow_response = self.client.post("/follow", {"username": "usuario_a_seguir"})
        self.assertEqual(follow_response.status_code, 200)
        self.assertEqual(follow_response.json().get("action"), "followed")
        
        # Dejar de seguir al usuario
        unfollow_response = self.client.post("/follow", {"username": "usuario_a_seguir"})
        self.assertEqual(unfollow_response.status_code, 200)
        self.assertEqual(unfollow_response.json().get("action"), "unfollowed")

    
