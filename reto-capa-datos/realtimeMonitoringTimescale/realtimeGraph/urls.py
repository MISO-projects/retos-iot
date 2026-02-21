from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .views import *

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    path("historical/", HistoricalView.as_view(), name="historical"),
    path("rema/", RemaView.as_view(), name="rema"),
    path("rema/<str:measure>", RemaView.as_view(), name="rema"),
    path("mapJson/", get_map_json, name="mapJson"),
    path("mapJson/<str:measure>", get_map_json, name="mapJson"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("historical/data", download_csv_data, name="historical-data"),
    # Performance comparison API endpoints
    path("api/rollups/", get_rollups, name="api-rollups"),
    path("api/rollups/<str:measure>", get_rollups, name="api-rollups-measure"),
    path("api/daily-extremes/", get_daily_extremes, name="api-daily-extremes"),
    path("api/daily-extremes/<str:measure>", get_daily_extremes, name="api-daily-extremes-measure"),
    path("api/moving-average/", get_moving_average, name="api-moving-average"),
    path("api/moving-average/<str:measure>", get_moving_average, name="api-moving-average-measure"),
    path("api/peak-hours/", get_peak_hours, name="api-peak-hours"),
    path("api/peak-hours/<str:measure>", get_peak_hours, name="api-peak-hours-measure"),
    path("api/histogram/", get_histogram, name="api-histogram"),
    path("api/histogram/<str:measure>", get_histogram, name="api-histogram-measure"),
    path("api/extremes/", get_extremes, name="api-extremes"),
    path("api/extremes/<str:measure>", get_extremes, name="api-extremes-measure"),
]

