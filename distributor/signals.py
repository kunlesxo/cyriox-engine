from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from  .models import Distributor

User = get_user_model()

@receiver(post_save, sender=Distributor)
def create_distributor_user(sender, instance, created, **kwargs):
    if created:
        # Create a user automatically for this distributor
        user = User.objects.create(
            username=instance.name.lower().replace(" ", "_"),
            email=f"{instance.name.lower().replace(' ', '_')}@distributors.com",
            role=User.ROLE.DISTRIBUTOR,
        )
        # Optionally, set the password (for now, randomly or to something default)
        user.set_password("defaultpassword123")  # You can use a secure default
        user.save()

        # Link the user to the distributor (via ForeignKey if you want)
        instance.user = user
        instance.save()
