import re

from Products.DataCollector.plugins.CollectorPlugin import SnmpPlugin, GetMap, GetTableMap
from Products.DataCollector.plugins.DataMaps import MultiArgs, ObjectMap, RelationshipMap


class StandardUPS(SnmpPlugin):

    snmpGetMap = GetMap({
        '.1.3.6.1.2.1.33.1.1.1.0': 'upsIdentManufacturer',
        '.1.3.6.1.2.1.33.1.1.2.0': 'upsIdentModel',
        '.1.3.6.1.2.1.33.1.1.5.0': 'upsIdentName',
    })

    snmpGetTableMaps = (
        GetTableMap(
            'upsInputTable', '.1.3.6.1.2.1.33.1.3.3.1', {
                                        '.2': 'upsInputFrequency',
                                        '.3': 'upsInputVoltage',
                                        '.4': 'upsInputCurrent',
                                        '.5': 'upsInputTruePower',
                                        }
                    ),
        GetTableMap(
            'upsOutputTable', '.1.3.6.1.2.1.33.1.4.4.1', {
                                        '.2': 'upsOutputVoltage',
                                        '.3': 'upsOutputCurrent',
                                        '.4': 'upsOutputPower',
                                        '.5': 'upsOutputPercentLoad',
                                        }
                    ),
        GetTableMap(
            'upsBypassTable', '.1.3.6.1.2.1.33.1.5.3.1', {
                                        '.2': 'upsBypassVoltage',
                                        '.3': 'upsBypassCurrent',
                                        '.4': 'upsBypassPower',
                                        }
                    ),
        )

    def process(self, device, results, log):
        log.info("Processing %s for device %s", self.name(), device.id)
        getdata, tabledata = results
        if not getdata:
            log.warn(' No SNMP response from %s for the %s plugin ' % (device.id, self.name()))
            return
        log.info('getdata: {}'.format(getdata))
        log.info('tabledata: {}'.format(tabledata))

        # Device
        maps = []
        om = ObjectMap()
        try:
            om.setHWProductKey = getdata['upsIdentModel']
            try:
                r = re.match('ID: (.*) ,.*', getdata['upsIdentName'])
                if r:
                    om.setHWSerialNumber = r.group(1)
            except errorInfo:
                log.warn(' Error in StandardUPS modeler plugin %s', errorInfo)
        except (KeyError, IndexError, AttributeError, TypeError), errorInfo:
            log.warn(' Error in StandardUPS modeler plugin %s', errorInfo)

        maps.append(om)
        maps.append(self.get_inputs(results, log))
        maps.append(self.get_outputs(results, log))
        maps.append(self.get_bypasses(results, log))
        log.debug('Process maps: {}'.format(maps))
        return maps

    def get_inputs(self, results, log):
        input_maps = []
        getdata, tabledata = results
        for snmpindex, row in tabledata.get('upsInputTable', {}).items():
            inputData = {}
            snmpindex = snmpindex.strip('.')
            name = 'Input {}'.format(snmpindex)
            inputData['id'] = self.prepId(name)
            inputData['title'] = name
            inputData['snmpindex'] = snmpindex
            input_maps.append(inputData)

        inputRelMap = RelationshipMap(
            relname='upsinputs',
            compname='',
            modname='ZenPacks.community.StandardUPS.UPSInput',
            objmaps=input_maps,
            )
        return inputRelMap

    def get_outputs(self, results, log):
        output_maps = []
        getdata, tabledata = results
        for snmpindex, row in tabledata.get('upsOutputTable', {}).items():
            outputData = {}
            snmpindex = snmpindex.strip('.')
            name = 'Output {}'.format(snmpindex)
            outputData['id'] = self.prepId(name)
            outputData['title'] = name
            outputData['snmpindex'] = snmpindex
            output_maps.append(outputData)

        outputRelMap = RelationshipMap(
            relname='upsoutputs',
            compname='',
            modname='ZenPacks.community.StandardUPS.UPSOutput',
            objmaps=output_maps,
            )
        return outputRelMap

    def get_bypasses(self, results, log):
        bypass_maps = []
        getdata, tabledata = results
        for snmpindex, row in tabledata.get('upsBypassTable', {}).items():
            bypassData = {}
            snmpindex = snmpindex.strip('.')
            name = 'Bypass {}'.format(snmpindex)
            bypassData['id'] = self.prepId(name)
            bypassData['title'] = name
            bypassData['snmpindex'] = snmpindex
            bypass_maps.append(bypassData)

        bypassRelMap = RelationshipMap(
            relname='upsbyPasss',
            compname='',
            modname='ZenPacks.community.StandardUPS.UPSByPass',
            objmaps=bypass_maps,
            )
        return bypassRelMap
