

# XXX: This handler moves spl from SYNC_SCHEDULED to IN_SYNC state
# This logic should be provided in structure workflow and implemented in backend
def sync_service_project_link(sender, instance, created=False, **kwargs):
    if created:
        instance.begin_syncing()
        instance.set_in_sync()
        instance.save()
