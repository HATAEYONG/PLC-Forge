"""LS ELECTRIC Adapter (PRD §21, 초기 개발 1순위).

XGB/XGI 계열 주소 체계로 IR을 매핑하고 Structured Text + CSV + Mapping Report를 생성한다.
실제 제조사 바이너리 프로젝트 파일이 아닌 텍스트 산출물을 우선한다 (PRD §21 MVP).
"""

import csv
import io

from apps.generators.adapters.base import VendorAdapter
from core.exceptions import DomainError

# 벤더 중립 → LS ELECTRIC(IEC) 데이터 타입
DATA_TYPE_MAP = {"BOOL": "BOOL", "INT": "INT", "REAL": "REAL", "WORD": "WORD"}

# 신호 유형별 주소 접두 (XGI 직접변수 표기)
ADDRESS_PREFIX = {"DI": "%IX", "DO": "%QX", "AI": "%IW", "AO": "%QW"}


def _csv(rows, header):
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(header)
    writer.writerows(rows)
    return buffer.getvalue()


class LSElectricAdapter(VendorAdapter):
    vendor_key = "ls"
    vendor_name = "LS ELECTRIC"

    def validate_ir(self, ir: dict) -> None:
        # 신호 이름 중복은 주소 충돌을 유발하므로 벤더 관점에서 거부
        names = [s["name"] for s in ir["signal_definitions"]]
        if len(names) != len(set(names)):
            raise DomainError(
                "IR에 중복된 신호 이름이 있어 LS 주소 매핑이 불가합니다.",
                code="ir_duplicate_signal",
            )

    def map_data_types(self, ir: dict) -> dict:
        return {dt: DATA_TYPE_MAP.get(dt, "WORD") for dt in ir["data_types"]}

    def map_addresses(self, ir: dict) -> dict:
        counters = {"DI": 0, "DO": 0, "AI": 0, "AO": 0}
        addresses = {}
        for sig in ir["signal_definitions"]:
            st = sig["signal_type"]
            prefix = ADDRESS_PREFIX[st]
            if st in ("DI", "DO"):
                byte, bit = divmod(counters[st], 8)
                addresses[sig["name"]] = f"{prefix}{byte}.{bit}"
            else:
                addresses[sig["name"]] = f"{prefix}{counters[st]}"
            counters[st] += 1
        return addresses

    def map_instructions(self, ir: dict) -> list:
        lines = []
        for expr in ir["logic_expressions"]:
            op = expr["operation"]
            target = expr.get("target", "")
            if op == "SET_RESET":
                lines.append(
                    f"(* {expr.get('comment', '')} *) "
                    f"IF {target}_COND THEN {target} := TRUE; "
                    f"ELSIF {target}_RESET THEN {target} := FALSE; END_IF;"
                )
            elif op == "COMPARE":
                lines.append(f"(* {expr.get('comment', '')} *) {target} := {target}_COND;")
            elif op == "CONTROL_FLOW":
                lines.append(f"(* Sequence {target}: {expr.get('steps', 0)} steps *)")
            else:
                lines.append(f"(* {op} {target} *)")
        return lines

    def generate_program_structure(self, ir: dict, addresses: dict) -> str:
        dt_map = self.map_data_types(ir)
        var_lines = [
            f"    {sig['name']} AT {addresses[sig['name']]} : {dt_map[sig['data_type']]};"
            f"  (* {sig.get('description', '')} *)"
            for sig in ir["signal_definitions"]
        ]
        body = self.map_instructions(ir)
        meta = ir["project_metadata"]
        return (
            f"(* PLC-Forge → LS ELECTRIC (XGI) *)\n"
            f"(* Project: {meta['code']} - {meta['name']} *)\n"
            f"PROGRAM Main\n"
            f"VAR\n" + ("\n".join(var_lines) if var_lines else "    (* no I/O *)") + "\n"
            "END_VAR\n\n" + "\n".join(body) + "\nEND_PROGRAM\n"
        )

    def generate_tags(self, ir: dict, addresses: dict) -> str:
        dt_map = self.map_data_types(ir)
        rows = [
            [s["name"], addresses[s["name"]], dt_map[s["data_type"]], s.get("description", "")]
            for s in ir["signal_definitions"]
        ]
        return _csv(rows, ["Name", "Address", "DataType", "Comment"])

    def generate_io_csv(self, ir: dict, addresses: dict) -> str:
        rows = [
            [s["name"], s["signal_type"], addresses[s["name"]], s.get("description", "")]
            for s in ir["signal_definitions"]
        ]
        return _csv(rows, ["Name", "Signal", "Address", "Description"])

    def generate_alarm_mapping(self, ir: dict) -> str:
        rows = [
            [a["code"], a["condition"], a["priority"], a.get("latching", False)]
            for a in ir["alarms"]
        ]
        return _csv(rows, ["Code", "Condition", "Priority", "Latching"])

    def generate_hmi_tags(self, ir: dict) -> str:
        rows = [[t["name"], t["screen"]] for t in ir["hmi_tags"]]
        return _csv(rows, ["Tag", "Screen"])

    def generate_test_artifacts(self, ir: dict) -> str:
        rows = [[t["test_id"], t["phase"], t["category"]] for t in ir["test_requirements"]]
        return _csv(rows, ["TestID", "Phase", "Category"])

    def package_output(self, ir: dict) -> dict:
        self.validate_ir(ir)
        addresses = self.map_addresses(ir)
        files = {
            "Main.st": self.generate_program_structure(ir, addresses),
            "tags.csv": self.generate_tags(ir, addresses),
            "io.csv": self.generate_io_csv(ir, addresses),
            "alarms.csv": self.generate_alarm_mapping(ir),
            "hmi_tags.csv": self.generate_hmi_tags(ir),
            "tests.csv": self.generate_test_artifacts(ir),
        }
        mapping_report = {
            "vendor": self.vendor_name,
            "data_type_map": self.map_data_types(ir),
            "signal_count": len(ir["signal_definitions"]),
            "address_map": addresses,
            "alarm_count": len(ir["alarms"]),
            "interlock_count": len(ir["interlocks"]),
            "sequence_count": len(ir["sequences"]),
            "instruction_count": len(ir["logic_expressions"]),
        }
        return {"files": files, "mapping_report": mapping_report}
