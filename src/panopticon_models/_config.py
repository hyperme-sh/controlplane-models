from pydantic import ConfigDict

model_config_contracts = ConfigDict(
    str_strip_whitespace=True,
    validate_assignment=True,
    extra="forbid",
)
