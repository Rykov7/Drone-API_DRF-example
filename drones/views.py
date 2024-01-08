from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.throttling import ScopedRateThrottle

from django_filters import AllValuesFilter, DateTimeFilter, NumberFilter, FilterSet

from drones import custompermission
from drones.models import Drone, DroneCategory, Pilot, Competition
from drones.serializers import DroneCategorySerializer, DroneSerializer, PilotSerializer, PilotCompetitionSerializer


class DroneCategoryList(generics.ListCreateAPIView):
    queryset = DroneCategory.objects.all()
    serializer_class = DroneCategorySerializer
    name = 'dronecategory-list'
    filterset_fields = ("name",)
    search_fields = ("^name",)
    ordering_fields = ("name",)


class DroneCategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = DroneCategory.objects.all()
    serializer_class = DroneCategorySerializer
    name = 'dronecategory-detail'


class DroneList(generics.ListCreateAPIView):
    throttle_scope = 'drones'
    throttle_classes = (ScopedRateThrottle,)
    queryset = Drone.objects.all()
    serializer_class = DroneSerializer
    name = 'drone-list'
    filterset_fields = ('name', 'drone_category', 'manufacturing_date', 'has_it_competed',)
    search_fields = ("^name",)
    ordering_fields = ("name", "manufacturing_date")
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, custompermission.IsCurrentUserOwnerOrReadOnly)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class DroneDetail(generics.RetrieveUpdateDestroyAPIView):
    throttle_scope = 'drones'
    throttle_classes = (ScopedRateThrottle,)
    queryset = Drone.objects.all()
    serializer_class = DroneSerializer
    name = 'drone-detail'
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, custompermission.IsCurrentUserOwnerOrReadOnly)


class PilotList(generics.ListCreateAPIView):
    throttle_scope = 'pilots'
    throttle_classes = (ScopedRateThrottle,)
    queryset = Pilot.objects.all()
    serializer_class = PilotSerializer
    name = 'pilot-list'
    filterset_fields = ('name', 'gender', 'races_count')
    search_fields = ("^name",)
    ordering_fields = ("name", "races_count")
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)


class PilotDetail(generics.RetrieveUpdateDestroyAPIView):
    throttle_scope = 'pilots'
    throttle_classes = (ScopedRateThrottle,)
    queryset = Pilot.objects.all()
    serializer_class = PilotSerializer
    name = 'pilot-detail'
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)


class CompetitionFilter(FilterSet):
    from_achievement_date = DateTimeFilter(field_name="distance_achievement_date", lookup_expr='gte')
    to_achievement_date = DateTimeFilter(field_name="distance_achievement_date", lookup_expr='lte')
    min_distance_in_meters = NumberFilter(field_name="distance_in_meters", lookup_expr='gte')
    max_distance_in_meters = NumberFilter(field_name="distance_in_meters", lookup_expr='lte')
    drone_name = AllValuesFilter(field_name='drone__name')
    pilot_name = AllValuesFilter(field_name='pilot__name')

    class Meta:
        model = Competition
        fields = ('from_achievement_date',
                  'to_achievement_date',
                  'min_distance_in_meters',
                  'max_distance_in_meters',
                  # drone__name will be accessed as drone_name
                  'drone_name',
                  # pilot__name  will be accessed as pilot_name
                  'pilot_name')


class CompetitionList(generics.ListCreateAPIView):
    queryset = Competition.objects.all()
    serializer_class = PilotCompetitionSerializer
    name = 'competition-list'
    filterset_class = CompetitionFilter
    ordering_fields = ('distance_in_meters', 'distance_achievement_date')


class CompetitionDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Competition.objects.all()
    serializer_class = PilotCompetitionSerializer
    name = 'competition-detail'


class ApiRoot(generics.GenericAPIView):
    name = 'api-root'

    def get(self, request, *args, **kwargs):
        return Response({
            'drone-categories': reverse(DroneCategoryList.name, request=request),
            'drones': reverse(DroneList.name, request=request),
            'pilots': reverse(PilotList.name, request=request),
            'competitions': reverse(CompetitionList.name, request=request),
        })
