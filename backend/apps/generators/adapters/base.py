"""Vendor Adapter 인터페이스 (PRD §21).

모든 제조사 어댑터는 이 계약을 구현한다. 입력은 Vendor Independent IR(§20).
"""

from abc import ABC, abstractmethod


class VendorAdapter(ABC):
    vendor_key: str = ""
    vendor_name: str = ""

    @abstractmethod
    def validate_ir(self, ir: dict) -> None:
        """IR을 벤더 관점에서 추가 검증한다 (스키마 검증은 ir.validate_ir가 선행)."""

    @abstractmethod
    def map_data_types(self, ir: dict) -> dict:
        """벤더 중립 데이터 타입 → 벤더 데이터 타입 매핑."""

    @abstractmethod
    def map_addresses(self, ir: dict) -> dict:
        """신호 → 벤더 주소(예: %IX0.0) 매핑."""

    @abstractmethod
    def map_instructions(self, ir: dict) -> list:
        """LogicExpression → 벤더 명령/구문 매핑."""

    @abstractmethod
    def generate_program_structure(self, ir: dict, addresses: dict) -> str:
        """Structured Text 프로그램 본문 생성."""

    @abstractmethod
    def generate_tags(self, ir: dict, addresses: dict) -> str:
        """Tag CSV 생성."""

    @abstractmethod
    def generate_alarm_mapping(self, ir: dict) -> str:
        """Alarm CSV 생성."""

    @abstractmethod
    def generate_hmi_tags(self, ir: dict) -> str:
        """HMI Tag CSV 생성."""

    @abstractmethod
    def generate_test_artifacts(self, ir: dict) -> str:
        """테스트 요구 CSV 생성."""

    @abstractmethod
    def package_output(self, ir: dict) -> dict:
        """전체 산출물을 {파일명: 내용} + mapping_report로 묶는다."""
