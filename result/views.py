from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from .decorators import lecturer_required, student_required
from .forms import *
from .models import User, Student, Course, CourseAllocation, TakenCourse, Session, Semester, CarryOverStudent, RepeatingStudent
from django.views.generic import CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.contrib.auth import update_session_auth_hash, authenticate
from django.contrib.auth.forms import PasswordChangeForm
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.db.models import Sum
#pdf
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse



from mysite.settings import MEDIA_ROOT, BASE_DIR, STATIC_URL
import os



@login_required
def home(request):
    """ 
    Shows our dashboard containing number of students, courses, lecturers, repating students, 
    carry over students and 1st class students in an interactive graph

    """
    students = Student.objects.all().count()
    staff = User.objects.filter(is_lecturer=True).count()
    courses = Course.objects.all().count()
    current_semester = Semester.objects.get(is_current_semester=True)
    no_of_1st_class_students = Result.objects.filter(cgpa__gte=4.5).count()
    no_of_carry_over_students = CarryOverStudent.objects.all().count()
    no_of_students_to_repeat = RepeatingStudent.objects.all().count()

    context = {
        "no_of_students": students,
        "no_of_staff":staff,
        "no_of_courses": courses,
        "no_of_1st_class_students": no_of_1st_class_students,
        "no_of_students_to_repeat": no_of_students_to_repeat,
        "no_of_carry_over_students": no_of_carry_over_students,
    }

    return render(request, 'result/home.html', context)



@login_required
def profile(request):
    """ Show profile of any user that fire out the request """
    current_semester = Semester.objects.get(is_current_semester=True)
    if request.user.is_lecturer:
        courses = Course.objects.filter(allocated_course__lecturer__pk=request.user.id).filter(semester=current_semester)
        return render(request, 'account/profile.html', {"courses": courses,})
    elif request.user.is_student:
        level = Student.objects.get(user__pk=request.user.id)
        courses = TakenCourse.objects.filter(student__user__id=request.user.id, course__level=level.level)
        context = {
        'courses': courses,
        'level': level,
        }
        return render(request, 'account/profile.html', context)
    else:
        staff = User.objects.filter(is_lecturer=True)
        return render(request, 'account/profile.html', { "staff": staff })

@login_required
def user_profile(request, id):
    """ Show profile of any selected user """
    if request.user.id == id:
        return redirect("/profile/")

    current_semester = Semester.objects.get(is_current_semester=True)
    user = User.objects.get(pk=id)
    if user.is_lecturer:
        courses = Course.objects.filter(allocated_course__lecturer__pk=id).filter(semester=current_semester)
        context = {
            "user": user,
            "courses": courses,
            }
        return render(request, 'account/user_profile.html', context)
    elif user.is_student:
        level = Student.objects.get(user__pk=id)
        courses = TakenCourse.objects.filter(student__user__id=id, course__level=level.level)
        context = {
            "user_type": "student",
            'courses': courses,
            'level': level,
            'user':user,
        }
        return render(request, 'account/user_profile.html', context)
    else:
        context = {
            "user": user,
            "user_type": "superuser"
            }
        return render(request, 'account/user_profile.html', context)

@login_required
def profile_update(request):
    """ Check if the fired request is a POST then grap changes and update the records otherwise we show an empty form """
    user = request.user.id
    user = User.objects.get(pk=user)
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            user.first_name = form.cleaned_data.get('first_name')
            user.last_name = form.cleaned_data.get('last_name')
            user.email = form.cleaned_data.get('email')
            user.phone = form.cleaned_data.get('phone')
            user.address = form.cleaned_data.get('address')
            if request.FILES:
                user.picture = request.FILES['picture']
            user.save()
            messages.success(request, 'Your profile was successfully edited.')
            return redirect("/profile/")
    else:
        form = ProfileForm(instance=user, initial={
            'firstname': user.first_name,
            'lastname': user.last_name,
            'email': user.email,
            'phone': user.phone,
            'picture': user.picture,
            })

    return render(request, 'account/profile_update.html', {'form': form})


@login_required
@lecturer_required
def course_list(request):
    """ Show list of all registered courses in the system """
    courses = Course.objects.all()
    context = {
        "courses":courses,
        }
    return render(request, 'course/course_list.html', context)

@login_required
@lecturer_required
def student_list(request):
    """ Show list of all registered students in the system """
    students = Student.objects.all()
    user_type = "Student"
    context = {
        "students": students, 
        "user_type": user_type,
        }
    return render(request, 'students/student_list.html', context)

@login_required
@lecturer_required
def staff_list(request):
    """ Show list of all registered staff """
    staff = User.objects.filter(is_student=False)
    user_type = "Staff"
    context = {
        "staff": staff, 
        "user_type": user_type,
        }
    return render(request, 'staff/staff_list.html', context)


@login_required
@lecturer_required
def session_list_view(request):
    """ Show list of all sessions """
    sessions = Session.objects.all().order_by('-session')
    return render(request, 'result/manage_session.html', {"sessions": sessions,})

