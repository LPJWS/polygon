from django.conf.urls import url
from django.urls import path
from rest_framework.routers import SimpleRouter

from polygon.views import *

router = SimpleRouter()

urlpatterns = [
    path('signup/', signup),
    path('signin/', signin),
    path('logout/', logout_),
    path('', admin_page),
    path('results/', results),
    path('w_get_pass/', w_get_pass),
    path('w_change_pass/', w_change_pass),
    path('b_get_count/', b_get_count),
    path('b_clear/', b_clear),
    path('accept/', accept),
    path('accept/manual/', accept_manual),
    path('send_flag/<int:task_id>/', send_flag),
    path('results/student/<int:student_id>/', results_student),
    path('results/group/<int:group_id>/', results_group),
    path('results/task/<int:task_id>/', results_task),
    path('report/<int:task_id>/', report),
    # url(r'^auth/registration/$', TokenViewSet.as_view()),
]

urlpatterns += router.urls
