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
        create_post_response = self.client.post("/post/new_post", {"content": "Contenido original"}, content_type="application/json")
        self.post_id = create_post_response.json().get("new_post", {}).get("id")

        create_comment_response = self.client.post("/post/new_comment", data=json.dumps({
            "post_id": self.post_id, 
            "content": "Este es un comentario"
            }), content_type="application/json")
        
        self.comment_id = create_comment_response.json().get("new_comment", {}).get("id")


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
        like_response = self.client.post("/post/like", data=json.dumps({
            "post_id": self.post_id, 
            "content_type": "post"
            }), content_type="application/json")
        self.assertEqual(like_response.status_code, 200)
        self.assertEqual(like_response.json().get("action"), "liked")
        
        # Quitar like al post
        unlike_response = self.client.post("/post/like", data=json.dumps({
            "post_id": self.post_id, 
            "content_type": "post"
            }), content_type="application/json")
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

    def test_create_comment(self):
        # Crear un comentario
        comment_response = self.client.post("/post/new_comment", data=json.dumps({
            "post_id": self.post_id, 
            "content": "Este es un comentario"
            }), content_type="application/json")
        self.assertEqual(comment_response.status_code, 200)
        self.assertEqual(comment_response.json().get("status"), "success")

    def test_like_unlike_comment(self):
        # Dar like al comentario        
        like_reponse = self.client.post("/post/comment/like", data=json.dumps({
            "comment_id": self.comment_id, 
            "content_type": "comment"
            }), content_type="application/json")
        self.assertEqual(like_reponse.status_code, 200)
        self.assertEqual(like_reponse.json().get("action"), "liked")

        # Quitar like al comentario
        unlike_response = self.client.post('/post/comment/like', data=json.dumps({
            'comment_id': self.comment_id,
            'content_type': 'comment'
        }), content_type='application/json')
        self.assertEqual(unlike_response.status_code, 200)
        self.assertEqual(unlike_response.json().get('action'), 'unliked')

    def test_post_deletion(self):
        # Eliminar el post
        delete_response = self.client.post("/post/delete", data=json.dumps({"post_id": self.post_id}), content_type="application/json")
        self.assertEqual(delete_response.status_code, 200)
        self.assertEqual(delete_response.json().get("status"), "success")
    
