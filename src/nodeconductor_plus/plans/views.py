from rest_framework import viewsets, permissions

import models
import serializers


class PlanViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Plan.objects.all()
    serializer_class = serializers.PlanSerializer
    lookup_field = 'uuid'
    permission_classes = (permissions.IsAuthenticated,)
