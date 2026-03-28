"""Unit tests for TSValidator."""
import pytest
from domain.models import FrequencyData
from domain.validators import TSValidator


def test_valid_ts():
    fd = FrequencyData(frequencies=[-150.0, 300.0, 450.0])
    warnings = TSValidator().check_frequency(fd)
    assert warnings == []


def test_no_imaginary():
    fd = FrequencyData(frequencies=[100.0, 200.0, 300.0])
    warnings = TSValidator().check_frequency(fd)
    assert len(warnings) == 1
    assert "0個" in warnings[0]


def test_two_imaginary():
    fd = FrequencyData(frequencies=[-150.0, -80.0, 300.0])
    warnings = TSValidator().check_frequency(fd)
    assert len(warnings) == 1
    assert "2個" in warnings[0]
