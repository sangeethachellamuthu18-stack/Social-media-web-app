from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserRegister(models.Model):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length = 100)
    email = models.CharField(max_length = 100)
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    password = models.CharField(max_length=100)
    first_name = models.CharField(max_length = 100)
    last_name = models.CharField(max_length = 100)
    gender = models.CharField(max_length=10,choices=[
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other')
    ])
    date_of_birth = models.DateField()
    profile_picture = models.ImageField(upload_to = 'profile_picture/', null=True, blank=True)
    bio = models.TextField(max_length=500, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=[
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('banned','Banned')
    ],
    default='active')
    is_verified = models.BooleanField(default=False)

    class Meta:
        db_table = 'user_register'

    def __str__(self):
        return self.username

class Post(models.Model):
    user=models.ForeignKey(UserRegister, on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    media = models.ImageField(upload_to="posts/media/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'posts'

    def __str__(self):
        return f"{self.user.username} - {self.content[:20]}"

class Likes(models.Model):
    user = models.ForeignKey(UserRegister, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'likes'


class Comments(models.Model):
    post = models.ForeignKey(Post, related_name='comments' ,on_delete=models.CASCADE)
    user = models.ForeignKey(UserRegister, on_delete=models.CASCADE)
    comment_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'comments'


class Messages(models.Model):
    id = models.AutoField(primary_key=True)
    sender = models.ForeignKey(
        UserRegister,
        on_delete=models.CASCADE,
        related_name="sent_messages"  # ✅ unique name
    )
    receiver = models.ForeignKey(
        UserRegister,
        on_delete=models.CASCADE,
        related_name="received_messages"  # ✅ unique name
    )
    message_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'messages'

    def __str__(self):
        return f"{self.sender} → {self.receiver}: {self.message_text[:20]}"

class Follow(models.Model):
    follower = models.ForeignKey(
        UserRegister,
        related_name="following_relations",
        on_delete=models.CASCADE
    )
    following = models.ForeignKey(
        UserRegister,
        related_name="follower_relations",
        on_delete=models.CASCADE
    )
    class Meta:
        unique_together = ('follower', 'following')

class Notification(models.Model):
    user = models.ForeignKey("users.UserRegister", on_delete=models.CASCADE, related_name="notifications")
    actor = models.ForeignKey("users.UserRegister", on_delete=models.CASCADE, related_name="actor_notifications",
                              null=True, blank=True)
    type = models.CharField(max_length=50)  # e.g. "like", "comment", "follow"
    reference_id = models.IntegerField(null=True, blank=True)
    status = models.BooleanField(default=False)  # False = unread, True = read
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.actor.username} {self.type} {self.user.username}"