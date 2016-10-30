from django import forms


class GameForm(forms.Form):
    teamstrengths = forms.ChoiceField(label="Team Strengths",
        choices=(
            ("all", "All"),
            ("even", "Even Strength 5v5"),
            ("pp", "Power Play"),
            ("pk", "Short Handed"),
            ("4v4", "4v4"),
            ("og", "Opposing Goalie Pulled"),
            ("tg", "Team Goalie Pulled"),
            ("3v3", "3v3")
        ),
        widget=forms.Select(attrs={'class' : 'form-control input-md'})
    )
    scoresituation = forms.ChoiceField(label="Score Situation",
        choices=(
            ("all", "All"),
            ("t3+", "Trailing by 3+"),
            ("t2", "Trailing by 2"),
            ("t1", "Trailing by 1"),
            ("t", "Tied"),
            ("l1", "Leading by 1"),
            ("l2", "Leading by 2"),
            ("l3+", "Leading by 3+"),
            ("w1", "Within 1")
        ),
        widget=forms.Select(attrs={'class' : 'form-control input-md'})
    )
    period = forms.ChoiceField(label="Period",
        choices=(
            ("all", "All"),
            ("1", "1"),
            ("2", "2"),
            ("3", "3"),
            ("4", "OT")
        ),
        widget=forms.Select(attrs={'class' : 'form-control input-md'})
    )