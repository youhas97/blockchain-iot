import os
import json
from functools import reduce

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

  data.sort(key=lambda x: x["fields"]["sent"])
  return [time["fields"]["value"] for time in data]

def add_line_trace(figure, data, name, color):
  figure.add_trace(go.Scatter(
    x=[*range(1, len(data) + 1)], 
    y=data, 
    name=name,
    mode="lines+markers",
    line=dict(width=1, color=color)
  ))

def add_box_trace(figure, data, name):
  figure.add_trace(go.Box(
    y=data,
    name=name,
    line_width=1
    ))


if __name__ == '__main__':
  file_path = os.path.dirname(os.path.realpath(__file__))
  os.chdir(os.path.abspath(os.path.join(file_path, "data")))

  drones_1_nodes_1_data = load_json_to_python("1_node_success_drone1.json")
  
  line_fig = go.Figure()
  box_fig = go.Figure()

  add_line_trace(line_fig, drones_1_nodes_1_data, "1_drone_1_node", "orange")
  add_box_trace(box_fig, drones_1_nodes_1_data, "1_drone_1_node")

  line_fig.update_layout(
    title="Iroha block commit time", 
    xaxis_title="Number of request",
    yaxis_title="Time (ms)"
  )

  box_fig.update_layout(
    title="Iroha block commit time box plots"
  )

  line_fig.show()
  box_fig.show()