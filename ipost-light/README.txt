What is ipost-light?

  - minimal Python + Jinja2 code to create arbitrarily large ACI configurations
  - ipost-light.py reads config parameters from file aci_credentials.py
  - aci_credentials.py provides APIC IP, admin username, admin password,
                                Jinja2 XML template filename, template variables

  - ipost-light.py renders the specified template with the variables supplied
  - the resulting XML data is then POSTed to the specified APIC
  - the URL to POST to is contained on the second line of the XML template (see below)


Dependencies:

  - requests
  - Jinja2


About aci_credentials.py

  - here is a valid aci_credentials.py file:

    apic_ip_address = "10.48.58.5"
    apic_admin_user = "admin"
    apic_admin_password = "password"
    template_file = "template.xml"
    template_params = "{'tnPrefix': 'iPost-light', 'tnQuant': 10}"

  - template_params must contain a dictionary of Jinja2 variables passed to the template
  - here is the template that matches those variables:

    <?xml version="1.0" encoding="UTF-8"?>
    <!-- /api/policymgr/mo/.xml -->
    <polUni>
    {% for tenant in range (0, tnQuant) %}
     <fvTenant name="{{tnPrefix}}-{{loop.index}}">
        <fvCtx name="main"/>
        <fvBD name="BD1" unicastRoute='no' unkMacUcastAct='flood' arpFlood='yes'>
            <fvSubnet ip="192.168.1.1/24"/>
            <fvRsCtx tnFvCtxName="main"/>
        </fvBD>
        <fvAp name="MyApp">
            <fvAEPg name="EPG1">
                <fvRsBd tnFvBDName="BD1"/>
            </fvAEPg>
        </fvAp>
     </fvTenant>
    {% endfor -%}
    </polUni>
 
  - this template contains a for loop that, with the supplied parameters, creates 10 tenants
  - note: loop.index is a Jinja2 'system' variable that simply records the current iteration



