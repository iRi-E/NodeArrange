
import sys
import bpy

CYCLES = True
VRAY = not CYCLES

class NodePanel(bpy.types.Panel):
	bl_label = "Nodes"
	bl_space_type = "NODE_EDITOR"
	bl_region_type = "TOOLS"
	bl_category = "Trees"


	def draw(self, context):

		layout = self.layout
		row = layout.row()
		row.operator('node.button')
		row = layout.row()
		row.prop(bpy.context.scene,'nodemargin_x',text="Margin x")
		row = layout.row()
		row.prop(bpy.context.scene,'nodemargin_y',text="Margin y")

class NodeButton(bpy.types.Operator):

	'Show the nodes for this material'
	bl_idname = 'node.button'
	bl_label = 'Arrange nodes'

	def execute(self, context):


		nodemargin(self,context)

		return {'FINISHED'}

def nodemargin(self, context):

	values.margin_x = context.scene.nodemargin_x
	values.margin_y = context.scene.nodemargin_y
	mat = bpy.context.object.active_material
	nodes_iterate(mat)

def outputnode_search(mat): #return node/None

	if VRAY:
		for node in mat.vray.ntree.nodes:
			#print (mat.name, node)
			if node.bl_idname == 'VRayNodeOutputMaterial' and node.inputs[0].is_linked:
				return node
	else:
		for node in mat.node_tree.nodes:
			if "OUTPUT" in node.type and node.inputs[0].is_linked:
				return node

	print ("No material output node found")
	return None

###############################################################
def nodes_iterate(mat):

	nodeoutput = outputnode_search(mat)
	if nodeoutput is None:
		return None
	nodeoutput.label = str(0)
	#print ("nodeoutput:",nodeoutput)


	a = []
	a.append(nodeoutput)
	a.append(0)
	nodelist = []
	nodelist.append(a)

	nodecounter = 0
	level = 0

	while nodecounter < len(nodelist):

		basenode = nodelist[nodecounter][0]
		inputlist = (i for i in basenode.inputs if i.is_linked)
		nodecounter +=1

		for input in inputlist:

			for nlinks in input.links:

				node = nlinks.from_node
				node.label = str(int(basenode.label) + 1)
				level = int(basenode.label)

				b =[]
				b.append(node)
				b.append(level + 1)
				nodelist.append(b)

########################################
	newnodes = []
	newlevels = []

	for i, item in enumerate(reversed(nodelist)):

		#node label back to default
		item[0].label = ""
		if item[0] not in newnodes:
			newnodes.append(item[0])
			newlevels.append(item[1])
			#print (i,item[0],item[1])

	nodelist = []
	for i, item in enumerate(newnodes):
		#print ("newnodes:",i,item,newlevels[i])
		a = []
		a.append(item)
		a.append(newlevels[i])
		nodelist.append(a)

	nodelist.reverse()
	newnodes.reverse()
	newlevels.reverse()

########################################
	level = 0
	levelmax = max(newlevels) +1
	values.x_last = 0

	while level < levelmax:

		values.average_y = 0
		nodes = [x for i,x in enumerate(newnodes) if newlevels[i] == level]
		nodes_arrange(nodes, level)
		#print ("level:", level, nodes)
		level = level + 1

	return None

###############################################################
class values():
	average_y = 0
	x_last = 0
	margin_x = 100
	margin_y = 20

def nodes_arrange(nodelist, level):


#node x positions

	widthmax = max([x.dimensions.x for x in nodelist])
	xpos = values.x_last - (widthmax + values.margin_x) if level !=0 else 0
	#print ("nodelist, xpos", nodelist,xpos)
	values.x_last = xpos

#node y positions
	x = 0
	y = 0

	for node in nodelist:

		if node.hide:
			hidey = (node.dimensions.y / 2) - 8
			y = y -  hidey
		else:
			hidey = 0

		node.location.y = y
		y = y - values.margin_y - node.dimensions.y + hidey

		node.location.x = xpos

	y = y + values.margin_y

	center = (0 + y) /2
	values.average_y = center - values.average_y

	for node in nodelist:

		node.location.y -= values.average_y


def register():
	bpy.utils.register_module(__name__)
	bpy.types.Scene.nodemargin_x = bpy.props.IntProperty(default = 100,update = nodemargin)
	bpy.types.Scene.nodemargin_y = bpy.props.IntProperty(default = 20,update = nodemargin)

def unregister():
	bpy.utils.unregister_module(__name__)
	del bpy.types.Scene.nodemargin_x
	del bpy.types.Scene.nodemargin_y
if __name__ == "__main__":
	register()


