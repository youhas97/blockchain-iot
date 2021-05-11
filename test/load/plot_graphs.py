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
    line_width=2
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
  mean = reduce(lambda a,b: a+b, response_times)/len(response_times)
  print("{} mean time: {} ms".format(name, mean))
  box_fig.update_traces(mean=[mean], boxmean=True)
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

  plot_data(line_fig, box_fig, block_size_bar_fig, nodes4_drones4, "4 drones")
  plot_data(line_fig, box_fig, block_size_bar_fig, nodes4_drones8, "8 drones")
  plot_data(line_fig, box_fig, block_size_bar_fig, nodes4_drones16, "16 drones")
  plot_data(line_fig, box_fig, block_size_bar_fig, nodes4_drones32, "32 drones")

  plot_data(line_fig_elmo, box_fig_elmo, block_size_bar_fig_elmo, nodes4_drones32_elmo, "4 nodes, 32 drones")
  plot_data(line_fig_elmo, box_fig_elmo, block_size_bar_fig_elmo, nodes4_drones64_elmo, "4 nodes, 64 drones")
  plot_data(line_fig_elmo, box_fig_elmo, block_size_bar_fig_elmo, nodes8_drones32_elmo, "8 nodes, 32 drones")

  line_fig.update_layout(
    title=dict(
      text="Iroha response time for AWS instance using 4 nodes",
      y=0.95,
      x=0.5,
      font=dict(size=18)
    ),
    xaxis_title=dict(text="Request #", font=dict(size=16)),
    yaxis_title=dict(text="Response time (ms)", font=dict(size=16)),
    legend=dict(
      xanchor="center",
      yanchor="bottom",
      x=0.5, 
      y=-0.21,
      orientation="h",
      font=dict(size=16)
    ),
    margin=dict(
      l=5,
      r=10,
      t=45,
      b=0
    )
  )

  box_fig.update_layout(
    title=dict(
      text="Iroha response time box plots for AWS instance using 4 nodes, quartilemethod=linear",
      y=0.95,
      x=0.5,
      font=dict(size=18)
    ),
    xaxis_title=dict(text="Configuration", font=dict(size=16)),
    yaxis_title=dict(text="Response time (ms)", font=dict(size=16)),
    font=dict(size=16),
    margin=dict(
      l=5,
      r=10,
      t=45,
      b=0
    ),
    showlegend=False,
    boxgap=0
  )

  block_size_bar_fig.update_layout(
    title=dict(
      text="Average block size for AWS instance using 4 nodes",
      y=0.95,
      x=0.5,
      font=dict(size=18)
    ),
    xaxis_title=dict(text="Configuration", font=dict(size=16)),
    yaxis_title=dict(text="Block size (bytes)", font=dict(size=16)),
    font=dict(size=16),
    margin=dict(
      l=5,
      r=10,
      t=45,
      b=0
    ),
    showlegend=False
  )

  line_fig_elmo.update_layout(
    title=dict(
      text="Iroha response time for home laptop",
      y=0.95,
      x=0.5,
      font=dict(size=18)
    ),
    xaxis_title=dict(text="Request #", font=dict(size=16)),
    yaxis_title=dict(text="Response time (ms)", font=dict(size=16)),
    legend=dict(
      xanchor="center",
      yanchor="bottom",
      x=0.5, 
      y=-0.21,
      orientation="h",
      font=dict(size=16)
    ),
    margin=dict(
      l=5,
      r=10,
      t=45,
      b=0
    )
  )

  box_fig_elmo.update_layout(
    title=dict(
      text="Iroha response time box plots for home laptop, quartilemethod=linear",
      y=0.95,
      x=0.5,
      font=dict(size=18)
    ),
    xaxis_title=dict(text="Configuration", font=dict(size=16)),
    yaxis_title=dict(text="Response time (ms)", font=dict(size=16)),
    font=dict(size=16),
    margin=dict(
      l=5,
      r=10,
      t=45,
      b=0
    ),
    showlegend=False,
    boxgap=0
  )

  block_size_bar_fig_elmo.update_layout(
    title=dict(
      text="Average block size for home laptop",
      y=0.95,
      x=0.5,
      font=dict(size=18)
    ),
    xaxis_title=dict(text="Configuration", font=dict(size=16)),
    yaxis_title=dict(text="Block size (bytes)", font=dict(size=16)),
    font=dict(size=16),
    margin=dict(
      l=5,
      r=10,
      t=45,
      b=0
    ),
    showlegend=False
  )

  line_fig.write_image("aws_response_time.pdf")
  box_fig.write_image("aws_response_time_box.pdf")
  block_size_bar_fig.write_image("aws_avg_block_size.pdf")

  line_fig_elmo.write_image("laptop_response_time.pdf")
  box_fig_elmo.write_image("laptop_response_time_box.pdf")
  block_size_bar_fig_elmo.write_image("laptop_avg_block_size.pdf")

  #line_fig.write_image("test.pdf")
  #box_fig.write_image("test.pdf")
  #block_size_bar_fig.write_image("test.pdf")
  #line_fig.show()
  #box_fig.show()
  # block_size_bar_fig.show()

  # line_fig_elmo.show()
  # box_fig_elmo.show()
  # block_size_bar_fig_elmo.show()