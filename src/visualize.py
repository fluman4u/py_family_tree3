from dataclasses import dataclass
from typing import List, Optional

from pyvis.network import Network

from .lineage import LineageSystem
from .model import Person

GEN_COLORS = [
    "#e6194b",
    "#3cb44b",
    "#ffe119",
    "#4363d8",
    "#f58231",
    "#911eb4",
    "#46f0f0",
    "#f032e6",
    "#bcf60c",
    "#fabebe",
]


@dataclass
class VisualizationConfig:
    height: str = "800px"
    width: str = "100%"
    bgcolor: str = "#ffffff"
    font_color: str = "black"


def visualize_family(
    persons: List[Person],
    output_html: str = "family.html",
    lineage_path: str = "data/lineage.yaml",
    config: Optional[VisualizationConfig] = None,
):
    lineage = LineageSystem.from_yaml(lineage_path)
    config = config or VisualizationConfig()

    net = Network(
        height=config.height,
        width=config.width,
        bgcolor=config.bgcolor,
        font_color=config.font_color,
        directed=True,
        layout=True,
    )

    net.set_options(
        """
    {
      "layout": {
        "hierarchical": {
          "enabled": true,
          "direction": "UD",
          "sortMethod": "directed",
          "levelSeparation": 150,
          "nodeSpacing": 200
        }
      },
      "physics": {
        "enabled": false
      },
      "interaction": {
        "hover": true,
        "tooltipDelay": 200
      },
      "nodes": {
        "font": {
          "size": 14
        }
      },
      "edges": {
        "arrows": {
          "to": {
            "enabled": true,
            "scaleFactor": 1
          }
        },
        "smooth": {
          "type": "cubicBezier",
          "forceDirection": "vertical"
        }
      }
    }
    """
    )

    for p in persons:
        gen = p.generation or p.depth
        color = GEN_COLORS[(gen - 1) % len(GEN_COLORS)]
        lineage_char = lineage.generation_char(gen)
        display_name = lineage.annotate_name(p.name, gen)
        label = f"{display_name}\n({p.wbs})"

        birth = p.birth_year if p.birth_year else "不详"
        death = p.death_year if p.death_year else "不详"
        note = p.note if p.note else "无"

        title = (
            f"【{p.name}】\n━━━━━━━━━━━━\nWBS: {p.wbs}\n世代: 第 {gen} 代\n"
            f"行辈: {lineage_char}\n生卒: {birth} - {death}\n备注: {note}"
        )
        net.add_node(
            p.id,
            label=label,
            title=title,
            color=color,
            shape="ellipse",
            level=gen,
        )

    node_ids = {p.id for p in persons}
    for p in persons:
        if p.parent_id and p.parent_id in node_ids:
            net.add_edge(p.parent_id, p.id)

    net.write_html(output_html)
