from dashboard.models import Catalogue


def catalogue_list(request):
    return {"catalogue_list": Catalogue.objects.all()}