@login_required
@lecturer_required
def session_add_view(request):
    """ check request method, if POST we add session otherwise show empty form """
    if request.method == 'POST':
        form = SessionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Session added successfully ! ')

    else:
        form = SessionForm()
    return render(request, 'result/session_update.html', {'form': form})

@login_required
@lecturer_required
def session_update_view(request, pk):
    session = Session.objects.get(pk=pk)
    if request.method == 'POST':
        a = request.POST.get('is_current_session')
        if a == '2':
            unset = Session.objects.get(is_current_session=True)
            unset.is_current_session = False
            unset.save()
            form = SessionForm(request.POST, instance=session)
            if form.is_valid():
                form.save()
                messages.success(request, 'Session updated successfully ! ')
        else:
            form = SessionForm(request.POST, instance=session)
            if form.is_valid():
                form.save()
                messages.success(request, 'Session updated successfully ! ')

    else:
        form = SessionForm(instance=session)
    return render(request, 'result/session_update.html', {'form': form})

@login_required
@lecturer_required
def session_delete_view(request, pk):
    session = get_object_or_404(Session, pk=pk)
    if session.is_current_session == True:
    	messages.info(request, "You cannot delete current session")
    	return redirect('manage_session')
    else:
    	session.delete()
    	messages.success(request, "Session successfully deleted")
    return redirect('manage_semester')

@login_required
@lecturer_required
def semester_list_view(request):
    semesters = Semester.objects.all().order_by('-semester')
    return render(request, 'result/manage_semester.html', {"semesters": semesters,})

@login_required
@lecturer_required
def semester_add_view(request):
    if request.method == 'POST':
        form = SemesterForm(request.POST)
        if form.is_valid():
            data = form.data.get('is_current_semester') # returns string of 'True' if the user selected Yes
            if data == 'True':
            	semester = form.data.get('semester')
            	ss = form.data.get('session')
            	session = Session.objects.get(pk=ss)
            	try:
            		if Semester.objects.get(semester=semester, session=ss):
	            		messages.info(request, semester + " semester in " + session.session +" session already exist")
	            		return redirect('create_new_semester')
            	except:
	            	semester = Semester.objects.get(is_current_semester=True)
	            	semester.is_current_semester = False
	            	semester.save()
	            	form.save()
            form.save()
            messages.success(request, 'Semester added successfully ! ')
            return redirect('manage_semester')
    else:
        form = SemesterForm()
    return render(request, 'result/semester_update.html', {'form': form})

@login_required
@lecturer_required
def semester_update_view(request, pk):
    semester = Semester.objects.get(pk=pk)
    if request.method == 'POST':
        if request.POST.get('is_current_semester') == 'True': # returns string of 'True' if the user selected yes for 'is current semester'
            unset_semester = Semester.objects.get(is_current_semester=True)
            unset_semester.is_current_semester = False
            unset_semester.save()
            unset_session = Session.objects.get(is_current_session=True)
            unset_session.is_current_session = False
            unset_session.save()
            new_session = request.POST.get('session')
            form = SemesterForm(request.POST, instance=semester)
            if form.is_valid():
            	set_session = Session.objects.get(pk=new_session)
            	set_session.is_current_session = True
            	set_session.save()
            	form.save()
            	messages.success(request, 'Semester updated successfully !')
            	return redirect('manage_semester')
        else:
            form = SemesterForm(request.POST, instance=semester)
            if form.is_valid():
                form.save()
                return redirect('manage_semester')

    else:
        form = SemesterForm(instance=semester)
    return render(request, 'result/semester_update.html', {'form': form})

@login_required
@lecturer_required
def semester_delete_view(request, pk):
    semester = get_object_or_404(Semester, pk=pk)
    if semester.is_current_semester == True:
    	messages.info(request, "You cannot delete current semester")
    	return redirect('manage_semester')
    else:
    	semester.delete()
    	messages.success(request, "Semester successfully deleted")
    return redirect('manage_semester')


@method_decorator([login_required, lecturer_required], name='dispatch')
class StaffAddView(CreateView):
    model = User
    form_class = StaffAddForm
    template_name = 'registration/add_staff.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'staff'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        return redirect('staff_list')

@login_required
@lecturer_required
def edit_staff(request, pk):
    staff = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        form = StaffAddForm(request.POST, instance=staff)
        if form.is_valid():
            staff.save()
            return redirect('staff_list')
    else:
        form = StaffAddForm(instance=staff)
    return render(request, 'registration/edit_staff.html', {'form': form})

@login_required
@lecturer_required
def delete_staff(request, pk):
    staff = get_object_or_404(User, pk=pk)
    staff.delete()
    return redirect('staff_list')

@method_decorator([login_required, lecturer_required], name='dispatch')
class StudentAddView(CreateView):
    model = User
    form_class = StudentAddForm
    template_name = 'registration/add_student.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'student'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        return redirect('student_list')

