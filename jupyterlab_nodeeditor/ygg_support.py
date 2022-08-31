# Improved version of making a JLNE-compliant dictionary from a Yggdrasil Model YAML
import yaml
from jupyterlab_nodeeditor import SocketCollection


class YggdrasilConfig:
    def __init__(self, file, node_editor=None):
        self.file = file
        with open(file, "r") as fstream:
            ygg_config = yaml.safe_load(fstream)
        self.ygg_config = ygg_config
        self.components = []
        self._n_outputs = 0  # counters for when adding default types
        self._n_inputs = 0  # counters for when adding default types
        self.sockets = set()  # tracking sockets found in the config
        self._process_config()
        if node_editor:
            self.add_to_node_editor(node_editor)

    def _process_config(self):
        if "model" in self.ygg_config:
            self.components.append(self._process_model(self.ygg_config["model"]))
        elif "models" in self.ygg_config:
            for model in self.ygg_config["models"]:
                self.components.append(self._process_model(model))
        else:
            raise RuntimeError("No models found")

        if "connections" in self.ygg_config:
            # could (should?) be used to initialize socket connections values
            # for controls?
            print("ignoring connections")

        self.sockets = tuple(self.sockets)

    def _process_inout(self, ygg_inout: dict, default_suffix: str = "") -> dict:
        input_output = {'title': ygg_inout["name"], 'key': "temp_in"+default_suffix}
        self._n_outputs = self._n_outputs + 1
        if "type" in ygg_inout:
            input_output["socket_type"] = ygg_inout["type"]
        elif "default_file" in ygg_inout:
            input_output["socket_type"] = ygg_inout["default_file"]["filetype"]
        else:
            input_output["socket_type"] = "temp_socket"+default_suffix
        return input_output

    def _process_model(self, ygg_model: dict) -> dict:

        # Setup initial dictionary to be filled
        new_dict, new_dict["inputs"], new_dict["outputs"], = {}, [], []
        sockets = set()

        # ygg config models also have language and args attributes,
        # those should probably be controls, which dont exist yet...
        # new_dicts["controls"] = []

        if "name" in ygg_model:
            new_dict["title"] = ygg_model["name"]
        else:
            new_dict["title"] = "yggdrasil_model"

        for inout_key in ["input", "output"]:
            ne_key = inout_key + "s"  # node editor always has an s
            if inout_key not in ygg_model:
                inout_key = inout_key + "s"
                if inout_key not in ygg_model:
                    continue
            inout = ygg_model[inout_key]
            if isinstance(inout, list):
                for inout_i, inout_dict in enumerate(inout):
                    new_dict[ne_key].append(self._process_inout(inout_dict, default_suffix=f"_{inout_i}"))
                    self.sockets.update((new_dict[ne_key][-1]["socket_type"],))
            else:
                new_dict[ne_key].append(self._process_inout(inout))
                self.sockets.update(new_dict[ne_key][-1])
        return new_dict

    def add_to_node_editor(self, node_editor):
        for component in self.components:
            node_editor.add_component(component)


def load_yggdrasil_sample(sample: str = "fakeplant", language: str = "python"):
    try:
        from yggdrasil.examples import yamls as ex_yamls
    except ImportError:
        raise ImportError("This functionality requires yggdrasil.")
    return YggdrasilConfig(ex_yamls[sample][language])
