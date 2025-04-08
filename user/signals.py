from django.db.models.signals import post_save
from django.dispatch import receiver
from user.models import User
from distributor.models import DistributorCustomer

@receiver(post_save, sender=User)
def assign_customer_to_distributor(sender, instance, created, **kwargs):
    # Check if a new user with the 'Customer' role is created
    if created and instance.role == 'Customer':
        # Ensure the user has a distributor profile
        if instance.distributor_profile:
            # Create the DistributorCustomer relationship
            DistributorCustomer.objects.get_or_create(distributor=instance.distributor_profile, customer=instance)



# distributor/signals.py
