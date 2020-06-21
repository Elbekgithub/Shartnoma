from django.urls import path
from .import views

urlpatterns = [
	path('', views.home, name="home"),

	path('groups/', views.group_list, name='group_list'),
	path('groups/add/new/', views.GroupAddView.as_view(), name='add_new_group'),
	path('group/delete/<int:pk>/', views.group_delete, name="group_delete"),
	path('group/edit/<int:pk>/', views.group_edit, name="group_edit"),
	path('group/<int:pk>/students/', views.group_students, name="group_students"),

	path('shartnoma/', views.shartnoma_list_view, name="manage_shartnoma"),
	path('shartnoma/add/new', views.shartnoma_add_view, name="create_new_shartnoma"),
	path('shartnoma/edit/<int:pk>/', views.shartnoma_update_view, name="edit_shartnoma"),
	path('shartnoma/delete/<int:pk>/', views.shartnoma_delete_view, name="delete_shartnoma"),
	path('shartnoma/payment/add/new', views.payment_add_view, name="create_new_payment"),
	path('shartnoma/payment/edit/<int:pk>/', views.shartnoma_update_view, name="edit_payment"),

	#path('score/', views.add_score, name='add_score'),
	#path('score/<int:id>/', views.add_score_for, name='add_score_for'),
	
	path('profile/', views.profile, name='profile'),
	path('profile/view/<int:id>/', views.user_profile, name='user_profile'),
	path('profile/edit/', views.profile_update, name='edit_profile'),
	
	path('staff/', views.staff_list, name="staff_list"),
	path('staff/add/new/', views.StaffAddView.as_view(), name="add_new_staff"),
	path('staff/edit/<int:pk>/', views.edit_staff, name="edit_staff"),
	path('staff/delete/<int:pk>/', views.delete_staff, name="delete_staff"),
	
	
	path('students/', views.student_list, name="student_list"),
	path('student/add/new/', views.StudentAddView.as_view(), name="add_new_student"),
	path('student/delete/<int:pk>/', views.delete_student, name="delete_student"),
	path('student/edit/<int:pk>/', views.edit_student, name="edit_student"),
	
	path('session/', views.session_list_view, name="manage_session"),
	path('session/add/new', views.session_add_view, name="create_new_session"),
	path('session/edit/<int:pk>/', views.session_update_view, name="edit_session"),
	path('session/delete/<int:pk>/', views.session_delete_view, name="delete_session"),
	
	path('semester/', views.semester_list_view, name="manage_semester"),
	path('semester/add/new', views.semester_add_view, name="create_new_semester"),
	path('semester/edit/<int:pk>/', views.semester_update_view, name="edit_semester"),
	path('semester/delete/<int:pk>/', views.semester_delete_view, name="delete_semester"),

	
	path('password/', views.change_password, name='change_password'),
	

]