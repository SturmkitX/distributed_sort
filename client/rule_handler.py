# this class provides safe rule setting methods for clients which use multi-threading
# basically, it allows the writing of the rule file only once per machine
# on a single-threaded machine it has no particular effect, but on multi-threaded ones it provides a "shield" against data corruption

import threading
import importlib.util as IU

class RuleHandler:
    generate_count = 0
    lock = threading.Lock()

    def generate_rule_file(settings):
        RuleHandler.lock.acquire()
        if RuleHandler.generate_count == 0:
            with open(settings["sort_rule"] + ".py", "wb") as fileout:
                fileout.write(settings["rule_data"])
                fileout.flush()
            module_name = settings["sort_rule"].replace("/", ".")
            while IU.find_spec(module_name) is None:
                sleep(0.01)
            RuleHandler.generate_count += 1
        RuleHandler.lock.release()
