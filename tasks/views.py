from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Task, Comment
from .forms import TaskForm, CommentForm
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import PermissionDenied

from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.shortcuts import render


# 📋 Список задач
class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        queryset = Task.objects.all()

        # 🔍 поиск (если есть)
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(title__icontains=search) | queryset.filter(description__icontains=search)

        # 🔽 сортировка
        order = self.request.GET.get('order')

        if order == 'due_date':
            queryset = queryset.order_by('due_date')

        elif order == '-due_date':
            queryset = queryset.order_by('-due_date')

        elif order == 'priority':
            queryset = queryset.order_by('priority')

        elif order == '-priority':
            queryset = queryset.order_by('-priority')

        elif order == 'title':
            queryset = queryset.order_by('title')

        return queryset

@method_decorator(staff_member_required, name='dispatch')
class UserListView(ListView):
    model = User
    template_name = 'tasks/user_list.html'
    context_object_name = 'users'

    def dispatch(self, request, *args, **kwargs):
        # ❗ только superuser может заходить
        if not request.user.is_superuser:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


def toggle_admin(request, user_id):
    if not request.user.is_superuser:
        raise PermissionDenied

    user = User.objects.get(id=user_id)

    # нельзя менять самого себя
    if user != request.user:
        user.is_staff = not user.is_staff
        user.save()

    return redirect('user_list')

# ➕ Создание задачи
class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('task_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('task_list')

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        user = self.request.user

        if obj.user != user and user not in obj.admins.all():
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)

class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = 'tasks/task_confirm_delete.html'
    success_url = reverse_lazy('task_list')

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        user = self.request.user

        if obj.user != user and user not in obj.admins.all:
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)

# 🔍 Детали задачи + комментарии
class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'tasks/task_detail.html'
    context_object_name = 'task'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.all()
        context['form'] = CommentForm()
        context['users'] = User.objects.all()  # 👈 важно
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.task = self.object
            comment.user = request.user
            comment.save()

        return redirect('task_detail', pk=self.object.pk)
    
class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'tasks/register.html'
    success_url = reverse_lazy('login')


def add_task_admin(request, task_id, user_id):
    task = Task.objects.get(id=task_id)

    # только владелец может назначать
    if request.user != task.user:
        raise PermissionDenied

    user = User.objects.get(id=user_id)
    task.admins.add(user)

    return redirect('task_detail', pk=task.id)


def remove_task_admin(request, task_id, user_id):
    task = Task.objects.get(id=task_id)

    if request.user != task.user:
        raise PermissionDenied

    user = User.objects.get(id=user_id)
    task.admins.remove(user)

    return redirect('task_detail', pk=task.id)

def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user != comment.user:
        raise PermissionDenied

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('task_detail', pk=comment.task.id)
    else:
        form = CommentForm(instance=comment)

    return render(request, 'tasks/edit_comment.html', {'form': form})


def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user != comment.user:
        raise PermissionDenied

    task_id = comment.task.id
    comment.delete()

    return redirect('task_detail', pk=task_id)

def mark_done(request, pk):
    task = get_object_or_404(Task, pk=pk)

    # проверка прав
    if request.user == task.user or request.user in task.admins.all() or request.user.is_staff:
        task.status = 'done'
        task.save()

    return redirect('task_list')

def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)

    context['total'] = Task.objects.count()
    context['done'] = Task.objects.filter(status='done').count()
    context['in_progress'] = Task.objects.filter(status='in_progress').count()
    context['new'] = Task.objects.filter(status='new').count()

    return context