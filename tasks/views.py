from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Task, Comment
from .forms import TaskForm, CommentForm
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import PermissionDenied

# 📋 Список задач
class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        queryset = Task.objects.filter(user=self.request.user)

        status = self.request.GET.get('status')
        priority = self.request.GET.get('priority')
        due_date = self.request.GET.get('due_date')

        if status:
            queryset = queryset.filter(status=status)

        if priority:
            queryset = queryset.filter(priority=priority)

        if due_date:
            queryset = queryset.filter(due_date=due_date)

        return queryset


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
        if obj.user != self.request.user:
            raise PermissionDenied  # если не владелец — запрет
        return super().dispatch(request, *args, **kwargs)

class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = 'tasks/task_confirm_delete.html'
    success_url = reverse_lazy('task_list')

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != self.request.user:
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

