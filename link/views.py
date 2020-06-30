import logging

from datetime import datetime

from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.db.models import Case, When, Q, F, FloatField, ExpressionWrapper, Max, Count
from django.shortcuts import render
from django.utils import timezone

from link.models import Link

from .utils.url import clean_url, get_root_url


class LinkListView(ListView):
    model = Link
    paginate_by = 50

    def get_queryset(self):
        queryset = (Link.objects.exclude(liked__isnull=True)
                                .exclude(liked__exact=0)
                                .exclude(summary__isnull=True)
                                .exclude(summary__exact='')
                                .exclude(summary__exact='nan'))
        url = self.request.GET.get('url')
        if url:
            queryset = queryset.filter(Q(url__icontains=url))
        title = self.request.GET.get('title')
        if title:
            queryset = queryset.filter(Q(title__icontains=title))
        aggregator = self.request.GET.get('aggregator')
        if aggregator:
            queryset = queryset.filter(Q(aggregator__icontains=aggregator))
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(Q(category__icontains=category))
        summary = self.request.GET.get('summary')
        if summary:
            queryset = queryset.filter(Q(summary__icontains=summary))
        sort = self.request.GET.get('sort')
        if sort == 'random':
            queryset = queryset.order_by('seed', 'id')
        elif sort == 'diversity':
            queryset = queryset.order_by('aggregator', '-modified').distinct('aggregator')
        else:
            queryset = queryset.order_by('-modified')
            
        queryset = queryset.all()
        return queryset

    context_object_name = 'link_list'
    template_name = 'link/link_list.html'


class UpcomingListView(ListView):
    model = Link
    paginate_by = 17

    def get_context_data(self, **kwargs):
        context = super(UpcomingListView, self).get_context_data(**kwargs)
        today = datetime.today()
        today = datetime(today.year, today.month, today.day)
        context['read_count'] = (Link.objects.exclude(liked__isnull=True)
                                             .filter(modified__gte=today)
                                             .count())
        return context

    def get_queryset(self):
        queryset = Link.objects.filter(liked__isnull=True)
        url = self.request.GET.get('url')
        if url:
            queryset = queryset.filter(Q(url__icontains=url))
        title = self.request.GET.get('title')
        if title:
            queryset = queryset.filter(Q(title__icontains=title))
        aggregator = self.request.GET.get('aggregator')
        if aggregator:
            queryset = queryset.filter(Q(aggregator__icontains=aggregator))
        sort = self.request.GET.get('sort')
        if sort == 'recent':
            queryset = queryset.order_by('-added')
        elif sort == 'random':
            queryset = queryset.order_by('seed', 'id')
        elif sort == 'diversity':
            queryset = queryset.order_by('seed', 'aggregator', '-added')
        else:
            queryset = (queryset.annotate(priority=Case(
                                            When(Q(aggregator__exact='LFaA'), then=30),
                                            When(Q(aggregator__exact='FPMorning'), then=30),
                                            When(Q(aggregator__exact='FPSecurity'), then=30),
                                            When(Q(aggregator__exact='FPChina'), then=30),
                                            When(Q(aggregator__exact='FPSouthAsia'), then=30),
                                            When(Q(aggregator__exact='FP-WYWL'), then=30),
                                            When(Q(aggregator__exact='MorningAg'), then=30),
                                            When(Q(aggregator__exact='Dispatch'), then=25),
                                            When(Q(aggregator__exact='EAForum'), then=16),
                                            When(Q(aggregator__exact='538'), then=14),
                                            When(Q(aggregator__exact='Vox'), then=14),
                                            When(Q(aggregator__exact='SSC'), then=14),
                                            When(Q(aggregator__exact='Custom'), then=12),
                                            When(Q(aggregator__exact='LW'), then=8),
                                            When(Q(aggregator__exact='EABlogs'), then=8),
                                            When(Q(aggregator__exact='DanWahl'), then=8),
                                            When(Q(aggregator__exact='JenSkerritt'), then=8),
                                            When(Q(aggregator__exact='Lusk'), then=8),
                                            When(Q(aggregator__exact='CurrentAffairs'), then=8),
                                            When(Q(aggregator__exact='Caplan'), then=6),
                                            When(Q(aggregator__exact='Leo'), then=6),
                                            When(Q(aggregator__exact='NMA'), then=6),
                                            When(Q(aggregator__exact='NerdFitness'), then=6),
                                            When(Q(aggregator__exact='MOF'), then=6),
                                            When(Q(aggregator__exact='MR'), then=6),
                                            When(Q(aggregator__exact='Rosewater'), then=6),
                                            When(Q(aggregator__exact='Sumner'), then=4),
                                            When(Q(aggregator__exact='Noah'), then=4),
                                            When(Q(aggregator__exact='D4P'), then=4),
                                            When(Q(aggregator__exact='3P'), then=3),
                                            When(Q(aggregator__exact='HN'), then=0.5),
                                            default=1,
                                            output_field=FloatField()))
                        .annotate(priority=ExpressionWrapper((1 + (F('priority') / 17.0)) +
                                                                 (F('id') / 1700.0) +
                                                                 (F('seed') / 75.0),
                                                             output_field=FloatField()))
                        .order_by('-priority'))
        queryset = queryset.all()
        return queryset

    context_object_name = 'upcoming_list'
    template_name = 'link/upcoming_list.html'


class LinkCreate(CreateView):
    model = Link
    fields = ['url', 'title', 'summary', 'liked', 'category', 'aggregator']

    def form_valid(self, form):
        form.instance.modified = timezone.now()
        form.instance.added = timezone.now()
        form.instance.domain = get_root_url(clean_url(form.instance.url)) 
        return super().form_valid(form)

    def create(self, *args, **kwargs):
        self.modified = timezone.now()
        self.added = timezone.now()
        self.domain = get_root_url(clean_url(self.url)) 
        return super().create(*args, **kwargs)


class LinkUpdate(UpdateView):
    model = Link
    fields = ['url', 'title', 'summary', 'liked', 'category', 'aggregator']
    template_name_suffix = '_update_form'

    def get_success_url(self):
        get_ = self.request.GET
        url = get_.get('url', '')
        title = get_.get('title', '')
        aggregator = get_.get('aggregator', '')
        page = get_.get('page')
        sort = get_.get('sort')
        return '/?url={}&title={}&aggregator={}&page={}&sort={}'.format(url, title, aggregator, page, sort)

    def form_valid(self, form):
        if not form.instance.liked:
            form.instance.liked = 0
            logging.info('Deleted "{}"'.format(form.instance.title))
        else:
            logging.info('Liked "{}"'.format(form.instance.title))

        form.instance.modified = timezone.now()
        form.instance.domain = get_root_url(clean_url(form.instance.url)) 
        return super().form_valid(form)

