from core.redis   import rds
from core.triage  import Triage
from core.parser  import ScanParser, ConfParser

class Rule:
  def __init__(self):
    self.rule = 'CFG_DFFF'
    self.rule_severity = 0
    self.rule_description = 'Checks if CORS Headers support Wildcard Origins'
    self.rule_confirm = 'Webserver is allowing all domains in CORS'
    self.rule_details = ''
    self.rule_mitigation = '''Consider hardening your CORS Policy to define specific Origins'''
    self.intensity = 1
    
  def check_rule(self, ip, port, values, conf):
    c = ConfParser(conf)
    t = Triage()
    p = ScanParser(port, values)
    
    domain  = p.get_domain()
    module  = p.get_module()
    product  = p.get_product()
    
    if 'http' not in module:
      return
    
    resp = None
    
    if domain:
      resp = t.http_request(domain, port)
    else:
      resp = t.http_request(ip, port)
    
    if resp is None:
      return
    
    for header, value in resp.headers.items():
      if header.lower() == 'access-control-allow-origin' and value == '*':
        self.rule_details = 'Access-Control-Allow-Origin is set to: *'
        js_data = {
                'ip':ip,
                'port':port,
                'domain':domain,
                'rule_id':self.rule,
                'rule_sev':self.rule_severity,
                'rule_desc':self.rule_description,
                'rule_confirm':self.rule_confirm,
                'rule_details':self.rule_details,
                'rule_mitigation':self.rule_mitigation
              }
        rds.store_vuln(js_data)
        return
  
    return