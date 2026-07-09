"""Spec Loader Service - Fetches product specifications from database."""
import logging
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.product import Product, ValidationStatus
from app.models.specification import ProductSpecification
from app.models.category import Category
from app.schemas.simulation import (
    BatterySpec,
    InverterSpec,
    PanelSpec,
    ChargeControllerSpec,
    ComponentSpecs,
    SystemValidationResult,
    ValidationError,
)

logger = logging.getLogger(__name__)


class SpecLoaderError(Exception):
    """Custom exception for spec loader errors."""
    pass


class SpecLoader:
    """Service for loading product specifications from database."""

    CATEGORY_MAP = {
        "battery": "battery",
        "inverter": "inverter",
        "solar_panel": "solar_panel",
        "charge_controller": "charge_controller",
    }

    # Spec key mappings for standardization
    BATTERY_SPEC_KEYS = {
        "voltage": ["voltage", "nominal_voltage", "system_voltage", "battery_voltage"],
        "capacity": ["capacity", "capacity_ah", "battery_capacity", "rated_capacity", "amp_hours"],
        "max_discharge_current": ["max_discharge_current", "max_discharge", "discharge_current", "continuous_discharge_current"],
        "max_charge_current": ["max_charge_current", "max_charge", "charge_current", "continuous_charge_current"],
        "cycle_life": ["cycle_life", "cycles", "expected_cycles", "cycle_count"],
        "round_trip_efficiency": ["round_trip_efficiency", "efficiency", "battery_efficiency"],
        "dod_max_safe": ["dod", "depth_of_discharge", "max_dod", "safe_dod"],
        "battery_type": ["battery_type", "chemistry", "type"],
    }

    INVERTER_SPEC_KEYS = {
        "rated_power": ["rated_power", "power", "output_power", "continuous_power", "watts"],
        "battery_voltage_range_min": ["battery_voltage_min", "min_battery_voltage", "voltage_min", "min_voltage"],
        "battery_voltage_range_max": ["battery_voltage_max", "max_battery_voltage", "voltage_max", "max_voltage"],
        "surge_power": ["surge_power", "surge", "peak_power", "startup_power", "surge_capacity"],
        "efficiency": ["efficiency", "inverter_efficiency", "conversion_efficiency"],
    }

    PANEL_SPEC_KEYS = {
        "wattage": ["wattage", "power", "rated_power", "panel_power", "max_power"],
        "Voc": ["voc", "open_circuit_voltage", "open_circuit_volts"],
        "Isc": ["isc", "short_circuit_current", "short_circuit_amps"],
        "Vmp": ["vmp", "max_power_voltage", "operating_voltage"],
        "Imp": ["imp", "max_power_current", "operating_current"],
    }

    CONTROLLER_SPEC_KEYS = {
        "max_input_voltage": ["max_input_voltage", "input_voltage", "pv_voltage", "max_voltage"],
        "rated_current": ["rated_current", "current", "controller_current", "amps"],
        "max_charge_current": ["max_charge_current", "charge_current", "max_current", "battery_current"],
        "efficiency": ["efficiency", "controller_efficiency", "conversion_efficiency"],
    }

    def __init__(self, db: Session):
        """Initialize the spec loader with a database session."""
        self.db = db

    def _get_spec_value(self, specs: list[ProductSpecification], keys: list[str]) -> Optional[str]:
        """Get spec value by trying multiple possible key names."""
        for key in keys:
            for spec in specs:
                if spec.spec_key.lower().replace("_", "").replace(" ", "") == key.lower().replace("_", "").replace(" ", ""):
                    return spec.spec_value
        return None

    def _parse_float(self, value: Optional[str]) -> Optional[float]:
        """Parse string value to float."""
        if value is None:
            return None
        try:
            # Remove common units and extra characters
            cleaned = value.lower().replace("v", "").replace("a", "").replace("w", "").replace("ah", "").replace("wh", "").replace("%", "").replace("ah", "").strip()
            return float(cleaned)
        except (ValueError, TypeError):
            return None

    def _parse_int(self, value: Optional[str]) -> Optional[int]:
        """Parse string value to int."""
        if value is None:
            return None
        try:
            return int(float(value.replace(",", "").strip()))
        except (ValueError, TypeError):
            return None

    def _load_product_with_validation(self, product_id: int, category_name: str) -> Product:
        """Load and validate a product from database."""
        product = self.db.query(Product).filter(
            and_(
                Product.id == product_id,
                Product.validation_status == ValidationStatus.APPROVED,
                Product.is_verified == True
            )
        ).first()

        if not product:
            raise SpecLoaderError(f"Product ID {product_id} not found, not verified, or not approved")

        # Verify category matches expected type
        if product.category.name != category_name:
            raise SpecLoaderError(
                f"Product ID {product_id} is a '{product.category.name}', "
                f"expected '{category_name}'"
            )

        return product

    def load_battery_specs(self, battery_id: int) -> BatterySpec:
        """Load battery specifications from database."""
        product = self._load_product_with_validation(battery_id, "battery")
        specs = product.specifications

        voltage = self._parse_float(self._get_spec_value(specs, self.BATTERY_SPEC_KEYS["voltage"]))
        capacity = self._parse_float(self._get_spec_value(specs, self.BATTERY_SPEC_KEYS["capacity"]))
        
        if voltage is None or capacity is None:
            raise SpecLoaderError(
                f"Battery ID {battery_id} missing required specs. "
                f"Need: voltage, capacity. Found voltage={voltage}, capacity={capacity}"
            )

        battery_type = self._get_spec_value(specs, self.BATTERY_SPEC_KEYS["battery_type"]) or "lithium"

        return BatterySpec(
            voltage=voltage,
            capacity_ah=capacity,
            max_discharge_current=self._parse_float(self._get_spec_value(specs, self.BATTERY_SPEC_KEYS["max_discharge_current"])),
            max_charge_current=self._parse_float(self._get_spec_value(specs, self.BATTERY_SPEC_KEYS["max_charge_current"])),
            cycle_life=self._parse_int(self._get_spec_value(specs, self.BATTERY_SPEC_KEYS["cycle_life"])),
            round_trip_efficiency=self._parse_float(self._get_spec_value(specs, self.BATTERY_SPEC_KEYS["round_trip_efficiency"])) or 0.85,
            dod_max_safe=self._parse_float(self._get_spec_value(specs, self.BATTERY_SPEC_KEYS["dod_max_safe"])) or 0.80,
            battery_type=battery_type,
        )

    def load_inverter_specs(self, inverter_id: int) -> InverterSpec:
        """Load inverter specifications from database."""
        product = self._load_product_with_validation(inverter_id, "inverter")
        specs = product.specifications

        rated_power = self._parse_float(self._get_spec_value(specs, self.INVERTER_SPEC_KEYS["rated_power"]))
        
        if rated_power is None:
            raise SpecLoaderError(
                f"Inverter ID {inverter_id} missing required spec 'rated_power'. "
                f"Found: {[s.spec_key for s in specs]}"
            )

        return InverterSpec(
            rated_power=rated_power,
            battery_voltage_range_min=self._parse_float(self._get_spec_value(specs, self.INVERTER_SPEC_KEYS["battery_voltage_range_min"])),
            battery_voltage_range_max=self._parse_float(self._get_spec_value(specs, self.INVERTER_SPEC_KEYS["battery_voltage_range_max"])),
            surge_power=self._parse_float(self._get_spec_value(specs, self.INVERTER_SPEC_KEYS["surge_power"])) or rated_power * 1.5,
            efficiency=self._parse_float(self._get_spec_value(specs, self.INVERTER_SPEC_KEYS["efficiency"])) or 0.95,
        )

    def load_panel_specs(self, panel_id: int) -> PanelSpec:
        """Load solar panel specifications from database."""
        product = self._load_product_with_validation(panel_id, "solar_panel")
        specs = product.specifications

        wattage = self._parse_float(self._get_spec_value(specs, self.PANEL_SPEC_KEYS["wattage"]))
        
        if wattage is None:
            raise SpecLoaderError(
                f"Panel ID {panel_id} missing required spec 'wattage'. "
                f"Found: {[s.spec_key for s in specs]}"
            )

        return PanelSpec(
            wattage=wattage,
            Voc=self._parse_float(self._get_spec_value(specs, self.PANEL_SPEC_KEYS["Voc"])),
            Isc=self._parse_float(self._get_spec_value(specs, self.PANEL_SPEC_KEYS["Isc"])),
            Vmp=self._parse_float(self._get_spec_value(specs, self.PANEL_SPEC_KEYS["Vmp"])),
            Imp=self._parse_float(self._get_spec_value(specs, self.PANEL_SPEC_KEYS["Imp"])),
        )

    def load_charge_controller_specs(self, controller_id: int) -> ChargeControllerSpec:
        """Load charge controller specifications from database."""
        product = self._load_product_with_validation(controller_id, "charge_controller")
        specs = product.specifications

        return ChargeControllerSpec(
            max_input_voltage=self._parse_float(self._get_spec_value(specs, self.CONTROLLER_SPEC_KEYS["max_input_voltage"])),
            rated_current=self._parse_float(self._get_spec_value(specs, self.CONTROLLER_SPEC_KEYS["rated_current"])),
            max_charge_current=self._parse_float(self._get_spec_value(specs, self.CONTROLLER_SPEC_KEYS["max_charge_current"])),
            efficiency=self._parse_float(self._get_spec_value(specs, self.CONTROLLER_SPEC_KEYS["efficiency"])) or 0.95,
        )

    def load_all_specs(self, battery_id: int, inverter_id: int, panel_id: int, controller_id: int) -> ComponentSpecs:
        """Load all component specifications from database."""
        return ComponentSpecs(
            battery=self.load_battery_specs(battery_id),
            inverter=self.load_inverter_specs(inverter_id),
            panel=self.load_panel_specs(panel_id),
            charge_controller=self.load_charge_controller_specs(controller_id),
        )

    def validate_system(self, battery_id: int, inverter_id: int, panel_id: int, controller_id: int) -> SystemValidationResult:
        """Validate that all components are compatible."""
        errors = []
        warnings = []

        try:
            specs = self.load_all_specs(battery_id, inverter_id, panel_id, controller_id)
        except SpecLoaderError as e:
            errors.append(ValidationError(
                field="product_id",
                message=str(e),
                suggestion="Ensure all product IDs are valid and products are verified"
            ))
            return SystemValidationResult(valid=False, errors=errors, warnings=warnings)

        # Validate voltage compatibility
        battery_voltage = specs.battery.voltage
        inv_min = specs.inverter.battery_voltage_range_min
        inv_max = specs.inverter.battery_voltage_range_max
        
        if inv_min and inv_max:
            if battery_voltage < inv_min:
                errors.append(ValidationError(
                    field="battery.voltage",
                    message=f"Battery voltage ({battery_voltage}V) is below inverter minimum ({inv_min}V)",
                    suggestion=f"Choose a battery with voltage >= {inv_min}V or an inverter that accepts {battery_voltage}V"
                ))
            elif battery_voltage > inv_max:
                errors.append(ValidationError(
                    field="battery.voltage",
                    message=f"Battery voltage ({battery_voltage}V) exceeds inverter maximum ({inv_max}V)",
                    suggestion=f"Choose a battery with voltage <= {inv_max}V or an inverter that accepts {battery_voltage}V"
                ))
            else:
                warnings.append(f"Battery voltage ({battery_voltage}V) is within inverter range ({inv_min}-{inv_max}V)")
        elif inv_min and battery_voltage < inv_min:
            warnings.append(f"Inverter minimum battery voltage is {inv_min}V, battery is {battery_voltage}V")
        elif inv_max and battery_voltage > inv_max:
            warnings.append(f"Inverter maximum battery voltage is {inv_max}V, battery is {battery_voltage}V")

        # Validate charge controller current rating
        cc_current = specs.charge_controller.rated_current
        bat_max_charge = specs.battery.max_charge_current
        
        if cc_current and bat_max_charge:
            if cc_current < bat_max_charge * 0.5:
                warnings.append(
                    f"Charge controller rated current ({cc_current}A) may be undersized for battery "
                    f"max charge current ({bat_max_charge}A)"
                )

        return SystemValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
