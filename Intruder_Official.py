bl_info = {
    "name": "Intrude",
    "category": "Object",
}

import bpy
import bmesh
from mathutils import Vector
from bpy import context 

class ObjectIntrude(bpy.types.Operator):
    """My Intruder Script"""
    bl_idname = "object.intrude"
    bl_label = "Intrude"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        
        scene = bpy.context.scene 

        ob = bpy.context.object
        me = ob.data

        bm = bmesh.from_edit_mesh(me)
        bm.select_mode = {'VERT', 'EDGE', 'FACE'}
        selected_edges = [e for e in bm.edges if e.select]
        selected_faces = [f for f in bm.faces if f.select]

        bmesh.ops.delete(bm, geom=selected_faces, context=5)
         
        for e in selected_edges:
            e.select = False

        edges_to_rip = [e for e in bm.edges if e.smooth and e in selected_edges]
        sharp_edges = [e for e in bm.edges if not e.smooth]
        
        edges_to_rip_verts = {v for e in edges_to_rip for v in e.verts} 
        sharp_edges_verts = {v for e in sharp_edges for v in e.verts}
       
        intersected_verts = list(set(edges_to_rip_verts).intersection(sharp_edges_verts))
        extrudable_verts = [v for v in sharp_edges_verts if v not in intersected_verts]

        ret = bmesh.ops.extrude_vert_indiv(bm, verts=extrudable_verts)
        geom_extrude = ret["verts"]
        print(ret)
        del ret
        
        verts_extrude = {ele for ele in geom_extrude if isinstance(ele, bmesh.types.BMVert)}
        
        for e in edges_to_rip:
            e.select = True
        
        bpy.ops.mesh.rip_move_fill('INVOKE_DEFAULT')
        
        for v in verts_extrude:
            v.select = True
        
        bpy.ops.mesh.edge_face_add()
        
        for e in sharp_edges:
            e.select = True
        
        selected_edges2 = [e for e in bm.edges if e.select]
        print(selected_edges2)
        
        ret = bmesh.ops.holes_fill(bm, edges=selected_edges2)
        geom_faces = ret["faces"]
        print(ret)
        del ret
        print(geom_faces)
        
        bpy.ops.mesh.fill_holes()
        for e in sharp_edges:
           e.select = False
        bmesh.update_edit_mesh(me)
            
        return {'FINISHED'} 

def register():
    bpy.utils.register_class(ObjectIntrude)
    
def unregister():
    bpy.utils.unregister_class(ObjectIntrude)
    
if __name__ == "__main__":
    register()