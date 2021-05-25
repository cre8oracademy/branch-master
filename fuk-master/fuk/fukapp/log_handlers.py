import amonpy
import logging

# Log handlers need to be in their own file, 
# or there are circular import problems (see logging docs)


amonpy.config.address="http://127.0.0.1:2464"
# This is different for each server, so needs to be sourced from
# settings, once we have found a way to deal with circular import
# problem above. Use with caution!
amonpy.config.secret_key="C1RFrEGX3BgAphMCxAwGHvONlm1DctqfIGkE16EwHBU"

class AmonLogHandler(logging.Handler):
  def emit(self, record):
    if hasattr(record, 'args'):
      amonpy.log(record.args)