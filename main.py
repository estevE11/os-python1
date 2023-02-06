import sys

def load_conf(path):
    f = open(path, "r")
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
    if len(sys.argv) < 2:
        print(f"Error: Missing arguments")
        print(f"Usage: {sys.argv[0]} conf_path *snippet_path")
        print(f"* -> optional")
        exit(1)

    snippet_path = "snippet.html"
    if len(sys.argv) == 3:
        snippet_path = sys.argv[2]

    f = open(snippet_path, "r")
    snippet = f.read()

    conf_path = sys.argv[1]
    conf = load_conf(conf_path)

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

    save_path = conf_path.split(".")[0] + ".html"
    print("Saving " + save_path)
    f = open(save_path, "w")
    f.write(snippet)
    f.close()
