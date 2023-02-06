import configparser

def load_conf(path):
    f = open("FW_1238.conf", "r")
    raw_data = f.read()
    raw_data = raw_data.split("\n")

    conf = {}

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



if __name__ == "__main__":
    f = open("snippet.html", "r")
    snippet = f.read()

    conf = load_conf("FW_1238.conf")

    interf = conf['config system interface']
    for key in interf.keys():
        name = key[6:-1]
        if name.startswith("port"):
            print(f"----------------------")
            print(f"interficie: {name}")
            print(f"alias: " + interf[key]["alias"][0][1:-1])
            print(f"ip: " + interf[key]["ip"][0])
            if "dhcp-relay-ip" in interf[key]:
                print(f"relay: " + interf[key]["dhcp-relay-ip"][0])
            else:
                print("relay: -")

    print("Saving FW_1238.html")
    f = open("FW_1238.html", "w")
    f.write(snippet)
    f.close()
