from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Control

class ControlListView(ListView):
    model = Control
    template_name = 'helix/control_list.html'
    context_object_name = 'controls'

class ControlDetailView(DetailView):
    model = Control
    template_name = 'helix/control_detail.html'
    context_object_name = 'control'

class ControlCreateView(CreateView):
    model = Control
    template_name = 'helix/control_form.html'
    fields = '__all__'
    success_url = reverse_lazy('helix:control_list')

class ControlUpdateView(UpdateView):
    model = Control
    template_name = 'helix/control_form.html'
    fields = '__all__'
    success_url = reverse_lazy('helix:control_list')

class ControlDeleteView(DeleteView):
    model = Control
    template_name = 'helix/control_confirm_delete.html'
    success_url = reverse_lazy('helix:control_list')