@login_required
@lecturer_required
def edit_student(request, pk):
	student = get_object_or_404(Student, pk=pk)
	if request.method == "POST":
		form = StudentAddForm(request.POST, instance=student)
		if form.is_valid():
			form.save()
			return redirect('student_list')
	else:
		form = StudentAddForm(instance=student)
	return render(request, 'registration/edit_student.html', {'form': form, 'student': student})

@login_required
@lecturer_required
def delete_student(request, pk):
    user = get_object_or_404(User, pk=pk)
    student = get_object_or_404(Student, pk=pk)
    user.delete()
    student.delete()
    return redirect('student_list')

@login_required
def change_password(request):
	if request.method == 'POST':
		form = PasswordChangeForm(request.user, request.POST)
		if form.is_valid():
			user = form.save()
			update_session_auth_hash(request, user)
			messages.success(request, 'Your password was successfully updated!')
		else:
			messages.error(request, 'Please correct the errors below. ')
	else:
		form = PasswordChangeForm(request.user)
	return render(request, 'account/change_password.html', {
		'form': form,
        })

@method_decorator([login_required], name='dispatch')
class GroupAddView(CreateView):
    model = Group
    form_class = GroupCreateForm
    template_name = 'group/group_form.html'


    def form_valid(self, form):
        form.save()
        return redirect('group_list')

def group_list(request):
    groups = Group.objects.all().order_by('number')
    context = {
        'groups' : groups
    }
    return render (request, 'group/group_list.html', context)

def group_students(request, pk):
    group = get_object_or_404(Group, pk=pk)
    return render (request, 'group/group_students.html', {'group':group})

@login_required
def group_delete(request, pk):
    group = get_object_or_404(Group, pk=pk)
    group.delete()
    messages.success(request, 'Deleted successfully!')
    return redirect('group_list')

@login_required
def group_edit(request, pk):
    group = get_object_or_404(Group, pk=pk)
    if request.method == "POST":
        form = GroupCreateForm(request.POST, instance=group)
        if form.is_valid():
            group.save()
            messages.success(request, "Successfully Updated")
            return redirect('group_list')
    else:
        form = GroupCreateForm(instance=group)
    return render(request, 'group/group_form.html', {'form': form})


@login_required
@student_required
def shartnoma_list_view(request):
    """ Show list of all sessions """
    shartnomas = Contract.objects.all().order_by('-miqdor')
    payments = Payment.objects.all().order_by('-payment_date').filter(student__user=request.user)
    current_shartnoma = Contract.objects.get(is_current_shartnoma=True)
    sum = {}
    if request.user.is_student:
        sum = Payment.objects.filter(student__user=request.user).aggregate(jami=Sum('miqdor'))
    context = {
        "shartnomas": shartnomas,
        'payments':payments,
        'sum':sum,
        'current_shartnoma':current_shartnoma,
    }
    return render(request, 'result/manage_shartnoma.html',context)

@login_required
def shartnoma_add_view(request):
    """ check request method, if POST we add session otherwise show empty form """
    if request.method == 'POST':
        form = ShartnomaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Shartnoma added successfully ! ')

    else:
        form = ShartnomaForm()
    return render(request, 'result/shartnoma_update.html', {'form': form})

@login_required
def shartnoma_update_view(request, pk):
    shartnoma = Contract.objects.get(pk=pk)
    if request.method == 'POST':
        a = request.POST.get('is_current_shartnoma')
        if a == True:
            shartnoma.is_current_shartnoma = False
            shartnoma.save()
            form = ShartomaForm(request.POST, instance=shartnoma)
            if form.is_valid():
                form.save()
                messages.success(request, 'Shartnoma updated successfully ! ')
        else:
            form = ShartnomaForm(request.POST, instance=shartnoma)
            if form.is_valid():
                form.save()
                messages.success(request, 'Shartnoma updated successfully ! ')

    else:
        form = ShartnomaForm(instance=shartnoma)
    return render(request, 'result/shartnoma_update.html', {'form': form})

@login_required
def shartnoma_delete_view(request, pk):
    shartnoma = get_object_or_404(Contract, pk=pk)
    if shartnoma.is_current_shartnoma == True:
    	messages.info(request, "You cannot delete current shartnoma")
    	return redirect('manage_shartnoma')
    else:
    	session.delete()
    	messages.success(request, "Session successfully deleted")
    return redirect('manage_shartnoma')

@login_required
@student_required
def payment_add_view(request):
    """ check request method, if POST we add session otherwise show empty form """
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Shartnoma added successfully ! ')

    else:
        form = PaymentForm()
    return render(request, 'result/shartnoma_update.html', {'form': form})

@login_required
def payment_update_view(request, pk):
    payment = Payment.objects.get(pk=pk)
    if request.method == 'POST':
        form = PaymentForm(request.POST, instance=payment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Payment updated successfully ! ')

    else:
        form = PaymentForm(instance=payment)
    return render(request, 'result/shartnoma_update.html', {'form': form})

