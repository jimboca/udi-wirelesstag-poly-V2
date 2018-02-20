"""
This is a NodeServer for CAO Gadgets Wireless Sensor Tags for Polyglot v2 written in Python3
by JimBoCA jimboca3@gmail.com
"""
import polyinterface
import sys
import time
from wt_funcs import id_to_address,myfloat

LOGGER = polyinterface.LOGGER

class wTag(polyinterface.Node):
    """
    This is the class that all the Nodes will be represented by. You will add this to
    Polyglot/ISY with the controller.addNode method.

    Class Variables:
    self.primary: String address of the Controller node.
    self.parent: Easy access to the Controller Class from the node itself.
    self.address: String address of this Node 14 character limit. (ISY limitation)
    self.added: Boolean Confirmed added to ISY

    Class Methods:
    start(): This method is called once polyglot confirms the node is added to ISY.
    setDriver('ST', 1, report = True, force = False):
        This sets the driver 'ST' to 1. If report is False we do not report it to
        Polyglot/ISY. If force is True, we send a report even if the value hasn't changed.
    reportDrivers(): Forces a full update of all drivers to Polyglot/ISY.
    query(): Called when ISY sends a query request to Polyglot for this specific node
    """
    def __init__(self, controller, primary, address=None, name=None, tag_type=None, tdata=None, node_data=None):
        """
        Optional.
        Super runs all the parent class necessities. You do NOT have
        to override the __init__ method, but if you do, you MUST call super.

        :param controller: Reference to the Controller class
        :param primary: Controller address
        :param address: This nodes address
        :param name: This nodes name
        """
        if node_data is not None:
            # An existing node,
            self.is_new = False
            # We need to pull tag_type from GV1 for existing tags.
            for driver in node_data['drivers']:
                if driver['driver'] == 'GV1':
                    self.tag_type = driver['value']
                elif driver['driver'] == 'GPV':
                    self.tag_id   = driver['value']
        elif address is None or name is None or tag_type is None:
            if tdata is None:
                self.l_error('__init__',"address ({0}), name ({1}), and type ({2}) must be specified when tdata is None".format(address,tdata,type))
                return False
            self.is_new = True
            self.tdata = tdata
            self.tag_type = tdata['tagType']
            self.tag_id   = tdata['slaveId']
            self.uuid  = tdata['uuid']
            address    = id_to_address(self.uuid)
            name       = tdata['name']
        self.name = name
        self.tdata = tdata
        self.id = 'wTag' + str(self.tag_type)
        self.l_info('__init__','address={0} name={1} type={2}'.format(address,name,tag_type))
        super(wTag, self).__init__(controller, primary, address, name)

    def start(self):
        """
        Optional.
        This method is run once the Node is successfully added to the ISY
        and we get a return result from Polyglot. Only happens once.
        """
        self.setDriver('ST', 1)
        self.primary_n = self.controller.nodes[self.primary]
        # Alwasy set driver from tag type
        self.set_tag_type(self.tag_type)
        self.set_tag_id(self.tag_id)
        self.set_from_tag_data()
        self.query()

    def query(self):
        """
        Called by ISY to report all drivers for this node. This is done in
        the parent class, so you don't need to override this method unless
        there is a need.
        """
        self.reportDrivers()

    def l_info(self, name, string):
        LOGGER.info("%s:%s:%s: %s" %  (self.id,self.name,name,string))
        
    def l_error(self, name, string):
        LOGGER.error("%s:%s:%s: %s" % (self.id,self.name,name,string))
        
    def l_warning(self, name, string):
        LOGGER.warning("%s:%s:%s: %s" % (self.id,self.name,name,string))
        
    def l_debug(self, name, string):
        LOGGER.debug("%s:%s:%s: %s" % (self.id,self.name,name,string))

    """
    Set Functions
    """
    def set_from_tag_data(self):
        if self.tdata is None: return False
        if 'temperature' in self.tdata:
            self.set_temp(self.tdata['temperature'])
        if 'batteryVolt' in self.tdata:
            self.set_batv(self.tdata['batteryVolt'])
        if 'batteryRemaining' in self.tdata:
            self.set_batp(float(self.tdata['batteryRemaining']) * 100)
        if 'lux' in self.tdata:
            self.set_lux(self.tdata['lux'])
        if 'hum' in self.tdata:
            self.set_hum(self.tdata['hum'])
        if 'lit' in self.tdata:
            self.set_lit(self.tdata['lit'])

    # This is the tag_type number, we don't really need to show it, but 
    # we need the info when recreating the tags from the config.
    def set_tag_type(self,value,force=False):
        if not force and hasattr(self,"tag_type") and self.tag_type == value:
            return True
        self.tag_type = value
        self.setDriver('GV1', value)
        
    def set_tag_id(self,value,force=False):
        if not force and hasattr(self,"tag_id") and self.tag_id == value:
            return True
        self.tag_id = value
        self.setDriver('GVP', value)
        
    def set_temp(self,value,force=False):
        if self.primary_n.degFC == 0:
            value = myfloat(value,2)
        else:
            # Convert C to F
            value = myfloat(float(value) * 1.8 + 32.0,2)
        if not force and hasattr(self,"temp") and self.temp == value:
            return True
        self.temp = value
        self.setDriver('CLITEMP', self.temp)
        
    def set_hum(self,value,force=False):
        value = int(value)
        if not force and hasattr(self,"hum") and self.hum == value:
            return True
        self.hum = value
        self.setDriver('CLIHUM', self.hum)
 
    def set_lit(self,value,force=False):
        value = int(value)
        if not force and hasattr(self,"lit") and self.lit == value:
            return True
        self.lit = value
        self.setDriver('GV7', value)
      
    def set_lux(self,value,force=False):
        value = int(value)
        if not force and hasattr(self,"lux") and self.lux == value:
            return True
        self.lux = value
        self.setDriver('LUMIN', self.lux)
        
    def set_batp(self,value,force=False):
        value = myfloat(value,2)
        if not force and hasattr(self,"batp") and self.batp == value:
            return True
        self.batp = value
        self.setDriver('BATLVL', self.batp)
        
    def set_batv(self,value,force=False):
        value = myfloat(value,3)
        if not force and hasattr(self,"batv") and self.batv == value:
            return True
        self.batv = value
        self.setDriver('CV', self.batv)
        
    def set_motion(self,value,force=False):
        if not force and hasattr(self,"motion") and self.motion == value:
            return True
        self.motion = value
        self.setDriver('GV2', self.motion)
        
    def set_orien(self,value,force=False):
        value = myfloat(value,1)
        if not force and hasattr(self,"orien") and self.orien == value:
            return True
        self.orien = value
        self.setDriver('GV3', self.orien)
        
    def set_xaxis(self,value,force=False):
        value = int(value)
        if not force and hasattr(self,"xaxis") and self.xaxis == value:
            return True
        self.xaxis = value
        self.setDriver('GV4', self.xaxis)
        
    def set_yaxis(self,value,force=False):
        value = int(value)
        if not force and hasattr(self,"yaxis") and self.yaxis == value:
            return True
        self.yaxis = value
        self.setDriver('GV5', self.yaxis)
        
    def set_zaxis(self,value,force=False):
        value = int(value)
        if not force and hasattr(self,"zaxis") and self.zaxis == value:
            return True
        self.zaxis = value
        self.setDriver('GV6', self.zaxis)
        
    """
    """

    def cmd_set_on(self, command):
        """
        Example command received from ISY.
        Set DON on MyNode.
        Sets the ST (status) driver to 1 or 'True'
        """
        self.setDriver('ST', 1)

    def cmd_set_off(self, command):
        """
        Example command received from ISY.
        Set DOF on MyNode
        Sets the ST (status) driver to 0 or 'False'
        """
        self.setDriver('ST', 0)

    
    """
    {"d":[
    {
      "__type":"MyTagList.Tag2",
      "managerName":"Rangwood",
      "mac":"0E994A04A300",
      "dbid":1,
      "mirrors":[],
      "notificationJS":"",
      "name":"Garage Freezer",
      "uuid":"7911937f-c758-4b88-a33a-0761ed284f29",
      "comment":"",
      "slaveId":0,
      "tag_type":12,
      "lastComm":131628820472086602,
      "alive":true,
      "signaldBm":-64,
      "batteryVolt":3.3048022377777824,
      "beeping":false,
      "lit":false,
      "migrationPending":false,
      "beepDurationDefault":15,
      "eventState":0,
      "tempEventState":1,
      "OutOfRange":false,
      "lux":0,
      "temperature":-21.421393532917921,
      "tempCalOffset":0,
      "capCalOffset":0,
      "image_md5":null,
      "cap":0,
      "capRaw":0,
      "az2":0,
      "capEventState":0,
      "lightEventState":0,
      "shorted":false,
      "thermostat":null,
      "playback":null,
      "postBackInterval":3600,
      "rev":12,
      "version1":1,
      "freqOffset":12828,
      "freqCalApplied":0,
      "reviveEvery":4,
      "oorGrace":2,
      "LBTh":2.5,
      "enLBN":true,
      "txpwr":204,
      "rssiMode":false,
      "ds18":false,
      "v2flag":16,
      "batteryRemaining":1.13 # = 113% ?
    }]}
    """

    drivers = [
        {'driver': 'ST',      'value': 0, 'uom': 2},
        {'driver': 'GPV',     'value': 0, 'uom': 56}, # tag_id
        {'driver': 'GV1',     'value': 0, 'uom': 56}, # tag_type:    
        {'driver': 'CLITEMP', 'value': 0, 'uom': 17}, # temp:   Curent temperature (17=F 4=C)
        {'driver': 'BATLVL',  'value': 0, 'uom': 51}, # batp:   Battery percent (51=percent)
        {'driver': 'LUMIN',   'value': 0, 'uom': 36}, # lux:    Lux (36=lux)
        {'driver': 'CLIHUM',  'value': 0, 'uom': 21}, # hum:    Humidity (21 = absolute humidity)
        {'driver': 'CV',      'value': 0, 'uom': 72}, # batv:   Battery Voltag 72=Volt
        {'driver': 'GV2',     'value': 0, 'uom': 25}, # motion: Might use True, False, Open for door mode?
        {'driver': 'GV3',     'value': 0, 'uom': 56}, # orien:  Orientation
        {'driver': 'GV4',     'value': 0, 'uom': 56}, # xaxis:  X-Axis
        {'driver': 'GV5',     'value': 0, 'uom': 56}, # yasis:  Y-Axis
        {'driver': 'GV6',     'value': 0, 'uom': 56}, # zaxis:  Z-Asis
        {'driver': 'GV7',     'value': 0, 'uom': 78}  # lit:    Lighth 78=off/off
    ]

    commands = {
        'DON': cmd_set_on,
        'DOF': cmd_set_off,
    }
