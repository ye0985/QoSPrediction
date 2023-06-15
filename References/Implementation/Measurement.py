import pydantic

class Measurement(pydantic.BaseModel):
    # Reference Signal Received Power (see 3GPP 36.214)
    signalStrength: int
    signalStrengthLTE: int
    networkProvider: str
    cellId: int
    # E-UTRA frequency band (see 3GPP 36.101)
    frequency: int

    #GEO Information
    lat: float
    #latC: str
    lon: float
    #lonC: str
    gpsNmea: str