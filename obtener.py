import requests

agentes =[('AgentAlpha', '192.168.1.10'),
('AgentBravo', '192.168.1.11'),
('AgentCharlie', '192.168.1.12'),
('AgentDelta', '192.168.1.13'),
('AgentEcho', '192.168.1.14'),
('AgentFoxtrot', '192.168.1.15'),
('AgentGolf', '192.168.1.16'),
('AgentHotel', '192.168.1.17'),
('AgentIndia', '192.168.1.18'),
('AgentJuliet', '192.168.1.19')]



url = "http://localhost:8000/agents/all/"
payload = {
  "Hostname": "Mateo murcia",
  "IP_address": "192.168.20.30"
}


response = requests.get(url, json=payload)

print(response.status_code)
print(response.json())


