import factory

from apps.companies.tests.factories import CompanyFactory
from apps.projects.models import Project


class ProjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Project

    company = factory.SubFactory(CompanyFactory)
    name = factory.Sequence(lambda n: f"자동화 프로젝트 {n}")
    code = factory.Sequence(lambda n: f"PRJ-{n:04d}")
