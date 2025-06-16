from django.db.models import F
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views import generic

from .models import Question, Choice


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        now = timezone.now()
        return [q for q in Question.objects.filter(pub_date__lte=now).order_by('-pub_date')[:5] if q.choice_set.all()]


class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.object.choice_set.exists():
            raise Http404("No choices for this question.")
        return context

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        now = timezone.now()
        return Question.objects.filter(pub_date__lte=now)


class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.object.choice_set.exists():
            raise Http404("No choices for this question.")
        return context

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        now = timezone.now()
        return Question.objects.filter(pub_date__lte=now)


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice: Choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(
            request,
            'polls/display.html',
            {
                'question': question,
                'error_message': "You didn't select a choice.",
            }
        )
    else:
        selected_choice.votes = F('votes') + 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
