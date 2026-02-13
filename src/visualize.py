from pyvis.network import Network
from typing import List
from .model import Person
from .lineage import LineageSystem

GEN_COLORS = [
    "#e6194b", "#3cb44b", "#ffe119", "#4363d8",
    "#f58231", "#911eb4", "#46f0f0", "#f032e6",
    "#bcf60c", "#fabebe"
]


def visualize_family(
    persons: List[Person],
    output_html: str = "family.html",
    lineage_path: str = "data/lineage.yaml"
):
    lineage = LineageSystem.from_yaml(lineage_path)

    net = Network(
        height="800px",
        width="100%",
        bgcolor="#ffffff",
        font_color="black",
        directed=True,
        layout=True  # 启用布局算法
    )
    
    # 设置 hierarchical 布局选项，实现自上而下的树状结构
    net.set_options("""
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
    """)

    for p in persons:
        gen = p.generation or p.depth
        color = GEN_COLORS[(gen - 1) % len(GEN_COLORS)]
        lineage_char = lineage.generation_char(gen)
        display_name = lineage.annotate_name(p.name, gen)
        label = f"{display_name}\n({p.wbs})"
        # 美化提示框，使用换行符格式化
        birth = p.birth_year if p.birth_year else "不详"
        death = p.death_year if p.death_year else "不详"
        note = p.note if p.note else "无"
        
        title = f"【{p.name}】\n━━━━━━━━━━━━\nWBS: {p.wbs}\n世代: 第 {gen} 代\n行辈: {lineage_char}\n生卒: {birth} - {death}\n备注: {note}"
        # 设置 level 属性，确保同代节点在同一水平线
        net.add_node(
            p.id,
            label=label,
            title=title,
            color=color,
            shape="ellipse",
            level=gen  # 关键：设置层级，同代节点会在同一水平线
        )

    for p in persons:
        if p.parent_id:
            net.add_edge(p.parent_id, p.id)

    net.write_html(output_html)
