import factory

from apps.companies.models import Company


class CompanyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Company

    name = factory.Sequence(lambda n: f"테스트기업{n}")
    industry = "식품"
