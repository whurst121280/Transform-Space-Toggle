bl_info = {
    "name": "Transform Space Toggle",
    "author": "Some guy and an LLM",
    "version": (1, 4),
    "blender": (4, 4, 3),
    "location": "View3D",
    "description": "Toggle between Local and Global transform orientations",
    "category": "3D View",
}

import bpy

addon_keymaps = []

class TRANSFORM_OT_toggle_space(bpy.types.Operator):
    bl_idname = "transform.toggle_space"
    bl_label = "Toggle Transform Space"
    bl_description = "Toggle between Local and Global transform orientations"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        slot = context.scene.transform_orientation_slots[0]
        slot.type = "GLOBAL" if slot.type == "LOCAL" else "LOCAL"
        self.report({"INFO"}, f"Transform Orientation set to {slot.type}")
        return {"FINISHED"}

class TRANSFORM_SPACE_PT_panel(bpy.types.Panel):
    bl_label = "Transform Space Toggle"
    bl_idname = "TRANSFORM_SPACE_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Item"

    def draw(self, context):
        layout = self.layout
        layout.operator("transform.toggle_space", text="Toggle Transform Space")

class TRANSFORM_SPACE_Preferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    def draw(self, context):
        layout = self.layout
        layout.label(text="To customize the hotkey for Transform Space Toggle:")
        layout.separator()
        layout.label(text="1. Go to Edit > Preferences > Keymap.")
        layout.label(text="2. Expand '3D View' > '3D View (Global)'.")
        layout.label(text="3. Click 'Add New', then:")
        layout.label(text="   - Identifier: transform.toggle_space")
        layout.label(text="   - Choose desired key, mouse, and modifiers.")
        layout.label(text="4. Save Preferences to keep it persistent.")

def register():
    bpy.utils.register_class(TRANSFORM_OT_toggle_space)
    bpy.utils.register_class(TRANSFORM_SPACE_PT_panel)
    bpy.utils.register_class(TRANSFORM_SPACE_Preferences)

    wm = bpy.context.window_manager
    if wm.keyconfigs.addon:
        km = wm.keyconfigs.addon.keymaps.new(name="3D View", space_type="VIEW_3D")
        kmi = km.keymap_items.new("transform.toggle_space", type='Q', value='PRESS', ctrl=True, shift=True)
        addon_keymaps.append((km, kmi))

def unregister():
    bpy.utils.unregister_class(TRANSFORM_OT_toggle_space)
    bpy.utils.unregister_class(TRANSFORM_SPACE_PT_panel)
    bpy.utils.unregister_class(TRANSFORM_SPACE_Preferences)

    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

if __name__ == "__main__":
    register()
