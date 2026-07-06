import factory

from apps.design.models import Rule, RuleType


class RuleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Rule

    code = factory.Sequence(lambda n: f"RULE-{n:04d}")
    rule_type = RuleType.RECOMMENDATION
    conditions_json = {"var": "TANK_EXISTS"}
    effects_json = [{"recommend": "RADAR_LEVEL"}]
