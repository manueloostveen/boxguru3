from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from .models import Session, Referral, Visitor, VisitData, UniqueVisitWeek, UniqueVisitMonth
import datetime


def is_valid_url(url):
    """
    Helper function to check if a fetched url is valid
    """
    validate = URLValidator()
    try:
        validate(url)  # check if url format is valid
    except ValidationError:
        return False

    return True

# Create your views here.
def save_clicked_link(request):

    # Save referral in database
    clicked_link = request.GET.get('link')

    if is_valid_url(clicked_link):
        pass
    else:
        return JsonResponse({'message': 'Oeps! Er is iets mis met de link.'})

    domain = clicked_link.split('/')[2]


    referral, referral_created = Referral.objects.get_or_create(
        url=clicked_link,
        domain=domain
    )

    # Save visitor IP in database
    client_ip = request.META['REMOTE_ADDR']
    visitor, visitor_created = Visitor.objects.get_or_create(ip=client_ip)

    # Save session in database
    session, session_created = Session.objects.get_or_create(
        visitor=visitor,
        session_id=request.COOKIES.get('sessionid', 'No sessionid cookie'),
    )

    # Add referral to session
    session.referrals.add(referral)

    # Save data to VisitData
    visit_data, visit_data_created = VisitData.objects.get_or_create(
        domain=domain
    )
    visit_data.unique_visitors.add(visitor)
    visit_data.visits += 1
    visit_data.save()

    # Save unique weekly visit
    week_number = datetime.date.today().isocalendar()[1]

    # week_number = datetime.date(2020, 5, 16).isocalendar()[1] #TEST DATE
    unique_week_visit, unique_week_visit_created = UniqueVisitWeek.objects.get_or_create(
        ip=client_ip,
        week_number=week_number,
        domain=domain
    )

    if unique_week_visit_created:
        visit_data.unique_week_visits.add(unique_week_visit)
        visit_data.save()

    # Save unique month visit
    month_number = datetime.date.today().month
    unique_month_visit, unique_month_visit_created = UniqueVisitMonth.objects.get_or_create(
        ip=client_ip,
        month_number=month_number,
        domain=domain
    )

    if unique_month_visit_created:
        visit_data.unique_month_visits.add(unique_month_visit)
        visit_data.save()

    return HttpResponse()
