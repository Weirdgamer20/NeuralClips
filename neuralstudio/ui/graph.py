from PySide6.QtWidgets import QGraphicsView,QGraphicsScene
from PySide6.QtGui import QBrush,QPen,QColor,QPainter
from PySide6.QtCore import Qt,QPointF
class GraphView(QGraphicsView):
    def __init__(self,parent=None):
        super().__init__(parent); self.scene=QGraphicsScene(self); self.setScene(self.scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setBackgroundBrush(QBrush(QColor("#101722"))); self.setMinimumHeight(360)
    def show_graph(self,nodes,edges):
        self.scene.clear()
        if not nodes: self.scene.addText("No graph yet. Scan a project or build a network."); return
        pos={n.id:QPointF(80+i*185,90+(i%2)*65) for i,n in enumerate(nodes)}
        for e in edges:
            if e.source in pos and e.target in pos:
                a,b=pos[e.source],pos[e.target]
                self.scene.addLine(a.x()+30,a.y()+15,b.x()-30,b.y()+15,QPen(QColor("#62a6ff"),2))
        for n in nodes:
            p=pos[n.id]
            item=self.scene.addEllipse(p.x()-30,p.y()-5,60,45,QPen(QColor("#7dd3fc"),2),QBrush(QColor("#17324b")))
            item.setZValue(1)
            label=self.scene.addText(n.label); label.setDefaultTextColor(QColor("#f2f6fc"))
            label.setPos(p.x()-42,p.y()+43); label.setZValue(2)
        self.scene.setSceneRect(self.scene.itemsBoundingRect().adjusted(-40,-40,60,60))
        self.fitInView(self.scene.sceneRect(),Qt.AspectRatioMode.KeepAspectRatio)
