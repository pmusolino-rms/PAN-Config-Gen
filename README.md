# Pan-Config-Gen
<html><head><meta charset="utf-8"><style>

</style><title>README</title></head><body><article class="markdown-body"><h1 id="fw-tenant-config-gen"><a name="user-content-fw-tenant-config-gen" href="#fw-tenant-config-gen" class="headeranchor-link" aria-hidden="true"><span class="headeranchor"></span></a>fw-tenant-config-gen</h1>
<p>Generates firewall configuration for Palo Alto devices based on Infoblox iPam information</p>
<p>In order to run this, you will need to meet the following pre-requisites:<br />
Python 2.7 or later<br />
pip<br />
Ablilty to connect to Infoblox master<br />
account able to access infoblox</p>
<p>The program uses basic python libraries, though you may need to install the following to squelch SSL certificate warnings<br />
as Self Signed certificates are used by the infoblox for https connections<br />
requests<br />
certifi<br />
urllib3<br />
pyopenssl<br />
pyasnl<br />
ndghttpsclient<br />
PrettyTable</p>
<p>Once Everything is installed, you will need to edit the config.ini and modify:<br />
IBLOX-MASTER for the dnsname or IP of the Infoblox master<br />
Username and Password for the credentials with access to the Infoblox master.</p>
</article></body></html>
