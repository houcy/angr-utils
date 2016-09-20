
from ..base import *

import capstone

class AngrColorSimprocedures(NodeAnnotator):
    def __init__(self):
        super(AngrColorSimprocedures, self).__init__()
    
    def annotate_node(self, node):
        if node.obj.is_simprocedure:
            if node.obj.simprocedure_name in ['PathTerminator','ReturnUnconstrained','UnresolvableTarget']:
                node.style = 'filled'
                node.fillcolor = '#ffcccc'
            else:
                node.style = 'filled'
                node.fillcolor = '#dddddd'

class AngrColorExit(NodeAnnotator):
    def __init__(self):
        super(AngrColorExit, self).__init__()

    def annotate_node(self, node):
        if not node.obj.is_simprocedure:
            found = False
            for e in self.graph.edges:
                if e.src == node:                
                    found = True
                    if 'jumpkind' in e.meta and e.meta['jumpkind'] == 'Ijk_Ret':
                        node.style = 'filled'
                        node.fillcolor = '#ddffdd'
            if not found:
                node.style = 'filled'
                node.fillcolor = '#ddffdd'
            
class AngrColorEntry(NodeAnnotator):
    def __init__(self):
        super(AngrColorEntry, self).__init__()

    def annotate_node(self, node):
        if not node.obj.is_simprocedure:
            if hasattr(node.obj, 'function_address') and node.obj.addr == node.obj.function_address:
                node.style = 'filled'
                node.fillcolor = '#ffffcc'

class AngrColorEdgesVex(EdgeAnnotator):
    EDGECOLOR_CONDITIONAL_TRUE  = 'green'
    EDGECOLOR_CONDITIONAL_FALSE = 'red'
    EDGECOLOR_UNCONDITIONAL     = 'blue'
    EDGECOLOR_CALL              = 'black'
    EDGECOLOR_RET               = 'grey'
    EDGECOLOR_UNKNOWN           = 'yellow'

    def __init__(self):
        super(AngrColorEdgesVex, self).__init__()


    def annotate_edge(self, edge):
        vex = None
        if 'vex' in edge.src.content:
            vex = edge.src.content['vex']['vex']

        if 'jumpkind' in edge.meta:
            jk = edge.meta['jumpkind']
            if jk == 'Ijk_Ret':
                edge.color = self.EDGECOLOR_RET
            elif jk == 'Ijk_FakeRet':
                edge.color = self.EDGECOLOR_RET
                edge.style = 'dotted'
            elif jk == 'Ijk_Call':
                edge.color = self.EDGECOLOR_CALL
                if len (vex.next.constants) == 1 and vex.next.constants[0].value != edge.dst.obj.addr:
                    edge.style='dotted'
            elif jk == 'Ijk_Boring':
                if len(vex.constant_jump_targets) > 1:
                    if len (vex.next.constants) == 1:
                        if edge.dst.obj.addr == vex.next.constants[0].value:
                            edge.color=self.EDGECOLOR_CONDITIONAL_FALSE
                        else:
                            edge.color=self.EDGECOLOR_CONDITIONAL_TRUE
                    else:
                        edge.color=self.EDGECOLOR_UNKNOWN
                else:
                    edge.color=self.EDGECOLOR_UNCONDITIONAL
            else:
                #TODO warning
                edge.color = self.EDGECOLOR_UNKNOWN


class AngrPathAnnotator(EdgeAnnotator, NodeAnnotator):
    
    def __init__(self, path):
        super(AngrPathAnnotator, self).__init__()
        self.path = path
        self.trace = list(path.addr_trace)

    def set_graph(self, graph):
        super(AngrPathAnnotator, self).set_graph(graph)
        self.vaddr = self.valid_addrs()        
        ftrace = filter(lambda _: _ in self.vaddr, self.trace)
        self.edges_hit = set(zip(ftrace[:-1], ftrace[1:]))
        
            
    def valid_addrs(self):
        vaddr = set()
        for n in self.graph.nodes:
            vaddr.add(n.obj.addr)
        return vaddr
        
    #TODO add caching
    #TODO not sure if this is valid
    def node_hit(self, node):
        ck = list(node.callstack_key)
        ck.append(node.addr)
        rtrace = list(reversed(self.trace))
        
        found = True
        si = 0
        for c in reversed(ck):
            if c == None:
                break
            try: 
                si = rtrace[si:].index(c)
            except:
                found = False
                break
        return found
        
    def annotate_edge(self, edge):
        key = (edge.src.obj.addr, edge.dst.obj.addr)
        if key in self.edges_hit:
            edge.width = 3
    
    def annotate_node(self, node):
        if self.node_hit(node.obj):
            node.width = 3

