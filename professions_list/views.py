import time
from datetime import datetime

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.views.generic.detail import SingleObjectMixin, DetailView

from professions_list.mixins import CategoryDetailMixin
from professions_list.models import Profession, Skill
from professions_list.profession_parser import profession_getter

from django.utils import timezone
from django.views.generic.list import ListView


def my_view(request):
    if request.method == 'GET':
        profession_getter()
        return HttpResponse('result')


class ProfessionListView(CategoryDetailMixin, ListView):
    model = Profession
    paginate_by = 6

    def get_queryset(self):
        skill_id = self.request.GET.get("skill_id")
        if skill_id:
            return Profession.objects.filter(
                skills__id=skill_id
            )
        else:
            return Profession.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        skill_id = self.request.GET.get("skill_id")
        if not skill_id:
            for block in context["categories"]:
                if block["name"] == "Список профессий":
                    block["is_activated"] = True
        else:
            context["skill_id"] = skill_id
            context["categories"].append(
                {"name": 'Список профессий по умению "' + Skill.objects.get(id=skill_id).name +'"', "is_activated": True,
                 "link": "professions_list?skill_id=" + skill_id})
        return context


class ProfessionDetailView(CategoryDetailMixin, DetailView):
    model = Profession

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class MainPageView(CategoryDetailMixin, View):

    def get_context_data(self, **kwargs):
        context = super(MainPageView, self).get_context_data(**kwargs)
        for block in context["categories"]:
            if block["name"] == "Главная":
                block["is_activated"] = True
        return context

    def get(self, request):
        context = self.get_context_data()
        return render(request, "professions_list/mainpage.html", context)

    def post(self, request):
        profession_getter(4)
        context = self.get_context_data()
        info = context["server_info"]
        info.last_updated = datetime.now()
        info.save()
        return render(request, "professions_list/mainpage.html", context)


class SkillListView(CategoryDetailMixin, ListView):
    model = Skill
    paginate_by = 100

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for block in context["categories"]:
            if block["name"] == "Список умений":
                block["is_activated"] = True
        return context
