# FranklinWH Direct Connect Bridge

An **unofficial** local REST + MQTT bridge and web UI for the FranklinWH aGate, using the
gateway's Direct Connect local API. It runs as a **Home Assistant add-on**, in **Docker**, or
standalone.

!!! warning "Unofficial software"
    Not affiliated with or endorsed by FranklinWH. Provided as-is, without warranty. Don't
    contact FranklinWH support about it; raise issues on
    [GitHub](https://github.com/david2069/franklinwh-direct-connect-bridge/issues).

## Start here

- **[User guide](guide/README.md):** the web UI, the scheduler, Home Assistant and MQTT,
  controls, energy and costs, several gateways.
- **Installing:** see
  [INSTALL.md](https://github.com/david2069/franklinwh-direct-connect-bridge/blob/main/INSTALL.md)
  and the add-on's
  [DOCS.md](https://github.com/david2069/franklinwh-direct-connect-bridge/blob/main/DOCS.md).
- **What changed:** the
  [CHANGELOG](https://github.com/david2069/franklinwh-direct-connect-bridge/blob/main/CHANGELOG.md).

## How it is built and released

- **[Test and release policy](TEST_POLICY.md):** the gates every release passes.
- **[Feature parity](PARITY_GAP.md)** with the FranklinWH Modbus Bridge and FWHAI.

## Related FranklinWH docs

- [franklinwh-cloud](https://david2069.github.io/franklinwh-cloud/): the cloud API library.
- [franklinwh-direct-connect-api](https://david2069.github.io/franklinwh-direct-connect-api/):
  the Direct Connect local API library this bridge is built on.
