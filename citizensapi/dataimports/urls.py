from django.urls import path

from .apiviews import DataImportCitizens, PatchCitizens, GetCitizensBirthdays, GetStats


urlpatterns = [
    path('imports/<int:pk>/towns/stat/percentile/age', GetStats.as_view()),
    path('imports/<int:pk>/towns/stat/percentile/age/', GetStats.as_view()),
    path('imports/<int:import_pk>/citizens/<int:citizen_pk>', PatchCitizens.as_view()),
    path('imports/<int:import_pk>/citizens/<int:citizen_pk>/', PatchCitizens.as_view()),
    path('imports/<int:pk>/citizens/birthdays', GetCitizensBirthdays.as_view()),
    path('imports/<int:pk>/citizens/birthdays/', GetCitizensBirthdays.as_view()),
    path('imports/<int:pk>/citizens', DataImportCitizens.as_view()),
    path('imports/<int:pk>/citizens/', DataImportCitizens.as_view()),
    path('imports', DataImportCitizens.as_view()),
    path('imports/', DataImportCitizens.as_view()),
]