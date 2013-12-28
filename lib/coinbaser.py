import util
from twisted.internet import defer

import settings

import lib.logger
log = lib.logger.get_logger('coinbaser')

# TODO: Add on_* hooks in the app
    
class SimpleCoinbaser(object):
    '''This very simple coinbaser uses constant bitcoin address
    for all generated blocks.'''
    
    def __init__(self, bitcoin_rpc, address):
	log.debug("Got to coinbaser")
	# Fire Callback when the coinbaser is ready
	self.on_load = defer.Deferred()

        self.address = address
	self.is_valid = False

	self.bitcoin_rpc = bitcoin_rpc
	self._validate()

    def _validate(self):
	d = self.bitcoin_rpc.validateaddress(self.address)
	if settings.COINDAEMON_Reward == 'POW':
        	d.addCallback(self._POW_address_check)
	else:   d.addCallback(self._POS_address_check)
	d.addErrback(self._failure)

    def _POW_address_check(self, result):
	if result['isvalid'] == True:
           log.debug("Is Valid = %s" % result['isvalid'])
           log.debug("Address = %s " % result['address'])
           log.debug("Is Script = %s" % result['isscript'])
	   log.debug("PubKey = %s " % result['pubkey'])
	   log.debug("Is Compressed = %s " % result['iscompressed'])
	   log.debug("Account = %s " % result['account'])
	   self.address = result['address']
           if result['isvalid'] and result['ismine']:
              self.is_valid = True
      	      log.info("Wallet address '%s' is valid" % self.address)
       
      	      if not self.on_load.called:
              	  self.on_load.callback(True)
     
      	   elif result['isvalid'] and settings.ALLOW_NONLOCAL_WALLET == True :
      	        self.is_valid = True
      	        log.warning("!!! Wallet  address '%s' is valid BUT it is not local" % self.address)
     
       	        if not self.on_load.called:
                     self.on_load.callback(True)
                
      	else:
      	   self.is_valid = False
      	   log.exception("Wallet address '%s' is NOT valid!" % self.address)

    def _POS_address_check(self, result):
	if result['isvalid'] == True:
           log.debug("Is Valid = %s" % result['isvalid'])
           log.debug("Address = %s " % result['address'])
           log.debug("Is Script = %s" % result['isscript'])
           log.debug("PubKey = %s " % result['pubkey'])
           log.debug("Is Compressed = %s " % result['iscompressed'])
           log.debug("Account = %s " % result['account'])
           self.pubkey = result['pubkey']
           if result['isvalid'] and result['ismine']:
              self.is_valid = True
              log.info("Wallet address '%s' is valid" % self.address)

              if not self.on_load.called:
                  self.on_load.callback(True)

           elif result['isvalid'] and settings.ALLOW_NONLOCAL_WALLET == True :
                self.is_valid = True
                log.warning("!!! Wallet  address '%s' is valid BUT it is not local" % self.address)

                if not self.on_load.called:
                     self.on_load.callback(True)

        else:
           self.is_valid = False
           log.exception("Wallet address '%s' is NOT valid!" % self.address)

    #def on_new_block(self):
    #    pass
    
    #def on_new_template(self):
    #    pass
    def _failure(self, failure):
           log.exception("Cannot validate Wallet address '%s'" % self.address)
           raise
    
    def get_script_pubkey(self):
	if settings.COINDAEMON_Reward == 'POW':
	   self._validate()
	   return util.script_to_address(self.address)
 	else: return util.script_to_pubkey(self.pubkey)    
                   
    def get_coinbase_data(self):
        return ''
