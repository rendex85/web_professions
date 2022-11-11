from django.views import View
from django.views.generic.detail import SingleObjectMixin

from professions_list.models import ParserUpdaterInfo


class CategoryDetailMixin(object, ):

    def get_context_data(self, **kwargs):
        try:
            context = super(CategoryDetailMixin, self).get_context_data(**kwargs)
        except AttributeError:
            context = {}
        context["categories"] = [
            {"name": "Главная", "is_activated": False, "link": ""},
            {"name": "Список профессий", "is_activated": False, "link": "professions_list"},
            {"name": "Список умений", "is_activated": False, "link": "skills_list"}
        ]
        context["color_list"] = ["primary", "secondary", "success", "danger", "warning", "info", "light", "dark"]
        context["server_info"] = ParserUpdaterInfo.load()
        return context
