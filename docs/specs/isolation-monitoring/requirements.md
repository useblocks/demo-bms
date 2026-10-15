# Isolation Monitoring — Requirements

```{req} The battery management system shall report an isolation fault when the isolation resistance falls below 500 Ω per volt of pack voltage
:id: REQ_ISOLATION_FAULT
:status: draft
:asil: B
:traces_to: US_ISOLATION_MONITORING

The battery management system shall set the isolation fault whenever the
measured isolation resistance between the high-voltage bus and the vehicle
chassis, divided by the measured pack voltage, is below 500 Ω/V — the minimum
ISO 6469-1 requires of a DC high-voltage system. The ratio, not the absolute
resistance, is what is compared, so the same barrier is judged more strictly
on a higher-voltage pack.
```
