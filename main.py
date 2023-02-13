import sys

def load_conf(path):
    f = open(path, "r")
    raw_data = f.read()
    raw_data = raw_data.split("\n")

    conf = {}

    header = raw_data[:4]
    conf_version = header[0].split("=")[1].split("-")
    version = conf_version[0][-3:]
    op=conf_version[4].split(":")[0]
    firm = f"v{conf_version[1]},{conf_version[3]} ({op})"

    conf['#version'] = version
    conf['#firm'] = firm

    i = 0
    current_stack = []

    def set_conf_based_on_stack(key, val):
        curr = conf[current_stack[0]]
        for i in range(1, len(current_stack)):
            if current_stack[i] not in curr:
                curr[current_stack[i]] = {}
            curr = curr[current_stack[i]]
        curr[key] = val.split(" ")[2:]

    for i in range(len(raw_data)):
        line = raw_data[i].strip()

        if line.startswith("set"):
            key = line.split(" ")[1]
            set_conf_based_on_stack(key, line)
        elif line.startswith("config") or line.startswith("edit"):
            conf[line] = {}
            current_stack.append(line)
        elif line.startswith("end") or line.startswith("next"):
            current_stack.pop()

        i += 1

    return conf

def fill_snippet(snippet, conf):
    set_var = lambda var, val: snippet.replace("%"+var+"%", val)

    # 1.1
    snippet = set_var('config-version', conf['#version'])
    snippet = set_var('version', conf['#version'])
    snippet = set_var('firm', conf['#firm'])

    #2.2
    port = conf['config system global'].get('admin-sport', ['x'])[0]
    snippet = set_var('acc',port)
    
    conf_admin = conf['config system admin']['edit "admin"']
    ip1 = conf_admin.get('trusthost1', ['0.0.0.0'])
    ip2 = conf_admin.get('trusthost2', ['0.0.0.0'])
    ip3 = conf_admin.get('trusthost3', ['0.0.0.0'])
    snippet = set_var('ip1', ip1[0])
    snippet = set_var('ip2', ip2[0])
    snippet = set_var('ip3', ip3[0])

    #2.3
    prima = conf['config system dns']['primary'][0]
    secon = conf['config system dns']['secondary'][0]
    domain = conf['config system dns'].get('domain', ['"-"'])[0][1:-1]
    snippet = set_var('spri', prima)
    snippet = set_var('ssec', secon)
    snippet = set_var('dom', domain)
    
    
    # 2.4
    table_interf = ""
    interf = conf['config system interface']
    for key in interf.keys():
        name = key[6:-1]
        if 'ip' in interf[key]:
            table_interf += "<tr>"

            # Interficie
            table_interf += f"<td>{name}</td>"

            # Alias            
            table_interf += f"<td>" + interf[key].get("alias", ['"-"'])[0][1:-1] + "</td>"

            # Adress/FQDN
            table_interf += "<td>" + interf[key]["ip"][0] + "</td>"

            # DHCPRelay
            table_interf += f"<td>" + interf[key].get("dhcp-relay-ip", ['"-"'])[0][1:-1] + "</td>"


            table_interf +="</tr>"
    snippet = set_var("table_interf", table_interf)

    #2.5
    count = len(conf['config router static'])
    router_static = conf['config router static']

    table_enr = ""
    for key in router_static.keys():
        table_enr += "<tr>"
        
        # Xarxa destí
        dst = router_static[key].get('dst', ['0.0.0.0', '0.0.0.0'])
        table_enr +=f"<td>" + dst[0] + "/" + dst[1] + "</td>"

        # GW
        table_enr += f"<td>" + router_static[key].get("gateway", ['0.0.0.0'])[0] + "</td>"

        # Interficie
        table_enr +=f"<td>" + router_static[key]["device"][0][1:-1] + "</td>"

        # Prioritat
        table_enr += f"<td>" + router_static[key].get("priority", ['-'])[0] + "</td>"

    snippet = set_var('defa', str(count))
    snippet = set_var('table_enr', table_enr)

    # Health-checks (optional, missing in some conf)
    if "config system link-monitor" in conf:
        snippet = set_var('sys_link_enabled', 'block')
        system_link = conf['config system link-monitor']

        table_health = ""
        for key in system_link.keys():
            table_health += "<tr>"

            # Xarxa destí
            dst = system_link[key].get('server', ['"0.0.0.0"'])
            table_health +=f"<td>" + dst[0][1:-1] + "</td>"

            # GW
            table_health += f"<td>" + system_link[key].get("gateway-ip", ['0.0.0.0'])[0] + "</td>"

            # Interficie
            table_health +=f"<td>" + system_link[key].get("srcintf")[0][1:-1] + "</td>"

            # Interval
            table_health +=f"<td>" + system_link[key].get("interval", '-')[0] + "</td>"

            # Failtime
            table_health +=f"<td>" + system_link[key].get("failtime", '-')[0] + "</td>"

            # Recovery
            table_health +=f"<td>" + system_link[key].get("recoverytime", '-')[0] + "</td>"


        snippet = set_var('table_health', table_health)
 
    return snippet

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Error: Missing arguments")
        print(f"Usage: {sys.argv[0]} conf_path *snippet_path")
        print(f"* -> optional")
        exit(1)

    # loading html snippet
    snippet_path = "snippet.html"
    if len(sys.argv) == 3:
        snippet_path = sys.argv[2]

    f = open(snippet_path, "r")
    snippet = f.read()

    # loading and parsing conf file
    conf_path = sys.argv[1]
    conf = load_conf(conf_path)

    snippet = fill_snippet(snippet, conf)

    # saving output
    save_path = conf_path.split(".")[0] + ".html"
    print("Saving " + save_path)
    f = open(save_path, "w")
    f.write(snippet)
    f.close()
