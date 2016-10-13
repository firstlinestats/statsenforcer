from django import template

register = template.Library()

@register.filter
def get_period(period):
    if period.period == 1:
        periodTime = "1st Period"
    elif period == 2:
        periodTime = "2nd Period"
    elif period == 3:
        periodTime = "3rd Period"
    else:
        periodTime = "Overtime (" + str(period.period) + ")"
    return periodTime