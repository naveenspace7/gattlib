import logging

from gattlib import *
from .gatt import GattService, GattCharacteristic

CONNECTION_OPTIONS_LEGACY_BDADDR_LE_PUBLIC  = (1 << 0)
CONNECTION_OPTIONS_LEGACY_BDADDR_LE_RANDOM  = (1 << 1)
CONNECTION_OPTIONS_LEGACY_BT_SEC_LOW        = (1 << 2)
CONNECTION_OPTIONS_LEGACY_BT_SEC_MEDIUM     = (1 << 3)
CONNECTION_OPTIONS_LEGACY_BT_SEC_HIGH       = (1 << 4)

CONNECTION_OPTIONS_LEGACY_DEFAULT = \
        CONNECTION_OPTIONS_LEGACY_BDADDR_LE_PUBLIC | \
        CONNECTION_OPTIONS_LEGACY_BDADDR_LE_RANDOM | \
        CONNECTION_OPTIONS_LEGACY_BT_SEC_LOW


class Device:

    def __init__(self, adapter, addr, name=None):
        self._adapter = adapter
        self._addr = addr
        self._name = name
        self._connection = c_void_p(None)

    @property
    def id(self):
        return self._addr.decode("utf-8")

    @property
    def connection(self):
        return self._connection

    def connect(self, options=CONNECTION_OPTIONS_LEGACY_DEFAULT):
        adapter_name = self._adapter.name

        self._connection = gattlib.gattlib_connect(adapter_name, self._addr, options)

    def disconnect(self):
        gattlib.gattlib_disconnect(self._connection)

    def discover(self):
        #
        # Discover GATT Services
        #
        _services = POINTER(GattlibPrimaryService)()
        _services_count = c_int(0)
        ret = gattlib_discover_primary(self._connection, byref(_services), byref(_services_count))

        self._services = {}
        for i in range(0, _services_count.value):
            service = GattService(self, _services[i])
            self._services[service.short_uuid] = service

            logging.debug("Service UUID:0x%x" % service.short_uuid)

        #
        # Discover GATT Characteristics
        #
        _characteristics = POINTER(GattlibCharacteristic)()
        _characteristics_count = c_int(0)
        ret = gattlib_discover_char(self._connection, byref(_characteristics), byref(_characteristics_count))

        self._characteristics = {}
        for i in range(0, _characteristics_count.value):
            characteristic = GattCharacteristic(self, _characteristics[i])
            self._characteristics[characteristic.short_uuid] = characteristic

            logging.debug("Characteristic UUID:0x%x" % characteristic.short_uuid)

        return ret

    @property
    def services(self):
        if not hasattr(self, '_services'):
            logging.warning("Start GATT discovery implicitly")
            self.discover()

        return self._services

    @property
    def characteristics(self):
        if not hasattr(self, '_characteristics'):
            logging.warning("Start GATT discovery implicitly")
            self.discover()

        return self._characteristics

    def __str__(self):
        name = self._name
        if name:
            return str(name)
        else:
            return str(self._addr)
