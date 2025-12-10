from django.test import TestCase, Client
import json

class PostTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Crear un usuario y loguearse
        self.client.post("/register", {
            "username": "test_user", 
            "email": "test@example.com", 
            "password": "testpass", 
            "confirmation": "testpass"
            })
        self.client.post("/register", {
            "username": "usuario_a_seguir", 
            "email": "usuario_a_seguir@email.com",
            "password": "testpass",
            "confirmation": "testpass"
        })
        self.client.login(username="test_user", password="testpass")
        
        # Crear un post primero
        create_response = self.client.post("/post/new_post", {"content": "Contenido original"})
        self.post_id = create_response.json().get("post", {}).get("id")

    def test_post_creation(self):
        response = self.client.post("/post/new_post", {"content": "Hola mundo"})
        self.assertEqual(response.status_code, 200)

    
    def test_post_editing(self):
        # Editar el post
        edit_response = self.client.post("/post/edit", data=json.dumps({
            "post_id": self.post_id, 
            "content": "Contenido editado"
            }), content_type="application/json")
        self.assertEqual(edit_response.status_code, 200)
        self.assertEqual(edit_response.json().get("new_content"), "Contenido editado")

    def test_like_unlike_post(self):
        # Dar like al post
        like_response = self.client.post("/post/like", data=json.dumps({"post_id": self.post_id}), content_type="application/json")
        self.assertEqual(like_response.status_code, 200)
        self.assertEqual(like_response.json().get("action"), "liked")
        
        # Quitar like al post
        unlike_response = self.client.post("/post/like", data=json.dumps({"post_id": self.post_id}), content_type="application/json")
        self.assertEqual(unlike_response.status_code, 200)
        self.assertEqual(unlike_response.json().get("action"), "unliked")

    def test_follow_unfollow_user(self):
        # Seguir a un usuario
        follow_response = self.client.post("/follow", data=json.dumps({"username": "usuario_a_seguir"}), content_type="application/json")
        self.assertEqual(follow_response.status_code, 200)
        self.assertEqual(follow_response.json().get("action"), "followed")
        
        # Dejar de seguir al usuario
        unfollow_response = self.client.post("/follow", data=json.dumps({"username": "usuario_a_seguir"}), content_type="application/json")
        self.assertEqual(unfollow_response.status_code, 200)
        self.assertEqual(unfollow_response.json().get("action"), "unfollowed")

    def test_post_deletion(self):
        # Eliminar el post
        delete_response = self.client.post("/post/delete", data=json.dumps({"post_id": self.post_id}), content_type="application/json")
        self.assertEqual(delete_response.status_code, 200)
        self.assertEqual(delete_response.json().get("status"), "success")
    
