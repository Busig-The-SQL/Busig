from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Agency(models.Model):
    agency_id = models.CharField(max_length=20, primary_key=True)
    agency_name = models.CharField(max_length=100)

    def __str__(self):
        return self.agency_name

    class Meta:
        db_table = "agency"


class Route(models.Model):
    route_id = models.CharField(max_length=12, primary_key=True)
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE)
    route_short_name = models.CharField(max_length=10)
    route_long_name = models.CharField(max_length=100)
    route_type = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(3)]
    )

    def __str__(self):
        return self.route_short_name

    class Meta:
        db_table = "routes"


class Shape(models.Model):
    shape_id = models.CharField(max_length=20)
    shape_pt_lat = models.FloatField()
    shape_pt_lon = models.FloatField()
    shape_pt_sequence = models.IntegerField()
    shape_dist_traveled = models.FloatField()

    class Meta:
        unique_together = (
            ("shape_id", "shape_pt_lat", "shape_pt_lon"),
        )  # Maybe wrong pk
        db_table = "shapes"


class Stop(models.Model):
    stop_id = models.CharField(max_length=20, primary_key=True)
    stop_code = models.CharField(max_length=20)
    stop_name = models.CharField(max_length=100)
    stop_lat = models.FloatField()
    stop_lon = models.FloatField()

    def __str__(self):
        return self.stop_name

    class Meta:
        db_table = "stops"


class Calendar(models.Model):
    service_id = models.CharField(max_length=5, primary_key=True)
    monday = models.BooleanField()
    tuesday = models.BooleanField()
    wednesday = models.BooleanField()
    thursday = models.BooleanField()
    friday = models.BooleanField()
    saturday = models.BooleanField()
    sunday = models.BooleanField()
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        db_table = "calendar"


class CalendarDate(models.Model):
    service = models.ForeignKey(Calendar, on_delete=models.CASCADE)
    date = models.DateField()
    exception_type = models.IntegerField(
        choices=[(1, "Added"), (2, "Removed")],
        validators=[MinValueValidator(1), MaxValueValidator(2)]
    )

    class Meta:
        unique_together = (("service", "date"),)
        db_table = "calendar_dates"


class Trip(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    service = models.ForeignKey(Calendar, on_delete=models.CASCADE)
    trip_id = models.CharField(max_length=20, primary_key=True)
    trip_headsign = models.CharField(max_length=40)
    trip_shortname = models.CharField(max_length=40)
    direction = models.BooleanField()
    block_id = models.CharField(max_length=100)
    shape = models.CharField(max_length=20)

    class Meta:
        db_table = "trips"


class StopTime(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    arrival_time = models.CharField(max_length=8)
    departure_time = models.CharField(max_length=8)
    stop = models.ForeignKey(Stop, on_delete=models.CASCADE)
    stop_sequence = models.IntegerField()
    stop_headsign = models.CharField(max_length=100)
    pickup_type = models.BooleanField()
    drop_off_type = models.BooleanField()
    timepoint = models.BooleanField()

    class Meta:
        db_table = "stop_times"


class RouteIdToName(models.Model):
    route = models.OneToOneField(
        Route,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="route_id_to_name",
    )
    route_short_name = models.CharField(max_length=10)

    class Meta:
        db_table = "route_id_to_name"


class ChosenRoute(models.Model):
    route_short_name = models.CharField(max_length=10, primary_key=True)

    class Meta:
        db_table = "chosen_routes"
