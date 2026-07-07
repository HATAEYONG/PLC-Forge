"""LS ELECTRIC Adapter 테스트 (PRD §21)."""

import pytest

from apps.generators.adapters.ls_electric import LSElectricAdapter


def make_ir(signals):
    return {
        "project_metadata": {"code": "P1", "name": "라인"},
        "device_definitions": [],
        "signal_definitions": signals,
        "data_types": sorted({s["data_type"] for s in signals}) or ["BOOL"],
        "logic_expressions": [
            {"operation": "SET_RESET", "target": "IL_ESTOP", "comment": "Interlock"},
            {"operation": "COMPARE", "target": "AL_HIGH", "comment": "Alarm"},
        ],
        "alarms": [{"code": "AL_HIGH", "condition": "TEMP>90", "priority": "HIGH"}],
        "interlocks": [{"code": "IL_ESTOP", "condition": "ESTOP"}],
        "sequences": [],
        "hmi_tags": [{"name": "MOTOR_RUN", "screen": "IO_MONITOR"}],
        "test_requirements": [{"test_id": "FAT-1", "phase": "FAT", "category": "ALARM"}],
    }


def sample_signals():
    return [
        {"name": "PUMP_RUN", "signal_type": "DO", "data_type": "BOOL", "description": "기동"},
        {"name": "PUMP_FB", "signal_type": "DI", "data_type": "BOOL", "description": "피드백"},
        {"name": "LEVEL_AI", "signal_type": "AI", "data_type": "REAL", "description": "레벨"},
    ]


def test_address_mapping_by_signal_type():
    adapter = LSElectricAdapter()
    addr = adapter.map_addresses(make_ir(sample_signals()))
    assert addr["PUMP_RUN"] == "%QX0.0"
    assert addr["PUMP_FB"] == "%IX0.0"
    assert addr["LEVEL_AI"] == "%IW0"


def test_data_type_mapping():
    adapter = LSElectricAdapter()
    dt = adapter.map_data_types(make_ir(sample_signals()))
    assert dt["BOOL"] == "BOOL"
    assert dt["REAL"] == "REAL"


def test_structured_text_generated():
    adapter = LSElectricAdapter()
    ir = make_ir(sample_signals())
    st = adapter.generate_program_structure(ir, adapter.map_addresses(ir))
    assert "PROGRAM Main" in st
    assert "PUMP_RUN AT %QX0.0 : BOOL" in st
    assert "END_PROGRAM" in st


def test_package_output_bundles_all_files():
    adapter = LSElectricAdapter()
    out = adapter.package_output(make_ir(sample_signals()))
    assert set(out["files"]) == {
        "Main.st",
        "tags.csv",
        "io.csv",
        "alarms.csv",
        "hmi_tags.csv",
        "tests.csv",
    }
    assert out["mapping_report"]["signal_count"] == 3
    assert out["mapping_report"]["vendor"] == "LS ELECTRIC"
    # Tag CSV에 주소 포함
    assert "%QX0.0" in out["files"]["tags.csv"]


def test_duplicate_signal_rejected():
    from core.exceptions import DomainError

    dup = sample_signals() + [
        {"name": "PUMP_RUN", "signal_type": "DO", "data_type": "BOOL", "description": "dup"}
    ]
    with pytest.raises(DomainError) as excinfo:
        LSElectricAdapter().package_output(make_ir(dup))
    assert excinfo.value.code == "ir_duplicate_signal"
