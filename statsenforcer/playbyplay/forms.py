from django import forms

from team import models as tmodels
import models

from fancystats import constants


class GameForm(forms.Form):
    teamstrengths = forms.ChoiceField(label="Team Strengths",
        choices=constants.TEAMSTRENGTHS_CHOICES,
        widget=forms.Select(attrs={'class' : 'form-control input-md'})
    )
    scoresituation = forms.ChoiceField(label="Score Situation",
        choices=constants.SCORESITUATION_CHOICES,
        widget=forms.Select(attrs={'class' : 'form-control input-md'})
    )
    period = forms.ChoiceField(label="Period",
        choices=constants.PERIOD_CHOICES,
        widget=forms.Select(attrs={'class' : 'form-control input-md'})
    )
    seasons = forms.MultipleChoiceField(
        required=False,
        choices=tuple((season, "-".join([str(season)[:4], str(season)[4:]])) for season in models.Game.objects.order_by('season').values_list('season', flat=True).distinct()))


class GamesForm(forms.Form):
    teams = forms.ModelMultipleChoiceField(
        required=False,
        queryset=tmodels.Team.objects.order_by("name").all())
    startDate = forms.DateField(required=False)
    seasons = forms.MultipleChoiceField(
        required=False,
        choices=tuple((season, "-".join([str(season)[:4], str(season)[4:]])) for season in models.Game.objects.order_by('season').values_list('season', flat=True).distinct()))
    endDate = forms.DateField(required=False)
    venues = forms.ModelMultipleChoiceField(
        required=False,
        queryset=tmodels.Venue.objects.order_by('name').all())
    gameTypes = forms.MultipleChoiceField(
        required=False,
        choices=constants.gameTypes,
        widget=forms.CheckboxSelectMultiple,
        initial=[x[0] for x in constants.gameTypes])
