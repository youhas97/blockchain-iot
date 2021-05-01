import os
import json

import plotly.graph_objects as go


def load_json_to_python(filename):
  data = []
  with open(filename, 'r') as f:
    open_curly_brace_count = 0
    obj_string = ""
    for char in iter(lambda : f.read(1), ''):
      obj_string += char
      if char == '\n':
        continue
      elif char == '{':
        open_curly_brace_count += 1
      elif char == '}':
        open_curly_brace_count -= 1
      
      if open_curly_brace_count == 0:
        data.append(json.loads(obj_string))
        obj_string = ""

  return data


if __name__ == '__main__':
  file_path = os.path.dirname(os.path.realpath(__file__))
  os.chdir(os.path.abspath(os.path.join(file_path, "data")))

  drones_1_nodes_1_data = load_json_to_python("1_node_success_drone1.json")
  drones_1_nodes_1_data.sort(key=lambda p: p["fields"]["sent"])
  response_time = [time["fields"]["value"] for time in drones_1_nodes_1_data]
  
  fig = go.Figure()

  fig.add_trace(go.Scatter(x=[*range(1, len(response_time) + 1)], \
    y=response_time, 
    name="1_drone_1_node", 
    line=dict(color="royalblue", width=4)))

  fig.update_layout(title="Time until blocks are commited", \
    xaxis_title="Transaction",
    yaxis_title="Time (ms)")

  fig.show()