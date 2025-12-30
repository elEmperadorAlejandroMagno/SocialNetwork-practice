from ..model.network_model import NetworkModel
from ..models import User


class NetworkController:
    @staticmethod
    def get_all_posts(user: User, filter: str|None = None):
        return NetworkModel.get_all_posts(user, filter)
    
    @staticmethod
    def get_all_following_posts(user: User):
        return NetworkModel.get_all_following_posts(user)
    
    @staticmethod
    def get_slice_posts(user: User, starts: int, ends: int):
        return NetworkModel.get_slice_posts(user, starts, ends)
    
    @staticmethod
    def get_user_posts(user: User):
        return NetworkModel.get_user_posts(user)
    
    @staticmethod
    def get_post_by_id(user: User, post_id: int):
        return NetworkModel.get_post_by_id(user, post_id)
    
    @staticmethod
    def create_new_post(user: User, content: str):
        return NetworkModel.create_new_post(user, content)
    
    @staticmethod
    def update_post(post_id: int, new_content: str):
        return NetworkModel.update_post(post_id, new_content)
    
    @staticmethod
    def del_post(user: User, post_id: int):
        return NetworkModel.del_post(user, post_id)
    
    @staticmethod
    def toggle_like(user: User, content_type: str, object_id: int):
        return NetworkModel.toggle_like(user, content_type, object_id)
    
    @staticmethod    
    def toggle_follow(follower: User, username_to_follow: str):
        return NetworkModel.toggle_follow(follower, username_to_follow)
    
    @staticmethod
    def post_comment(user: User, post_id: int, content: str):
        return NetworkModel.post_comment(user, post_id, content)

    @staticmethod
    def del_comment(user: User, comment_id: int):
        return NetworkModel.del_comment(user, comment_id)
    
    @staticmethod
    def mark_notifications_as_read(user: User, notif_id: int):
        return NetworkModel.mark_notifications_as_read(user, notif_id)