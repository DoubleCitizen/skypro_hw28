import json

from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView, ListView

from ads.models import Category, Ad
from avito import settings
from users.models import User


class Index(View):
    def get(self, request):
        return JsonResponse({"status": "ok"})


@method_decorator(csrf_exempt, name='dispatch')
class CategoryView(View):
    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        result = []
        for cat in categories:
            result.append({"id": cat.id, "name": cat.name})

        return JsonResponse(result, safe=False, json_dumps_params={'ensure_ascii': False})

    def post(self, request):
        data = json.loads(request.body)
        new_category = Category.objects.create(name=data['name'])
        return JsonResponse({'id': new_category.id, 'name': new_category.name}, safe=False,
                            json_dumps_params={'ensure_ascii': False})


@method_decorator(csrf_exempt, name='dispatch')
class CategoryCreateView(CreateView):
    model = Category
    fields = ['name']

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        category = Category.objects.create(name=data['name'])
        return JsonResponse({
            "pk": category.pk,
            "name": category.name
        }, safe=False, json_dumps_params={'ensure_ascii': False})


@method_decorator(csrf_exempt, name='dispatch')
class CategoryUpdateView(UpdateView):
    model = Category
    fields = ['name']

    def patch(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)
        data = json.loads(request.body)
        self.object.name = data['name']
        self.object.save()
        return JsonResponse({
            "pk": self.object.pk,
            "name": self.object.name
        }, safe=False, json_dumps_params={'ensure_ascii': False})


@method_decorator(csrf_exempt, name='dispatch')
class CategoryDeleteView(DeleteView):
    model = Category
    success_url = '/'

    def delete(self, request, *args, **kwargs):
        super().delete(request, *args, **kwargs)

        return JsonResponse({"ok"}, status=204)


class CategoryDetailView(DetailView):
    model = Category

    def get(self, request, *args, **kwargs):
        category = self.get_object()

        return JsonResponse({
            "pk": category.pk,
            "name": category.name
        }, safe=False, json_dumps_params={'ensure_ascii': False})


class AdsListView(ListView):
    model = Ad
    queryset = Ad.objects.all()

    def get(self, request, *args, **kwargs):
        super().get(self, request, *args, **kwargs)
        self.object_list = self.object_list.order_by("-price")
        paginator = Paginator(object_list=self.object_list, per_page=settings.TOTAL_ON_PAGE)
        page = request.GET.get('page')
        page_obj = paginator.get_page(page)
        result = []

        for ad in page_obj:
            result.append(
                {"id": ad.id,
                 "name": ad.name,
                 "author": ad.author.username,
                 "category": ad.category.name if ad.category.name else "?????? ??????????????????",
                 "price": ad.price,
                 "description": ad.description,
                 "is_published": ad.is_published,
                 "image": ad.image.url
                 })
        return JsonResponse({"ads": result, "pages": page_obj.number, "total": page_obj.paginator.count}, safe=False,
                            json_dumps_params={'ensure_ascii': False})


@method_decorator(csrf_exempt, name='dispatch')
class AdsCreateView(CreateView):
    model = Ad
    fields = ['name', 'author', 'price', 'description', 'address', 'is_published']

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)

        author = get_object_or_404(User, pk=data['author_id'])
        category = get_object_or_404(Category, pk=data['category_id'])

        new_ad = Ad.objects.create(name=data['name'],
                                   author=author,
                                   category=category,
                                   price=data['price'],
                                   description=data['description'],
                                   is_published=data['is_published'])

        return JsonResponse({"id": new_ad.id,
                             "name": new_ad.name,
                             "author": new_ad.author.username,
                             "category": new_ad.category.name,
                             "price": new_ad.price,
                             "description": new_ad.description,
                             "is_published": new_ad.is_published
                             }, safe=False,
                            json_dumps_params={'ensure_ascii': False})


@method_decorator(csrf_exempt, name='dispatch')
class AdsUploadView(UpdateView):
    model = Ad
    fields = ['image']

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.image = request.FILES.get("image")
        self.object.save()

        return JsonResponse(
            {"id": self.object.id,
             "name": self.object.name,
             "author": self.object.author.username,
             "category": self.object.category.name,
             "price": self.object.price,
             "description": self.object.description,
             "is_published": self.object.is_published,
             "image": self.object.image.url
             }, safe=False,
            json_dumps_params={'ensure_ascii': False})


class AdsDetailView(DetailView):
    model = Ad

    def get(self, request, *args, **kwargs):
        ad = self.get_object()

        return JsonResponse(
            {"id": ad.id, "name": ad.name, "author": ad.author, "category": ad.category, "price": ad.price,
             "description": ad.description,
             "is_published": ad.is_published, "image": ad.image.url}, safe=False,
            json_dumps_params={'ensure_ascii': False})
