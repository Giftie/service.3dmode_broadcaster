import os, traceback, socket, time, sys, datetime
import xbmcaddon, xbmc

if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson
    
__addon__                = xbmcaddon.Addon( "service.3dmode_broadcaster" )
__language__             = __addon__.getLocalizedString
__scriptname__           = __addon__.getAddonInfo('name')
__scriptID__             = __addon__.getAddonInfo('id')
__author__               = __addon__.getAddonInfo('author')
__version__              = __addon__.getAddonInfo('version')

_3d_mode_query           = '''{"jsonrpc": "2.0", "method": "Settings.GetSettingValue",  "params": { "setting": "videoscreen.stereoscopicmode" }, "id": 1}'''

_3d_modes = [ "none",                   
              "over_under",            
              "side_by_side",           
              "anaglyph_cyan_red",      
              "anaglyph_green_magenta", 
              "interlaced",       
              "hardware",       
              "mono_2d",
              "",
              "",
              "",
              "",              
            ]
            
def log( text, severity=xbmc.LOGDEBUG ):
    if type( text).__name__=='unicode':
        text = text.encode('utf-8')
    message = ('[%s] - %s' % ( __scriptname__ ,text.__str__() ) )
    xbmc.log( msg=message, level=severity )

class _3D_handler():
    def __init__( self, *args, **kwargs ):
        self._3d_mode = 'mono'
    
    def _3d_mode_test( self ):
        result = xbmc.executeJSONRPC( _3d_mode_query )
        self._3d_mode = 'mono'
        json = simplejson.loads( result)
        if json.has_key('result'):
            if json[ 'result' ].has_key( 'value' ):
                self._3d_mode = _3d_modes[ int( json[ 'result' ][ 'value' ] ) ]
                self.broadcastUDP( "3D_Mode_Event<%s>" % self._3d_mode )        
        
    def broadcastUDP( self, data, port = 8278, ipaddress = '255.255.255.255' ): # XBMC's former HTTP API output port is 8278
        IPADDR = ipaddress
        PORTNUM = port
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        if hasattr(socket,'SO_BROADCAST'):
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.connect((IPADDR, PORTNUM))
        s.send(data)
        s.close()
    
class _Monitor( xbmc.Monitor ):
    def __init__(self, *args, **kwargs):
        xbmc.Monitor.__init__(self)
        self.enabled = kwargs['enabled']
        self.previous_method = ""
        
    def onNotification( self, sender, method, data):
        if sender == "xbmc":
            if method.startswith( "Player."):
                if method == "Player.OnPause":
                    log( 'Playback Paused' )
                elif method == "Player.OnPlay" and self.previous_method == "Player.OnPause":
                    log( 'Playback Resumed' )
                elif method == "Player.OnStop":
                    log( "Playback Stopped" )
                    xbmc.sleep( 500 )
                    _3D_handler()._3d_mode_test()
                elif method == "Player.OnPlay":
                    log( 'Playback Started' )
                    xbmc.sleep( 500 )
                    _3D_handler()._3d_mode_test()
                self.previous_method = method
            
if (__name__ == "__main__"):
    log( '3D Mode Broadcaster service script version %s started' % __version__ )
    Monitor = _Monitor( enabled = True )
    while ( not xbmc.abortRequested ):
        xbmc.sleep( 250 )
    del Monitor
    log( '3D Mode Broadcaster service script version %s stopped' % __version__ )