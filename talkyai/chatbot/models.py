import hashlib
from django.db import models
from django.conf import settings

class Key(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    hash_key = models.TextField(blank=True, editable=False)
    model_name = models.CharField(max_length=255, default='chatbot')

    def save(self, *args, **kwargs):
        if not self.hash_key:  # Only generate the hash if it hasn't been set
            super().save(*args, **kwargs)  # Save the instance to get the primary key
            self.hash_key = hashlib.sha256(str(self.pk).encode('utf-8')).hexdigest()
            self._meta.model.objects.filter(pk=self.pk).update(hash_key=self.hash_key)
        else:
            super().save(*args, **kwargs)  # For subsequent saves, just save normally

    def __str__(self):
        return f"{self.user.username}'s GROQ Key"

    
    
class Analytics_Of_Bot(models.Model):
    username = models.CharField(max_length=255)
    question = models.TextField()
    response = models.TextField()
    ip_address = models.TextField()
    
class Prompt_Template(models.Model):
    prompt = models.TextField()
    key = models.ForeignKey(Key, on_delete=models.CASCADE)
    key_hash = models.CharField(max_length=64, editable=False)
    instructions = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        # Update key_hash only if it's not set or the key changes
        if not self.key_hash or self.key.hash_key != self.key_hash:
            self.key_hash = self.key.hash_key
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Prompt: {self.prompt} (Key Hash: {self.key_hash})"



class ChatMessage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bot_id = models.TextField()
    message = models.TextField()
    sender = models.CharField(max_length=10)  # 'user' or 'bot'
    timestamp = models.DateTimeField(auto_now_add=True)

    
    def __str__(self):
        return f"{self.user.username} - {self.sender} - {self.timestamp}"


class Chart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    chart_type = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='charts/')

    def __str__(self):
        return f"{self.user.username} - {self.chart_type} - {self.created_at}"
    
    
