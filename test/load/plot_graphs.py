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
  return data

def add_line_trace(figure, data, name):
  figure.add_trace(go.Scatter(
    x=[*range(1, len(data) + 1)],
    y=data,
    name=name,
    mode="lines",
    line=dict(width=1)
  ))

def add_box_trace(figure, data, name):
  figure.add_trace(go.Box(
    y=data,
    name=name,
    line_width=1
    ))


def add_bar_trace(figure, data, name):
  figure.add_trace(go.Bar(
    x=[name],
    y=[data]
  ))


def plot_data(line_fig, box_fig, bar_fig, data, name):
  response_times = [response["fields"]["value"] for response in data]
  add_line_trace(line_fig, response_times, name)
  add_box_trace(box_fig, response_times, name)
  print("{} average response time: {}".format(name, reduce(lambda a,b: a+b, response_times)/len(response_times)))
  avg_block_size = reduce(lambda a,b: a+b, [response["total_block_size"] for response in data])/len(data)
  add_bar_trace(bar_fig, avg_block_size, name)


if __name__ == '__main__':
  file_path = os.path.dirname(os.path.realpath(__file__))
  os.chdir(os.path.abspath(os.path.join(file_path, "data")))

  nodes4_drones4  = load_json_to_python("4_nodes_4_users_success.json")
  nodes4_drones8  = load_json_to_python("4_nodes_8_users_success.json")
  nodes4_drones16 = load_json_to_python("4_nodes_16_users_success.json")
  nodes4_drones32 = load_json_to_python("4_nodes_32_users_success.json")

  nodes4_drones32_elmo = load_json_to_python("4_nodes_32_users_success_elmedin.json")
  nodes4_drones64_elmo = load_json_to_python("4_nodes_64_users_success_elmedin.json")
  nodes8_drones32_elmo = load_json_to_python("8_nodes_32_users_success_elmedin.json")

  line_fig = go.Figure()
  block_size_bar_fig = go.Figure()
  box_fig = go.Figure()

  line_fig_elmo = go.Figure()
  block_size_bar_fig_elmo = go.Figure()
  box_fig_elmo = go.Figure()

  plot_data(line_fig, box_fig, block_size_bar_fig, nodes4_drones4, "4_nodes_4_drones")
  plot_data(line_fig, box_fig, block_size_bar_fig, nodes4_drones8, "4_nodes_8_drones")
  plot_data(line_fig, box_fig, block_size_bar_fig, nodes4_drones16, "4_nodes_16_drones")
  plot_data(line_fig, box_fig, block_size_bar_fig, nodes4_drones32, "4_nodes_32_drones")

  plot_data(line_fig_elmo, box_fig_elmo, block_size_bar_fig_elmo, nodes4_drones32_elmo, "4_nodes_32_drones")
  plot_data(line_fig_elmo, box_fig_elmo, block_size_bar_fig_elmo, nodes4_drones64_elmo, "4_nodes_64_drones")
  plot_data(line_fig_elmo, box_fig_elmo, block_size_bar_fig_elmo, nodes8_drones32_elmo, "8_nodes_32_drones")

  line_fig.update_layout(
    title="Iroha response time for AWS instance",
    xaxis_title="Request #",
    yaxis_title="Response time (ms)"
  )

  box_fig.update_layout(
    title="Iroha response time box plots for AWS instance, quartilemethod=linear",
    xaxis_title="Configuration",
    yaxis_title="Response time (ms)"
  )

  block_size_bar_fig.update_layout(
    title="Average block size for AWS instance",
    xaxis_title="Configuration",
    yaxis_title="Block size (bytes)"
  )

  line_fig_elmo.update_layout(
    title="Iroha response time for home laptop",
    xaxis_title="Request #",
    yaxis_title="Response time (ms)"
  )

  box_fig_elmo.update_layout(
    title="Iroha response time box plots for home laptop, quartilemethod=linear",
    xaxis_title="Configuration",
    yaxis_title="Response time (ms)"
  )

  block_size_bar_fig_elmo.update_layout(
    title="Average block size for home laptop",
    xaxis_title="Configuration",
    yaxis_title="Block size (bytes)"
  )

  line_fig.show()
  box_fig.show()
  block_size_bar_fig.show()

  line_fig_elmo.show()
  box_fig_elmo.show()
  block_size_bar_fig_elmo.show()